#!/usr/bin/env python3
"""
Automated test runner with comprehensive reporting
"""
import subprocess
import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime


class TestRunner:
    """Automated test runner with reporting"""

    def __init__(self, project_root=None):
        self.project_root = Path(project_root or Path(__file__).parent.parent)
        self.reports_dir = self.project_root / "reports"
        self.reports_dir.mkdir(exist_ok=True)

    def run_unit_tests(self):
        """Run unit tests with coverage"""
        print("🧪 Running unit tests...")
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/test_execution.py",
            "tests/test_ideas.py",
            "tests/test_infra_bus.py",
            "tests/api/test_all_api.py",
            "--cov=backend",
            "--cov=src",
            "--cov-report=html",
            "--cov-report=xml",
            "--junitxml=reports/junit_unit.xml",
            "-v"
        ]

        result = self._run_command(cmd, cwd=self.project_root)
        return result

    def run_integration_tests(self):
        """Run integration tests"""
        print("🔗 Running integration tests...")
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/test_integration.py",
            "--junitxml=reports/junit_integration.xml",
            "-v",
            "-m", "integration"
        ]

        result = self._run_command(cmd, cwd=self.project_root)
        return result

    def run_performance_tests(self):
        """Run performance tests"""
        print("⚡ Running performance tests...")
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/test_performance.py",
            "--junitxml=reports/junit_performance.xml",
            "-v",
            "-m", "slow"
        ]

        result = self._run_command(cmd, cwd=self.project_root)
        return result

    def run_shell_script_tests(self):
        """Run shell script tests"""
        print("🐚 Running shell script tests...")
        bundle_script = self.project_root / "scripts" / "test_bundle.sh"

        if bundle_script.exists():
            result = self._run_command([str(bundle_script)], cwd=self.project_root)
            return result
        else:
            print("⚠️  Bundle test script not found")
            return {"success": False, "returncode": 1}

    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Running complete test suite...")

        results = {
            "timestamp": datetime.now().isoformat(),
            "unit_tests": self.run_unit_tests(),
            "integration_tests": self.run_integration_tests(),
            "performance_tests": self.run_performance_tests(),
            "shell_tests": self.run_shell_script_tests()
        }

        # Generate summary report
        self._generate_summary_report(results)

        return results

    def _run_command(self, cmd, cwd=None):
        """Run a command and return results"""
        try:
            start_time = time.time()
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            end_time = time.time()

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration": end_time - start_time
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": "Command timed out",
                "duration": 300
            }
        except Exception as e:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "duration": 0
            }

    def _generate_summary_report(self, results):
        """Generate a summary report"""
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        total_duration = 0

        for test_type, result in results.items():
            if test_type == "timestamp":
                continue

            total_duration += result.get("duration", 0)
            if result["success"]:
                passed_tests += 1
            else:
                failed_tests += 1
            total_tests += 1

        summary = {
            "timestamp": results["timestamp"],
            "summary": {
                "total_suites": total_tests,
                "passed_suites": passed_tests,
                "failed_suites": failed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_duration": total_duration
            },
            "results": results
        }

        # Save summary report
        report_file = self.reports_dir / "test_summary.json"
        with open(report_file, 'w') as f:
            json.dump(summary, f, indent=2)

        # Print summary
        print("\n" + "="*50)
        print("📊 TEST SUMMARY")
        print("="*50)
        print(f"Total test suites: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(".1f")
        print(".2f")
        print(f"Report saved to: {report_file}")

        return summary


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Automated test runner")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--performance", action="store_true", help="Run only performance tests")
    parser.add_argument("--shell", action="store_true", help="Run only shell script tests")
    parser.add_argument("--all", action="store_true", help="Run all tests (default)")

    args = parser.parse_args()

    runner = TestRunner()

    if args.unit:
        result = runner.run_unit_tests()
    elif args.integration:
        result = runner.run_integration_tests()
    elif args.performance:
        result = runner.run_performance_tests()
    elif args.shell:
        result = runner.run_shell_script_tests()
    else:
        # Default to all tests
        result = runner.run_all_tests()

    # Exit with appropriate code
    if isinstance(result, dict) and "success" in result:
        sys.exit(0 if result["success"] else 1)
    elif isinstance(result, dict) and "summary" in result:
        sys.exit(0 if result["summary"]["failed_suites"] == 0 else 1)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()