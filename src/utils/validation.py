"""CSV and Transaction payload validation."""
import io
from datetime import datetime
from typing import Dict, Any, Tuple
import pandas as pd

REQUIRED_COLUMNS = ["transaction_id", "date", "description", "payee", "amount", "channel"]
VALID_CHANNELS = {"UPI", "CARD", "NEFT", "RTGS", "IMPS", "ATM", "NETBANKING", "BRANCH"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


class ValidationError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


def parse_flexible_date(date_str: str) -> datetime:
    """Parse date strings supporting common formats."""
    date_str = str(date_str).strip()
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%d",
        "%d-%m-%Y %H:%M:%S",
        "%d-%m-%Y %H:%M",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y %H:%M:%S"
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Invalid date format: '{date_str}'")


def validate_and_parse_csv(content_bytes: bytes) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Validate and parse uploaded CSV file contents.
    Returns: (cleaned_dataframe, summary_metadata)
    Raises: ValidationError on any schema violation.
    """
    if len(content_bytes) == 0:
        raise ValidationError("EMPTY_FILE", "The uploaded CSV file is empty.")

    if len(content_bytes) > MAX_FILE_SIZE_BYTES:
        raise ValidationError("FILE_TOO_LARGE", "The uploaded CSV file exceeds the 10MB limit.")

    try:
        # Decode as utf-8
        decoded_content = content_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            decoded_content = content_bytes.decode("latin-1")
        except Exception:
            raise ValidationError("INVALID_ENCODING", "File must be a valid UTF-8 encoded CSV.")

    try:
        df = pd.read_csv(io.StringIO(decoded_content), dtype=str)
    except Exception as e:
        raise ValidationError("MALFORMED_CSV", f"Failed to parse CSV format: {str(e)}")

    if df.empty:
        raise ValidationError("EMPTY_DATASET", "The uploaded CSV contains headers but no transaction rows.")

    # Normalize column names: strip and lowercase
    raw_columns = list(df.columns)
    col_map = {c: c.strip().lower() for c in raw_columns}
    df.rename(columns=col_map, inplace=True)

    # Check for missing required columns
    for req_col in REQUIRED_COLUMNS:
        if req_col not in df.columns:
            raise ValidationError(
                "MISSING_REQUIRED_COLUMN",
                f"Required column '{req_col}' is missing from the transaction file."
            )

    # Check for duplicate transaction IDs
    duplicate_ids = df[df["transaction_id"].duplicated()]["transaction_id"].unique()
    if len(duplicate_ids) > 0:
        sample_dupes = ", ".join(duplicate_ids[:3])
        raise ValidationError(
            "DUPLICATE_TRANSACTION_ID",
            f"Duplicate transaction IDs detected: {sample_dupes}"
        )

    # Validate each row
    cleaned_rows = []
    seen_channels = set()
    seen_payees = set()
    dates = []

    for idx, row in df.iterrows():
        row_num = idx + 2  # 1-indexed header + 1
        txn_id = str(row["transaction_id"]).strip()
        if not txn_id:
            raise ValidationError("EMPTY_TRANSACTION_ID", f"Row {row_num} has an empty transaction_id.")

        # Validate date
        raw_date = str(row["date"]).strip()
        try:
            dt = parse_flexible_date(raw_date)
            formatted_date = dt.strftime("%Y-%m-%d %H:%M:%S")
            dates.append(dt)
        except ValueError as e:
            raise ValidationError("INVALID_DATE", f"Row {row_num} has an invalid date: '{raw_date}'.")

        # Validate payee
        payee = str(row["payee"]).strip()
        if not payee or payee.lower() == "nan":
            raise ValidationError("EMPTY_PAYEE", f"Row {row_num} has an empty or missing payee.")
        seen_payees.add(payee)

        # Validate amount
        raw_amount = str(row["amount"]).replace(",", "").strip()
        try:
            amount = float(raw_amount)
            if amount < 0:
                raise ValidationError("NEGATIVE_AMOUNT", f"Row {row_num} has a negative transaction amount: {raw_amount}.")
            if amount == 0:
                raise ValidationError("ZERO_AMOUNT", f"Row {row_num} has a zero transaction amount.")
        except ValueError:
            raise ValidationError("NON_NUMERIC_AMOUNT", f"Row {row_num} has a non-numeric amount: '{raw_amount}'.")

        # Validate channel
        channel = str(row["channel"]).strip().upper()
        if channel not in VALID_CHANNELS:
            raise ValidationError(
                "UNSUPPORTED_CHANNEL",
                f"Row {row_num} has an unsupported channel: '{channel}'. Allowed: {', '.join(sorted(VALID_CHANNELS))}."
            )
        seen_channels.add(channel)

        desc = str(row["description"]).strip() if pd.notna(row["description"]) else "Transaction"

        cleaned_rows.append({
            "transaction_id": txn_id,
            "timestamp": formatted_date,
            "description": desc,
            "payee": payee,
            "amount": amount,
            "channel": channel
        })

    cleaned_df = pd.DataFrame(cleaned_rows)
    # Sort chronologically
    cleaned_df.sort_values(by="timestamp", inplace=True)
    cleaned_df.reset_index(drop=True, inplace=True)

    # Calculate coverage
    if dates:
        min_date = min(dates)
        max_date = max(dates)
        months_covered = max(1, round((max_date - min_date).days / 30.0, 1))
    else:
        months_covered = 0

    metadata = {
        "transactions_count": len(cleaned_df),
        "payees_count": len(seen_payees),
        "channels_count": len(seen_channels),
        "channels": sorted(list(seen_channels)),
        "months_covered": months_covered,
        "date_range": {
            "start": min_date.strftime("%Y-%m-%d") if dates else None,
            "end": max_date.strftime("%Y-%m-%d") if dates else None
        }
    }

    return cleaned_df, metadata
