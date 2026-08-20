"""Продюсер: читает PaySim по одной операции и шлёт в Redis Stream."""
import time
import pandas as pd
import redis

STREAM = "transactions"


def main(limit: int = 1000, delay: float = 0.01):
    r = redis.Redis(host="localhost", port=6379, decode_responses=True)
    r.delete(STREAM)   # чистим поток перед новым прогоном

    df = pd.read_csv("data/paysim.csv")
    df = df.sort_values("step")                          # хронологический порядок
    df = df[df["type"].isin(["TRANSFER", "CASH_OUT"])]   # только релевантные типы

    cols = ["step", "type", "amount", "nameOrig", "oldbalanceOrg", "newbalanceOrig",
            "nameDest", "oldbalanceDest", "newbalanceDest", "isFraud"]

    for _, row in df.head(limit).iterrows():
        txn = {col: str(row[col]) for col in cols}   # Redis Stream хранит строки
        r.xadd(STREAM, txn)                           # добавляем операцию в конец потока
        time.sleep(delay)                            # имитируем поток во времени

    print(f"Отправлено {min(limit, len(df))} операций в поток '{STREAM}'")


if __name__ == "__main__":
    main()