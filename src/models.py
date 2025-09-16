from pydantic import BaseModel
from typing import Optional, List, Literal
from datetime import datetime, timezone
from enum import Enum


def utcnow() -> datetime:
    return datetime.now(timezone.utc)

# Idea Model
class IdeaStatus(str, Enum):
    NEW = "NEW"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    READY_FOR_QA = "READY_FOR_QA"
    APPROVED = "APPROVED"
    SCHEDULED = "SCHEDULED"
    CANCELLED = "CANCELLED"


class Idea(BaseModel):
    id: str
    source: Literal["research", "analysis"]
    asset: str  # e.g., "SOL", "PUMP"
    type: Literal["yield", "short-term trade", "swing", "airdrop", "other"]
    risk: int  # 1-5
    budget: float  # in SOL
    status: IdeaStatus  # pipeline status
    created_at: datetime
    ttl: Optional[int] = 5400  # seconds, default 90 min

# Strategy Model
class StrategyStatus(str, Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"


class Strategy(BaseModel):
    id: str
    idea_id: str
    entry_conditions: str
    exit_conditions: str
    stop_loss: float
    take_profit: float
    max_dd: float
    status: StrategyStatus

# Trade Model
class TradeAction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    AIRDROP = "AIRDROP"


class TradeStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    FAILED = "FAILED"


class Trade(BaseModel):
    id: str
    strategy_id: str
    action: TradeAction
    asset: str
    quantity: float
    price: Optional[float]
    pnl: Optional[float]
    status: TradeStatus
    executed_at: datetime

# QA Report
class QAReport(BaseModel):
    id: str
    target_id: str  # idea or strategy id
    checks_passed: bool
    issues: List[str]
    approved: bool

# Agent Version
class AgentVersion(BaseModel):
    name: str  # e.g., "quality", "research"
    version: str  # SemVer, e.g., "1.2.3"

# Wallet Balance
class WalletBalance(BaseModel):
    address: str
    balance_sol: float
    timestamp: datetime
