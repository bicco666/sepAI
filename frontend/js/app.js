// Frontend JavaScript for Solana/Ethereum Trading Dashboard

class TradingDashboard {
    constructor() {
        this.apiBase = '/api/v1';
        this.init();
    }

    async init() {
        console.log('Initializing Trading Dashboard...');
        await this.loadData();
        this.bindEvents();
        this.startPolling();
    }

    async loadData() {
        try {
            await Promise.all([
                this.loadIdeas(),
                this.loadOrders()
            ]);
        } catch (error) {
            console.error('Error loading data:', error);
        }
    }

    async loadIdeas() {
        try {
            const response = await fetch(`${this.apiBase}/ideas`);
            const data = await response.json();
            this.renderIdeas(data.ideas);
        } catch (error) {
            console.error('Error loading ideas:', error);
        }
    }

    async loadOrders() {
        try {
            const response = await fetch(`${this.apiBase}/orders`);
            const data = await response.json();
            this.renderOrders(data.orders);
        } catch (error) {
            console.error('Error loading orders:', error);
        }
    }

    renderIdeas(ideas) {
        const tbody = document.getElementById('tbl-ideas');
        if (!tbody) return;

        if (!ideas || ideas.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="sub">Keine Ideen vorhanden</td></tr>';
            return;
        }

        tbody.innerHTML = ideas.map(idea => `
            <tr data-idea-id="${idea.id}">
                <td>${idea.id}</td>
                <td>${idea.chain}</td>
                <td>${idea.budget}</td>
                <td>${idea.state}</td>
                <td>
                    ${idea.state === 'NEW' ?
                        `<button class="btn" onclick="dashboard.moveToAnalysis('${idea.id}')">Zu Analyse</button>` :
                        idea.state === 'NEEDS_REVIEW' ?
                        `<button class="btn" onclick="dashboard.scheduleIdea('${idea.id}')">Einplanen</button>` :
                        ''
                    }
                </td>
            </tr>
        `).join('');
    }

    renderOrders(orders) {
        const tbody = document.getElementById('tbl-orders');
        if (!tbody) return;

        if (!orders || orders.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="sub">Keine Aufträge vorhanden</td></tr>';
            return;
        }

        tbody.innerHTML = orders.map(order => `
            <tr data-order-id="${order.id}">
                <td>${order.id}</td>
                <td>${order.idea_id}</td>
                <td>${order.chain}</td>
                <td>${order.amount}</td>
                <td>${order.state}</td>
                <td>
                    ${order.state === 'NEW' ?
                        `<button class="btn" onclick="dashboard.executeOrder('${order.id}')">Ausführen</button>` :
                        ''
                    }
                </td>
            </tr>
        `).join('');
    }

    async createIdea() {
        const chain = document.getElementById('idea-chain')?.value;
        const budget = parseFloat(document.getElementById('idea-budget')?.value);
        const description = document.getElementById('idea-description')?.value || '';

        if (!chain || !budget) {
            alert('Bitte Chain und Budget angeben');
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/ideas`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ chain, budget, description })
            });

            if (response.ok) {
                await this.loadIdeas();
                // Clear form
                document.getElementById('idea-budget').value = '';
                document.getElementById('idea-description').value = '';
            } else {
                const error = await response.json();
                alert('Fehler: ' + error.error);
            }
        } catch (error) {
            console.error('Error creating idea:', error);
            alert('Fehler beim Erstellen der Idee');
        }
    }

    async moveToAnalysis(ideaId) {
        try {
            const response = await fetch(`${this.apiBase}/ideas/${ideaId}/to-analysis`, {
                method: 'POST'
            });

            if (response.ok) {
                await this.loadIdeas();
            } else {
                alert('Fehler beim Verschieben zur Analyse');
            }
        } catch (error) {
            console.error('Error moving to analysis:', error);
        }
    }

    async scheduleIdea(ideaId) {
        try {
            const response = await fetch(`${this.apiBase}/ideas/${ideaId}/schedule`, {
                method: 'POST'
            });

            if (response.ok) {
                await Promise.all([this.loadIdeas(), this.loadOrders()]);
            } else {
                alert('Fehler beim Einplanen der Idee');
            }
        } catch (error) {
            console.error('Error scheduling idea:', error);
        }
    }

    async executeOrder(orderId) {
        try {
            const response = await fetch(`${this.apiBase}/orders/${orderId}/execute`, {
                method: 'POST'
            });

            if (response.ok) {
                await this.loadOrders();
            } else {
                alert('Fehler bei der Ausführung');
            }
        } catch (error) {
            console.error('Error executing order:', error);
        }
    }

    async runTest(testCase) {
        try {
            const response = await fetch(`${this.apiBase}/tests/run?case=${testCase}`);
            const result = await response.json();

            if (result.success) {
                alert(`Test ${testCase} erfolgreich: ${result.message}`);
            } else {
                alert(`Test ${testCase} fehlgeschlagen: ${result.error}`);
            }
        } catch (error) {
            console.error('Error running test:', error);
            alert('Fehler beim Ausführen des Tests');
        }
    }

    async runBundleTest() {
        try {
            const response = await fetch(`${this.apiBase}/tests/bundle`);
            const result = await response.json();

            alert(`Bundle-Test abgeschlossen: ${result.summary.passed}/${result.summary.total} erfolgreich`);
        } catch (error) {
            console.error('Error running bundle test:', error);
            alert('Fehler beim Ausführen des Bundle-Tests');
        }
    }

    async runAudit() {
        try {
            const response = await fetch(`${this.apiBase}/audit/run`, {
                method: 'POST'
            });
            const result = await response.json();

            alert('Audit abgeschlossen - Bericht wurde in reports/ gespeichert');
        } catch (error) {
            console.error('Error running audit:', error);
            alert('Fehler beim Ausführen des Audits');
        }
    }

    bindEvents() {
        // Idea creation
        const btnIdea = document.getElementById('btn-idea');
        if (btnIdea) {
            btnIdea.addEventListener('click', () => this.createIdea());
        }

        // Test buttons
        const testButtons = document.querySelectorAll('[data-test-case]');
        testButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const caseNum = e.target.getAttribute('data-test-case');
                this.runTest(caseNum);
            });
        });

        // Bundle test
        const bundleBtn = document.getElementById('btn-bundle-test');
        if (bundleBtn) {
            bundleBtn.addEventListener('click', () => this.runBundleTest());
        }

        // Audit button
        const auditBtn = document.getElementById('btn-audit');
        if (auditBtn) {
            auditBtn.addEventListener('click', () => this.runAudit());
        }
    }

    startPolling() {
        // Refresh data every 10 seconds
        setInterval(() => {
            this.loadData();
        }, 10000);
    }
}

// Global instance
let dashboard;

document.addEventListener('DOMContentLoaded', () => {
    dashboard = new TradingDashboard();
});

// Expose functions globally for onclick handlers
window.moveToAnalysis = (ideaId) => dashboard.moveToAnalysis(ideaId);
window.scheduleIdea = (ideaId) => dashboard.scheduleIdea(ideaId);
window.executeOrder = (orderId) => dashboard.executeOrder(orderId);