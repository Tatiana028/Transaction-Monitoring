"""Консьюмер: читает поток, гоняет конвейер, пишет решения в БД."""
import joblib
import pandas as pd
import redis
from scoring.features import RedisVelocityState, FEATURE_COLUMNS
from scoring.rules import check_rules
from scoring.decision import decide
from scoring.store import get_connection, save_decision
import os

STREAM = "transactions"


def parse(data: dict) -> dict:
    """Redis отдаёт всё строками — возвращаем числам их типы."""
    return {
        "step": int(data["step"]), "type": data["type"], "amount": float(data["amount"]),
        "nameOrig": data["nameOrig"], "oldbalanceOrg": float(data["oldbalanceOrg"]),
        "newbalanceOrig": float(data["newbalanceOrig"]), "nameDest": data["nameDest"],
        "oldbalanceDest": float(data["oldbalanceDest"]), "newbalanceDest": float(data["newbalanceDest"]),
        "isFraud": int(data["isFraud"]),
    }


def main():
    #r = redis.Redis(host="localhost", port=6379, decode_responses=True)
    r = redis.Redis(host=os.environ.get("REDIS_HOST", "localhost"),
                    port=6379, decode_responses=True)
    model = joblib.load("models/fraud_model.pkl")
    state = RedisVelocityState()
    conn = get_connection()

    last_id = "0"          # читаем с начала ленты
    processed = 0
    empty_reads = 0
    while empty_reads < 3:                # выходим после ~15 сек тишины (3 × 5 сек)
        resp = r.xread({STREAM: last_id}, count=1, block=5000)
        if not resp:
            empty_reads += 1             # пустое чтение — ждём ещё
            continue
        empty_reads = 0                  # пришли данные — сбрасываем счётчик
        for _, messages in resp:
            for msg_id, data in messages:
                last_id = msg_id
                txn = parse(data)
                feats = state.features_one(txn)
                prob = model.predict_proba(pd.DataFrame([feats])[FEATURE_COLUMNS])[0, 1]
                rules = check_rules(txn, feats)
                decision = decide(prob, rules)
                save_decision(conn, txn, prob, rules, decision)
                processed += 1

    conn.close()
    print(f"Обработано {processed} операций")


if __name__ == "__main__":
    main()