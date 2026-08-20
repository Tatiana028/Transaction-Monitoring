"""Обучение модели фрода (batch-режим)."""
import pandas as pd
from scoring.features import build_features, FEATURE_COLUMNS

import lightgbm as lgb
from sklearn.metrics import average_precision_score

# 1. Загружаем сырые данные
df = pd.read_csv("data/paysim.csv")

# 2. Считаем все признаки (velocity по полной истории + мгновенные)
df = build_features(df)

# 3. Оставляем только типы, где бывает фрод
df = df[df["type"].isin(["TRANSFER", "CASH_OUT"])]

# 4. ВРЕМЕННОЙ сплит: ранние часы — на обучение, поздние — на проверку
split_step = 500  # граница по времени (шагу)
train = df[df["step"] <= split_step]
test = df[df["step"] > split_step]

print("Train:", train.shape, "| доля фрода:", round(train["isFraud"].mean(), 4))
print("Test :", test.shape, "| доля фрода:", round(test["isFraud"].mean(), 4))

# 5. Делим на признаки (X) и правильный ответ (y)
X_train, y_train = train[FEATURE_COLUMNS], train["isFraud"]
X_test,  y_test  = test[FEATURE_COLUMNS],  test["isFraud"]

# 6. Компенсация дисбаланса: во сколько раз честных больше, чем фрода.
#    Этот вес заставит модель НЕ игнорировать редкий класс.
scale = (y_train == 0).sum() / (y_train == 1).sum()
print("scale_pos_weight:", round(scale, 1))

# 7. Обучаем модель
model = lgb.LGBMClassifier(
    n_estimators=200,       # сколько деревьев строим
    learning_rate=0.05,     # насколько осторожно учимся
    scale_pos_weight=scale, # вес редкого класса (фрод)
    random_state=42,        # фиксируем случайность → воспроизводимость
)
model.fit(X_train, y_train)

# 8. Проверяем на тесте. Главная метрика — PR-AUC.
probs = model.predict_proba(X_test)[:, 1]        # вероятность «это фрод» для каждой операции
pr_auc = average_precision_score(y_test, probs)
print("PR-AUC на тесте:", round(pr_auc, 4))

# Насколько активно модель использовала каждый признак
importances = pd.Series(model.feature_importances_, index=FEATURE_COLUMNS)
print("\nВажность признаков:")
print(importances.sort_values(ascending=False))