import time
import uuid
from typing import List, Dict, Optional
from enum import Enum

class IdeaState(Enum):
    NEW = "NEW"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    SCHEDULED = "SCHEDULED"
    CLOSED = "CLOSED"
    FAILED = "FAILED"

class OrderState(Enum):
    NEW = "NEW"
    SCHEDULED = "SCHEDULED"
    EXECUTING = "EXECUTING"
    CLOSED = "CLOSED"
    FAILED = "FAILED"

class Idea:
    def __init__(self, chain: str, budget: float, description: str = ""):
        self.id = str(uuid.uuid4())[:8]
        self.chain = chain  # "solana" or "ethereum"
        self.budget = budget
        self.description = description
        self.state = IdeaState.NEW
        self.created_at = time.time()
        self.updated_at = time.time()

    def to_dict(self):
        return {
            "id": self.id,
            "chain": self.chain,
            "budget": self.budget,
            "description": self.description,
            "state": self.state.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class Order:
    def __init__(self, idea_id: str, chain: str, amount: float):
        self.id = str(uuid.uuid4())[:8]
        self.idea_id = idea_id
        self.chain = chain
        self.amount = amount
        self.state = OrderState.NEW
        self.created_at = time.time()
        self.updated_at = time.time()
        self.executed_at = None
        self.result = None

    def to_dict(self):
        return {
            "id": self.id,
            "idea_id": self.idea_id,
            "chain": self.chain,
            "amount": self.amount,
            "state": self.state.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "executed_at": self.executed_at,
            "result": self.result
        }

class StateStore:
    def __init__(self):
        self.ideas: Dict[str, Idea] = {}
        self.orders: Dict[str, Order] = {}
        self.budget_total = 1.0  # Total available budget

    def add_idea(self, idea: Idea) -> Idea:
        self.ideas[idea.id] = idea
        return idea

    def get_idea(self, idea_id: str) -> Optional[Idea]:
        return self.ideas.get(idea_id)

    def get_all_ideas(self) -> List[Idea]:
        return list(self.ideas.values())

    def update_idea_state(self, idea_id: str, new_state: IdeaState) -> bool:
        idea = self.get_idea(idea_id)
        if idea:
            idea.state = new_state
            idea.updated_at = time.time()
            return True
        return False

    def add_order(self, order: Order) -> Order:
        self.orders[order.id] = order
        return order

    def get_order(self, order_id: str) -> Optional[Order]:
        return self.orders.get(order_id)

    def get_all_orders(self) -> List[Order]:
        return list(self.orders.values())

    def update_order_state(self, order_id: str, new_state: OrderState, result: str = None) -> bool:
        order = self.get_order(order_id)
        if order:
            order.state = new_state
            order.updated_at = time.time()
            if new_state in [OrderState.CLOSED, OrderState.FAILED]:
                order.executed_at = time.time()
            if result:
                order.result = result
            return True
        return False

def validate_budget(amount: float, chain: str, p_success: float = 0.8) -> bool:
    """Validate budget against policy: cap = min(0.05*budget_total*p_success, 0.05*budget_total)"""
    store = get_store()
    cap = min(0.05 * store.budget_total * p_success, 0.05 * store.budget_total)
    return amount <= cap

# Global store instance
_store = None

def get_store() -> StateStore:
    global _store
    if _store is None:
        _store = StateStore()
    return _store