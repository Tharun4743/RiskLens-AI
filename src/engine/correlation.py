"""Correlation Engine.
Connects flagged transactions across rules by payee, time window, channel, and behavioral clusters.
"""
from typing import List, Dict, Any, Set
import pandas as pd
from src.utils.helpers import format_currency_inr


def correlate_findings(
    findings: List[Dict[str, Any]],
    transactions_df: pd.DataFrame
) -> List[Dict[str, Any]]:
    """
    Correlates triggered findings and their underlying transactions into cohesive events.
    Groups transactions sharing the same payee, close temporal proximity, or common attack vector.
    """
    if not findings or transactions_df.empty:
        return []

    # Map transaction IDs to row data
    df = transactions_df.copy()
    df["dt"] = pd.to_datetime(df["timestamp"])
    txn_lookup = {str(row["transaction_id"]): row for _, row in df.iterrows()}

    # Collect all unique flagged transaction IDs
    all_flagged_txn_ids: Set[str] = set()
    txn_to_rules: Dict[str, Set[str]] = {}
    for f in findings:
        r_id = f.get("rule_id", "UNKNOWN")
        for tid in f.get("transaction_ids", []):
            all_flagged_txn_ids.add(tid)
            if tid not in txn_to_rules:
                txn_to_rules[tid] = set()
            txn_to_rules[tid].add(r_id)

    if not all_flagged_txn_ids:
        return []

    flagged_records = []
    for tid in all_flagged_txn_ids:
        if tid in txn_lookup:
            row = txn_lookup[tid]
            flagged_records.append({
                "transaction_id": tid,
                "timestamp": row["timestamp"],
                "dt": row["dt"],
                "amount": float(row["amount"]),
                "payee": row["payee"],
                "channel": row["channel"],
                "description": row["description"],
                "triggered_rules": sorted(list(txn_to_rules.get(tid, [])))
            })

    # Sort flagged records chronologically
    flagged_records.sort(key=lambda x: x["dt"])

    # Cluster by payee and close temporal window (< 120 minutes)
    clusters: List[List[Dict[str, Any]]] = []
    for rec in flagged_records:
        matched_cluster = None
        for c in clusters:
            # Check if same payee or window within 2 hours of any transaction in cluster
            same_payee = any(x["payee"] == rec["payee"] for x in c)
            close_time = any(abs((x["dt"] - rec["dt"]).total_seconds()) <= 7200 for x in c)
            if same_payee or close_time:
                matched_cluster = c
                break

        if matched_cluster is not None:
            matched_cluster.append(rec)
        else:
            clusters.append([rec])

    # Build structured correlation events
    correlated_events = []
    for idx, c in enumerate(clusters, 1):
        c.sort(key=lambda x: x["dt"])
        total_amt = sum(x["amount"] for x in c)
        c_txns = [x["transaction_id"] for x in c]
        payees = list(set(x["payee"] for x in c))
        channels = list(set(x["channel"] for x in c))
        rules_involved = sorted(list(set(r for x in c for r in x["triggered_rules"])))

        start_dt = c[0]["dt"]
        end_dt = c[-1]["dt"]
        duration_minutes = max(1, round((end_dt - start_dt).total_seconds() / 60.0))

        # Build visual node chain: TXN -> Payee -> Related TXNs
        primary_txn = c[0]["transaction_id"]
        primary_payee = payees[0] if payees else "Unknown"

        relationship_nodes = [
            {"id": primary_txn, "type": "PRIMARY_TRANSACTION", "label": primary_txn},
            {"id": primary_payee, "type": "PAYEE_HUB", "label": primary_payee}
        ]
        relationship_links = [
            {"source": primary_txn, "target": primary_payee, "label": "routed_to"}
        ]

        for other_item in c[1:]:
            otid = other_item["transaction_id"]
            relationship_nodes.append({"id": otid, "type": "CORRELATED_TRANSACTION", "label": otid})
            relationship_links.append({"source": primary_payee, "target": otid, "label": "co-occurred_with"})

        event = {
            "event_id": f"CORR-EVT-{idx:02d}",
            "title": f"Correlated Cluster: {len(c)} transactions to {', '.join(payees)}",
            "transaction_count": len(c),
            "transaction_ids": c_txns,
            "total_amount": total_amt,
            "formatted_amount": format_currency_inr(total_amt),
            "payees": payees,
            "channels": channels,
            "rules_involved": rules_involved,
            "time_window": {
                "start": start_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "end": end_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "duration_minutes": duration_minutes
            },
            "graph": {
                "nodes": relationship_nodes,
                "links": relationship_links
            },
            "summary": f"{len(c)} transactions totaling {format_currency_inr(total_amt)} across {duration_minutes} minutes involving {', '.join(payees)} via {', '.join(channels)}."
        }
        correlated_events.append(event)

    return correlated_events
