"""RewriteEngine: orquestador central del motor de reescritura.

Ensambla las capas (detección → protección → tokenización → candidatos →
puntuación → oración → gramática) y mueve los datos entre ellas. No contiene
lógica de negocio propia de cada capa: sólo las cablea (mismo patrón que
humanizer-workbench/core/engine.HumanizerEngine).

Funciona 100% offline. Si se le pasa un ``BaseTransformer`` disponible, lo usa
como etapa de refinado opcional, sin cambiar nada más.
"""

from __future__ import annotations

import json

import regex as re

from rewrite_engine.core.config import EngineConfig
from rewrite_engine.core.models import (
    ChangedWord,
    LanguageGuess,
    Mode,
    RewriteRequest,
    RewriteResult,
)
from rewrite_engine.core.pipeline import Pipeline
from rewrite_engine.lang.detector import LanguageDetector
from rewrite_engine.lang.protector import TextProtector
from rewrite_engine.lang.tokenizer import TokenizerLemmatizer
from rewrite_engine.rewrite.ai_scorer import AIScorer
from rewrite_engine.rewrite.candidates import CandidateGenerator
from rewrite_engine.rewrite.grammar import GrammarChecker
from rewrite_engine.rewrite.ranker import OutputRanker
from rewrite_engine.rewrite.scorer import ContextScorer
from rewrite_engine.rewrite.sentence import SentenceRewriter
from rewrite_engine.synonyms.dict_source import DictSource
from rewrite_engine.synonyms.engine import SynonymEngine
from rewrite_engine.synonyms.wordnet_source import WordNetSource
from rewrite_engine.transformers.base import BaseTransformer
from rewrite_engine.transformers.null import NullTransformer

# Floor de similitud léxica (sin embeddings): sólo evita divergencias graves.
# La similitud léxica no distingue una buena paráfrasis de un cambio de
# significado, y en textos cortos cae mucho aunque el sentido se conserve; por
# eso el floor es bajo (sólo atrapa divergencias casi totales). La puerta
# semántica estricta (>=0.88) sólo aplica cuando hay embeddings reales.
_LEXICAL_FLOOR = 0.12

_HTML_RE = re.compile(r"<[a-zA-Z/][^>]*>")

# Patrón de claims médicos sensibles (regla del prompt: no reescribir como
# afirmación médica). Heurística mínima multilenguaje.
_MEDICAL_CLAIM_RE = re.compile(
    r"\b("
    r"cura|curar|curam|cure[sn]?|heals?|elimina enfermedad|trata el cáncer|"
    r"treats?\s+\w*\s*(disease|cancer)|guérit|guérir|soigne|heilt|behandelt|"
    r"geneest|leczy|wylecza|лечит|исцеляет|лікує|зцілює|botar|läker"
    r")\b",
    re.IGNORECASE,
)


