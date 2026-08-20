"""Консьюмер: читает поток, гоняет конвейер, пишет решения в БД."""
import joblib
import pandas as pd
import redis
from scoring.features import RedisVelocityState, FEATURE_COLUMNS
from scoring.rules import check_rules
from scoring.decision import decide
from scoring.store import get_connection, save_decision

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
    r = redis.Redis(host="localhost", port=6379, decode_responses=True)
    model = joblib.load("models/fraud_model.pkl")
    state = RedisVelocityState()
    conn = get_connection()

    last_id = "0"          # читаем с самого начала ленты
    processed = 0
    while True:
        resp = r.xread({STREAM: last_id}, count=1, block=3000)  # ждём до 3 сек новую операцию
        if not resp:
            break          # тишина 3 сек -> поток кончился

        for _, messages in resp:
            for msg_id, data in messages:
                last_id = msg_id
                txn = parse(data)
                # ВЕСЬ конвейер на одной операции:
                feats = state.features_one(txn)                                     # признаки
                prob = model.predict_proba(pd.DataFrame([feats])[FEATURE_COLUMNS])[0, 1]  # ML
                rules = check_rules(txn, feats)                                     # правила
                decision = decide(prob, rules)                                      # решение
                save_decision(conn, txn, prob, rules, decision)                     # в БД
                processed += 1

    conn.close()
    print(f"Обработано {processed} операций")


if __name__ == "__main__":
    main()