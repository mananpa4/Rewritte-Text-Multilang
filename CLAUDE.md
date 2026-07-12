# CLAUDE.md

Guía permanente del proyecto para Claude Code. Contiene información estable
(arquitectura, tecnologías, convenciones, comandos). El **estado vivo** del
desarrollo (tareas, decisiones, pendientes) vive en `CLAUDE_CONTEXT.md`.

> ⚠️ **REGLA OBLIGATORIA:** Antes de realizar cualquier cambio importante, **lee
> primero `CLAUDE_CONTEXT.md`** para conocer el estado actual, las decisiones ya
> tomadas y los problemas conocidos. Al terminar tareas relevantes o tomar
> decisiones técnicas, **actualiza `CLAUDE_CONTEXT.md`** para mantenerlo
> sincronizado con la realidad del código.

---

## 1. Qué es el proyecto

`rewrite-engine` es un **módulo Python de reescritura inteligente, natural y
multilenguaje**. No es un "spinner" tonto: es un **motor híbrido** que combina
diccionarios de sinónimos curados, WordNet/OMW y procesamiento NLP, con
validación de significado y protección de entidades. Funciona **100% offline y
gratis** (sin API keys), y expone una interfaz (`BaseTransformer`) para
**enchufar un LLM** opcional sin reescribir el núcleo.

Objetivo: reescribir texto preservando el significado pero mejorando estilo,
naturalidad y tono, en varios idiomas y modos (formal, marketplace, SEO, etc.),
sin romper URLs, precios, marcas ni HTML.

Origen: se construyó a partir de `prompt.txt` (recopilación de prompts de varias
IAs; el de ChatGPT define la arquitectura más completa) y 4 repos de referencia
en `repos/` (ver §8 Licencias).

## 2. Tecnologías

- **Lenguaje:** Python ≥ 3.11 (usa `StrEnum`, `match`, type hints modernos).
- **Build/empaquetado:** Hatchling (`pyproject.toml`, layout `src/`).
- **Núcleo (dependencias ligeras, siempre):** `langdetect`, `wordfreq`,
  `simplemma`, `regex`, `beautifulsoup4`, `rapidfuzz`, `pydantic`, `pyyaml`.
- **Extras opcionales** (degradación elegante si faltan):
  - `[wordnet]` → `nltk` (WordNet + OMW) — sinónimos multilenguaje.
  - `[api]` → `fastapi`, `uvicorn`.
  - `[cli]` → `click`, `rich`.
  - `[semantic]` → `sentence-transformers` (embeddings multilenguaje).
  - `[spacy]` → `spacy` (POS/NER por idioma).
  - `[grammar]` → `language-tool-python`.
  - `[ai]` → `anthropic` (gancho LLM en la nube, **no cableado todavía**).
  - `[ai-paraphrase]` → `transformers` + `torch` + `sentencepiece` (T5 local + puente de traducción MarianMT, **sí cableados**: toggles opt-in en GUI/CLI. El T5 solo entiende inglés; el puente de traducción lo extiende a los 12 idiomas).
  - `[desktop]` → `pyspellchecker` (corrector de la app de escritorio).
  - `[build-exe]` → `pyinstaller`.
  - `[dev]` → `pytest`, `ruff`.
- **Idiomas soportados de fábrica:** es, en, pt, fr, it, de, nl, pl, ru, uk, sv, eo
  (Esperanto, con lematizador por reglas en `lang/esperanto.py`).

## 3. Arquitectura

Diseño por **capas con interfaces** (cada capa depende de una abstracción, no de
una implementación → componentes opcionales y LLM enchufables). Orquestador
central: `RewriteEngine`.

Flujo de `RewriteEngine.rewrite(request)`:

```
detectar idioma → proteger entidades → tokenizar (sin pérdida) →
generar candidatos → puntuar → reescribir por oración →
(gramática / IA opcional) → restaurar entidades → rankear variantes
```

Capas y archivos clave:

| Capa | Archivo | Responsabilidad |
|------|---------|-----------------|
| Orquestador | `core/engine.py` | Cablea todo; gate semántico; HTML; medical guard |
| Modelos | `core/models.py` | `RewriteRequest`, `RewriteResult`, `Mode`, dataclasses |
| Config | `core/config.py` | Defaults + YAML + entorno; umbrales; rutas de datos |
| Pipeline | `core/pipeline.py` | Qué etapas corren según modo/recursos |
| Idioma | `lang/metadata.py` | Idiomas soportados, aliases, stopwords, función, spaCy/WordNet |
| Idioma | `lang/detector.py` | Detección (langdetect + fallback heurístico) |
| Idioma | `lang/protector.py` | Protege URLs/precios/marcas/HTML… vía tokens (1 pasada) |
| Idioma | `lang/tokenizer.py` | Tokenización **sin pérdida** + lematización (simplemma/spaCy) + `analyze()` (POS+morfología) |
| Idioma | `lang/morphology.py` | Concordancia morfológica: reflexiona el reemplazo (género/número en ADJ, conjugación regular presente-3ª en VERB) usando `token.morph` de spaCy |
| Sinónimos | `synonyms/dict_source.py` | Diccionarios JSON por idioma/industria |
| Sinónimos | `synonyms/wordnet_source.py` | WordNet/OMW vía NLTK (reimplementado) |
| Sinónimos | `synonyms/engine.py` | Combina fuentes; filtra por modo/formalidad/contexto |
| Reescritura | `rewrite/candidates.py` | Elegibilidad + candidatos (filtra derivadas, frecuencia) |
| Reescritura | `rewrite/scorer.py` | Similitud semántica (embeddings/léxica) + legibilidad |
| Reescritura | `rewrite/ai_scorer.py` | "AI-likeness" 0–100 multilenguaje (burned-words) |
| Reescritura | `rewrite/sentence.py` | Reescribe por oración (dithering determinista) |
| Reescritura | `rewrite/grammar.py` | LanguageTool opcional (no-op si falta) |
| Reescritura | `rewrite/ranker.py` | Elige mejor variante + ordena alternativas |
| IA | `transformers/base.py` | Interfaz `BaseTransformer` (gancho LLM) |
| IA | `transformers/null.py` | `NullTransformer` (offline por defecto) |
| IA | `transformers/_guards.py` | Guardas compartidas (tokens protegidos, longitud, repetición degenerada) + defensa `torchvision` a nivel de módulo |
| IA | `transformers/t5_paraphraser.py` | `T5ParaphraserTransformer` opt-in: T5 local, sólo inglés |
| IA | `transformers/translation_bridge.py` | `TranslationBridgeTransformer`: envuelve un transformer inglés-only y lo extiende a los 12 idiomas vía MarianMT (traduce ida y vuelta) |
| Reescritura | `rewrite/summarizer.py` | Resumen extractivo offline (modo `summarized`) |
| API | `api/app.py` | FastAPI `POST /api/rewrite`, `GET /health` |
| CLI | `cli/main.py` | Comando `rewrite-engine` (Click) |
| Escritorio | `desktop/app.py` | App Tkinter de 2 paneles + `desktop/spell.py` (corrector) |
| Idioma | `lang/esperanto.py` | Lematizador por reglas de Esperanto (idioma súper regular) |

**Principio transversal:** todo lo pesado (spaCy, embeddings, LanguageTool,
WordNet) es opcional y **degrada con gracia** (try/except import → fallback). El
motor corre solo con el núcleo ligero.

## 4. Estructura de carpetas

```
.
├── pyproject.toml              # paquete, extras, scripts, config de tests/ruff
├── README.md                   # documentación de usuario (instalación, uso, licencias)
├── CLAUDE.md                   # este archivo (info permanente)
├── CLAUDE_CONTEXT.md           # memoria viva (estado del desarrollo)
├── prompt.txt                  # prompts originales que motivaron el proyecto
├── src/rewrite_engine/         # código del paquete (ver §3)
│   ├── core/  lang/  synonyms/  rewrite/  transformers/  api/  cli/  desktop/
│   └── data/                   # (en wheel) copia de /data empaquetada
├── data/                       # datos editables (fuente en desarrollo)
│   ├── dictionaries/{es,en,pt,fr,it,de,nl,pl,ru,uk,sv,eo}/...
│   ├── ai_markers/burned_words.json
│   └── protected/{brands,legal_terms,medical_terms}.json
├── scripts/build_burned_words.py   # convierte HumanAI *.md → burned_words.json
├── scripts/build_thesaurus.py      # convierte un tesauro de texto plano → JSON
├── packaging/                  # spec de PyInstaller + entry point del .exe
├── examples/demo.py            # demo ejecutable es/en
├── tests/                      # pytest (los 20 casos obligatorios del prompt + regresiones)
└── repos/                      # repos de referencia (NO son código del proyecto)
```

Nota sobre `data/`: en desarrollo se lee de `<repo>/data`; en un wheel instalado
se lee de `rewrite_engine/data` (incluido vía `force-include` en `pyproject.toml`).
La detección está en `core/config.py` (`DATA_DIR`).

## 5. Comandos