class RewriteEngine:
    """Punto de entrada principal del motor."""

    def __init__(
        self,
        config: EngineConfig | None = None,
        transformer: BaseTransformer | None = None,
    ) -> None:
        self._cfg = config or EngineConfig.load()
        cfg = self._cfg

        self._detector = LanguageDetector(cfg.languages, cfg.default_language)

        protected_literals = self._load_protected_literals()
        self._protector = TextProtector(protected_literals)

        self._tokenizer = TokenizerLemmatizer(use_spacy=cfg.use_spacy)

        sources = [
            DictSource(cfg.data_dir, industries=cfg.industries),
            WordNetSource(enabled=cfg.use_wordnet is not False),
        ]
        self._synonyms = SynonymEngine(sources)
        self._candidates = CandidateGenerator(self._synonyms, self._tokenizer.lemmatize)
        self._rewriter = SentenceRewriter(
            self._tokenizer, self._candidates, max_change_ratio=cfg.max_change_ratio
        )

        self._scorer = ContextScorer(use_embeddings=cfg.use_embeddings)
        self._ai_scorer = AIScorer(cfg.data_dir)
        self._ranker = OutputRanker(self._scorer, self._ai_scorer)
        self._grammar = GrammarChecker(enabled=cfg.use_grammar)
        self._transformer = transformer or NullTransformer()

    def set_transformer(self, transformer: BaseTransformer | None) -> None:
        """Cambia el backend de refinado (IA) en caliente, sin recrear el motor.

        Usado por la GUI/CLI para el toggle de IA: activar/desactivar no
        recarga diccionarios ni WordNet, sólo sustituye esta etapa opcional.
        ``None`` restaura el comportamiento 100% offline (``NullTransformer``).
        """
        self._transformer = transformer or NullTransformer()

    @property
    def transformer(self) -> BaseTransformer:
        return self._transformer

    # -- carga de datos -----------------------------------------------------
    def _load_protected_literals(self) -> list[str]:
        """Marcas + términos legales/médicos a proteger literalmente."""
        protected_dir = self._cfg.data_dir / "protected"
        files = {
            "brands.json": "brands",
            "legal_terms.json": "terms",
            "medical_terms.json": "terms",
        }
        literals: list[str] = []
        for filename, key in files.items():
            path = protected_dir / filename
            if not path.exists():
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            if isinstance(data, dict):
                data = data.get(key, [])
            literals.extend(str(b) for b in data if str(b).strip())
        return literals

    # -- API pública --------------------------------------------------------
    def rewrite(self, request: RewriteRequest) -> RewriteResult:
        """Reescribe el texto de la petición y devuelve un resultado completo."""
        original = request.text
        mode = request.normalized_mode()
        strength = request.clamped_strength()

        guess: LanguageGuess = self._detector.detect(
            original, force=request.language
        )
        lang = guess.language

        pipeline = Pipeline.build(
            mode,
            has_transformer=self._transformer.available,
            has_grammar=self._grammar.available,
        )

        warnings: list[str] = []
        self._preflight_warnings(original, mode, warnings)

        # Seguridad: ante un posible claim médico, NO se reescribe (evita
        # convertirlo en una afirmación médica). Sólo se avisa.
        medical = bool(_MEDICAL_CLAIM_RE.search(original))
        if medical:
            return RewriteResult(
                original=original,
                rewritten=original,
                language=lang,
                similarity_score=1.0,
                readability_score=self._scorer.readability(original),
                warnings=warnings,
                mode=mode,
            )

        sensitive = mode == Mode.TECHNICAL
        creative = mode == Mode.CREATIVE
        threshold = (
            self._cfg.similarity_threshold(sensitive=sensitive, creative=creative)
            if self._scorer.uses_embeddings
            else _LEXICAL_FLOOR
        )
        target_ratio = min(self._cfg.max_change_ratio, strength)

        # Construye un pool de variantes (la solicitada + vecinas si se piden
        # alternativas) y deja que el OutputRanker elija la mejor que conserve el
        # significado por encima del umbral.
        pool = self._variant_pool(
            original, lang, request, mode, strength, pipeline,
            n_extra=request.return_alternatives,
        )
        ranked = self._ranker.rank(
            original, pool, lang=lang,
            target_ratio=target_ratio, similarity_floor=threshold,
        )

        if not ranked:
            # Ninguna variante superó la puerta semántica: devuelve el original.
            best_sim = self._scorer.similarity(original, pool[0][0]) if pool else 1.0
            warnings.append(
                f"Reescritura descartada: la similitud ({best_sim:.2f}) cayó por "
                f"debajo del umbral ({threshold:.2f}). Se devuelve el original."
            )
            rewritten, changes, protected = original, [], (pool[0][2] if pool else [])
            similarity, readability = 1.0, self._scorer.readability(original)
            alternatives: list[str] = []
        else:
            best = ranked[0]
            rewritten, changes, protected = best.text, best.changes, best.protected
            similarity, readability = best.similarity, best.readability
            alternatives = [
                r.text for r in ranked[1:]
                if r.text.strip() != rewritten.strip()
                and r.text.strip() != original.strip()
            ][: request.return_alternatives]
            if rewritten.strip() == original.strip():
                warnings.append(
                    "No se encontró una mejora con la configuración actual; se "
                    "devuelve el texto original."
                )

        # Modo resumido: reduce el texto ya reescrito a sus oraciones clave
        # (extractivo, offline). Mayor intensidad → resumen más corto.
        if mode == Mode.SUMMARIZED and rewritten.strip():
            from rewrite_engine.rewrite.summarizer import summarize

            ratio = max(0.25, min(0.75, 1.0 - strength))
            short = summarize(rewritten, lang=lang, ratio=ratio)
            if short.strip() and short.strip() != rewritten.strip():
                rewritten = short
                changes = []  # las posiciones ya no aplican tras recortar
                readability = self._scorer.readability(rewritten)
                similarity = self._scorer.similarity(original, rewritten)
                alternatives = [summarize(a, lang=lang, ratio=ratio) for a in alternatives]
            else:
                warnings.append("El texto es demasiado corto para resumirlo.")

        return RewriteResult(
            original=original,
            rewritten=rewritten,
            language=lang,
            alternatives=alternatives,
            similarity_score=similarity,
            readability_score=readability,
            changed_words=changes,
            protected_terms=sorted({p for p in protected}),
            warnings=warnings,
            mode=mode,
        )

    # -- preflight ----------------------------------------------------------
    def _preflight_warnings(self, text: str, mode: Mode, warnings: list[str]) -> None:
        from rewrite_engine.core.models import LLM_PREFERRED_MODES

        if mode in LLM_PREFERRED_MODES and not self._transformer.available:
            warnings.append(
                f"El modo '{mode}' rinde mejor con un transformer/LLM; el "
                f"resultado offline es limitado."
            )
        if not self._synonyms.has_lexical_source:
            warnings.append(
                "Sin fuentes de sinónimos disponibles (instala el extra [wordnet] "
                "o añade diccionarios JSON); la reescritura será mínima."
            )
        if _MEDICAL_CLAIM_RE.search(text):
            warnings.append(
                "Posible claim médico sensible. No se reescribe como afirmación "
                "médica; verifica el contenido."
            )

    # -- despacho plano / HTML ---------------------------------------------
    def _dispatch(
        self, text, lang, request, mode, strength, pipeline
    ) -> tuple[str, list[ChangedWord], list[str]]:
        if _HTML_RE.search(text):
            return self._rewrite_html(text, lang, request, mode, strength, pipeline)
        return self._rewrite_plain(text, lang, request, mode, strength, pipeline)

    def _rewrite_plain(
        self, text, lang, request, mode, strength, pipeline
    ) -> tuple[str, list[ChangedWord], list[str]]:
        masked, terms = self._protector.protect(
            text, extra_terms=request.preserve_keywords
        )
        avoid = frozenset(w.lower() for w in request.avoid_words)
        preserve = frozenset(w.lower() for w in request.preserve_keywords)

        parts = self._tokenizer.split_sentences(masked)
        changes: list[ChangedWord] = []
        word_offset = 0
        rebuilt: list[str] = []
        for i, part in enumerate(parts):
            if i % 2 == 1:  # separador entre oraciones
                rebuilt.append(part)
                continue
            if not part.strip():
                rebuilt.append(part)
                continue
            new_part, sent_changes = self._rewriter.rewrite(
                part, lang=lang, mode=mode, strength=strength,
                preserve=preserve, avoid_words=avoid, word_offset=word_offset,
            )
            word_offset += SentenceRewriter.count_words(part, self._tokenizer, lang=lang)
            changes.extend(sent_changes)
            rebuilt.append(new_part)

        result = "".join(rebuilt)

        if pipeline.grammar_fix:
            result = self._grammar.correct(result, lang)
        if pipeline.transformer_refine and self._transformer.available:
            result = self._transformer.refine(result, language=lang, mode=mode)

        restored = self._protector.restore(result, terms)
        return restored, changes, [t.original for t in terms]

    def _rewrite_html(
        self, text, lang, request, mode, strength, pipeline
    ) -> tuple[str, list[ChangedWord], list[str]]:
        try:
            from bs4 import BeautifulSoup, NavigableString
        except ImportError:
            # Sin bs4 no arriesgamos romper el HTML: tratamos como texto plano
            # protegiendo las etiquetas.
            return self._rewrite_plain(text, lang, request, mode, strength, pipeline)

        soup = BeautifulSoup(text, "html.parser")
        all_changes: list[ChangedWord] = []
        all_protected: list[str] = []
        skip_parents = {"script", "style", "code", "pre"}

        for node in list(soup.find_all(string=True)):
            if not isinstance(node, NavigableString):
                continue
            if node.parent and node.parent.name in skip_parents:
                continue
            chunk = str(node)
            if not chunk.strip():
                continue
            new_chunk, changes, protected = self._rewrite_plain(
                chunk, lang, request, mode, strength, pipeline
            )
            if new_chunk != chunk:
                node.replace_with(new_chunk)
            all_changes.extend(changes)
            all_protected.extend(protected)

        return str(soup), all_changes, all_protected

    # -- pool de variantes --------------------------------------------------
    def _variant_pool(
        self, text, lang, request, mode, strength, pipeline, *, n_extra: int
    ) -> list[tuple[str, list[ChangedWord], list[str]]]:
        """Genera variantes para que el ranker elija la mejor.

        Siempre incluye la intensidad solicitada (primera). Si se piden
        alternativas, añade variantes a distintas intensidades para dar opciones.
        """
        pool = [self._dispatch(text, lang, request, mode, strength, pipeline)]
        if n_extra <= 0:
            return pool

        seen = {pool[0][0].strip()}
        for delta in (0.2, -0.15, 0.35, -0.25, 0.5):
            if len(pool) >= n_extra + 1:
                break
            alt_strength = max(0.1, min(0.9, strength + delta))
            if alt_strength == strength:
                continue
            variant = self._dispatch(text, lang, request, mode, alt_strength, pipeline)
            key = variant[0].strip()
            if key in seen:
                continue
            seen.add(key)
            pool.append(variant)
        return pool
