"""Tests for CSV validation layer (TC08, TC09, TC10, TC11)."""
import pytest
from src.utils.validation import validate_and_parse_csv, ValidationError


def test_tc08_missing_column():
    """TC08: Rejects CSV missing required column."""
    content = b"transaction_id,date,description,amount,channel\nTXN1,2026-01-01 10:00,Salary,5000,NEFT"
    with pytest.raises(ValidationError) as exc:
        validate_and_parse_csv(content)
    assert exc.value.code == "MISSING_REQUIRED_COLUMN"
    assert "payee" in exc.value.message


def test_tc09_invalid_amount():
    """TC09: Rejects non-numeric and negative amounts."""
    # Negative amount
    neg_content = b"transaction_id,date,description,payee,amount,channel\nTXN1,2026-01-01 10:00,Salary,ABC,-5000,NEFT"
    with pytest.raises(ValidationError) as exc1:
        validate_and_parse_csv(neg_content)
    assert exc1.value.code == "NEGATIVE_AMOUNT"

    # Non-numeric amount
    non_num_content = b"transaction_id,date,description,payee,amount,channel\nTXN1,2026-01-01 10:00,Salary,ABC,INVALID,NEFT"
    with pytest.raises(ValidationError) as exc2:
        validate_and_parse_csv(non_num_content)
    assert exc2.value.code == "NON_NUMERIC_AMOUNT"


def test_tc10_duplicate_transaction_id():
    """TC10: Rejects duplicate transaction IDs."""
    dupe_content = (
        b"transaction_id,date,description,payee,amount,channel\n"
        b"TXN1,2026-01-01 10:00,Salary,ABC,5000,NEFT\n"
        b"TXN1,2026-01-02 10:00,Salary,ABC,5000,NEFT\n"
    )
    with pytest.raises(ValidationError) as exc:
        validate_and_parse_csv(dupe_content)
    assert exc.value.code == "DUPLICATE_TRANSACTION_ID"


def test_tc11_empty_dataset():
    """TC11: Rejects completely empty file and header-only CSV."""
    with pytest.raises(ValidationError) as exc1:
        validate_and_parse_csv(b"")
    assert exc1.value.code == "EMPTY_FILE"

    header_only = b"transaction_id,date,description,payee,amount,channel\n"
    with pytest.raises(ValidationError) as exc2:
        validate_and_parse_csv(header_only)
    assert exc2.value.code == "EMPTY_DATASET"


def test_valid_csv_parsing():
    """Verify correct parsing of valid CSV."""
    valid_csv = (
        b"transaction_id,date,description,payee,amount,channel\n"
        b"TXN101,2026-01-05 10:30:00,Salary,ABC Corp,55000,NEFT\n"
        b"TXN102,2026-01-06 14:15:00,Grocery,Fresh Mart,2350,CARD\n"
    )
    df, meta = validate_and_parse_csv(valid_csv)
    assert len(df) == 2
    assert meta["transactions_count"] == 2
    assert meta["channels_count"] == 2
    assert meta["payees_count"] == 2
