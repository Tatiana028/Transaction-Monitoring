-- Каждая обработанная транзакция и её итог
CREATE TABLE IF NOT EXISTS decisions (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,  -- уникальный номер записи
    step         INTEGER,      -- час симуляции
    amount       REAL,         -- сумма операции
    name_orig    TEXT,         -- отправитель
    name_dest    TEXT,         -- получатель
    fraud_prob   REAL,         -- вероятность фрода от модели
    fired_rules  TEXT,         -- сработавшие правила (через запятую)
    decision     TEXT,         -- allow / review / block
    is_fraud     INTEGER,      -- истинная метка (для метрик на дашборде)
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- когда записали
);
