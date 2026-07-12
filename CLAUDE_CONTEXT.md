# CLAUDE_CONTEXT.md — Memoria viva del proyecto

Estado dinámico del desarrollo. Se actualiza periódicamente. Para info estable
(arquitectura, comandos, convenciones) ver `CLAUDE.md`.

- **Última actualización:** 2026-07-12
- **Versión:** 0.1.0
- **Estado general:** ✅ MVP funcional y verificado. Núcleo offline completo,
  API + CLI + **app de escritorio (.exe)** operativas, 95 tests en verde (90
  rápidos + 5 de integración: T5 real, spaCy real ×2, puente de traducción
  real ×2), wheel empaquetable. 12 idiomas, español enriquecido con tesauro de
  ~3.5k voces. **Nuevo:** toggle de IA (T5, sólo inglés) + **puente de
  traducción** (`TranslationBridgeTransformer`, MarianMT) que lo extiende a
  los **12 idiomas**, concordancia morfológica vía spaCy, y tema visual nativo
  de Windows (`vista`/`xpnative`) en la app de escritorio.

---

## 1. Estado actual del desarrollo

El motor `rewrite_engine` está **completo a nivel MVP** según el plan de 6 fases
(todas cerradas). Funciona 100% offline con diccionarios + WordNet/OMW. La capa
de IA existe como interfaz pero **no está cableada** a ningún LLM (es el siguiente
paso opcional).

Idiomas de primera clase actuales: **es, en, pt, fr, it, de, nl, pl, ru, uk, sv, eo**
(Esperanto añadido con lematizador por reglas propio en `lang/esperanto.py`).
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
- **App de escritorio (Tkinter)** `rewrite_engine/desktop/`: dos paneles
  (izq. original / der. reescrito), los **12 modos como radio-botones**, checkbox
  **"Resumir texto"**, checkbox de autocorrección, slider intensidad, alternativas,
  botones Reescribir/Ortografía/Copiar/Limpiar, motor en hilo de fondo. Script
  `rewrite-engine-gui`.
- **Corrector ortográfico** (`desktop/spell.py`, extra `[desktop]`): dos motores
  offline con cobertura pareja — `pyspellchecker` (en/es/fr/pt/de/ru/nl) +
  **respaldo `wordfreq`** (it/pl/uk/sv y demás). Subraya desconocidas en ambos
  paneles y sugiere con clic derecho. Sólo eo queda sin corrector (sin datos).
- **Resumen extractivo** (`rewrite/summarizer.py`): el modo `summarized` reduce a
  las oraciones clave por frecuencia de contenido (offline, determinista);
  intensidad mayor → resumen más corto.
- **Ejecutable .exe** (PyInstaller, `packaging/rewrite_engine_gui.spec`):
  ~163 MB, autónomo; excluye deps pesadas (nltk/torch/spacy) → dictionary-driven.
  Bundlea las DLLs de conda que PyInstaller no detecta (`libexpat.dll` para
  pyexpat; `tcl86t.dll`/`tk86t.dll`/`zlib.dll` para `_tkinter`). Verificado con
  `RewriteEngine.exe --selftest` (carga 12 idiomas y reescribe, exit 0).
- **Español enriquecido:** `data/dictionaries/es/thesaurus.json` (~3.5k voces,
  ~17.9k sinónimos) generado desde `repos/repos-new/sinonimos.txt` con
  `scripts/build_thesaurus.py`.
- **Esperanto (eo):** diccionario + lematizador y **re-flexión** por reglas
  (`lang/esperanto.py`: acusativo -n, plural -j, verbos -as/-is/-os/-us/-u→-i).
- **CI:** GitHub Actions ejecuta `pytest` + `ruff` en Python 3.11 y 3.13.
- **Empaquetado:** wheel con los 41 JSON de datos incluidos (12 idiomas, cada uno
  con general+marketplace+technical). El `.exe` incluye datos vía spec de
  PyInstaller.
- **Menú contextual completo** en la app de escritorio: clic derecho ahora
  ofrece Cortar/Copiar/Pegar/Seleccionar todo/Deshacer/Rehacer en ambos paneles
  (antes sólo aparecía si el clic caía sobre una palabra subrayada por el
  corrector — bug reportado por el usuario, corregido). `Ctrl+A` también
  bindeado explícitamente (Tkinter no lo trae de fábrica).
