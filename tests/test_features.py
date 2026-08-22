"""Тесты признаков."""
from scoring.features import instant_features_one, VelocityState


def test_instant_features_on_fraud_row():
    txn = {"step": 1, "amount": 181.0,
           "oldbalanceOrg": 181.0, "newbalanceOrig": 0.0,
           "nameDest": "C1", "oldbalanceDest": 21182.0, "newbalanceDest": 0.0}
    f = instant_features_one(txn)
    assert f["errorBalanceOrig"] == 0.0
    assert f["errorBalanceDest"] == 21363.0
    assert f["origBalanceZeroed"] == 1
    assert f["hourOfDay"] == 1


def test_velocity_state_accumulates():
    state = VelocityState()
    f1 = state.velocity_features_one({"nameDest": "C9", "amount": 100.0})
    assert f1 == {"destTxnCountSoFar": 0, "destAmountSoFar": 0.0}   # до первого — ничего
    f2 = state.velocity_features_one({"nameDest": "C9", "amount": 200.0})
    assert f2 == {"destTxnCountSoFar": 1, "destAmountSoFar": 100.0}  # помнит первый