# CLAUDE_CONTEXT.md — Memoria viva

Lee primero `CLAUDE.md` para arquitectura, comandos y reglas permanentes. Este
archivo conserva sólo el estado necesario para retomar trabajo sin reconstruir
todo el historial. Actualízalo al cerrar una tarea importante, cambiar una
decisión o descubrir un riesgo; elimina información que ya no sea vigente.

- **Actualizado:** 2026-07-12
- **Versión del paquete:** 0.1.0
- **Rama:** `main`
- **Estado:** MVP funcional; motor offline, CLI, API, GUI y empaquetado Windows
  implementados. IA local opcional mediante T5/MarianMT y Ollama.

## Estado actual

- El núcleo funciona sin servicios ni modelos pesados y usa fallbacks cuando
  faltan WordNet, spaCy, embeddings o LanguageTool.
- Idiomas de primera clase: `es`, `en`, `pt`, `fr`, `it`, `de`, `nl`, `pl`,
  `ru`, `uk`, `sv`, `eo`, `ar`, `hi`, `tr`, `id`.
- El español incluye un tesauro generado de unas 3.5k entradas; los demás
  idiomas tienen menos cobertura y dependen más de WordNet/OMW.
- `summarized` ya es un resumen extractivo offline. `expanded` y `creative`
  siguen siendo limitados sin transformer.
- La GUI usa Tkinter, corrector offline, tema `winxpblue` cuando está disponible
  y fallback nativo `vista`/`xpnative`.
- El wheel y `packaging/rewrite_engine_gui.spec` incluyen los datos. El último
  ejecutable registrado pasó `RewriteEngine.exe --selftest`.
- La CI prueba Python 3.11 y 3.13 con pytest y Ruff.
- Verificación local 2026-07-12: **105 passed, 2 skipped** y Ruff limpio en
  `src`, `tests`, `scripts` y `packaging`.
- Distribución `dist/RewriteEngineAI` generada: ~2.07 GB, 16 idiomas, Ateeqq y
  MarianMT ES↔EN incluidos. `--selftest` y `--ai-selftest` pasan; los snapshots
  de traducción también cargan con `HF_HUB_OFFLINE=1`.

## Funcionalidades implementadas

- Detección de idioma y normalización de aliases.
- Protección/restauración exacta de URLs, correo, teléfono, fechas, precios,
  porcentajes, códigos, marcas, HTML, Markdown y palabras preservadas.
- Tokenización sin pérdida, lematización y segmentación conservadora CJK/Thai.
- Sinónimos desde JSON y WordNet/OMW, con filtros de contexto, frecuencia y modo.
- Reescritura determinista por oración, alternativas, ranking, legibilidad,
  AI-likeness y puerta de similitud semántica.
- Doce modos, guardas médicas, `avoid_words` y reescritura de nodos HTML visibles.
- Concordancia conservadora con spaCy: género/número de adjetivos, número de
  sustantivos y presente indicativo en tercera persona para lenguas soportadas.
- API `POST /api/rewrite` y `GET /health`; CLI `rewrite-engine`; GUI
  `rewrite-engine-gui`; scripts de batch y construcción de datos.
- `T5ParaphraserTransformer` opt-in para inglés y
  `TranslationBridgeTransformer` con MarianMT para los 16 idiomas.
- El modelo predeterminado es `Ateeqq/Text-Rewriter-Paraphraser` (Apache-2.0).
  `model_assets.py` prioriza modelos empaquetados y evita descargas al congelar.
- `OllamaTransformer` local por HTTP, usado por `scripts/batch_rewrite.py`; aún
  no tiene flags propios en la CLI general ni controles en la GUI.
- Guardas de transformers contra pérdida de tokens protegidos, longitud anómala
  y repetición degenerada.

## Trabajo en progreso

No hay una implementación activa registrada. Antes de empezar una tarea, añade
aquí su objetivo, archivos afectados y criterio de finalización.

## Pendientes priorizados

1. Mejorar desambiguación de WordNet/WSD. Es el mayor riesgo de calidad: una
   sustitución incorrecta puede mantener una similitud de oración alta.
2. Enriquecer tesauros de idiomas distintos de español con fuentes trazables y
   pruebas lingüísticas por idioma.
3. Añadir pruebas unitarias para `OllamaTransformer` (servidor simulado, timeout,
   modelo ausente, tokens protegidos) y decidir si se expone en CLI/GUI.
4. Ampliar conjugación sólo con una fuente morfológica fiable; no añadir reglas
   de sufijos para irregulares.
5. Añadir job de CI para construir/inspeccionar el wheel y un workflow Windows
   para el ejecutable; conservar el self-test como smoke test.
6. Añadir benchmarks versionados de calidad por idioma, modo y backend, con
   invariantes de entidades y medición de deriva semántica.
7. Completar diccionarios de industria (legal, salud, educación, marketing) y
   salidas estructuradas de SEO/marketplace.

## Hallazgos de los repositorios de referencia

`repos/` es material de investigación, no parte importable del producto. En la
revisión de 2026-07-12 se identificaron líneas de mejora, sin integrarlas aún:

- `harper-master`: arquitectura de lint gramatical rápida; útil como referencia
  para reglas locales, pero integrar Rust/WASM aumentaría complejidad.
- `language_tool_python-master` y `pyLanguagetool-master`: confirman que la
  integración actual opcional con LanguageTool es la vía de menor riesgo.
- `MUSE-main`: embeddings multilingües alineados; candidato para experimentos
  de similitud léxica, no sustituto demostrado de WSD contextual.
- `esperanto-analyzer-master` e `iVerbs-master`: posibles fuentes conceptuales
  para morfología, sujetas a verificar cobertura, licencia y pruebas antes de
  portar datos o lógica.
