# rewrite-engine

**Reescritura inteligente, natural y multilenguaje** — motor híbrido *offline* (diccionarios de sinónimos + WordNet/OMW + NLP) con interfaz lista para enchufar un LLM. No es un "spinner" tonto: protege entidades, valida el significado y respeta el tono.

> *Intelligent, natural, multilingual text rewriting — a hybrid offline engine (synonym dictionaries + WordNet/OMW + NLP) with an optional pluggable LLM layer.*

---

## ✨ Características

- **Híbrido y offline**: funciona 100% local y gratis (diccionarios JSON + WordNet/OMW). Sin API keys.
- **IA opcional y enchufable**: implementa `BaseTransformer` para añadir Claude, un paraphraser de HuggingFace, etc., sin tocar el núcleo.
- **Multilenguaje**: es, en, pt, fr, it, de, nl, pl, ru, uk, sv (y fácil de extender).
- **Protección de entidades**: URLs, emails, teléfonos, fechas, precios, %, SKUs/códigos, hashtags, menciones, **HTML** y markdown nunca se rompen.
- **12 modos**: `natural, formal, informal, professional, seo, marketplace, technical, simple, expanded, summarized, grammar_only, creative`.
- **Validación semántica**: embeddings multilenguaje si están disponibles; si no, similitud léxica robusta.
- **Degradación elegante**: spaCy, sentence-transformers y LanguageTool son opcionales; el motor corre sin ellos.
- **Seguridad**: avisa ante claims médicos sensibles y no los reescribe; respeta marcas y palabras protegidas.

## 📦 Instalación

```bash
# Núcleo (ligero, suficiente para reescribir):
pip install -e .

# Con WordNet/OMW (recomendado para sinónimos multilenguaje):
pip install -e ".[wordnet]"
python -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4')"

# Todo lo razonable (API, CLI, embeddings, spaCy, gramática):
pip install -e ".[all]"
```

Extras disponibles: `wordnet`, `api`, `cli`, `semantic`, `spacy`, `grammar`, `ai`, `all`, `dev`.

## 🚀 Uso (Python)

```python
from rewrite_engine import RewriteEngine, RewriteRequest

engine = RewriteEngine()
result = engine.rewrite(RewriteRequest(
    text="Necesito ayuda para arreglar este error en mi sitio web.",
    language="auto",          # o "es", "en"...
    mode="formal",
    strength=0.5,             # 0.1 mínimo … 0.9 muy creativo
    preserve_keywords=["Mananpa Labs"],
    avoid_words=[],
    return_alternatives=2,
))

print(result.rewritten)
# → "Necesito apoyo para arreglar este defecto en mi sitio web."
print(result.similarity_score, result.readability_score)
print(result.changed_words)
```

## 🖥️ CLI

```bash
rewrite-engine "Este producto es bueno y barato, cómpralo ahora." --lang es --mode marketplace --strength 0.4
echo "Buy this product now." | rewrite-engine - --lang en --mode natural
```

## 🌐 API

```bash
uvicorn rewrite_engine.api.app:app --reload
# POST http://127.0.0.1:8000/api/rewrite  (ver schema más abajo)
```

`POST /api/rewrite`:

```jsonc
// petición
{ "text": "...", "language": "auto", "mode": "natural", "strength": 0.35,
  "preserveKeywords": ["Mananpa Labs", "Shomex"], "avoidWords": [], "returnAlternatives": 3 }

// respuesta
{ "original": "...", "rewritten": "...", "alternatives": [], "language": "es",
  "similarityScore": 0.92, "readabilityScore": 0.86, "changedWords": [],
  "protectedTerms": [], "warnings": [] }
```

## 🏗️ Arquitectura

```
src/rewrite_engine/
  core/      models · config · pipeline · engine (orquestador)
  lang/      metadata · detector · protector (entidades) · tokenizer (sin pérdida)
  synonyms/  base · dict_source (JSON) · wordnet_source (OMW) · engine
  rewrite/   candidates · scorer (semántico/legibilidad) · sentence · grammar · ai_scorer · ranker
  transformers/ base (interfaz IA) · null (offline por defecto)
  api/ · cli/
data/
  dictionaries/{es,en,pt,fr,it,de,nl,pl,ru,uk,sv,...}/general.json   # editables
  protected/brands.json
```

Flujo: **detectar idioma → proteger entidades → tokenizar → generar candidatos → puntuar → reescribir por oración → (gramática/IA opcional) → restaurar → rankear**.

## ➕ Añadir idiomas y diccionarios

