# Testing Guide for sepAI

## Overview

This document outlines the comprehensive testing framework implemented for the sepAI project. The testing suite includes unit tests, integration tests, performance tests, and automated test pipelines.

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── api/
│   └── test_all_api.py     # Comprehensive API tests
├── test_execution.py       # Unit tests for execution logic
├── test_ideas.py          # Unit tests for ideas functionality
├── test_infra_bus.py      # Unit tests for Redis bus
├── test_integration.py    # Integration tests
└── test_performance.py    # Performance and load tests

scripts/
├── run_tests.py           # Automated test runner
├── test_bundle.sh         # Shell script test suite
└── test_wallet_balance.sh # Improved individual test scripts

reports/                   # Generated test reports
├── coverage/             # Coverage reports
├── junit_*.xml          # JUnit XML reports
└── test_summary.json    # Test summary
```

## Running Tests

### Quick Start

```bash
# Run all tests
python scripts/run_tests.py --all

# Run specific test types
python scripts/run_tests.py --unit
python scripts/run_tests.py --integration
python scripts/run_tests.py --performance

# Run with pytest directly
pytest tests/ -v --cov=backend --cov-report=html
```

### Test Categories

#### Unit Tests (`pytest -m "not integration and not slow"`)
- **test_execution.py**: Trade execution logic
- **test_ideas.py**: Idea lifecycle management
- **test_infra_bus.py**: Redis event bus functionality
- **api/test_all_api.py**: API endpoint testing with mocks

#### Integration Tests (`pytest -m integration`)
- **test_integration.py**: Full workflow testing
  - Wallet creation to balance checking
  - Idea generation to scheduling
  - Trade execution workflows
  - Concurrent request handling

#### Performance Tests (`pytest -m slow`)
- **test_performance.py**: Load and performance testing
  - Response time benchmarks
  - Concurrent request handling
  - Memory usage monitoring
  - Database connection efficiency

#### Shell Script Tests
- **scripts/test_bundle.sh**: Runs all shell-based tests
- Individual test scripts for specific functionality

## Test Configuration

### pytest.ini

```ini
[tool:pytest]
testpaths = tests
addopts =
    --verbose
    --tb=short
    --cov=backend
    --cov=src
    --cov-report=html:reports/coverage
    --cov-report=xml:reports/coverage.xml
    --junitxml=reports/junit.xml
markers =
    slow: Performance and load tests
    integration: Integration tests
    unit: Unit tests
    api: API-specific tests
```

### Shared Fixtures (conftest.py)

- `client`: FastAPI test client
- `temp_keys_dir`: Isolated keypair directory
- `mock_solana_services`: Mocked Solana blockchain services
- `isolated_keypair_store`: Clean keypair store for testing

## Key Improvements

### 1. Consolidated Test Suite
- **Before**: Duplicate tests across multiple files
- **After**: Single comprehensive test file with all wallet API tests
- **Benefit**: Reduced duplication, easier maintenance

### 2. Enhanced Mocking
- **Before**: Basic mock responses
- **After**: Sophisticated mocking with validation
- **Benefit**: More realistic test scenarios, better error detection

### 3. Error Scenario Testing
- **Before**: Limited error case coverage
- **After**: Comprehensive error testing including:
  - Invalid addresses
  - Network failures
  - Rate limiting
  - Service unavailability

### 4. Integration Testing
- **Before**: Isolated unit tests only
- **After**: Full workflow integration tests
- **Benefit**: Catches integration issues early

### 5. Performance Testing
- **Before**: No performance validation
- **After**: Automated performance benchmarks
- **Benefit**: Ensures system meets performance requirements

### 6. Automated Test Pipeline
- **Before**: Manual test execution
- **After**: Automated test runner with reporting
- **Benefit**: Consistent, repeatable test execution

### 7. Coverage Reporting
- **Before**: No coverage tracking
- **After**: HTML and XML coverage reports
- **Benefit**: Identifies untested code paths

## Test Examples

### API Testing with Mocks

```python
def test_wallet_balance_with_mock(monkeypatch, temp_keys_dir, test_client):
    """Test balance checking with mocked Solana services"""
    # Setup isolated environment
    from backend.services import keypair_store as ks
    monkeypatch.setattr(ks, "KEYS_DIR", temp_keys_dir, raising=False)

    # Mock Solana services
    def fake_import_ok():
        def get_balance(addr): return 1.2345
        def request_airdrop(addr, sol): return {"signature": "SIG"}
        return get_balance, request_airdrop, None

    monkeypatch.setattr(wallet, "_import_solana_services", fake_import_ok)

    # Test the endpoint
    r = test_client.get("/api/v1/wallet/balance")
    assert r.status_code == 200
    assert abs(r.json()["balance_sol"] - 1.2345) < 1e-9
