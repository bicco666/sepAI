import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.state import get_store, Idea, Order, IdeaState, OrderState

def test_basic_flow():
    """Test the complete flow: Idea → Analysis → Order → Execution"""
    store = get_store()

    # Clear any existing data
    store.ideas.clear()
    store.orders.clear()

    # 1. Create idea
    idea = Idea("solana", 0.01, "Test trading idea")
    store.add_idea(idea)

    assert idea.state == IdeaState.NEW
    assert len(store.get_all_ideas()) == 1

    # 2. Move to analysis
    success = store.update_idea_state(idea.id, IdeaState.NEEDS_REVIEW)
    assert success
    assert store.get_idea(idea.id).state == IdeaState.NEEDS_REVIEW

    # 3. Schedule idea (creates order)
    order = Order(idea.id, idea.chain, idea.budget)
    store.add_order(order)
    store.update_idea_state(idea.id, IdeaState.SCHEDULED)

    assert store.get_idea(idea.id).state == IdeaState.SCHEDULED
    assert len(store.get_all_orders()) == 1

    # 4. Execute order
    store.update_order_state(order.id, OrderState.SCHEDULED)
    assert store.get_order(order.id).state == OrderState.SCHEDULED

    print("✅ Basic flow test passed")

if __name__ == "__main__":
    test_basic_flow()