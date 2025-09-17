"""
Test execution API endpoints
"""
import subprocess
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

router = APIRouter()

class TestRequest(BaseModel):
    test_type: str
    test_name: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

class TestResult(BaseModel):
    test_name: str
    success: bool
    status_code: int
    output: str
    error: Optional[str] = None
    duration: float
    timestamp: str

class BundleTestResult(BaseModel):
    bundle_name: str
    timestamp: str
    total_tests: int
    passed: int
    failed: int
    errors: int
    results: List[TestResult]
    summary: Dict[str, Any]

# Test script mappings - absolute paths
SCRIPT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "scripts")
TEST_SCRIPTS = {
    "wallet_balance": os.path.join(SCRIPT_DIR, "test_wallet_balance.sh"),
    "wallet_status": os.path.join(SCRIPT_DIR, "test_wallet_status.sh"),
    "wallet_network": os.path.join(SCRIPT_DIR, "test_wallet_network.sh"),
    "wallet_health": os.path.join(SCRIPT_DIR, "test_wallet_health.sh"),
    "wallet_airdrop": os.path.join(SCRIPT_DIR, "test_wallet_airdrop.sh"),
    "agent_status": os.path.join(SCRIPT_DIR, "test_agent_status.sh"),
    "ideas_list": os.path.join(SCRIPT_DIR, "test_ideas_list.sh"),
    "strategies_list": os.path.join(SCRIPT_DIR, "test_strategies_list.sh"),
    "trades_history": os.path.join(SCRIPT_DIR, "test_trades_history.sh"),
    "system_health": os.path.join(SCRIPT_DIR, "test_system_health.sh"),
    "ideas_generate": os.path.join(SCRIPT_DIR, "test_ideas_generate.sh"),
    "trade_execute": os.path.join(SCRIPT_DIR, "test_trade_execute.sh"),
    "strategy_execute": os.path.join(SCRIPT_DIR, "test_strategy_execute.sh"),
    "bundle": os.path.join(SCRIPT_DIR, "test_bundle.sh")
}

def run_shell_script(script_path: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Execute a shell script and return the results
    """
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Test script not found: {script_path}")

    # Prepare environment variables from parameters
    env = os.environ.copy()
    if parameters:
        for key, value in parameters.items():
            env[f"TEST_{key.upper()}"] = str(value)

    # Set working directory to the script's directory
    script_dir = os.path.dirname(script_path)
    if not script_dir:
        script_dir = "."

    try:
        # Run the script with explicit shell
        result = subprocess.run(
            ["/bin/bash", script_path],
            capture_output=True,
            text=True,
            timeout=10,  # 10 second timeout
            env=env,
            cwd=script_dir
        )

        # Parse JSON output if possible
        output_data = {}
        stdout = result.stdout.strip()
        try:
            output_data = json.loads(stdout)
        except json.JSONDecodeError:
            # If not JSON, treat as plain text
            output_data = {"output": stdout}

        return {
            "success": result.returncode == 0,
            "status_code": result.returncode,
            "output": stdout,
            "error": result.stderr.strip() if result.stderr else None,
            "data": output_data
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "status_code": -1,
            "output": "",
            "error": "Test execution timed out",
            "data": {}
        }
    except Exception as e:
        return {
            "success": False,
            "status_code": -1,
            "output": "",
            "error": str(e),
            "data": {}
        }

@router.post("/run", response_model=TestResult)
async def run_test(test_request: TestRequest, background_tasks: BackgroundTasks):
    """
    Execute a specific test script
    """
    start_time = datetime.now()

    # Map test type to script
    script_key = test_request.test_type.lower().replace("-", "_").replace(" ", "_")
    script_path = TEST_SCRIPTS.get(script_key)

    if not script_path:
        raise HTTPException(status_code=404, detail=f"Test script not found for type: {test_request.test_type}")

    # Run the script
    result = run_shell_script(script_path, test_request.parameters)

    # Calculate duration
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Create test result
    test_result = TestResult(
        test_name=test_request.test_name or test_request.test_type,
        success=result["success"],
        status_code=result["status_code"],
        output=result["output"],
        error=result["error"],
        duration=duration,
        timestamp=end_time.isoformat()
    )

    return test_result

@router.post("/bundle", response_model=BundleTestResult)
async def run_bundle_test(background_tasks: BackgroundTasks):
    """
    Execute all test scripts and return a bundle result
    """
    start_time = datetime.now()
    results = []

    # Run all individual tests
    for test_type, script_path in TEST_SCRIPTS.items():
        if test_type == "bundle":
            continue  # Skip the bundle script itself

        try:
            result = run_shell_script(script_path)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            test_result = TestResult(
                test_name=test_type.replace("_", " ").title(),
                success=result["success"],
                status_code=result["status_code"],
                output=result["output"],
                error=result["error"],
                duration=duration,
                timestamp=end_time.isoformat()
            )
            results.append(test_result)

        except Exception as e:
            # Create error result for failed tests
            test_result = TestResult(
                test_name=test_type.replace("_", " ").title(),
                success=False,
                status_code=-1,
                output="",
                error=str(e),
                duration=0.0,
                timestamp=datetime.now().isoformat()
            )
            results.append(test_result)

    # Calculate summary
    total_tests = len(results)
    passed = sum(1 for r in results if r.success)
    failed = total_tests - passed
    errors = sum(1 for r in results if r.error)

    bundle_result = BundleTestResult(
        bundle_name="Complete Test Suite",
        timestamp=datetime.now().isoformat(),
        total_tests=total_tests,
        passed=passed,
        failed=failed,
        errors=errors,
        results=results,
        summary={
            "total": total_tests,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "success_rate": (passed / total_tests * 100) if total_tests > 0 else 0
        }
    )

    return bundle_result

@router.get("/scripts")
async def list_test_scripts():
    """
    List all available test scripts
    """
    scripts_info = []
    for test_type, script_path in TEST_SCRIPTS.items():
        exists = os.path.exists(script_path)
        scripts_info.append({
            "test_type": test_type,
            "script_path": script_path,
            "exists": exists
        })

    return {"scripts": scripts_info}