```

### Parametrized Testing

```python
@pytest.mark.parametrize("amount", [0.1, 1.0, 5.0, 10.0])
def test_airdrop_various_amounts(test_client, amount):
    """Test airdrop with different amounts"""
    r = test_client.post("/api/v1/wallet/airdrop", json={"sol": amount})
    assert r.status_code == 200
    assert r.json()["requested_sol"] == amount
```

### Integration Testing

```python
@pytest.mark.integration
def test_full_wallet_workflow(test_client, temp_keys_dir, monkeypatch):
    """Test complete wallet workflow"""
    # 1. Create address
    r1 = test_client.get("/api/v1/wallet/address")
    assert r1.status_code == 200
    address = r1.json()["public_key"]

    # 2. Mock balance service
    def fake_import_ok():
        def get_balance(addr): return 5.0
        def request_airdrop(addr, sol): return {"signature": f"SIG_{sol}"}
        return get_balance, request_airdrop, None
    monkeypatch.setattr(wallet, "_import_solana_services", fake_import_ok)

    # 3. Check balance
    r2 = test_client.get("/api/v1/wallet/balance")
    assert r2.status_code == 200
    assert r2.json()["balance_sol"] == 5.0
```

## Test Reports

### Coverage Report
```bash
pytest --cov=backend --cov-report=html
# Opens reports/coverage/index.html
```

### JUnit XML Reports
- `reports/junit_unit.xml`: Unit test results
- `reports/junit_integration.xml`: Integration test results
- `reports/junit_performance.xml`: Performance test results

### Test Summary
```bash
python scripts/run_tests.py --all
# Generates reports/test_summary.json
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Run tests
      run: python scripts/run_tests.py --all
    - name: Upload coverage
      uses: codecov/codecov-action@v2
      with:
        file: reports/coverage.xml
```

## Best Practices

### Writing Tests

1. **Use descriptive test names**: `test_wallet_balance_with_mock` vs `test_balance`
2. **Test one thing per test**: Keep tests focused and atomic
3. **Use fixtures for setup**: Leverage pytest fixtures for reusable setup
4. **Mock external dependencies**: Don't rely on external services in unit tests
5. **Test error scenarios**: Include tests for failure cases
6. **Use parametrized tests**: Test multiple inputs with one test function

### Test Organization

1. **Unit tests**: Test individual functions/classes
2. **Integration tests**: Test component interactions
3. **API tests**: Test HTTP endpoints
4. **Performance tests**: Test system performance under load

### Maintenance

1. **Keep tests updated**: Update tests when code changes
2. **Remove obsolete tests**: Delete tests for removed functionality
3. **Review test coverage**: Ensure adequate coverage of critical paths
4. **Monitor test performance**: Keep tests running quickly

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure PYTHONPATH includes project root
2. **Fixture errors**: Check fixture dependencies and scope
3. **Mock failures**: Verify mock setup and teardown
4. **Coverage issues**: Check source file paths in coverage configuration

### Debug Commands

```bash
# Run specific test with debug output
pytest tests/api/test_all_api.py::test_wallet_address -v -s

# Run tests with coverage details
pytest --cov=backend --cov-report=term-missing

# Run tests in verbose mode
pytest -v --tb=long
```

## Future Enhancements

1. **Property-based testing**: Use hypothesis for generative testing
2. **Visual testing**: Screenshot comparison for UI components
3. **Contract testing**: API contract validation
4. **Chaos testing**: Fault injection testing
5. **Security testing**: Automated security vulnerability scanning

---

This testing framework provides comprehensive coverage of the sepAI application with automated execution, detailed reporting, and maintainable test code.