```bash
# Instalación (desarrollo)
pip install -e ".[wordnet,api,cli,dev]"
python -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4')"

# Calidad máxima (embeddings, spaCy, gramática)
pip install -e ".[all]"

# Ejecutar / probar
python examples/demo.py                 # demo end-to-end
pytest -q                               # suite completa
pytest -m "not integration" -q          # sin dependencias pesadas
ruff check src/ tests/                  # lint

# CLI
rewrite-engine "Este producto es bueno y barato." --lang es --mode marketplace --explain
echo "Buy this now." | rewrite-engine - --lang en --json

# CLI con IA (T5 local, opt-in, sólo inglés)
pip install -e ".[ai-paraphrase]"
rewrite-engine "I need help to fix this error." --lang en --ai --explain

# CLI con IA + puente de traducción (extiende la IA a los 12 idiomas)
rewrite-engine "Necesito ayuda para arreglar este error." --lang es --ai --ai-translate --explain

# App de escritorio (dos paneles + corrector ortográfico)
pip install -e ".[desktop]"
rewrite-engine-gui                               # GUI Tkinter

# Generar el ejecutable .exe (Windows)
pip install -e ".[build-exe]"
pyinstaller packaging/rewrite_engine_gui.spec --noconfirm   # -> dist/RewriteEngine.exe

# Enriquecer un idioma desde un tesauro de texto (palabra; sin1, sin2, ...)
python scripts/build_thesaurus.py repos/repos-new/sinonimos.txt --lang es --out data/dictionaries/es/thesaurus.json

# API
uvicorn rewrite_engine.api.app:app --reload      # http://127.0.0.1:8000

# Empaquetado
python -m build --wheel                 # genera dist/*.whl (incluye data/)

# Regenerar marcadores de IA desde HumanAI
python scripts/build_burned_words.py repos/HumanAI-main/shared/burned-words.md --out data/ai_markers/burned_words.json
```

En Windows, fuerza UTF-8 al ejecutar scripts con acentos: `PYTHONUTF8=1`.

## 6. Convenciones de código

- **Idioma de comentarios y docstrings:** español (consistente en todo el repo).
- **Estilo:** type hints en todo; `from __future__ import annotations` en módulos
  de implementación; dataclasses para los modelos (no pydantic en el núcleo —
  pydantic solo en la capa API).
- **Regex:** usar el paquete `regex` (no `re`) por soporte Unicode (`\p{L}`).
- **Determinismo:** la reescritura **no usa azar** (dithering determinista en
  `sentence.py`, `DetectorFactory.seed = 0`) para que los tests sean reproducibles.
- **Degradación elegante:** cualquier dependencia opcional se carga con
  try/except y tiene fallback; nunca romper si falta.
- **Tokens protegidos:** formato `PROTECTEDTOKEN<n>X`; nunca deben alterarse ni
  contarse como palabras.
- **Líneas:** máx. 100 (configurado en ruff). Target `py311`.
- **Datos:** los diccionarios son JSON editables con el formato de
  `data/dictionaries/<lang>/general.json`; añadir idiomas = actualizar
  `lang/metadata.py` + añadir JSON. `lang/tokenizer.py` ya tiene segmentación
  Unicode conservadora para `zh`, `ja` y `th`, pero esos idiomas no deben
  declararse de primera clase sin diccionarios y pruebas de calidad.

## 7. Reglas de trabajo para Claude

1. **Lee `CLAUDE_CONTEXT.md` antes de cualquier cambio importante** y
   actualízalo al terminar tareas relevantes o tomar decisiones técnicas.
2. **Respeta la licencia de las repos de referencia** (ver §8): NO copiar código
   de `repos/Humanizer-main` (CC BY-NC, no comercial); reimplementar o usar las
   repos MIT.
3. **No rompas la degradación elegante:** toda dependencia nueva debe ser
   opcional con fallback, salvo que se acuerde lo contrario.
4. **Mantén el determinismo** del motor (sin `random` sin seed) para no romper
   tests.
5. **Verifica con `pytest -q`** tras cualquier cambio; los 20 casos del prompt
   (protección de entidades, idiomas, modos, HTML, gate semántico) deben seguir
   en verde.
6. **No cablees llamadas a un LLM** sin pedirlo explícitamente: el gancho es
   `BaseTransformer`; el comportamiento por defecto es offline.
7. **Seguridad de contenido:** no reescribir claims médicos como afirmaciones
   médicas; preservar marcas, precios, datos legales/médicos protegidos.
8. Reescribe el código en el estilo del que lo rodea (comentarios en español,
   type hints, dataclasses).

## 8. Licencias (importante)

- **Este proyecto:** MIT.
- **`repos/Humanizer-main` (VHumanize): CC BY-NC 4.0 — NO comercial.** Su código
  **no se copia**; solo se usó como referencia conceptual.
- **`repos/HumanAI-main`** (MIT) y **`repos/humanizer-workbench-main`** (MIT): sí
  reutilizables. Se usaron como esqueleto de arquitectura y fuente de datos
  lingüísticos.
- Dependencias del motor: todas permisivas (MIT/Apache/BSD). `language-tool-python`
  es opcional (LGPL / API).
