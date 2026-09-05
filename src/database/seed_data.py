"""Synthetic banking transaction dataset generator for RiskLens AI demo cases."""
import os
import random
import csv
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
DEMO_DIR = os.path.join(DATA_DIR, "demo_cases")

# Customer metadata
CUSTOMERS = [
    {
        "customer_id": "CUST-001",
        "name": "Priya Sharma",
        "profile": "Normal Behavioral Profile (Salary, groceries, utilities, typical daytime UPI/card usage)",
        "expected_result": "NO ATTENTION REQUIRED"
    },
    {
        "customer_id": "CUST-002",
        "name": "Arjun Patel",
        "profile": "Large Transfer Scenario (Normal ₹1k-₹10k range with anomalous ₹4,80,000 transfer)",
        "expected_result": "ATTENTION REQUIRED (R001: Unusually Large Transfer)"
    },
    {
        "customer_id": "CUST-003",
        "name": "Ananya Roy",
        "profile": "New Payee Rapid Burst Scenario (New payee XYZ Services with rapid burst within 47 minutes)",
        "expected_result": "ATTENTION REQUIRED (R002: New Payee Burst)"
    },
    {
        "customer_id": "CUST-004",
        "name": "Vikram Malhotra",
        "profile": "Odd-Hours Activity Scenario (Strict historical daytime activity with 02:00-04:00 night transactions)",
        "expected_result": "ATTENTION REQUIRED (R003: Odd-Hours Activity)"
    },
    {
        "customer_id": "CUST-005",
        "name": "Rajesh Verma",
        "profile": "Complex Multi-Vector Case (Large transfer + new payee burst + odd-hours + channel shift)",
        "expected_result": "ATTENTION REQUIRED (R001, R002, R003, R004)"
    }
]

# Standard Payee Pools
STANDARD_PAYEES = {
    "grocery": [("Fresh Mart", "CARD"), ("Nature Basket", "CARD"), ("BigBasket Online", "UPI"), ("Local Kirana Store", "UPI"), ("Daily Needs Supermarket", "CARD")],
    "utilities": [("State Electricity Board", "NETBANKING"), ("Metro Broadband", "UPI"), ("City Gas Corp", "UPI"), ("Municipal Water Dept", "NETBANKING"), ("Mobile Postpaid Airtel", "UPI")],
    "dining": [("Blue Tokai Coffee", "UPI"), ("Swiggy Orders", "UPI"), ("Zomato Delivery", "UPI"), ("Mainland China Resto", "CARD"), ("Chai Point", "UPI")],
    "shopping": [("Amazon India", "CARD"), ("Flipkart Internet", "CARD"), ("Zara Clothing", "CARD"), ("Decathlon Sports", "CARD")],
    "personal": [("Rahul Mehta", "UPI"), ("Sunita Nair", "UPI"), ("Amit Kapoor", "UPI"), ("Flat Rent Landlord", "NEFT"), ("Domestic Help Anita", "UPI")]
}