1. **Idioma nuevo**: añade su código y metadatos en `lang/metadata.py`
   (`DEFAULT_LANGUAGES`, stopwords, palabras función, intensificadores, spaCy
   opcional y WordNet/OMW opcional). Si quieres activarlo por entorno, usa
   `REWRITE_ENGINE_LANGUAGES=es,en,...`.
2. **Diccionario nuevo**: crea `data/dictionaries/<idioma>/general.json` (o `marketplace.json`, `legal.json`, `technical.json`) con el formato:

```json
{
  "word": "comprar", "lemma": "comprar", "pos": "VERB", "language": "es",
  "synonyms": [
    {"text": "adquirir", "formality": "formal", "frequency": 0.82,
     "contexts": ["marketplace", "legal"], "avoidContexts": ["informal"]}
  ],
  "antonyms": ["vender"]
}
```

3. **Industria nueva**: añade su nombre a `industries` en la config para cargar `data/dictionaries/<idioma>/<industria>.json`.
4. **Idiomas sin espacios claros** (p.ej. chino, japonés, tailandés): añade antes
   diccionarios y validación lingüística específica. El tokenizer ya incluye una
   segmentación Unicode conservadora para `zh`, `ja` y `th`, pero no se declaran
   idiomas de primera clase hasta tener diccionarios y pruebas de calidad.

## 🤖 Enchufar un LLM (futuro)

Implementa `rewrite_engine.transformers.base.BaseTransformer` (`available`, `refine(text, language, mode)`) y pásalo al motor:

```python
engine = RewriteEngine(transformer=MiTransformerDeClaude())
```

El motor lo usará como etapa de refinado **después** de la reescritura léxica, preservando los tokens protegidos.

## ⚠️ Limitaciones (motor offline)

- **WordNet sin embeddings introduce ruido.** Como respaldo de los diccionarios, WordNet/OMW puede ofrecer sinónimos de una acepción equivocada (mala desambiguación). Se mitiga con: prioridad a los diccionarios JSON curados, filtro de formas derivadas, lista de intensificadores intocables y limitación de acepciones. Para máxima calidad, instala `[semantic]`: los embeddings activan la **puerta semántica estricta** (≥0.88) que descarta cambios que alteran el significado.
- **La validación semántica sin embeddings es léxica.** El floor por defecto sólo atrapa divergencias casi totales; no distingue una buena paráfrasis de un cambio sutil de sentido. Con `[semantic]` la validación es real.
- **POS sin spaCy es limitado.** Sin `[spacy]`, la protección de nombres propios usa heurística (mayúscula a media frase). Instala `[spacy]` y el modelo del idioma para NER/POS de calidad.
- **Calidad por idioma desigual.** es/en tienen diccionarios más ricos; pt/fr/it/de/nl/pl/ru/uk/sv tienen diccionarios sembrados más pequeños y dependen más de WordNet/OMW. Amplía los JSON para igualar la calidad (ver sección anterior).
- **Modos `expanded`/`summarized`/`creative`** rinden mejor con un LLM enchufado (`BaseTransformer`); offline son limitados y lo advierten.

## ⚖️ Licencias

Este proyecto: **MIT**.

Material de referencia usado durante el diseño (carpeta `repos/`):

| Repo | Licencia | Uso en este proyecto |
|------|----------|----------------------|
| `humanizer-workbench` | MIT | Patrón de arquitectura por interfaces, scorer de AI-likeness. Adaptado. |
| `HUMAN-AI` | MIT | Listas lingüísticas (burned-words, tonos) por idioma. Convertidas a datos. |
| **`Humanizer` (VHumanize)** | **CC BY-NC 4.0** ⚠️ | **No comercial.** Solo se usó como *referencia conceptual*; su código **no** se copió. La lógica de WordNet aquí es una reimplementación de la API pública de NLTK. |
| `NLP` (Mayaluri) | notebook | Referencia conceptual de back-translation. |

> ⚠️ **Aviso**: no incorpores código de `Humanizer/` (VHumanize) en un producto comercial: su licencia CC BY-NC lo prohíbe. Las dependencias del motor (`nltk`, `spacy`, `wordfreq`, `sentence-transformers`, `langdetect`, `simplemma`, `beautifulsoup4`, `rapidfuzz`) son todas permisivas (MIT/Apache/BSD). `language-tool-python` es opcional (LGPL / API).

## 🧪 Tests

```bash
pip install -e ".[dev]"
pytest -q  # 54 tests en verde en el estado actual
ruff check src tests
```

GitHub Actions ejecuta `pytest` y `ruff` en Python 3.11 y 3.13.
