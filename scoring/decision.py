"""Decision layer: объединяет ML-скор и сработавшие правила в решение."""

DECISION_THRESHOLDS = {
    "block": 0.9,     # вероятность фрода, выше которой — блок
    "review": 0.5,    # выше которой — на ручную проверку
}


def decide(prob: float, fired_rules: list) -> str:
    """prob — вероятность фрода от модели (0..1),
    fired_rules — список сработавших правил.
    Возвращает 'allow' | 'review' | 'block'."""
    # Блок: модель очень уверена ИЛИ сработало несколько правил
    if prob >= DECISION_THRESHOLDS["block"] or len(fired_rules) >= 2:
        return "block"
    # Review: модель насторожена ИЛИ сработало хотя бы одно правило
    if prob >= DECISION_THRESHOLDS["review"] or len(fired_rules) >= 1:
        return "review"
    # Иначе — пропускаем
    return "allow"