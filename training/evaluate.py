
import joblib
import pandas as pd
from scoring.features import FEATURE_COLUMNS
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    precision_score,
    recall_score,
)

# 1. Загружаем готовую модель и тест  
model = joblib.load("models/fraud_model.pkl")
test = pd.read_pickle("models/test_set.pkl")

X_test, y_test = test[FEATURE_COLUMNS], test["isFraud"]
probs = model.predict_proba(X_test)[:, 1]   # вероятность фрода для каждой операции

print("PR-AUC:", round(average_precision_score(y_test, probs), 4))

# 2. Переводим вероятности в решения по порогу
threshold = 0.5
preds = (probs >= threshold).astype(int)     # >=0.5 → считаем фродом (1), иначе честной (0)

# 3. Метрики
print("\nМатрица ошибок:")
print(confusion_matrix(y_test, preds))
print("\nPrecision (точность тревог):", round(precision_score(y_test, preds), 3))
print("Recall (доля пойманного фрода):", round(recall_score(y_test, preds), 3))

import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve
from pathlib import Path

precisions, recalls, thresholds = precision_recall_curve(y_test, probs)

plt.figure(figsize=(6, 5))
plt.plot(recalls, precisions)
plt.xlabel("Recall (доля пойманного фрода)")
plt.ylabel("Precision (точность тревог)")
plt.title(f"PR-кривая (PR-AUC = {average_precision_score(y_test, probs):.3f})")
plt.grid(True)

Path("reports").mkdir(exist_ok=True)
plt.savefig("reports/pr_curve.png", dpi=120, bbox_inches="tight")
print("PR-кривая сохранена в reports/pr_curve.png")