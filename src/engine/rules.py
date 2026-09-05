"""Deterministic Risk Rules Engine (R001 - R004).
Python decides whether rules trigger. AI never decides rule triggers.
"""
from datetime import timedelta
from typing import Dict, Any, Optional
import pandas as pd
from src.utils.helpers import format_currency_inr


def evaluate_r001_large_transfer(
    transactions_df: pd.DataFrame,
    baseline: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    R001: Unusually Large Transfer.
    Identifies transactions materially above customer's normal distribution.
    Threshold: amount > 95th percentile AND amount > multiplier * median AND amount >= min_material_amount.
    """
    cfg = config or {}
    pct_threshold = cfg.get("percentile_threshold", 95.0)
    mult_threshold = cfg.get("multiplier_threshold", 5.0)
    min_material_amt = cfg.get("min_material_amount", 150000.0)

    rule_info = {
        "rule_id": "R001",
        "name": "Unusually Large Transfer",
        "status": "NOT_TRIGGERED",
        "findings": [],
        "insufficient_data": not baseline.get("is_reliable", False)
    }

    if not baseline.get("is_reliable", False) or transactions_df.empty:
        rule_info["status"] = "INSUFFICIENT_DATA"
        return rule_info

    median_amt = baseline["median_amount"]
    p95_amt = baseline["percentiles"]["p95"]
    trigger_cutoff = max(p95_amt, median_amt * mult_threshold, min_material_amt)

    df = transactions_df.copy()
    # Transactions at or above trigger cutoff
    candidate_txns = df[df["amount"] >= trigger_cutoff].copy()

    # Filter out established recurring transactions (e.g. exact regular recurring monthly salary/rent seen >= 3 times)
    flagged_rows = []
    for _, row in candidate_txns.iterrows():
        payee = row["payee"]
        amt = float(row["amount"])
        # Check frequency of this exact (payee, amount) pair in the dataset
        recurring_count = len(df[(df["payee"] == payee) & (abs(df["amount"] - amt) < 1.0)])
        if recurring_count >= 3:
            # Established recurring regular transaction
            continue
        flagged_rows.append(row)

    if not flagged_rows:
        return rule_info

    flagged_txns = pd.DataFrame(flagged_rows)

    rule_info["status"] = "TRIGGERED"
    finding_idx = 1

    for _, row in flagged_txns.iterrows():
        txn_id = str(row["transaction_id"])
        amt = float(row["amount"])
        dev_mult = round(amt / median_amt, 1) if median_amt > 0 else round(amt, 1)

        evidence_items = [{
            "transaction_id": txn_id,
            "evidence_type": "LARGE_TRANSFER_AMOUNT",
            "observed_value": format_currency_inr(amt),
            "baseline_value": format_currency_inr(median_amt),
            "deviation": f"{dev_mult}x customer median",
            "explanation": f"Transaction amount of {format_currency_inr(amt)} exceeds customer 95th percentile ({format_currency_inr(p95_amt)}) and is {dev_mult}x the historical median ({format_currency_inr(median_amt)})."
        }]

        finding = {
            "finding_id": f"F-001-{finding_idx:02d}",
            "rule_id": "R001",
            "severity": "HIGH",
            "title": f"Unusually Large Transfer of {format_currency_inr(amt)}",
            "description": f"Transaction {txn_id} to '{row['payee']}' for {format_currency_inr(amt)} exceeds historical threshold by {dev_mult}x.",
            "confidence": 0.98,
            "transaction_ids": [txn_id],
            "evidence": evidence_items,
            "observed_amount": amt,
            "baseline_median": median_amt,
            "multiplier": dev_mult,
            "payee": row["payee"],
            "channel": row["channel"],
            "date": row["timestamp"]
        }
        rule_info["findings"].append(finding)
        finding_idx += 1

    return rule_info


def evaluate_r002_new_payee_burst(
    transactions_df: pd.DataFrame,
    baseline: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    R002: New Payee Burst.
    Identifies multiple rapid transactions to a newly seen payee within a short time window.
    Default window: 60 minutes. Default min transactions: 3.
    """
    cfg = config or {}
    window_minutes = cfg.get("time_window_minutes", 60)
    min_txns = cfg.get("min_transactions", 3)
    min_total_amt = cfg.get("min_total_amount", 20000.0)

    rule_info = {
        "rule_id": "R002",
        "name": "New Payee Burst",
        "status": "NOT_TRIGGERED",
        "findings": [],
        "insufficient_data": not baseline.get("is_reliable", False)
    }

    if not baseline.get("is_reliable", False) or transactions_df.empty:
        rule_info["status"] = "INSUFFICIENT_DATA"
        return rule_info

    df = transactions_df.copy()
    df["dt"] = pd.to_datetime(df["timestamp"])
    df.sort_values(by="dt", inplace=True)

    # Group by payee and examine first appearance and clusters
    payees = df["payee"].unique()
    finding_idx = 1

    for payee in payees:
        payee_df = df[df["payee"] == payee].copy()
        if len(payee_df) < min_txns:
            continue

        # Check if payee has rapid burst
        # Sliding window over payee's transactions
        p_txns = payee_df.to_dict("records")
        first_seen_dt = p_txns[0]["dt"]

        # Find clusters of >= min_txns within window_minutes
        for i in range(len(p_txns)):
            cluster = [p_txns[i]]
            start_t = p_txns[i]["dt"]
            for j in range(i + 1, len(p_txns)):
                diff_mins = (p_txns[j]["dt"] - start_t).total_seconds() / 60.0
                if diff_mins <= window_minutes:
                    cluster.append(p_txns[j])
                else:
                    break

            if len(cluster) >= min_txns:
                cluster_amt = sum(float(x["amount"]) for x in cluster)
                if cluster_amt < min_total_amt:
                    continue

                duration_mins = max(1, round((cluster[-1]["dt"] - cluster[0]["dt"]).total_seconds() / 60.0))
                txn_ids = [str(x["transaction_id"]) for x in cluster]

                # Check if we already flagged these transactions
                already_flagged = any(
                    set(txn_ids).issubset(set(f["transaction_ids"]))
                    for f in rule_info["findings"]
                )
                if already_flagged:
                    continue

                rule_info["status"] = "TRIGGERED"

                evidence_items = []
                for item in cluster:
                    amt_str = format_currency_inr(item["amount"])
                    evidence_items.append({
                        "transaction_id": str(item["transaction_id"]),
                        "evidence_type": "NEW_PAYEE_BURST_TXN",
                        "observed_value": f"{amt_str} via {item['channel']} at {item['timestamp']}",
                        "baseline_value": "Payee previously unknown / 0 historical baseline transactions",
                        "deviation": f"{len(cluster)} transactions in {duration_mins}m",
                        "explanation": f"Part of {len(cluster)}-transaction rapid burst to newly seen payee '{payee}' within {duration_mins} minutes."
                    })

                finding = {
                    "finding_id": f"F-002-{finding_idx:02d}",
                    "rule_id": "R002",
                    "severity": "HIGH",
                    "title": f"Rapid Payment Burst to New Payee '{payee}'",
                    "description": f"Detected {len(cluster)} transactions totaling {format_currency_inr(cluster_amt)} to first-seen payee '{payee}' within a {duration_mins}-minute window.",
                    "confidence": 0.96,
                    "transaction_ids": txn_ids,
                    "evidence": evidence_items,
                    "payee": payee,
                    "first_seen": first_seen_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "transaction_count": len(cluster),
                    "duration_minutes": duration_mins,
                    "total_amount": cluster_amt
                }
                rule_info["findings"].append(finding)
                finding_idx += 1
                break  # avoid multiple overlapping clusters for same payee burst

    return rule_info


def evaluate_r003_odd_hours(
    transactions_df: pd.DataFrame,
    baseline: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    R003: Odd-Hours Activity.
    Default period: 00:00 - 05:00.
    Compares against customer history (customer has <= max_historical_rate, e.g. 3% odd-hours transactions).
    """
    cfg = config or {}
    start_hour = cfg.get("start_hour", 0)
    end_hour = cfg.get("end_hour", 5)
    max_hist_rate = cfg.get("max_historical_rate", 0.03)

    rule_info = {
        "rule_id": "R003",
        "name": "Odd-Hours Activity",
        "status": "NOT_TRIGGERED",
        "findings": [],
        "insufficient_data": not baseline.get("is_reliable", False)
    }

    if not baseline.get("is_reliable", False) or transactions_df.empty:
        rule_info["status"] = "INSUFFICIENT_DATA"
        return rule_info

    hist_rate = baseline["odd_hours"]["ratio"]
    hist_count = baseline["odd_hours"]["count"]
    typical_hours_str = baseline["typical_hours"]["display"]

    df = transactions_df.copy()
    df["dt"] = pd.to_datetime(df["timestamp"])
    df["hour"] = df["dt"].dt.hour

    odd_df = df[(df["hour"] >= start_hour) & (df["hour"] <= end_hour)].copy()

    if odd_df.empty:
        return rule_info

    # If customer historically routinely transacts late night (> max_hist_rate), do not trigger false alarm
    if hist_rate > max_hist_rate and hist_count > 10:
        return rule_info

    rule_info["status"] = "TRIGGERED"
    odd_txns = odd_df.to_dict("records")
    odd_txn_ids = [str(x["transaction_id"]) for x in odd_txns]
    total_odd_amt = sum(float(x["amount"]) for x in odd_txns)

    evidence_items = []
    for item in odd_txns:
        evidence_items.append({
            "transaction_id": str(item["transaction_id"]),
            "evidence_type": "ODD_HOURS_TIMESTAMP",
            "observed_value": f"{item['timestamp']} ({format_currency_inr(item['amount'])})",
            "baseline_value": f"Normal hours: {typical_hours_str} ({round(hist_rate * 100, 1)}% historical odd-hour rate)",
            "deviation": f"Transaction executed at {item['dt'].strftime('%H:%M:%S')} (00:00–05:00 window)",
            "explanation": f"Transaction initiated at {item['dt'].strftime('%H:%M:%S')}, outside customer's established active hours ({typical_hours_str})."
        })

    finding = {
        "finding_id": "F-003-01",
        "rule_id": "R003",
        "severity": "MEDIUM",
        "title": f"Unusual Odd-Hours Activity ({len(odd_txns)} transactions)",
        "description": f"Identified {len(odd_txns)} transactions executed between {start_hour:02d}:00 and {end_hour:02d}:59 totaling {format_currency_inr(total_odd_amt)}. Customer has {round(hist_rate * 100, 1)}% historical night activity.",
        "confidence": 0.92,
        "transaction_ids": odd_txn_ids,
        "evidence": evidence_items,
        "odd_transactions_count": len(odd_txns),
        "total_amount": total_odd_amt,
        "historical_rate_pct": round(hist_rate * 100, 2),
        "typical_hours": typical_hours_str
    }
    rule_info["findings"].append(finding)

    return rule_info


def evaluate_r004_behavioural_break(
    transactions_df: pd.DataFrame,
    baseline: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    R004: Behavioural Pattern Break.
    Compares historical customer behavior against recent activity window (last 7-10 days).
    Analyzes channel distribution shifts, volume spikes, and payment velocity breaks.
    """
    cfg = config or {}
    recent_days = cfg.get("recent_window_days", 10)
    min_deviation_pct = cfg.get("min_channel_deviation_pct", 30.0)
    min_recent_txns = cfg.get("min_recent_txns", 4)
    min_recent_vol = cfg.get("min_recent_volume", 75000.0)

    rule_info = {
        "rule_id": "R004",
        "name": "Behavioural Pattern Break",
        "status": "NOT_TRIGGERED",
        "findings": [],
        "insufficient_data": not baseline.get("is_reliable", False)
    }

    if not baseline.get("is_reliable", False) or transactions_df.empty:
        rule_info["status"] = "INSUFFICIENT_DATA"
        return rule_info

    df = transactions_df.copy()
    df["dt"] = pd.to_datetime(df["timestamp"])
    max_dt = df["dt"].max()
    cutoff_dt = max_dt - timedelta(days=recent_days)

    historical_df = df[df["dt"] < cutoff_dt]
    recent_df = df[df["dt"] >= cutoff_dt]

    if len(recent_df) < min_recent_txns or len(historical_df) < 10:
        return rule_info

    total_recent_vol = float(recent_df["amount"].sum())
    # Guard against small statistical noise: must represent material recent activity
    if total_recent_vol < min_recent_vol:
        return rule_info

    # Analyze Channel Distribution shift (both count and volume)
    hist_count = historical_df["channel"].value_counts(normalize=True) * 100.0
    recent_count = recent_df["channel"].value_counts(normalize=True) * 100.0

    hist_vol = historical_df.groupby("channel")["amount"].sum()
    total_hist_vol = historical_df["amount"].sum()
    hist_vol_pct = (hist_vol / total_hist_vol * 100.0) if total_hist_vol > 0 else pd.Series()

    recent_vol = recent_df.groupby("channel")["amount"].sum()
    total_recent_vol = recent_df["amount"].sum()
    recent_vol_pct = (recent_vol / total_recent_vol * 100.0) if total_recent_vol > 0 else pd.Series()

    all_chans = set(hist_count.index).union(set(recent_count.index))
    channel_shifts = {}
    max_shift_channel = None
    max_shift_val = 0.0

    for ch in all_chans:
        h_pct = round(float(hist_vol_pct.get(ch, hist_count.get(ch, 0.0))), 1)
        r_pct = round(float(recent_vol_pct.get(ch, recent_count.get(ch, 0.0))), 1)
        diff = round(r_pct - h_pct, 1)
        channel_shifts[ch] = {"historical_pct": h_pct, "recent_pct": r_pct, "difference_pct": diff}
        if abs(diff) > max_shift_val:
            max_shift_val = abs(diff)
            max_shift_channel = ch

    # Check if a material shift occurred (by count or volume)
    min_cutoff = cfg.get("min_channel_deviation_pct", 25.0)
    if max_shift_val >= min_cutoff and max_shift_channel is not None:
        driving_txns = recent_df[recent_df["channel"] == max_shift_channel].copy()
        if len(driving_txns) < 3:
            return rule_info

        # Require sustained behavioral break (at least 2 hours apart, distinguishing from a single short burst)
        time_span_hours = (driving_txns["dt"].max() - driving_txns["dt"].min()).total_seconds() / 3600.0
        if time_span_hours < 2.0:
            return rule_info

        rule_info["status"] = "TRIGGERED"
        txn_ids = [str(x) for x in driving_txns["transaction_id"].tolist()]
        total_recent_amt = float(driving_txns["amount"].sum())

        evidence_items = []
        for _, row in driving_txns.head(5).iterrows():
            evidence_items.append({
                "transaction_id": str(row["transaction_id"]),
                "evidence_type": "CHANNEL_BEHAVIORAL_BREAK",
                "observed_value": f"{row['channel']} ({format_currency_inr(row['amount'])})",
                "baseline_value": f"Historical {row['channel']} usage: {channel_shifts[max_shift_channel]['historical_pct']}%",
                "deviation": f"Recent {row['channel']} surged to {channel_shifts[max_shift_channel]['recent_pct']}% (+{channel_shifts[max_shift_channel]['difference_pct']}%)",
                "explanation": f"Transaction {row['transaction_id']} executed via {row['channel']} during sudden shift away from typical channel mix."
            })

        finding = {
            "finding_id": "F-004-01",
            "rule_id": "R004",
            "severity": "HIGH",
            "title": f"Structural Channel Behaviour Break ({max_shift_channel} Surge)",
            "description": f"Significant behavioral divergence detected in recent {recent_days} days. {max_shift_channel} usage surged from {channel_shifts[max_shift_channel]['historical_pct']}% historically to {channel_shifts[max_shift_channel]['recent_pct']}% recently (+{channel_shifts[max_shift_channel]['difference_pct']}% shift).",
            "confidence": 0.94,
            "transaction_ids": txn_ids,
            "evidence": evidence_items,
            "channel_shifts": channel_shifts,
            "primary_divergent_channel": max_shift_channel,
            "deviation_pct": max_shift_val,
            "recent_volume": total_recent_amt,
            "recent_window_days": recent_days
        }
        rule_info["findings"].append(finding)

    return rule_info