- `wikitextprocessor-main` y `langextract-main`: ideas para protección de
  estructura y extracción de entidades en entradas complejas; son demasiado
  pesadas para el núcleo actual y deben permanecer opcionales si se evalúan.
- `fairseq-gec-master`, `grammars-v4-master`, Ohm y los diccionarios RIME son
  infraestructuras amplias o especializadas; no deben incorporarse sin un caso
  de uso y benchmark concretos.
- Repositorios de diccionarios/tesauros pueden aportar cobertura, pero cada
  fuente requiere auditoría de licencia, formato, calidad y procedencia antes
  de generar JSON del proyecto.

## Decisiones técnicas vigentes

- Python 3.11+, layout `src/`, Hatchling y datos JSON empaquetados.
- Núcleo con dataclasses; Pydantic sólo en la API.
- Dependencias pesadas y backends de IA son opt-in con fallback seguro.
- El comportamiento predeterminado es local/offline y determinista.
- El protector opera antes del transformer y la restauración después; ningún
  backend puede omitir tokens `PROTECTEDTOKEN<n>X`.
- La similitud léxica usa un floor tolerante; embeddings habilitan la puerta
  estricta, pero ninguna de las dos garantiza detectar cambios sutiles de verbo.
- Los sustantivos no cambian de género por concordancia; sólo de número. Alemán
  no se reinflexiona con reglas simples.
- T5 se mantiene opt-in: el modelo predeterminado se entrenó para preguntas y
  puede no modificar declarativas. MarianMT se carga por idioma bajo demanda.
- Ollama usa biblioteca estándar y falla conservando la entrada; no es una
  dependencia obligatoria.
- `ttkthemes` es opcional y GPL-3.0-or-later; distribuirlo dentro del ejecutable
  implica obligaciones de copyleft que deben revisarse antes de publicar.
- Cualquier reutilización desde `repos/` exige comprobar licencia y procedencia;
  las ideas de referencia no convierten esos repositorios en dependencias.
- `HumanAI-main` (MIT) se integró mediante unión reproducible de marcadores para
  9 idiomas. `Humanizer-main` es CC BY-NC 4.0: se adoptó el concepto de catálogo
  multimodelo con implementación propia, sin copiar su código al paquete MIT.

## Problemas conocidos

- WordNet puede elegir una acepción incorrecta, especialmente en idiomas con
  diccionarios pequeños. Los embeddings reducen ruido, no resuelven WSD.
- Sin spaCy, POS/NER y nombres propios dependen de heurísticas.
- Sin LanguageTool o un transformer, quedan combinaciones gramaticales poco
  naturales; la conjugación regular cubre un subconjunto deliberado.
- Esperanto no tiene corrector ortográfico en la GUI.
- El puente de traducción puede propagar una sustitución léxica incorrecta y
  añadir coste/descargas de varios modelos.
- El T5 predeterminado no declara licencia explícita en su ficha de Hugging Face;
  verificar términos antes de distribución o uso comercial.
- El árbol de trabajo contiene eliminaciones locales de múltiples archivos
  `LICENSE` bajo `repos/`. No restaurarlas ni asumir intención; tampoco publicar
  esos cambios sin revisión del propietario.
- En el entorno de esta revisión el paquete no estaba instalado editable y Ruff
  no estaba instalado. Pytest requiere temporalmente `PYTHONPATH=src` hasta
  instalar `.[dev]`.

## Próximos pasos recomendados

1. Crear tests aislados de Ollama antes de exponerlo en más superficies.
2. Añadir benchmark lingüístico y ampliar diccionarios de ar/hi/tr/id; su
   cobertura inicial es deliberadamente pequeña.
3. Diseñar un benchmark pequeño de WSD para verbos comunes en es/en/pt/fr/it y
   usarlo para comparar diccionarios curados, WordNet y embeddings.
4. Elegir una sola fuente de tesauro adicional, auditarla y hacer una prueba de
   importación reproducible antes de ampliar todos los idiomas.

## Reanudación rápida

```powershell
cd E:\Usuarios\Tony\OneDrive\Documents\GitHub\Rewritte-Text-Multilang
python -m pip install -e ".[wordnet,api,cli,dev]"
python -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4')"
python -m pytest -q -m "not integration"
python -m ruff check src tests
python examples/demo.py
```

Al finalizar trabajo relevante, actualiza la fecha, el estado, los pendientes,
las decisiones afectadas y el resultado de validación. No acumules un diario
detallado: Git conserva el historial.

## Actualización 2026-07-12 — NLLB y dowdes.com

- NLLB-200 distilled 600M quedó convertido a CTranslate2 int8 en
  `models/nllb-200-distilled-600M-int8` (~651 MB). El backend es opcional,
  acepta los 16 ISO actuales y cualquier código FLORES-200 explícito.
- La GUI incorpora sincronización privada con dowdes.com: faltantes, todas o
  volver a reescribir, progreso estilo Windows 7, pausa, reanudación y cancelar.
- NLLB traduce y sirve para traducción/retrotraducción; no reemplaza el modelo
  de paráfrasis. Pesos CC-BY-NC-4.0; patrón de `NLLB_translator`, MIT.
- `dist/RewriteEngineAI` fue reconstruido con NLLB incluido: 2.73 GB. Tanto
  `--selftest` como `--ai-selftest` finalizaron con código 0.
- La ruta histórica `dist/RewriteEngine.exe` ahora es un lanzador ligero que
  abre `dist/RewriteEngineAI/RewriteEngineAI.exe` y propaga sus argumentos y
  códigos de salida. Ambos self-tests pasan también desde el lanzador.