- **Toggle de IA (T5 paráfrasis, opt-in, extra `[ai-paraphrase]`):**
  `transformers/t5_paraphraser.py` (`T5ParaphraserTransformer`). Checkbox en la
  GUI + flag `--ai` en el CLI. **Sólo aplica a texto en inglés** (comunicado
  explícitamente, no es degradación silenciosa); en los otros 11 idiomas es
  no-op. `RewriteEngine.set_transformer()` permite cambiar el backend en
  caliente sin recrear el motor (usado por el toggle). Guardas de seguridad:
  preserva tokens protegidos, rechaza longitud absurda y **repetición
  degenerada en bucle** (fallo real observado: el modelo pequeño puede invertir
  sujeto/objeto y repetir una cláusula). No se incluye en el `.exe` ligero por
  defecto (`torch` pesa cientos de MB); requiere instalar desde código.
- **Resumen extractivo** (`rewrite/summarizer.py`) y **corrector con respaldo
  wordfreq** ya estaban implementados (ver historial); siguen operativos.
- **Concordancia morfológica** (`lang/morphology.py`, activa automáticamente
  con `[spacy]` + modelo del idioma, sin toggle nuevo): `TokenizerLemmatizer.
  analyze()` extrae POS + `MorphFeatures` (género/número/tiempo/persona/modo)
  de spaCy en un único parseo; `SentenceRewriter` reflexiona el reemplazo antes
  de insertarlo. Alcance deliberadamente conservador:
  - **ADJ**: género + número (es/pt/it: -o/-a; fr: +e/-s; verificado con spaCy
    real: `bonita→hermosa`, no `hermoso`).
  - **NOUN**: **sólo número**, nunca género (ver bug real en §5: el género de
    un sustantivo es léxico fijo, no concuerda con nada).
  - **VERB**: sólo presente-indicativo-3ª persona con terminaciones regulares
    (verificado: `transforma→cambia`, no el infinitivo `cambiar`). Otros
    tiempos/modos y verbos irregulares con cambio de raíz se dejan sin tocar
    a propósito (mismo espíritu que `lang/esperanto.py`, pero es/pt/it/fr NO
    son regulares como Esperanto).
  - **Alemán**: sólo extracción, sin reflexión (declinación de adjetivos
    depende del artículo — demasiado compleja para reglas de sufijo seguras).
- **Puente de traducción** (`transformers/translation_bridge.py`,
  `TranslationBridgeTransformer`): envuelve cualquier transformer inglés-only
  (el T5) y lo extiende a **los 12 idiomas** traduciendo idioma→inglés,
  aplicando el transformer, y traduciendo de vuelta. Usa `Helsinki-NLP/
  opus-mt-<lang>-en` / `opus-mt-en-<lang>` (MarianMT, Apache-2.0), un modelo
  por idioma cargado bajo demanda. Checkbox "Traducir para IA en todos los
  idiomas" en la GUI (ligado al toggle de IA) + flag `--ai-translate` en CLI.
  Guardas compartidas con el T5 (extraídas a `transformers/_guards.py`).
- **Tema visual nativo de Windows**: la GUI usa el tema ttk `vista` (o
  `xpnative` de respaldo) en vez del `clam` genérico multiplataforma anterior
  — sin dependencias nuevas (son parte de Tcl/Tk en Windows).
- **Tests:** 95 pasando: 90 rápidos + 5 de integración (T5 real, spaCy real ×2,
  puente de traducción real ×2 — todos se saltan si falta la dependencia/
  modelo o hay red). Cubren los 20 casos obligatorios del prompt y regresiones
  para idiomas nuevos, diccionarios de industria, segmentación CJK/Thai,
  aliases, los transformers de IA y la concordancia morfológica.

## 3. Funcionalidades en progreso 🚧

- (ninguna activa) — concordancia morfológica vía spaCy completada (ver §2, §5).

## 4. Tareas pendientes / backlog 📋

**Completadas en 2026-07-11** (antes en este backlog):
- ✅ Los 12 idiomas tienen `general` + `marketplace` + `technical`; pt/fr/it/de
  general ampliados (~13 voces). Español con tesauro de ~3.5k.
- ✅ Modo `summarized` implementado offline (resumen extractivo real).
- ✅ Corrector ortográfico para los 11 idiomas naturales (pyspellchecker + fallback
  wordfreq).
- ✅ Re-flexión morfológica de Esperanto (`helpon→subtenon`).
- ✅ `.exe` arreglado (bug pyexpat/libexpat).

**Completadas en 2026-07-12:**
- ✅ Menú contextual completo (Cortar/Copiar/Pegar/Seleccionar todo) en la app
  de escritorio — antes sólo aparecía sobre palabras subrayadas.
- ✅ `BaseTransformer` real implementado: `T5ParaphraserTransformer` (T5 local,
  opt-in, sólo inglés) con toggle en GUI/CLI. Ya no sólo existe `NullTransformer`.
