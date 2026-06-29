# CLAUDE_CONTEXT.md — Memoria viva del proyecto

Estado dinámico del desarrollo. Se actualiza periódicamente. Para info estable
(arquitectura, comandos, convenciones) ver `CLAUDE.md`.

- **Última actualización:** 2026-06-28
- **Versión:** 0.1.0
- **Estado general:** ✅ MVP funcional y verificado. Núcleo offline completo,
  API + CLI operativas, 54 tests en verde, wheel empaquetable.

---

## 1. Estado actual del desarrollo

El motor `rewrite_engine` está **completo a nivel MVP** según el plan de 6 fases
(todas cerradas). Funciona 100% offline con diccionarios + WordNet/OMW. La capa
de IA existe como interfaz pero **no está cableada** a ningún LLM (es el siguiente
paso opcional).

Idiomas de primera clase actuales: **es, en, pt, fr, it, de, nl, pl, ru, uk, sv**.
Los metadatos de idioma viven centralizados en `src/rewrite_engine/lang/metadata.py`.

Entorno verificado: Python 3.13 (miniconda) en Windows. Dependencias instaladas
en desarrollo: núcleo + `nltk` (con corpora wordnet/omw descargados) + `[api]` +
`[cli]` + `pytest`. **No instalados en el shell actual:** `ruff`,
`sentence-transformers` (embeddings), `spacy`, `language-tool-python` → el motor
corre por sus fallbacks.

## 2. Funcionalidades implementadas ✅

- **Detección de idioma** (`langdetect` + fallback heurístico por stopwords) para
  11 idiomas sembrados.
- **Protección de entidades** (1 sola pasada regex): URLs, emails, teléfonos,
  fechas, precios, %, SKUs/códigos, hashtags, menciones, HTML, markdown, marcas
  y `preserve_keywords`. Restauración exacta.
- **Protección de literales** desde `data/protected/`: marcas + términos legales
  + médicos.
- **Tokenización sin pérdida** + lematización (simplemma; spaCy si está).
  Incluye segmentación Unicode conservadora para `zh`, `ja` y `th` cuando se
  fuerzan explícitamente, sin declararlos todavía como idiomas de primera clase.
- **Sinónimos híbridos:** diccionarios JSON (es/en ricos; pt/fr/it/de/nl/pl/ru/uk/sv
  básicos) + WordNet/OMW como respaldo. Filtrado por modo/formalidad/contexto de
  industria.
- **Diccionarios de industria:** `marketplace.json` y `technical.json` sembrados
  para nl/pl/ru/uk/sv, además de los existentes es/en.
- **Generación de candidatos** con reglas de naturalidad: salta función,
  intensificadores, nombres propios (heurística), formas derivadas
  (product/production, prodotto/produzione), frecuencia mínima.
- **Reescritura por oración** con presupuesto de cambio determinista (dithering)
  según `strength`; preserva mayúsculas y espaciado.
- **12 modos** (`Mode`): natural, formal, informal, professional, seo,
  marketplace, technical, simple, expanded, summarized, grammar_only, creative.
- **Validación semántica:** embeddings si `[semantic]`; si no, similitud léxica
  (jaccard unigramas+bigramas). Puerta semántica con umbral.
- **AI-likeness scorer** 0–100 multilenguaje (burned-words/fillers/intensifiers).
- **OutputRanker:** elige la mejor variante y ordena alternativas con métricas.
- **Legibilidad** heurística multilenguaje.
- **Seguridad:** claims médicos no se reescriben (solo avisan); se amplió la
  heurística de claims para los idiomas nuevos. `avoid_words` nunca aparecen;
  reversión a original si la similitud cae bajo el umbral.
- **HTML:** reescribe nodos de texto visibles con BeautifulSoup, etiquetas
  intactas; salta `script/style/code/pre`.
- **API FastAPI:** `POST /api/rewrite` (schema camelCase del prompt) + `/health`.
- **CLI** (`rewrite-engine`): archivo/stdin/texto literal, `--json`, `--explain`,
  `--output`, alternativas.
