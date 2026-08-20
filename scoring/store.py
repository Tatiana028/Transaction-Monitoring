"""Запись решений в SQLite."""
import sqlite3

DB_PATH = "db/fraud.db"


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Открывает соединение с базой (создаёт файл, если его нет)."""
    return sqlite3.connect(db_path)


def save_decision(conn, txn: dict, prob: float, fired_rules: list, decision: str) -> None:
    """Сохраняет одно решение в таблицу decisions."""
    conn.execute(
        """INSERT INTO decisions
           (step, amount, name_orig, name_dest, fraud_prob, fired_rules, decision, is_fraud)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            txn["step"],
            txn["amount"],
            txn["nameOrig"],
            txn["nameDest"],
            prob,
            ",".join(fired_rules),   # список правил -> строка через запятую
            decision,
            txn.get("isFraud"),      # истинная метка (None, если нет)
        ),
    )
    conn.commit()