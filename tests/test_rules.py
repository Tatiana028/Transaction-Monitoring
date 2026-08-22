"""Тесты правил и решений."""
from scoring.rules import check_rules
from scoring.decision import decide


def test_rule_account_drained_fires():
    txn = {"type": "TRANSFER", "amount": 5000.0, "oldbalanceOrg": 5000.0}
    feats = {"origBalanceZeroed": 1, "destTxnCountSoFar": 0}
    assert "orig_balance_zeroed" in check_rules(txn, feats)


def test_no_rules_on_normal():
    txn = {"type": "CASH_OUT", "amount": 500.0, "oldbalanceOrg": 20000.0}
    feats = {"origBalanceZeroed": 0, "destTxnCountSoFar": 0}
    assert check_rules(txn, feats) == []


def test_decision_blocks_on_high_prob():
    assert decide(0.95, []) == "block"


def test_decision_allows_when_clean():
    assert decide(0.0, []) == "allow"