- ✅ **Concordancia morfológica vía spaCy** (`lang/morphology.py`): género/número
  en ADJ/NOUN y conjugación regular presente-3ª en VERB, para es/pt/fr/it/en (de
  sólo extracción). Verificado con spaCy real: `bonita→hermosa`,
  `transforma→cambia`, `ayuda→apoyo` (no `apoya`, ver bug en §5).

**Completadas en 2026-07-12 (2ª tanda):**
- ✅ **Puente de traducción** (`TranslationBridgeTransformer`, MarianMT):
  extiende la IA (T5) a los 12 idiomas. mT5 evaluado y descartado (necesita
  fine-tuning, no funciona tal cual — verificado en la propia tarjeta del
  modelo). NLLB-200 y small100 evaluados y descartados por licencia/riesgo
  (ver §5). Guardas compartidas extraídas a `transformers/_guards.py`.
- ✅ **Tema visual "Windows clásico"**: `winxpblue` (`ttkthemes`, extra
  `[desktop]`) por defecto, con fallback a `vista`/`xpnative` nativos de
  Tcl/Tk si `ttkthemes` no está instalado. `ttkthemes` es GPL-3.0-or-later —
  se descartó primero por una atribución incorrecta de "política de
  dependencias permisivas" (nunca existió tal política; corregido tras
  aclaración del usuario) y luego se añadió: es software libre y gratuito,
  sólo con una obligación de divulgar el código fuente si se **distribuye**
  el `.exe` empaquetado (ver §5 y la entrada del historial de esta tanda).

Prioridad sugerida de mayor a menor:

1. **Ampliar la concordancia verbal más allá de presente-3ª** (§5, §6): hoy sólo
   se conjuga presente-indicativo-3ª persona por ser el caso más seguro/común.
   Extenderlo a más tiempos/personas requeriría una tabla de verbos irregulares
   real (no reglas de sufijo) para no arriesgar conjugaciones incorrectas.
2. **Activar embeddings** (`pip install -e ".[semantic]"`): mejora algo el
   filtrado de WordNet, pero **ya se verificó que NO detecta de forma fiable**
   la sustitución de un verbo por otro relacionado pero distinto (ver §5/§6) —
   no tratar como solución completa al ruido de WordNet, sólo como mejora
   parcial.
3. **Calibrar/ampliar el toggle de IA**: probar `Ateeqq/Text-Rewriter-Paraphraser`
   (Apache-2.0, T5-Base, mejor en frases declarativas pero más pesado y con más
   riesgo de repetición — ya mitigado por la guarda compartida) como
   alternativa seleccionable; considerar exponer `model_name` en la GUI.
4. **Mejorar la calidad léxica de WordNet** (causa raíz real del caso
   `cierra→bloquea` encontrado esta sesión, ver §5/§6): requeriría mejor WSD
   (desambiguación de sentido) o más cobertura de diccionario curado para
   verbos comunes, para que no dependa tanto de WordNet en primer lugar.
5. **Enriquecer con tesauros bulk** los idiomas no-es (como se hizo con
   `sinonimos.txt` para es) para igualar profundidad de vocabulario.
6. **Modos `expanded`/`creative`**: hoy degradan a heurística; el toggle de IA
   (+ puente de traducción) ya los mejora en los 12 idiomas, con las
   limitaciones de calidad documentadas en §6.
7. **Diccionarios de industria** legal/marketing/salud/educación por idioma.
8. **Modo SEO avanzado** (meta title/description) y **marketplace** (bullets).
9. Tests de integración `@pytest.mark.integration` para spaCy/embeddings; job de
   build wheel/exe en CI.

~~Back-translation opcional (MarianMT) como capa adicional~~ **YA IMPLEMENTADO**
(2026-07-12): es exactamente lo que hace `TranslationBridgeTransformer`.

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
- **Menú contextual reescrito en `_show_context_menu`** (antes `_on_word_menu`):
  el bug era que hacía *early return* si el clic no caía sobre una palabra
  subrayada, así que Cortar/Copiar/Pegar nunca aparecían. Ahora siempre
  construye el menú completo y antepone las sugerencias ortográficas sólo
  cuando aplica. `Ctrl+A` bindeado a mano (Tkinter no lo trae).
- **Modelo T5 por defecto elegido tras probar 2 candidatos con el modelo real**
  (no a ciegas): `mrm8488/t5-small-finetuned-quora-for-paraphrasing` (~240 MB,
  sin licencia declarada) parafrasea bien preguntas pero con beam search
  determinista suele no-opear frases declarativas (está afinado sobre pares de
  preguntas de Quora — verificado en la tarjeta del modelo). La alternativa
  `Ateeqq/Text-Rewriter-Paraphraser` (Apache-2.0, T5-Base ~850 MB) es mejor en
  frases declarativas pero a veces produce **repetición degenerada** (invierte
  sujeto/objeto y repite una cláusula) — se eligió el modelo ligero como
  default por ser el fallo más seguro (no-op) frente al fallo más arriesgado
  (contenido incorrecto), y se añadió la guarda `_has_degenerate_repetition`
  (ratio de bigramas distintos < 0.75) para blindar contra ambos modelos.