def generate_synthetic_transactions():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(DEMO_DIR, exist_ok=True)

    random.seed(42)  # Deterministic seed for reproducible testing
    start_date = datetime(2026, 1, 1, 9, 0, 0)
    end_date = datetime(2026, 6, 20, 18, 0, 0)
    total_days = (end_date - start_date).days

    all_txns = []
    customer_txns = {c["customer_id"]: [] for c in CUSTOMERS}
    txn_counter = 1000

    for cust in CUSTOMERS:
        cid = cust["customer_id"]
        # Generate 160-240 baseline transactions across 5.5 months
        cur_date = start_date

        # Monthly Salary: 1st of each month
        for m in range(1, 7):
            s_date = datetime(2026, m, 1, 10, 30, 0)
            txn_counter += 1
            txn = {
                "transaction_id": f"TXN-{txn_counter}",
                "customer_id": cid,
                "timestamp": s_date.strftime("%Y-%m-%d %H:%M:%S"),
                "date": s_date.strftime("%Y-%m-%d %H:%M:%S"),
                "description": "Monthly Salary Credit",
                "payee": "TechCorp Solutions India",
                "amount": 95000.0 if cid != "CUST-002" else 65000.0,
                "channel": "NEFT"
            }
            customer_txns[cid].append(txn)

            # Monthly Rent: 5th of each month
            r_date = datetime(2026, m, 5, 14, 15, 0)
            txn_counter += 1
            txn = {
                "transaction_id": f"TXN-{txn_counter}",
                "customer_id": cid,
                "timestamp": r_date.strftime("%Y-%m-%d %H:%M:%S"),
                "date": r_date.strftime("%Y-%m-%d %H:%M:%S"),
                "description": "Residential Apartment Rent",
                "payee": "Flat Rent Landlord",
                "amount": 22000.0,
                "channel": "NEFT"
            }
            customer_txns[cid].append(txn)

        # Baseline day-to-day transactions
        for day_offset in range(total_days):
            day_date = start_date + timedelta(days=day_offset)
            # 1 to 3 transactions per day on average
            num_txns = random.choices([0, 1, 2, 3], weights=[0.25, 0.4, 0.25, 0.1])[0]

            for _ in range(num_txns):
                # Normal hours: 08:30 to 21:30
                h = random.randint(8, 21)
                m = random.randint(0, 59)
                s = random.randint(0, 59)
                t_date = day_date.replace(hour=h, minute=m, second=s)

                category = random.choices(
                    ["grocery", "dining", "utilities", "shopping", "personal"],
                    weights=[0.35, 0.30, 0.15, 0.12, 0.08]
                )[0]
                payee, def_channel = random.choice(STANDARD_PAYEES[category])

                # Amounts typical for customer
                if category == "dining":
                    amt = round(random.uniform(120, 1800), 2)
                    desc = "Restaurant / Cafe Dining"
                    chan = "UPI"
                elif category == "grocery":
                    amt = round(random.uniform(450, 4200), 2)
                    desc = "Grocery & Household Supplies"
                    chan = random.choice(["CARD", "UPI"])
                elif category == "utilities":
                    amt = round(random.uniform(850, 3200), 2)
                    desc = "Utility & Telecom Bill Payment"
                    chan = random.choice(["NETBANKING", "UPI"])
                elif category == "shopping":
                    amt = round(random.uniform(1200, 6500), 2)
                    desc = "Retail E-Commerce Purchase"
                    chan = "CARD"
                else:
                    amt = round(random.uniform(500, 5000), 2)
                    desc = "Personal Transfer"
                    chan = "UPI"

                txn_counter += 1
                txn = {
                    "transaction_id": f"TXN-{txn_counter}",
                    "customer_id": cid,
                    "timestamp": t_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "date": t_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "description": desc,
                    "payee": payee,
                    "amount": amt,
                    "channel": chan
                }
                customer_txns[cid].append(txn)

    # NOW INJECT SCENARIO ANOMALIES FOR CUST-002, 003, 004, 005

    # CUST-002: Large Transfer Scenario
    # Median is ~1,800-3,200. Introduce ₹4,80,000 transfer
    txn_counter += 1
    large_date = datetime(2026, 6, 18, 14, 25, 10)
    customer_txns["CUST-002"].append({
        "transaction_id": f"TXN-{txn_counter}",
        "customer_id": "CUST-002",
        "timestamp": large_date.strftime("%Y-%m-%d %H:%M:%S"),
        "date": large_date.strftime("%Y-%m-%d %H:%M:%S"),
        "description": "Inter-Bank Funds Transfer",
        "payee": "Apex Global Ventures",
        "amount": 480000.0,
        "channel": "NEFT"
    })

    # CUST-003: New Payee Rapid Burst Scenario
    # First-seen payee "XYZ Services", 4 transactions in 47 mins totaling 240,000
    burst_base = datetime(2026, 6, 17, 11, 10, 0)
    burst_amounts = [60000.0, 50000.0, 75000.0, 55000.0]
    burst_offsets = [0, 12, 28, 47]  # minutes
    for i in range(4):
        txn_counter += 1
        b_time = burst_base + timedelta(minutes=burst_offsets[i], seconds=random.randint(5, 45))
        customer_txns["CUST-003"].append({
            "transaction_id": f"TXN-{txn_counter}",
            "customer_id": "CUST-003",
            "timestamp": b_time.strftime("%Y-%m-%d %H:%M:%S"),
            "date": b_time.strftime("%Y-%m-%d %H:%M:%S"),
            "description": f"Expedited Service Invoice #{1042 + i}",
            "payee": "XYZ Services",
            "amount": burst_amounts[i],
            "channel": "IMPS"
        })

    # CUST-004: Odd-Hours Activity Scenario
    # Historical transactions strictly 08:00 - 22:00.
    # Introduce 3 transactions between 02:00 and 04:00 on June 16, 2026
    odd_times = [
        datetime(2026, 6, 16, 2, 14, 22),
        datetime(2026, 6, 16, 2, 50, 18),
        datetime(2026, 6, 16, 3, 35, 45)
    ]
    odd_amounts = [14500.0, 18200.0, 12800.0]
    for i in range(3):
        txn_counter += 1
        customer_txns["CUST-004"].append({
            "transaction_id": f"TXN-{txn_counter}",
            "customer_id": "CUST-004",
            "timestamp": odd_times[i].strftime("%Y-%m-%d %H:%M:%S"),
            "date": odd_times[i].strftime("%Y-%m-%d %H:%M:%S"),
            "description": "Online Digital Wallet Load",
            "payee": "FastPay Virtual Card",
            "amount": odd_amounts[i],
            "channel": "NETBANKING"
        })

    # CUST-005: Complex Case Scenario (Master Hard Case)
    # Combines R001 (Large transfer), R002 (New Payee Burst), R003 (Odd-Hours), R004 (Channel Break)
    # Channel break: In last 7 days (June 12 to 19), multiple NEFT transfers amounting to 85% of volume
    # Rapid burst to XYZ Services at 02:14 - 03:01 (odd hours) including a huge ₹4,80,000 transfer
    complex_base = datetime(2026, 6, 18, 2, 14, 0)
    complex_burst = [
        {"desc": "Urgent Contract Settlement", "payee": "XYZ Services", "amount": 480000.0, "chan": "NEFT", "min": 0},
        {"desc": "Consulting Advance Tranche 1", "payee": "XYZ Services", "amount": 85000.0, "chan": "NEFT", "min": 14},
        {"desc": "Consulting Advance Tranche 2", "payee": "XYZ Services", "amount": 75000.0, "chan": "NEFT", "min": 29},
        {"desc": "Escrow Liquidation", "payee": "XYZ Services", "amount": 90000.0, "chan": "NEFT", "min": 47}
    ]
    for item in complex_burst:
        txn_counter += 1
        c_time = complex_base + timedelta(minutes=item["min"], seconds=random.randint(10, 40))
        customer_txns["CUST-005"].append({
            "transaction_id": f"TXN-{txn_counter}",
            "customer_id": "CUST-005",
            "timestamp": c_time.strftime("%Y-%m-%d %H:%M:%S"),
            "date": c_time.strftime("%Y-%m-%d %H:%M:%S"),
            "description": item["desc"],
            "payee": item["payee"],
            "amount": item["amount"],
            "channel": item["chan"]
        })

    # Additional recent NEFT shift for CUST-005 on June 17-19
    recent_dates = [datetime(2026, 6, 17, 15, 30), datetime(2026, 6, 19, 11, 45)]
    for r_dt in recent_dates:
        txn_counter += 1
        customer_txns["CUST-005"].append({
            "transaction_id": f"TXN-{txn_counter}",
            "customer_id": "CUST-005",
            "timestamp": r_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "date": r_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "description": "Commercial Equipment Procurement",
            "payee": "Apex Industrial Supply",
            "amount": 95000.0,
            "channel": "NEFT"
        })

    # Save individual demo CSV files for direct upload or inspection
    demo_file_mapping = {
        "CUST-001": "normal_customer.csv",
        "CUST-002": "large_transfer.csv",
        "CUST-003": "new_payee_burst.csv",
        "CUST-004": "odd_hours.csv",
        "CUST-005": "complex_case.csv"
    }

    fieldnames = ["transaction_id", "date", "description", "payee", "amount", "channel"]

    for cid, txns in customer_txns.items():
        # Sort chronologically
        txns.sort(key=lambda x: x["timestamp"])
        filename = demo_file_mapping[cid]
        filepath = os.path.join(DEMO_DIR, filename)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for t in txns:
                writer.writerow({
                    "transaction_id": t["transaction_id"],
                    "date": t["date"],
                    "description": t["description"],
                    "payee": t["payee"],
                    "amount": t["amount"],
                    "channel": t["channel"]
                })
        all_txns.extend(txns)

    # Save combined data/transactions.csv
    all_txns.sort(key=lambda x: x["timestamp"])
    with open(os.path.join(DATA_DIR, "transactions.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["transaction_id", "customer_id", "date", "description", "payee", "amount", "channel"])
        writer.writeheader()
        for t in all_txns:
            writer.writerow({
                "transaction_id": t["transaction_id"],
                "customer_id": t["customer_id"],
                "date": t["date"],
                "description": t["description"],
                "payee": t["payee"],
                "amount": t["amount"],
                "channel": t["channel"]
            })

    # Save customers.csv
    with open(os.path.join(DATA_DIR, "customers.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["customer_id", "name", "profile", "expected_result"])
        writer.writeheader()
        for c in CUSTOMERS:
            writer.writerow(c)

    print(f"Generated {len(all_txns)} synthetic transactions across 5 customers in {DATA_DIR}")
    return CUSTOMERS, all_txns


def seed_database_if_empty():
    """Seed database with synthetic demo scenarios if customer records are not present.
    Works identically across PostgreSQL and SQLite, preventing duplicate data.
    """
    from sqlalchemy import select, func
    from src.database.database import get_db_session, init_db
    from src.database.models import CustomerDB, TransactionDB, RuleDB
    import json

    init_db()

    with get_db_session() as session:
        cust_count = session.scalar(select(func.count()).select_from(CustomerDB)) or 0

        if cust_count == 0:
            customers, transactions = generate_synthetic_transactions()

            # Insert rules
            rules_path = os.path.join(DATA_DIR, "rules.json")
            if os.path.exists(rules_path):
                with open(rules_path, "r", encoding="utf-8") as rf:
                    rules_list = json.load(rf)
                    for r in rules_list:
                        existing_rule = session.get(RuleDB, r["rule_id"])
                        if not existing_rule:
                            session.add(RuleDB(
                                rule_id=r["rule_id"],
                                name=r["name"],
                                description=r["description"],
                                enabled=r.get("enabled", 1),
                                configuration_json=json.dumps(r["configuration"])
                            ))

            # Insert customers
            now_str = datetime.utcnow().isoformat()
            for c in customers:
                existing_c = session.scalar(select(CustomerDB).where(CustomerDB.customer_id == c["customer_id"]))
                if not existing_c:
                    session.add(CustomerDB(
                        customer_id=c["customer_id"],
                        name=c["name"],
                        profile=c.get("profile"),
                        expected_result=c.get("expected_result"),
                        created_at=now_str
                    ))
            session.flush()

            # Insert transactions in bulk batches
            txn_objects = []
            for t in transactions:
                txn_objects.append(TransactionDB(
                    transaction_id=t["transaction_id"],
                    customer_id=t["customer_id"],
                    timestamp=t["timestamp"],
                    description=t["description"],
                    payee=t["payee"],
                    amount=float(t["amount"]),
                    channel=t["channel"],
                    created_at=now_str
                ))
            session.add_all(txn_objects)
            print(f"Database seeded with {len(customers)} customers and {len(transactions)} transactions.")
        else:
            print("Database already contains customer data. Skipping seeding.")


if __name__ == "__main__":
    seed_database_if_empty()