- **CI:** GitHub Actions ejecuta `pytest` + `ruff` en Python 3.11 y 3.13.
- **Empaquetado:** wheel con los 29 JSON de datos incluidos (última revalidación
  previa con 19 archivos; falta revalidar wheel si se va a publicar este estado).
- **Tests:** 54 pasando, cubren los 20 casos obligatorios del prompt y regresiones
  para idiomas nuevos, diccionarios de industria, segmentación CJK/Thai y aliases.

## 3. Funcionalidades en progreso 🚧

- (ninguna activa) — el MVP está cerrado. Las mejoras de §6 son opcionales y no
  iniciadas.

## 4. Tareas pendientes / backlog 📋

Prioridad sugerida de mayor a menor:

1. **Activar embeddings** (`pip install -e ".[semantic]"`) y verificar que la
   puerta estricta ≥0.88 mejora la calidad y filtra el ruido de WordNet.
2. **Implementar un `BaseTransformer` real** (`transformers/anthropic.py` con
   Claude, o `hf_paraphraser.py`) como etapa de refinado opcional. Hoy solo
   existe `NullTransformer`. (Respetar: no romper offline por defecto.)
3. **Ampliar diccionarios** pt/fr/it/de/nl/pl/ru/uk/sv para igualar la calidad
   de es/en. Ya existen `marketplace` y `technical` para nl/pl/ru/uk/sv; faltan
   industrias legal/marketing/salud/educación y ampliar pt/fr/it/de.
4. **Modos `expanded`/`summarized`/`creative`**: hoy degradan a heurística;
   requieren LLM para resultados buenos.
5. **Modo SEO avanzado**: meta title/description opcionales, variantes semánticas.
6. **Modo marketplace avanzado**: generación de bullets de beneficios.
7. **Empaquetado/CI avanzado:** añadir job de build wheel y, si conviene, matriz
   opcional con `[wordnet]`.
8. **Back-translation opcional** (MarianMT) como capa adicional (referencia:
   `repos/NLP-main`).
9. Tests de integración marcados `@pytest.mark.integration` para spaCy/embeddings.

## 5. Decisiones técnicas tomadas

- **Stack Python**, motor **híbrido offline con IA opcional** (decisión del
  usuario). Esqueleto inspirado en `humanizer-workbench` (MIT); datos lingüísticos
  de `HumanAI` (MIT). **NO se copió** `Humanizer` (CC BY-NC, no comercial).
- **Dataclasses planas en el núcleo** (no pydantic) → núcleo testeable sin
  dependencias del servidor; pydantic solo en la API.
- **Una sola pasada en el protector** (regex combinada con alternativas por
  prioridad) para evitar re-emparejar tokens ya protegidos.
- **Tokenización sin pérdida** (spans word/prot/other) para preservar espaciado y
  puntuación al reconstruir.
- **Dithering determinista** (sin azar) para reescritura reproducible.
- **Floor de similitud léxica = 0.12** (no 0.25): sin embeddings, la similitud
  léxica cae mucho en textos cortos aunque el sentido se conserve; el floor solo
  atrapa divergencias casi totales. La puerta estricta (≥0.88) solo aplica con
  embeddings reales.
- **DictSource carga TODOS los `.json`** del idioma por defecto (general +
  industrias); el filtrado por contexto decide su uso.
- **Búsqueda de sinónimos por lema Y forma de superficie** (`candidates.py`):
  algunos lematizadores (simplemma en sv: `hjälp→hjälpa`) devuelven un lema que
  no coincide con la clave del diccionario; probar también la palabra original lo
  rescata. Robustece todos los idiomas ante lematización imprecisa.
- **WordNet limitado a 2 synsets sin POS, 4 con POS**; filtro de formas derivadas
  (prefijo compartido ≥4) para reducir ruido.
- **Intensificadores intocables** (muy/very/molto…) para evitar
  `very→identical` y similares.
- **Datos dentro del paquete** (`force-include` data → `rewrite_engine/data`) con
  fallback a `<repo>/data` en desarrollo.
