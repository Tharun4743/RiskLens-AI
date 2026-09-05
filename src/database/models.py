"""Data models and schemas for RiskLens AI database entities.
Defines SQLAlchemy 2.0 ORM models for PostgreSQL and Pydantic schemas for API validation.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from sqlalchemy import (
    Column, Integer, String, Float, Text, ForeignKey, Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# ==============================================================================
# SQLAlchemy 2.0 ORM Models for PostgreSQL / SQLite
# ==============================================================================

class CustomerDB(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    profile = Column(Text, nullable=True)
    expected_result = Column(String(255), nullable=True)
    created_at = Column(String(64), nullable=False)

    transactions = relationship("TransactionDB", back_populates="customer", cascade="all, delete-orphan")
    investigations = relationship("InvestigationDB", back_populates="customer", cascade="all, delete-orphan")



class TransactionDB(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String(64), unique=True, nullable=False, index=True)
    customer_id = Column(String(64), ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(String(64), nullable=False, index=True)
    description = Column(String(500), nullable=False)
    payee = Column(String(255), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    channel = Column(String(64), nullable=False)
    created_at = Column(String(64), nullable=False)

    customer = relationship("CustomerDB", back_populates="transactions")


class InvestigationDB(Base):
    __tablename__ = "investigations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(64), ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(64), nullable=False)
    risk_level = Column(String(64), nullable=False)
    started_at = Column(String(64), nullable=False)
    completed_at = Column(String(64), nullable=True)
    summary = Column(Text, nullable=True)

    customer = relationship("CustomerDB", back_populates="investigations")
    findings = relationship("FindingDB", back_populates="investigation", cascade="all, delete-orphan")


class FindingDB(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    finding_id = Column(String(64), nullable=False, index=True)
    rule_id = Column(String(64), nullable=False)
    severity = Column(String(32), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False)
    created_at = Column(String(64), nullable=False)

    investigation = relationship("InvestigationDB", back_populates="findings")


class EvidenceDB(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, autoincrement=True)
    finding_id = Column(String(64), nullable=False, index=True)
    transaction_id = Column(String(64), nullable=False, index=True)
    evidence_type = Column(String(64), nullable=False)
    observed_value = Column(Text, nullable=False)
    baseline_value = Column(Text, nullable=False)
    deviation = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)


class RuleDB(Base):
    __tablename__ = "rules"

    rule_id = Column(String(64), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    enabled = Column(Integer, nullable=False, default=1)
    configuration_json = Column(Text, nullable=False)


# Explicit composite / additional indexes
Index("idx_transactions_cust_time", TransactionDB.customer_id, TransactionDB.timestamp)
Index("idx_evidence_finding_txn", EvidenceDB.finding_id, EvidenceDB.transaction_id)


# ==============================================================================
# Pydantic Schemas for API Serialization & Validation
# ==============================================================================

class Customer(BaseModel):
    id: Optional[int] = None
    customer_id: str
    name: str
    profile: Optional[str] = None
    expected_result: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class Transaction(BaseModel):
    id: Optional[int] = None
    transaction_id: str
    customer_id: str
    timestamp: str  # Format: YYYY-MM-DD HH:MM[:SS]
    description: str
    payee: str
    amount: float
    channel: str  # UPI, CARD, NEFT, RTGS, IMPS, etc.
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class Finding(BaseModel):
    id: Optional[int] = None
    investigation_id: int
    finding_id: str
    rule_id: str
    severity: str  # LOW, MEDIUM, HIGH
    title: str
    description: str
    confidence: float
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class Evidence(BaseModel):
    id: Optional[int] = None
    finding_id: str
    transaction_id: str
    evidence_type: str
    observed_value: str
    baseline_value: str
    deviation: str
    explanation: str


class RuleModel(BaseModel):
    rule_id: str
    name: str
    description: str
    enabled: int = 1
    configuration_json: str


class Investigation(BaseModel):
    id: Optional[int] = None
    customer_id: str
    status: str
    risk_level: str
    started_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: Optional[str] = None
    summary: Optional[str] = None
