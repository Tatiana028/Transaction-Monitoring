"""Признаки для модели фрода. 
"""
import pandas as pd


def add_instant_features(df: pd.DataFrame) -> pd.DataFrame:
    """Добавляет признаки, считающиеся из ОДНОЙ строки (без истории клиента)."""
    df = df.copy()  # не портим исходный датафрейм, работаем с копией

    # Error-balance: в норме ≈ 0. Ненулевое отклонение — сильнейший сигнал фрода.
    df["errorBalanceOrig"] = df["oldbalanceOrg"] - df["amount"] - df["newbalanceOrig"]
    df["errorBalanceDest"] = df["oldbalanceDest"] + df["amount"] - df["newbalanceDest"]

    # Какую долю счёта двигаем. +1 в знаменателе — страховка от деления на ноль.
    df["amountToBalanceRatio"] = df["amount"] / (df["oldbalanceOrg"] + 1)

    # Флаг полного обнуления счёта отправителя (классика фрода).
    df["origBalanceZeroed"] = ((df["newbalanceOrig"] == 0) & (df["amount"] > 0)).astype(int)

    # Час суток (step идёт по часам) — ночная активность бывает подозрительной.
    df["hourOfDay"] = df["step"] % 24

    return df