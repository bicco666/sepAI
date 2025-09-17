import time
import threading
from state import get_store, OrderState

class Scheduler:
    def __init__(self):
        self.running = False
        self.thread = None

    def start(self):
        """Start the scheduler in a background thread"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.thread.start()

    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)

    def _run_scheduler(self):
        """Main scheduler loop - runs every 5 seconds"""
        while self.running:
            try:
                self._process_scheduled_orders()
                time.sleep(5)  # Check every 5 seconds
            except Exception as e:
                print(f"Scheduler error: {e}")
                time.sleep(5)

    def _process_scheduled_orders(self):
        """Process orders that are scheduled for execution"""
        store = get_store()

        for order in store.get_all_orders():
            if order.state == OrderState.SCHEDULED:
                # Mark as executing
                store.update_order_state(order.id, OrderState.EXECUTING)

                # Execute the order in a separate thread to avoid blocking
                threading.Thread(target=self._execute_order, args=(order.id,), daemon=True).start()

    def _execute_order(self, order_id: str):
        """Execute a single order"""
        store = get_store()
        order = store.get_order(order_id)

        if not order:
            return

        try:
            # Import the appropriate chain mock
            if order.chain == "solana":
                from chains.solana_mock import execute_solana_trade
                result = execute_solana_trade(order.amount)
            elif order.chain == "ethereum":
                from chains.ethereum_mock import execute_ethereum_trade
                result = execute_ethereum_trade(order.amount)
            else:
                raise ValueError(f"Unknown chain: {order.chain}")

            # Update order state based on result
            if result["success"]:
                store.update_order_state(order_id, OrderState.CLOSED, f"PNL: {result['pnl']}")
            else:
                store.update_order_state(order_id, OrderState.FAILED, result.get("error", "Unknown error"))

        except Exception as e:
            store.update_order_state(order_id, OrderState.FAILED, str(e))

# Global scheduler instance
_scheduler = None

def get_scheduler() -> Scheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = Scheduler()
    return _scheduler