- **Decodificación determinista para el T5** (`num_beams=4, do_sample=False`)
  en vez del muestreo que recomienda la tarjeta del modelo, por el principio de
  determinismo del proyecto.
- **Defensa de `torchvision` rota a nivel de MÓDULO** (ahora vive en
  `transformers/_guards.py`, no en `t5_paraphraser.py`): `transformers` decide
  si `torchvision` está disponible **una sola vez**, al importarse por primera
  vez (`is_torchvision_available()` cachea un booleano de módulo) — si algo
  más ya importó `transformers` antes de bloquear `torchvision`, la defensa
  llega tarde y el crash ocurre igual (confirmado empíricamente: funcionaba en
  un script aislado pero fallaba dentro de pytest). Se movió a `_guards.py`
  (2026-07-12) porque **ambos** transformers (`t5_paraphraser.py` y el nuevo
  `translation_bridge.py`) importan de ahí — así la defensa corre siempre,
  sin depender de qué transformer se importe primero. Nunca reduce
  funcionalidad; sólo evita un crash de arranque ajeno.
- **`RewriteEngine.set_transformer()`** añadido para hot-swap del backend de IA
  sin recrear el motor (evita recargar diccionarios/WordNet en cada toggle).
- **Género sólo se reflexiona en ADJETIVOS, nunca en SUSTANTIVOS** (bug real
  encontrado y corregido durante el desarrollo, no una decisión de diseño a
  priori): la primera versión de `_reinflect_nominal` aplicaba el cambio de
  género a ADJ y NOUN por igual, y producía `"Ella necesita ayuda urgente."` →
  `"Ella necesita apoya urgente."` — spaCy etiqueta correctamente "ayuda" como
  NOUN(Fem), pero el reemplazo del diccionario ("apoyo", masculino) se
  "feminizaba" a "apoya" (que además coincide por accidente con una forma
  verbal, empeorando el resultado). El género de un sustantivo es una
  propiedad léxica fija, no algo que "concuerde" con otra palabra — dos
  sustantivos sinónimos pueden tener géneros distintos legítimamente
  ("ayuda" fem. / "apoyo" masc.). Fix: el género sólo se toca para `pos ==
  "ADJ"`; los sustantivos sólo reciben la reflexión de número. Test de
  regresión: `test_sustantivo_no_cambia_genero` en `tests/test_morphology.py`.
- **Conjugación de verbos limitada a presente-indicativo-3ª persona** con
  terminaciones regulares (-ar/-er/-ir y equivalentes pt/it/fr): sin una tabla
  de verbos irregulares real, conjugar otros tiempos/modos arriesgaría producir
  formas incorrectas para verbos con cambio de raíz (es. "poder"→"puede", no
  "pode"; nuestras reglas de sufijo no lo detectarían y producirían la forma
  regular incorrecta). Se prefiere no tocar el reemplazo antes que arriesgar
  una conjugación mal hecha — mismo principio de "fallback seguro" que el
  resto del motor (gate semántico, medical guard, etc.).
- **`TokenizerLemmatizer.analyze()`** sustituye a `pos_of` como fuente única de
  verdad: un solo parseo de spaCy alimenta tanto el filtrado por POS
  (`CandidateGenerator`) como los rasgos morfológicos (`reinflect`). `pos_of`
  se mantiene como wrapper fino sobre `analyze()` (nadie más lo llamaba).
- **mT5 (`google/mt5-small`) descartado, no implementado** (pedido explícito
  del usuario, decisión tomada tras verificar, no por conveniencia): su propia
  tarjeta de modelo en HuggingFace declara "sólo se preentrenó con mC4...
  debe afinarse (fine-tune) antes de poder usarse en una tarea downstream".
  Se revisaron ~26 fine-tunes comunitarios de mT5 para paráfrasis: todos son
  proyectos experimentales monolingües (turco, chino, persa, urdu, bengalí…)
  con muy pocos likes/descargas, ninguno cubre los 12 idiomas del proyecto de
  forma fiable. Conectar el checkpoint crudo habría producido texto sin
  sentido — verificado que no era simplemente pereza evitarlo.
