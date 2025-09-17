// Test Links Handler - Enhanced version with debugging
(function() {
  'use strict';

  console.log('Test Links Handler loading...');

  // Wait for DOM to be ready
  function initTestLinks() {
    console.log('Initializing test links...');

    const testLinks = document.querySelectorAll('.test-link');
    const testLog = document.getElementById('testNavResult');

    console.log('Found test links:', testLinks.length);

    if (!testLog) {
      console.error('testNavResult element not found!');
      return;
    }

    if (testLinks.length === 0) {
      console.warn('No test links found!');
      return;
    }

    const pretty = (val) => typeof val === 'string' ? val : JSON.stringify(val, null, 2);

    testLinks.forEach((link, index) => {
      console.log(`Setting up test link ${index + 1}:`, link.dataset.endpoint);

      // Remove existing listeners to prevent duplicates
      if (link._testHandler) {
        link.removeEventListener('click', link._testHandler);
      }

      link._testHandler = async (event) => {
        event.preventDefault();
        console.log('Test link clicked:', link.dataset.endpoint);

        const testType = (link.dataset.testType || '').toLowerCase();
        const testName = link.textContent.trim();

        console.log('Test details:', { testType, testName });

        // Update UI
        document.querySelectorAll('.test-link').forEach(it => it.classList.remove('is-active'));
        link.classList.add('is-active');
        testLog.textContent = `Starte ${testName}…`;

        const startTime = Date.now();

        try {
          let apiEndpoint, requestBody;

          if (testType === 'bundle') {
            // Call bundle test endpoint
            apiEndpoint = '/api/v1/tests/bundle';
            requestBody = null;
          } else {
            // Call individual test endpoint
            apiEndpoint = '/api/v1/tests/run';
            requestBody = JSON.stringify({
              test_type: testType || 'unknown',
              test_name: testName,
              parameters: {}
            });
          }

          console.log('Making API call to:', apiEndpoint);
          const response = await fetch(apiEndpoint, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: requestBody
          });

          const responseTime = Date.now() - startTime;
          console.log('Response received:', response.status, responseTime + 'ms');

          const raw = await response.text();
          let parsed = raw;
          try {
            parsed = JSON.parse(raw);
          } catch (err) {
            parsed = raw;
          }

          let message = `Status ${response.status}: ${pretty(parsed)}`;
          let testResult = {
            success: response.ok,
            status: response.status,
            responseTime: responseTime
          };

          // Special handling for bundle tests
          if (testType === 'bundle' && parsed && typeof parsed === 'object') {
            const summary = parsed.summary || {};
            const total = summary.total || 0;
            const passed = summary.passed || 0;
            const failed = summary.failed || 0;
            const errors = summary.errors || 0;

            message = `Bundle-Funktionstest abgeschlossen: ${passed}/${total} bestanden`;
            if (failed > 0 || errors > 0) {
              message += `\nFehlgeschlagen: ${failed}, Fehler: ${errors}`;
            }

            // Show detailed results
            if (parsed.results && Array.isArray(parsed.results)) {
              message += '\n\nDetails:\n';
              parsed.results.forEach(result => {
                const icon = result.success ? '✓' : '✗';
                message += `${icon} ${result.test_name}: ${result.success ? 'OK' : 'FEHLER'}\n`;
                if (!result.success && result.error) {
                  message += `   Fehler: ${result.error}\n`;
                }
              });
            }
          }

          testLog.textContent = message;

          // Create and save test report
          const reportData = {
            type: testType || 'individual',
            name: testName,
            endpoint: apiEndpoint,
            method: 'POST',
            status: response.status,
            responseTime: responseTime,
            summary: {
              success: response.ok,
              status: response.status,
              responseTime: responseTime
            },
            details: {
              endpoint: apiEndpoint,
              method: 'POST',
              status: response.status,
              responseTime: responseTime,
              body: requestBody,
              response: parsed
            },
            fullReport: formatTestReport(testName, apiEndpoint, 'POST', response.status, responseTime, parsed, requestBody)
          };

          console.log('Saving report:', reportData.name);
          console.log('ReportsManager available:', !!window.ReportsManager);
          console.log('ReportsManager.saveReport available:', !!(window.ReportsManager && window.ReportsManager.saveReport));

          if (window.ReportsManager && window.ReportsManager.saveReport) {
            const reportSaved = window.ReportsManager.saveReport(reportData);
            console.log('Report save result:', reportSaved);
            if (reportSaved) {
              message += '\n\nReport wurde gespeichert und ist im Reports-Menü verfügbar.';
              testLog.textContent = message;
              // Refresh reports list
              if (window.ReportsManager.renderReportsList) {
                window.ReportsManager.renderReportsList();
                console.log('Reports list refreshed');
              }
              console.log('Report saved and list refreshed');
            } else {
              console.error('Failed to save report');
              message += '\n\nFehler: Report konnte nicht gespeichert werden.';
              testLog.textContent = message;
            }
          } else {
            console.warn('ReportsManager not available, report not saved');
            console.log('window.ReportsManager:', window.ReportsManager);
            message += '\n\nWarnung: ReportsManager nicht verfügbar, Report nicht gespeichert.';
            testLog.textContent = message;
          }

        } catch (error) {
          const responseTime = Date.now() - startTime;
          console.error('Test error:', error);
          testLog.textContent = `Fehler bei ${testName}: ${(error && error.message) || error}`;

          // Create error report
          const errorReport = {
            type: testType || 'individual',
            name: testName,
            endpoint: '/api/v1/tests/run',
            method: 'POST',
            status: 0,
            responseTime: responseTime,
            summary: {
              success: false,
              status: 0,
              responseTime: responseTime,
              error: (error && error.message) || error
            },
            details: {
              endpoint: '/api/v1/tests/run',
              method: 'POST',
              error: (error && error.message) || error,
              responseTime: responseTime
            },
            fullReport: formatTestReport(testName, '/api/v1/tests/run', 'POST', 0, responseTime, null, null, (error && error.message) || error)
          };

          if (window.ReportsManager && window.ReportsManager.saveReport) {
            const reportSaved = window.ReportsManager.saveReport(errorReport);
            if (reportSaved) {
              testLog.textContent += '\n\nFehler-Report wurde gespeichert und ist im Reports-Menü verfügbar.';
              if (window.ReportsManager.renderReportsList) {
                window.ReportsManager.renderReportsList();
              }
            }
          } else {
            console.warn('ReportsManager not available for error report');
            testLog.textContent += '\n\nWarnung: ReportsManager nicht verfügbar, Fehler-Report nicht gespeichert.';
          }
        }
      };

      link.addEventListener('click', link._testHandler);
      console.log(`Test link ${index + 1} handler attached`);
    });

    console.log('All test links initialized');
  }

  function formatTestReport(testName, endpoint, method, status, responseTime, response, body, error) {
    let text = `TEST REPORT: ${testName}\n`;
    text += `==========================\n\n`;
    text += `Zeitstempel: ${new Date().toISOString()}\n`;
    text += `Test Name: ${testName}\n`;
    text += `Endpoint: ${endpoint}\n`;
    text += `Method: ${method}\n`;
    text += `Status: ${status}\n`;
    text += `Response Time: ${responseTime}ms\n`;
    text += `Result: ${status >= 200 && status < 300 ? 'SUCCESS' : 'FAILED'}\n\n`;

    if (body) {
      text += `Request Body:\n`;
      text += `${body}\n\n`;
    }

    if (error) {
      text += `Error:\n`;
      text += `${error}\n\n`;
    }

    if (response) {
      text += `Response:\n`;
      if (typeof response === 'object') {
        text += JSON.stringify(response, null, 2);
      } else {
        text += response;
      }
      text += `\n\n`;
    }

    text += `Test completed at: ${new Date().toLocaleString('de-DE')}\n`;

    return text;
  }

  // Initialize when DOM is ready (ReportsManager is loaded before this script)
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTestLinks);
  } else {
    // DOM already loaded
    initTestLinks();
  }

  console.log('Test Links Handler loaded');
})();