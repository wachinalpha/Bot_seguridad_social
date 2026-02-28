# Evaluación del Sistema RAG

Scripts para medir la calidad de las respuestas del sistema.

## Setup

Las dependencias de eval se declaran como extras opcionales en `rag_app/pyproject.toml`. **No forman parte del entorno de producción.**

```bash
# Desde la carpeta rag_app/
cd rag_app
uv sync --extra eval
```

> Esto instala `matplotlib` además de las dependencias base. `requests` ya está incluido en el core.

## Uso

El backend debe estar corriendo antes de ejecutar los tests:

```bash
# Desde la raíz del proyecto
docker compose up -d

# Correr todos los casos
uv run --extra eval python3 tests/eval/run_eval.py

# Guardar reporte JSON
uv run --extra eval python3 tests/eval/run_eval.py --save-report

# Un solo caso
uv run --extra eval python3 tests/eval/run_eval.py --case q1_trabajo_informal

# Generar gráfico del último reporte
uv run --extra eval python3 tests/eval/plot_report.py

# Gráfico de un reporte específico
uv run --extra eval python3 tests/eval/plot_report.py tests/eval/reports/2026-02-21_17-45-30.json
```

## Estructura

```
tests/eval/
├── golden_dataset.json     ← 5 casos de prueba con ground truth
├── run_eval.py             ← orquestador principal
├── plot_report.py          ← genera PNG chart del reporte
├── metrics/
│   ├── retrieval.py        ← Hit Rate, Precision@k, NDCG@k
│   ├── citation.py         ← citation presence, keyword coverage
│   └── refusal.py         ← refusal accuracy, over/under refusal
└── reports/
    └── YYYY-MM-DD_HH-MM-SS.json   ← un archivo por run
    └── YYYY-MM-DD_HH-MM-SS.png    ← chart generado
```

## Métricas

| Métrica | Qué mide | Umbral objetivo |
|---|---|---|
| Hit Rate | ¿El doc correcto está en el top-3? | > 90% |
| Precision@k | % de docs recuperados que son relevantes | > 50% |
| NDCG@k | Hit rate ponderado por posición | > 80% |
| Citation Presence | ¿La respuesta tiene citas `[DOC_ID:Lx-Ly]`? | > 90% |
| Keyword Coverage | % de keywords del ground truth en la respuesta | > 75% |
| Refusal Accuracy | ¿Rechaza cuando debe y responde cuando debe? | 100% |