- **`facebook/nllb-200-distilled-600M` (Meta) descartado:** licencia CC BY-NC
  4.0 — **prohíbe explícitamente el uso comercial** del modelo (no es una
  cuestión de pago, sino de qué usos permite la licencia); mismo tipo de
  restricción que ya se documentó para `Humanizer`/VHumanize. Buena calidad de
  traducción, pero bloquearía cualquier uso comercial del motor si se incluye.
  (Nota: no existe una "política de dependencias permisivas" del proyecto —
  fue una atribución incorrecta mía, corregida tras aclaración del usuario:
  cualquier licencia sirve mientras no exija pago; este caso concreto se
  descarta por la restricción de uso comercial de CC BY-NC, no por "política".)
- **`alirezamsh/small100` descartado:** MIT (licencia OK) pero su tokenizer
  requiere cargar `tokenization_small100.py` con `trust_remote_code=True` —
  riesgo de cadena de suministro (ejecuta código Python arbitrario del repo
  del modelo) que se prefirió evitar en favor de `Helsinki-NLP/opus-mt-*`
  (tokenizer nativo de `transformers`, sin código remoto).
- **`google/translategemma-4b-it` descartado:** sí existe (798 likes, real),
  pero es un modelo **imagen-texto** (`Image-Text-to-Text`, arquitectura
  Gemma 3 multimodal), no un traductor de texto puro; 4B parámetros (pesado,
  pide GPU); licencia Gemma personalizada. No encaja con el perfil
  ligero/CPU/texto del proyecto — verificado en su tarjeta de HuggingFace, no
  descartado por el nombre.
- **`Helsinki-NLP/opus-mt-*` (MarianMT) elegido para el puente de traducción:**
  Apache-2.0, sin código remoto, tokenizer nativo, y **verificado que cubre
  incluso Esperanto** (`opus-mt-eo-en` existe). Un modelo por idioma
  (~300 MB c/u) cargado bajo demanda, en vez de un modelo único masivo.
- **Hallazgo importante verificado empíricamente durante el desarrollo del
  puente de traducción:** un round-trip de traducción limpio (sin pasar por
  el motor completo) reconstruye el original con fidelidad exacta. Al
  investigar un caso donde el resultado final sí tenía un error de sentido
  (`cierra`→`bloqueando`), se rastreó paso a paso y se confirmó que el puente
  de traducción NO introdujo el error: lo heredó de la capa léxica offline
  (WordNet ya había sustituido `cierra`→`bloquea` ANTES de que el texto
  llegara al transformer). Además, se comprobó que **ni la similitud léxica ni
  los embeddings reales (`sentence-transformers`, con el proyecto instalado y
  probado) detectan este patrón de forma fiable** — el caso con el error
  puntuó 0.926 de similitud (embeddings reales), más alto que un caso
  correctamente parafraseado (0.909). Es una limitación real de la similitud a
  nivel de oración (mide tema/estructura, no corrección palabra por palabra),
  no un defecto del puente ni algo que las guardas actuales puedan arreglar.
  Ver §6 y README §Limitaciones.
- **`ttkthemes` — descartado y luego incluido en la misma sesión.** Da un tema
  fijo "winxpblue" (azul XP-Luna) independiente de la versión de Windows;
  **GPL-3.0-or-later** (verificado con `pip show`, no MIT como parecía de
  memoria). Primero se descartó razonando que era "incompatible con la
  política de dependencias permisivas del proyecto" — **el usuario corrigió
  esto**: nunca se estableció tal política; su criterio real es "cualquier
  licencia sirve, mientras no exija pago". Se re-evaluó con el criterio
  correcto: GPL no cuesta dinero, así que no hay objeción real de su parte.
  El único dato objetivo que sigue siendo cierto sobre GPL (no una política,
  una característica de la licencia): si se **distribuye** el `.exe`
  empaquetado con este tema, GPL obliga a poder entregar el código fuente
  completo del programa a quien lo reciba si lo pide. Con esa información, el
  usuario pidió incluirlo. Ahora es el tema por defecto (`_create_style()` usa
  `ttkthemes.ThemedStyle` si está instalado), con fallback a `vista`/
  `xpnative` nativos de Tcl/Tk si no lo está. Añadido a `[desktop]` en
  `pyproject.toml` con el aviso de licencia en el comentario. El spec de
  PyInstaller ahora también empaqueta los datos de `ttkthemes` (pixmaps del
  tema) vía `collect_data_files("ttkthemes")`.

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
- ~~Esperanto sin re-flexión~~ **RESUELTO (2026-07-11):** `reinflect_eo` reaplica
  acusativo/plural/tiempo verbal al reemplazo (`helpon→subtenon`).
