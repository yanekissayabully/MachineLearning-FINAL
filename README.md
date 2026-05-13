# Stock Classifier — KZ & US Market

Система машинного обучения для классификации сигналов на фондовых рынках Казахстана (KASE) и США (NYSE/Nasdaq). Проект включает в себя пайплайн сбора данных, инженерию признаков (технических и фундаментальных), обучение модели XGBoost и веб-сервис для получения предсказаний в реальном времени.

## Основные возможности

- **Двойной рынок**: Поддержка KASE (Казахстан) через API kase.kz и US рынка через Yahoo Finance.
- **Инженерия признаков**:
  - Технические индикаторы (RSI, MACD, BB, ATR, скользящие средние и др.)
  - Фундаментальные показатели (EPS, P/E, P/B, маржинальность, долговая нагрузка)
- **Моделирование**: XGBoost Classifier с временной кросс-валидацией (TimeSeriesSplit).
- **Веб-сервис**: FastAPI backend + Streamlit frontend для интерактивного получения сигналов (Buy/Hold/Sell).
- **Docker Compose**: Легкий запуск всей инфраструктуры.

## Наш стек

- **Язык**: Python 3.12+
- **ML**: XGBoost, Scikit-learn, Pandas, NumPy
- **API**: FastAPI, Uvicorn
- **Frontend**: Streamlit
- **Источники данных**: Yahoo Finance (`yfinance`), KASE API
- **Контейнеризация**: Docker, Docker Compose

## Структура проекта

```
.
├── app/
│   ├── main.py                  # FastAPI эндпоинты (/predict/ticker, /info)
│   ├── predict.py               # Загрузка моделей и логика инференса
│   ├── frontend.py              # Streamlit UI
│   └── pipeline/
│       ├── features/            # Генерация признаков (technical.py, fundamental.py)
│       ├── labels/              # Формирование целевой переменной (forward_return.py)
│       └── ingest/              # Загрузчики данных (yfinance_fetcher.py, kase_fetcher.py)
├── data/                        # Сырые и обработанные датасеты (не включены в репозиторий)
├── notebooks/
│   ├── 3models.ipynb            # Сравнение моделей KZ vs US (технические vs фундаментальные)
│   └── test.ipynb               # Основной файл: обучение, оценка, сохранение модели
├── model_kz.pkl                 # Обученная модель XGBoost для рынка KZ
├── scaler_kz.pkl                # StandardScaler для предобработки
├── label_encoder_kz.pkl         # LabelEncoder для преобразования классов
├── features_list.pkl            # Список признаков, используемых моделью
├── requirements.txt             # Зависимости Python
├── docker-compose.yml           # Оркестрация API и Frontend
└── README.md
```

## Моделирование 

### Результаты

| Рынок          | Тип признаков      | Accuracy | F1 (macro) |
|----------------|--------------------|----------|------------|
| **KZ (KASE)**  | Технические        | **57.5%**| 0.35       |
| US             | Технические        | 41.7%    | 0.32       |
| US             | Фундаментальные    | 34.4%    | 0.30       |
| Baseline       | most_frequent      | 60.1%    | 0.25       |

> **Ключевые выводы**:
> - Рынок KZ предсказывается лучше, что может свидетельствовать о его меньшей эффективности и наличии аномалий.
> - Технические признаки оказались значительно информативнее фундаментальных для 20-дневного горизонта прогнозирования.
> - Модель XGBoost превосходит бейзлайн по макро F1-мере, несмотря на меньшую accuracy.

### Процесс обучения 

1. **Загрузка данных**: KASE (`kase.csv`) и US (`us.csv`) с 2019–2026 гг.
2. **Предобработка**:
   - Целевая переменная: `ret_fwd_20` -> троичная классификация (buy, hold, sell) с порогом 5%.
   - Imputation: медианная стратегия.
   - Scaling: StandardScaler.
3. **Временное разделение**:
   - Train: до 2025-01-01
   - Test: после 2025-01-01 (без утечек данных)
4. **Обучение XGBoost** с параметрами:
   - `max_depth=5`, `learning_rate=0.05`, `n_estimators=300`
   - `subsample=0.8`, `colsample_bytree=0.8`
5. **Оценка**: Accuracy, Macro F1, Confusion Matrix, Walk‑Forward CV.

## Запуск через Docker Compose

```bash
docker-compose up --build
```

После запуска будут доступны:

- **API**: http://localhost:8000
  - `GET /info` – информация о модели
  - `POST /predict/ticker` – предсказание по тикеру (JSON: `{"ticker": "KSPI", "market": "auto"}`)
- **Frontend**: http://localhost:8501 – веб-интерфейс Streamlit

## Локальный запуск 

1. **Установка зависимостей**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Запуск API**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

3. **Запуск Frontend** (в другом терминале):
   ```bash
   export API_URL="http://localhost:8000"
   streamlit run app/frontend.py
   ```

## Пример использования API

```bash
curl -X POST "http://localhost:8000/predict/ticker" \
     -H "Content-Type: application/json" \
     -d '{"ticker": "KSPI", "market": "auto"}'
```

**Ответ**:
```json
{
  "signal": "Buy",
  "confidence": 0.73,
  "probabilities": {
    "Buy": 0.73,
    "Hold": 0.20,
    "Sell": 0.07
  },
  "ticker": "KSPI",
  "market": "kz"
}
```

## Источники данных

- **KASE**: TradingView UDF эндпоинт (kase.kz/tv-charts/securities/history). Поддерживаются тикеры из списка `KASE_TICKERS`.
- **US**: Yahoo Finance (через `yfinance`). Используется подмножество S&P 500 (см. `US_TICKERS`).

## Тестирование и воспроизводимость

Все этапы анализа и обучения полностью воспроизводимы в Jupyter Notebook:
- `test.ipynb` – итоговое обучение модели KZ, оценка, сравнение с US и сохранение артефактов.
- `3models.ipynb` – расширенное сравнение трёх подходов (KZ technical, US technical, US fundamental).
