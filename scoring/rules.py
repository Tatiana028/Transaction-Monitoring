"""Rule engine: явные правила поверх ML. Каждое правило проверяется отдельно."""

# Пороги правил в ОДНОМ месте (конфиг), а не захардкожены по коду.
THRESHOLDS = {
    "large_amount": 1_000_000,    # было 200_000 — слишком часто
    "high_dest_velocity": 20,
}


def check_rules(txn: dict, feats: dict) -> list:
    """Прогоняет правила по одной транзакции. Возвращает список сработавших."""
    fired = []

    # Правило 1: по-настоящему крупная сумма
    if txn["amount"] > THRESHOLDS["large_amount"]:
        fired.append("large_amount")

    # Правило 2: TRANSFER, уводящий ВЕСЬ баланс с непустого счёта (классика фрода)
    if (txn["type"] == "TRANSFER"
            and txn["oldbalanceOrg"] > 0
            and feats["origBalanceZeroed"] == 1):
        fired.append("orig_balance_zeroed")

    # Правило 3: всплеск velocity получателя
    if feats["destTxnCountSoFar"] > THRESHOLDS["high_dest_velocity"]:
        fired.append("high_dest_velocity")

    return fired