- ~~Modo `summarized` no-op~~ **RESUELTO (2026-07-11):** resumen extractivo real
  en `rewrite/summarizer.py`.
- ~~Corrector sin cobertura total~~ **MEJORADO (2026-07-11):** respaldo `wordfreq`
  da corrector a it/pl/uk/sv y demás. Sólo **eo** queda sin corrector (ningún
  motor trae datos de Esperanto).
- ~~Clic derecho no ofrecía Copiar/Pegar~~ **RESUELTO (2026-07-12):** ver §5,
  menú contextual reescrito.
- ~~Concordancia morfológica (es/pt/fr/it/de)~~ **MEJORADA (2026-07-12):**
  `lang/morphology.py` reflexiona género/número (ADJ/NOUN) y conjuga presente-
  3ª persona regular (VERB) cuando `[spacy]` está instalado — sin él, sigue el
  comportamiento anterior (forma base). **Limitación residual, intencional:**
  sólo presente-3ª-persona; otros tiempos/modos y verbos con cambio de raíz
  (irregulares) se dejan sin conjugar para no arriesgar una forma incorrecta
  (ver §5). Alemán: sólo extracción, sin reflexión (declinación compleja).
- ~~Toggle de IA (T5) sólo inglés~~ **AMPLIADO (2026-07-12):** el puente de
  traducción (`TranslationBridgeTransformer`) lo extiende a los 12 idiomas.
  **Limitación que persiste:** el modelo T5 por defecto está afinado para
  parafrasear preguntas (Quora), no frases declarativas — con decodificación
  determinista, en textos declarativos suele no-opear (fallback seguro, no es
  un error). Ver §5 para la comparación empírica con
  `Ateeqq/Text-Rewriter-Paraphraser`.
- **Puente de traducción: riesgo de deriva semántica no detectada por ninguna
  guarda existente.** Verificado empíricamente (§5): si la capa léxica offline
  ya introdujo un sinónimo cuestionable (ruido de WordNet) antes de que el
  texto llegue al transformer, la traducción ida y vuelta lo propaga fielmente
  — y ni la similitud léxica ni los embeddings reales (`[semantic]`) lo
  detectan de forma fiable (un caso con error de sentido puntuó MÁS alto,
  0.926, que un caso correcto, 0.909). No es un bug del puente: es una
  limitación de la similitud a nivel de oración en general. Mitigación real
  pendiente: mejorar la calidad léxica de WordNet en origen (§4 punto 4), no
  perseguir un umbral de similitud más estricto (ya se comprobó que no basta).

## 7. Próximos pasos recomendados

1. Si se busca **mejorar la calidad del puente de traducción**: el cuello de
   botella real es el ruido de WordNet en la capa léxica offline (§5/§6), no
   el puente en sí — mejorar ahí primero antes de perseguir umbrales de
   similitud más estrictos (ya verificado que no bastan).
2. Si se busca **más concordancia verbal**: ampliar `lang/morphology.py` más
   allá de presente-3ª persona requeriría una tabla de conjugación real
   (verbos irregulares con cambio de raíz) — evaluar si vale la pena el costo
   frente a simplemente usar el toggle de IA para esos casos.
3. Si se busca **calidad general**: instalar `[semantic]` (embeddings) y medir
   — mejora el filtrado de WordNet en general, aunque no el caso específico
   de sustitución de verbos (§5/§6).
4. Si se busca **profundidad de vocabulario**: conseguir tesauros bulk para los
   idiomas no-es y correrlos por `scripts/build_thesaurus.py` (como `sinonimos.txt`).
5. Si se busca **mejorar el toggle de IA**: probar `Ateeqq/Text-Rewriter-Paraphraser`
   como alternativa seleccionable (mejor en declarativas, Apache-2.0, más pesado).
6. Si se busca **producto**: firmar/branding del `.exe`, instalador, meta-tags SEO
   y bullets marketplace; job de build wheel/exe en CI.

## 8. Cómo retomar en una sesión nueva