- **Metadatos de idioma centralizados** en `lang/metadata.py`: aliases regionales,
  idiomas por defecto, stopwords del detector, palabras función/intensificadores,
  modelos spaCy opcionales y códigos WordNet/OMW. Esto evita añadir un idioma en
  config sin sus filtros de seguridad.
- **CJK/Thai no son primera clase todavía**: `TokenizerLemmatizer.spans(...,
  lang="zh|ja|th")` segmenta corridas Han/Hiragana/Katakana/Thai por clusters
  Unicode y preserva texto/tokens protegidos. Falta añadir diccionarios, pruebas
  semánticas y quizá segmentadores reales antes de activarlos en `DEFAULT_LANGUAGES`.

## 6. Problemas conocidos ⚠️

- **Ruido de WordNet sin embeddings:** en pt/it/fr/nl/pl/ru/uk/sv puede dar
  sinónimos de acepción equivocada (mala WSD), p.ej. `produto→bem`. Mitigado con
  filtros y diccionarios locales, pero la solución real es instalar `[semantic]`.
  Documentado en README §Limitaciones.
- **Validación semántica léxica** no distingue paráfrasis buena de cambio sutil de
  sentido; es un proxy. Mejora con embeddings.
- **POS sin spaCy:** la protección de nombres propios es heurística (mayúscula a
  media frase); puede fallar en nombres propios sentence-initial.
- **Fluidez fina:** combinaciones como "muy excelente" (es) no se corrigen sin
  LanguageTool ni LLM.
- **`product→merchandise`** y similares: sinónimos válidos pero a veces poco
  naturales en contexto; aceptable para un motor offline.
- **Warnings en consola Windows:** usar `PYTHONUTF8=1` para evitar mojibake (solo
  display; los strings internos son UTF-8 correctos).

## 7. Próximos pasos recomendados

1. Si se busca **calidad**: instalar `[semantic]` y medir mejora; luego decidir si
   se cablea un LLM (`BaseTransformer`).
2. Si se busca **cobertura de idiomas**: ampliar los JSON de pt/fr/it/de/nl/pl/ru/uk/sv
   y crear diccionarios por industria legal/marketing/salud/educación.
3. Si se busca **producto**: API de meta-tags SEO + bullets marketplace + UI web.
4. Añadir job de **build wheel** al CI antes de publicar releases.

## 8. Cómo retomar en una sesión nueva

```bash
cd <repo>
pip install -e ".[wordnet,api,cli,dev]"
python -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4')"
PYTHONUTF8=1 python examples/demo.py    # ver el estado funcional
pytest -q                                # confirmar 54 en verde
```

Leer `CLAUDE.md` (estable) + este archivo (estado) antes de tocar nada.

---

### Historial de cambios de contexto

- **2026-06-28:** Creación del proyecto completo (Fases 0–6). MVP offline
  funcional, API+CLI, 29 tests, wheel empaquetable. Creados `CLAUDE.md` y
  `CLAUDE_CONTEXT.md`.
- **2026-06-28:** Robustez multilenguaje: `lang/metadata.py` centraliza metadatos
  lingüísticos; añadidos nl, pl, ru, uk y sv con diccionarios básicos, stopwords,
  palabras función, intensificadores, spaCy/WordNet opcionales, health API y tests
  de regresión. Suite verificada: 40 tests en verde.
- **2026-06-28:** Revisión de las mejoras multilenguaje. Corregido bug: el test
  de sueco fallaba porque simplemma sobre-lematiza (`hjälp→hjälpa`) y la búsqueda
  en diccionario solo usaba el lema → ahora busca por lema Y forma de superficie
  (`candidates.py`). 40/40 tests en verde; wheel revalidado (19 datos, 11 idiomas).
- **2026-06-28:** Siguientes mejoras: añadidos `marketplace.json` y
  `technical.json` para nl/pl/ru/uk/sv; CI GitHub Actions con Python 3.11/3.13,
  `pytest` y `ruff`; segmentación Unicode conservadora para `zh`, `ja` y `th`
  sin declararlos de primera clase. Suite verificada: 54 tests en verde.
