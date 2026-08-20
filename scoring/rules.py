"""Rule engine: явные правила поверх ML. Каждое правило проверяется отдельно."""

# Пороги правил в ОДНОМ месте (конфиг), а не захардкожены по коду.
THRESHOLDS = {
    "large_amount": 200_000,      # подозрительно крупная сумма
    "high_dest_velocity": 20,     # получатель принял слишком много переводов
}


def check_rules(txn: dict, feats: dict) -> list:
    """Прогоняет все правила по одной транзакции.
    txn   — сырые поля операции,
    feats — уже посчитанные признаки (из features_one).
    Возвращает список названий СРАБОТАВШИХ правил."""
    fired = []

    # Правило 1: слишком крупная сумма
    if txn["amount"] > THRESHOLDS["large_amount"]:
        fired.append("large_amount")

    # Правило 2: счёт отправителя обнулён под ноль
    if feats["origBalanceZeroed"] == 1:
        fired.append("orig_balance_zeroed")

    # Правило 3: всплеск velocity — получатель принял слишком много переводов
    if feats["destTxnCountSoFar"] > THRESHOLDS["high_dest_velocity"]:
        fired.append("high_dest_velocity")

    return fired