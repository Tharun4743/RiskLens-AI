"""Generate comprehensive Supabase SQL script with full schema, indexes, RLS, and seed records."""
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import json
from src.database.seed_data import DATA_DIR, generate_synthetic_transactions

def generate_full_sql():
    customers, transactions = generate_synthetic_transactions()

    sql_lines = []
    schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "supabase_schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        sql_lines.append(f.read())

    sql_lines.append("\n-- ==============================================================================")
    sql_lines.append("-- 4. Seed Rules Data")
    sql_lines.append("-- ==============================================================================\n")

    rules_path = os.path.join(DATA_DIR, "rules.json")
    if os.path.exists(rules_path):
        with open(rules_path, "r", encoding="utf-8") as rf:
            rules = json.load(rf)
            for r in rules:
                config_str = json.dumps(r["configuration"]).replace("'", "''")
                desc_str = r["description"].replace("'", "''")
                name_str = r["name"].replace("'", "''")
                sql_lines.append(f"INSERT INTO rules (rule_id, name, description, enabled, configuration_json) VALUES ('{r['rule_id']}', '{name_str}', '{desc_str}', {r.get('enabled', 1)}, '{config_str}') ON CONFLICT (rule_id) DO NOTHING;")

    sql_lines.append("\n-- ==============================================================================")
    sql_lines.append("-- 5. Seed Customers Data")
    sql_lines.append("-- ==============================================================================\n")

    for c in customers:
        p_str = (c.get("profile") or "").replace("'", "''")
        e_str = (c.get("expected_result") or "").replace("'", "''")
        name_str = c["name"].replace("'", "''")
        cid = c["customer_id"]
        sql_lines.append(f"INSERT INTO customers (customer_id, name, profile, expected_result, created_at) VALUES ('{cid}', '{name_str}', '{p_str}', '{e_str}', '2026-01-01T00:00:00Z') ON CONFLICT (customer_id) DO NOTHING;")

    sql_lines.append("\n-- ==============================================================================")
    sql_lines.append("-- 6. Seed Transactions Data")
    sql_lines.append("-- ==============================================================================\n")

    for t in transactions:
        desc = t["description"].replace("'", "''")
        payee = t["payee"].replace("'", "''")
        tid = t["transaction_id"]
        cid = t["customer_id"]
        ts = t["timestamp"]
        amt = t["amount"]
        chan = t["channel"]
        sql_lines.append(f"INSERT INTO transactions (transaction_id, customer_id, timestamp, description, payee, amount, channel, created_at) VALUES ('{tid}', '{cid}', '{ts}', '{desc}', '{payee}', {amt}, '{chan}', '2026-01-01T00:00:00Z') ON CONFLICT (transaction_id) DO NOTHING;")

    full_sql = "\n".join(sql_lines)
    out_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "supabase_schema.sql")
    with open(out_path, "w", encoding="utf-8") as out:
        out.write(full_sql)

    print(f"Updated supabase_schema.sql with {len(customers)} customers, {len(transactions)} transactions, and {len(rules)} rules.")

if __name__ == "__main__":
    generate_full_sql()
