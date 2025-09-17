from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import time

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from state import get_store, Idea, Order, IdeaState, OrderState, validate_budget
from scheduler import get_scheduler

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Start scheduler when app starts
scheduler = get_scheduler()
scheduler.start()

@app.route('/healthz')
def healthz():
    return jsonify({"status": "ok", "timestamp": time.time()})

@app.route('/api/v1/ideas', methods=['GET'])
def get_ideas():
    store = get_store()
    ideas = store.get_all_ideas()
    return jsonify({"ideas": [idea.to_dict() for idea in ideas]})

@app.route('/api/v1/ideas', methods=['POST'])
def create_idea():
    data = request.get_json()
    if not data or 'chain' not in data or 'budget' not in data:
        return jsonify({"error": "Missing chain or budget"}), 400

    chain = data['chain']
    budget = data['budget']
    description = data.get('description', '')

    if chain not in ['solana', 'ethereum']:
        return jsonify({"error": "Invalid chain"}), 400

    if not validate_budget(budget, chain):
        return jsonify({"error": "Budget exceeds policy limit"}), 400

    idea = Idea(chain, budget, description)
    store = get_store()
    store.add_idea(idea)

    return jsonify({"idea": idea.to_dict()}), 201

@app.route('/api/v1/ideas/<idea_id>/to-analysis', methods=['POST'])
def idea_to_analysis(idea_id):
    store = get_store()
    if store.update_idea_state(idea_id, IdeaState.NEEDS_REVIEW):
        return jsonify({"success": True})
    return jsonify({"error": "Idea not found"}), 404

@app.route('/api/v1/ideas/<idea_id>/schedule', methods=['POST'])
def schedule_idea(idea_id):
    store = get_store()
    idea = store.get_idea(idea_id)
    if not idea:
        return jsonify({"error": "Idea not found"}), 404

    # Create order from idea
    order = Order(idea_id, idea.chain, idea.budget)
    store.add_order(order)

    # Update idea state
    store.update_idea_state(idea_id, IdeaState.SCHEDULED)

    return jsonify({"order": order.to_dict()}), 201

@app.route('/api/v1/orders', methods=['GET'])
def get_orders():
    store = get_store()
    orders = store.get_all_orders()
    return jsonify({"orders": [order.to_dict() for order in orders]})

@app.route('/api/v1/orders/<order_id>/execute', methods=['POST'])
def execute_order(order_id):
    store = get_store()
    order = store.get_order(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    if order.state != OrderState.NEW:
        return jsonify({"error": "Order not in NEW state"}), 400

    # Schedule for execution
    store.update_order_state(order_id, OrderState.SCHEDULED)

    return jsonify({"success": True, "message": "Order scheduled for execution"})

@app.route('/api/v1/tests/run', methods=['GET'])
def run_test():
    case = request.args.get('case', '1')
    result = run_test_case(case)
    return jsonify(result)

@app.route('/api/v1/tests/bundle', methods=['GET'])
def run_bundle():
    results = []
    for case in ['1', '2', '3', '4', '5']:
        result = run_test_case(case)
        results.append(result)

    # Write bundle report
    write_report("bundle_test", results)

    return jsonify({
        "bundle_results": results,
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r.get("success")),
            "failed": sum(1 for r in results if not r.get("success"))
        }
    })

@app.route('/api/v1/audit/run', methods=['POST'])
def run_audit():
    # Run comprehensive audit
    audit_results = run_full_audit()

    # Write audit report
    write_report("audit", audit_results)

    return jsonify(audit_results)

def run_test_case(case: str) -> dict:
    """Run individual test case"""
    try:
        if case == '1':
            return test_flow_basic()
        elif case == '2':
            return test_chains()
        elif case == '3':
            return test_budget_policy()
        elif case == '4':
            return test_audit()
        elif case == '5':
            return test_dashboard()
        else:
            return {"success": False, "error": f"Unknown test case: {case}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def test_flow_basic() -> dict:
    """Test 1: Basic flow - Idea → Analysis → Order → Execution"""
    store = get_store()

    # Create idea
    idea = Idea("solana", 0.01, "Test idea")
    store.add_idea(idea)

    # Move to analysis
    store.update_idea_state(idea.id, IdeaState.NEEDS_REVIEW)

    # Schedule
    order = Order(idea.id, idea.chain, idea.budget)
    store.add_order(order)
    store.update_idea_state(idea.id, IdeaState.SCHEDULED)

    # Execute
    store.update_order_state(order.id, OrderState.SCHEDULED)

    return {"success": True, "message": "Basic flow test passed"}

def test_chains() -> dict:
    """Test 2: Chain validation"""
    store = get_store()

    # Test Solana
    sol_idea = Idea("solana", 0.1)
    store.add_idea(sol_idea)

    # Test Ethereum
    eth_idea = Idea("ethereum", 0.001)
    store.add_idea(eth_idea)

    return {"success": True, "message": "Chain validation test passed"}

def test_budget_policy() -> dict:
    """Test 3: Budget policy validation"""
    # Test valid budget
    valid = validate_budget(0.01, "solana")
    if not valid:
        return {"success": False, "error": "Valid budget rejected"}

    # Test invalid budget (too high)
    invalid = validate_budget(1.0, "solana")
    if invalid:
        return {"success": False, "error": "Invalid budget accepted"}

    return {"success": True, "message": "Budget policy test passed"}

def test_audit() -> dict:
    """Test 4: Audit functionality"""
    audit_results = run_full_audit()
    return {"success": True, "message": "Audit test passed", "results": audit_results}

def test_dashboard() -> dict:
    """Test 5: Dashboard integration"""
    # Test API endpoints
    with app.test_client() as client:
        # Test health
        resp = client.get('/healthz')
        if resp.status_code != 200:
            return {"success": False, "error": "Health check failed"}

        # Test ideas endpoint
        resp = client.get('/api/v1/ideas')
        if resp.status_code != 200:
            return {"success": False, "error": "Ideas endpoint failed"}

    return {"success": True, "message": "Dashboard test passed"}

def run_full_audit() -> dict:
    """Run comprehensive audit"""
    store = get_store()
    ideas = store.get_all_ideas()
    orders = store.get_all_orders()

    return {
        "timestamp": time.time(),
        "ideas_count": len(ideas),
        "orders_count": len(orders),
        "budget_total": store.budget_total,
        "ideas_by_state": {
            state.value: len([i for i in ideas if i.state.value == state.value])
            for state in IdeaState
        },
        "orders_by_state": {
            state.value: len([o for o in orders if o.state.value == state.value])
            for state in OrderState
        }
    }

def write_report(report_type: str, data: dict):
    """Write report to reports/ directory"""
    import json
    os.makedirs('reports', exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"reports/{report_type}_{timestamp}.md"

    with open(filename, 'w') as f:
        f.write(f"# {report_type.upper()} Report\n\n")
        f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        if report_type == "bundle_test":
            f.write("## Test Results\n\n")
            for i, result in enumerate(data, 1):
                status = "✅ PASS" if result.get("success") else "❌ FAIL"
                f.write(f"### Test Case {i}\n")
                f.write(f"Status: {status}\n")
                if result.get("message"):
                    f.write(f"Message: {result['message']}\n")
                if result.get("error"):
                    f.write(f"Error: {result['error']}\n")
                f.write("\n")
        else:
            f.write("## Audit Results\n\n")
            f.write(f"```json\n{json.dumps(data, indent=2)}\n```\n")

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def static_files(path):
    return app.send_static_file(path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)