```bash
cd <repo>
pip install -e ".[wordnet,api,cli,dev]"
python -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4')"
PYTHONUTF8=1 python examples/demo.py    # ver el estado funcional
pytest -q -m "not integration"           # confirmar ~90 en verde (rápidos)

# App de escritorio (dos paneles + corrector ortográfico + toggle de IA + tema nativo)
pip install -e ".[desktop]"
rewrite-engine-gui                       # o: python -m rewrite_engine.desktop.app

# Toggle de IA: T5 (sólo inglés) + puente de traducción (12 idiomas)
pip install -e ".[ai-paraphrase]"
pytest -q tests/test_ai_transformer.py tests/test_translation_bridge.py -m integration

# Concordancia morfológica (activa sola con [spacy] + modelo; sin toggle)
pip install -e ".[spacy]"
python -m spacy download es_core_news_sm  # y/o en_core_web_sm, etc.
pytest -q tests/test_morphology.py -m integration   # prueba con spaCy real

# Generar el .exe (Windows)
pip install -e ".[build-exe]"
pyinstaller packaging/rewrite_engine_gui.spec --noconfirm   # -> dist/RewriteEngine.exe
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
- **2026-07-11:** Revisadas las repos de `repos/repos-new`. (1) **Español
  enriquecido** desde `sinonimos.txt` → `es/thesaurus.json` (~3.5k voces, 17.9k
  sinónimos) vía `scripts/build_thesaurus.py`. (2) **Idioma nuevo: Esperanto (eo)**
  con diccionario y lematizador regular (`lang/esperanto.py`). (3) **App de
  escritorio** (`rewrite_engine/desktop/`, Tkinter): dos paneles + corrector
  ortográfico offline (`pyspellchecker`, extra `[desktop]`) con sugerencias por
  clic derecho. (4) **Ejecutable .exe** (PyInstaller, `packaging/`): 161.7 MB,
  validado (arranca y reescribe). 54 tests en verde; 12 idiomas, 31 JSON de datos.
- **2026-07-11 (2ª tanda):** Sobre el feedback del usuario (crash del .exe + GUI
  de modos + paridad de idiomas). (1) **Arreglado el crash del .exe**: faltaban en
  el spec `libexpat.dll` (pyexpat) y `tcl86t.dll`/`tk86t.dll`/`zlib.dll`
  (`_tkinter`), DLLs de conda que PyInstaller no escanea. Verificado end-to-end
  con `--selftest` (exit 0). (2) **GUI**: los 12
  modos como radio-botones + checkbox "Resumir texto" + autocorrección + Copiar.
  (3) **Modo `summarized` real** (`rewrite/summarizer.py`, extractivo offline).
  (4) **Corrector para 11 idiomas** vía respaldo `wordfreq` (antes solo 7).
  (5) **Re-flexión de Esperanto** (`reinflect_eo`). (6) **Paridad de diccionarios**:
  `marketplace`+`technical` para pt/fr/it/de/eo y general ampliado en pt/fr/it/de
  → 41 JSON. Limitación principal restante: concordancia morfológica (§6, §4.2).
- **2026-07-12:** Usuario confirmó abordar la concordancia morfológica con
  spaCy (siguiente tarea, ver §3) y reportó que el clic derecho no ofrecía
  copiar/pegar. (1) **Corregido el menú contextual**: `_on_word_menu` hacía
  *early return* sin palabra subrayada bajo el cursor; reescrito como
  `_show_context_menu` con Cortar/Copiar/Pegar/Seleccionar todo/Deshacer/Rehacer
  siempre disponibles + sugerencias ortográficas cuando aplica; `Ctrl+A`
  bindeado a mano. (2) **Toggle de IA implementado**: el usuario propuso 4
  modelos T5 de HuggingFace y preguntó si había que alojarlos en un servidor
  propio (no: `transformers` cachea localmente tras la 1ª descarga, corre
  offline). Se implementó `T5ParaphraserTransformer` (`transformers/
  t5_paraphraser.py`, extra `[ai-paraphrase]`) con: sólo-inglés explícito,
  decodificación determinista, guardas de seguridad (tokens protegidos,
  longitud, **repetición degenerada** — encontrada empíricamente al comparar
  los 2 modelos candidatos con descargas reales), y una defensa a nivel de
  módulo contra un `torchvision` desalineado que rompía el import de
  `transformers` (bug real, reproducido y corregido en este entorno; el fix
  ingenuo dentro de `_load()` no bastaba por el orden de imports — ver §5).
  Toggle en GUI (checkbox + carga en hilo de fondo) y CLI (`--ai`).
  `RewriteEngine.set_transformer()` para hot-swap. 60 tests rápidos + 1 de
  integración (con modelo real) en verde.
- **2026-07-12 (2ª tanda):** Concordancia morfológica vía spaCy, confirmada
  por el usuario. Instalados spaCy + modelos es/en reales para verificar de
  verdad (no en teoría). Nuevo `lang/morphology.py`: `MorphFeatures` +
  `reinflect()`, alimentado por un nuevo `TokenizerLemmatizer.analyze()` (POS +
  morph en un solo parseo; sustituye a `pos_of`). Verificado con el motor real:
  `bonita→hermosa` (antes `hermoso`), `transforma→cambia` (antes `cambiar`).
  **Bug real encontrado y corregido durante la verificación**: la primera
  versión aplicaba cambio de género también a SUSTANTIVOS, produciendo
  `"ayuda"→"apoya"` (un sustantivo femenino "corregido" a lo que parece una
  forma verbal) en vez de `"apoyo"` — el género de un sustantivo es léxico
  fijo, no concuerda con nada; sólo los ADJETIVOS deben reflexionar género.
  Corregido y con test de regresión. Alcance de verbos limitado a
  presente-indicativo-3ª-persona regular (decisión deliberada: sin tabla de
  irregulares, otros tiempos arriesgarían conjugaciones incorrectas). Alemán:
  sólo extracción, sin reflexión (declinación compleja). 24 tests nuevos
  (22 rápidos + 2 de integración con spaCy real). **85 tests totales en verde.**
- **2026-07-12 (3ª tanda):** Usuario pidió mT5 (Google) + una opción de
  traducción (idioma→inglés→rewrite→idioma original) + tema visual XP/7 para
  la GUI. (1) **mT5 investigado y descartado**: la propia tarjeta de
  `google/mt5-small` en HuggingFace dice que necesita fine-tuning antes de
  usarse — se revisaron ~26 fine-tunes comunitarios, ninguno fiable ni
  multilenguaje para los 12 idiomas del proyecto. (2) **Puente de traducción
  implementado** (`transformers/translation_bridge.py`,
  `TranslationBridgeTransformer`) con `Helsinki-NLP/opus-mt-*` (MarianMT,
  Apache-2.0) tras evaluar y descartar con evidencia verificada: NLLB-200
  (Meta, CC BY-NC no comercial), `small100` (MIT pero requiere
  `trust_remote_code=True`), `translategemma-4b-it` (existe pero es modelo de
  imagen, no de texto, 4B, licencia Gemma). Guardas de seguridad extraídas a
  `transformers/_guards.py` (compartidas entre T5 y el puente; incluye la
  defensa de `torchvision`, movida ahí para no depender del orden de import).
  **Hallazgo importante durante la verificación**: un caso con error de
  sentido (`cierra`→`bloqueando`) resultó ser causado por la capa léxica
  offline (ruido de WordNet preexistente), no por el puente — y se comprobó
  que ni la similitud léxica ni los embeddings reales lo detectan de forma
  fiable (el caso malo puntuó MÁS alto, 0.926, que uno bueno, 0.909).
  Documentado como limitación real, no oculto. (3) **Tema visual**: la app
  ahora usa el tema nativo `vista`/`xpnative` de Tcl/Tk en vez de `clam`
  genérico. `ttkthemes` (con un tema "winxpblue" fijo) se evaluó pero se
  descartó *inicialmente* al verificar que es **GPL-3.0-or-later**, no MIT
  (ver corrección en la entrada siguiente). 10 tests nuevos
  (`test_transformer_guards.py`, `test_translation_bridge.py`). **95 tests
  totales en verde** (90 rápidos + 5 de integración con modelos reales).
- **2026-07-12 (4ª tanda):** El usuario corrigió una atribución incorrecta mía:
  dije que GPL era "incompatible con la política de licencias permisivas de
  este proyecto" — **esa política nunca se estableció**. Lo único documentado
  en `CLAUDE.md` es no *copiar código* de `repos/Humanizer-main` (CC BY-NC),
  una regla puntual sobre copiar código con licencia no comercial, que
  generalicé mal a "evitar toda dependencia no permisiva". El criterio real
  del usuario: cualquier licencia sirve, incluso ninguna, mientras no exija
  pago. Corregidas todas las menciones de "política de dependencias
  permisivas" en README/CLAUDE_CONTEXT (NLLB-200 se sigue descartando, pero
  por su prohibición de uso *comercial* — una restricción de uso real de
  CC BY-NC, no una preferencia de licencia). Con el criterio correcto, se
  añadió `ttkthemes` (extra `[desktop]`, `winxpblue` como tema por defecto,
  fallback a `vista`/`xpnative`), con el aviso honesto de que sigue habiendo
  una obligación real (no inventada) de GPL: divulgar el código fuente si se
  distribuye el `.exe` empaquetado. Spec de PyInstaller actualizado para
  incluir los pixmaps de `ttkthemes`. Además, el usuario reportó que el clic
  derecho seguía sin copiar/pegar — se verificó con timestamps que el `.exe`
  que probaba era de **antes** del arreglo del menú contextual (compilado a
  las 01:17, el fix en el código quedó a las 10:24, +9h después): no era un
  bug nuevo, sino un `.exe` desactualizado nunca reconstruido tras el fix.
  Se reconstruyó dos veces (una con el fix del menú, otra con `ttkthemes`
  bundleado) y se verificó en vivo que la ventana abre y se mantiene estable.
