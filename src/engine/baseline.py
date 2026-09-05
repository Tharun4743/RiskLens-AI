"""Customer Behavioral Baseline Engine.
Computes robust customer-specific behavioral distributions and thresholds.
Does not compare one customer's behaviour against another.
"""
from datetime import datetime
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd


class BaselineProfile:
    """Stores calculated behavioral baseline metrics for a single customer."""
    def __init__(self, data: Dict[str, Any]):
        self.data = data

    def to_dict(self) -> Dict[str, Any]:
        return self.data


def calculate_baseline(transactions_df: pd.DataFrame, cutoff_date: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Calculate customer-specific behavioral profile using robust statistics.
    If cutoff_date is provided, baseline is calculated on transactions strictly prior to cutoff_date.
    """
    if transactions_df.empty:
        return {
            "is_reliable": False,
            "reason": "No transactions found for customer.",
            "transaction_count": 0
        }

    df = transactions_df.copy()
    df["dt"] = pd.to_datetime(df["timestamp"])

    if cutoff_date is not None:
        baseline_df = df[df["dt"] < cutoff_date].copy()
    else:
        baseline_df = df.copy()

    total_txns = len(baseline_df)
    if total_txns < 5:
        return {
            "is_reliable": False,
            "reason": "Insufficient historical transactions (minimum 5 required) to establish reliable baseline.",
            "transaction_count": total_txns
        }

    amounts = baseline_df["amount"].astype(float).values
    median_amt = float(np.median(amounts))
    mean_amt = float(np.mean(amounts))
    p25 = float(np.percentile(amounts, 25))
    p75 = float(np.percentile(amounts, 75))
    p90 = float(np.percentile(amounts, 90))
    p95 = float(np.percentile(amounts, 95))
    p99 = float(np.percentile(amounts, 99))
    iqr = p75 - p25

    # Hours analysis
    hours = baseline_df["dt"].dt.hour.values
    active_hours = sorted(list(set(int(h) for h in hours)))
    odd_hours_count = int(np.sum((hours >= 0) & (hours <= 5)))
    odd_hours_ratio = float(odd_hours_count / total_txns) if total_txns > 0 else 0.0

    # Payees analysis
    payee_counts = baseline_df["payee"].value_counts().to_dict()
    known_payees = sorted(list(payee_counts.keys()))

    # Channel distribution
    channel_counts = baseline_df["channel"].value_counts().to_dict()
    channel_pct = {ch: round((cnt / total_txns) * 100.0, 1) for ch, cnt in channel_counts.items()}
    channel_volume = baseline_df.groupby("channel")["amount"].sum().to_dict()
    total_vol = float(np.sum(amounts))
    channel_vol_pct = {ch: round((vol / total_vol) * 100.0, 1) if total_vol > 0 else 0.0 for ch, vol in channel_volume.items()}

    # Daily frequency
    dates = baseline_df["dt"].dt.date
    min_date = baseline_df["dt"].min()
    max_date = baseline_df["dt"].max()
    span_days = max(1, (max_date - min_date).days)
    daily_txns = baseline_df.groupby(dates).size().values
    mean_daily_frequency = float(np.mean(daily_txns)) if len(daily_txns) > 0 else 0.0
    median_daily_frequency = float(np.median(daily_txns)) if len(daily_txns) > 0 else 0.0

    # Hourly distribution map (0 to 23)
    hourly_distribution = {h: int(np.sum(hours == h)) for h in range(24)}

    # Typical transaction hours range
    typical_min_hour = int(np.percentile(hours, 5))
    typical_max_hour = int(np.percentile(hours, 95))

    return {
        "is_reliable": True,
        "transaction_count": total_txns,
        "date_span_days": span_days,
        "median_amount": round(median_amt, 2),
        "mean_amount": round(mean_amt, 2),
        "percentiles": {
            "p25": round(p25, 2),
            "p50": round(median_amt, 2),
            "p75": round(p75, 2),
            "p90": round(p90, 2),
            "p95": round(p95, 2),
            "p99": round(p99, 2),
            "iqr": round(iqr, 2)
        },
        "typical_range": {
            "min": round(p25, 2),
            "max": round(p75, 2),
            "upper_bound_iqr": round(p75 + 1.5 * iqr, 2)
        },
        "daily_frequency": {
            "mean": round(mean_daily_frequency, 1),
            "median": round(median_daily_frequency, 1)
        },
        "odd_hours": {
            "count": odd_hours_count,
            "ratio": round(odd_hours_ratio, 4),
            "percentage": round(odd_hours_ratio * 100.0, 2)
        },
        "typical_hours": {
            "min": typical_min_hour,
            "max": typical_max_hour,
            "display": f"{typical_min_hour:02d}:00–{typical_max_hour:02d}:00"
        },
        "hourly_distribution": hourly_distribution,
        "known_payees_count": len(known_payees),
        "known_payees": known_payees,
        "payee_frequencies": payee_counts,
        "channel_distribution_count_pct": channel_pct,
        "channel_distribution_volume_pct": channel_vol_pct,
        "total_volume": round(total_vol, 2)
    }
