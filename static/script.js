/**
 * Main Application Script
 * Handles UI interactions and API communication
 */

// Global state
let analysisData = null;

/**
 * Initialize event listeners
 */
function initializeEventListeners() {
    // Analyze button
    document.getElementById('analyze-btn').addEventListener('click', analyzeRisk);
    
    // Validate button
    document.getElementById('validate-btn').addEventListener('click', validateSymbols);
    
    // Chart tabs
    document.querySelectorAll('.chart-tab-btn').forEach(btn => {
        btn.addEventListener('click', switchChartTab);
    });
    
    // Optimization tabs
    document.querySelectorAll('.opt-tab-btn').forEach(btn => {
        btn.addEventListener('click', switchOptimizationTab);
    });
    
    // Stock selection tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', switchStockSelectionTab);
    });
    
    // Stock category dropdown
    document.getElementById('stock-category').addEventListener('change', loadStocksForCategory);
    
    // Add from dropdown button
    document.getElementById('add-from-dropdown').addEventListener('click', addStocksFromDropdown);
    
    // Load stocks on page load
    loadAllStocks();
}

/**
 * Validate stock symbols before analysis
 */
async function validateSymbols() {
    const symbolsInput = document.getElementById('stock-symbols').value.trim();
    const statusEl = document.getElementById('status-message');
    
    if (!symbolsInput) {
        showStatus('Please enter at least one stock symbol', 'error', statusEl);
        return;
    }
    
    try {
        const response = await fetch('/api/validate-symbols', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbols: symbolsInput })
        });
        
        const result = await response.json();
        
        if (result.valid.length > 0) {
            const msg = `✓ Found ${result.valid.length} valid symbol(s): ${result.valid.join(', ')}`;
            showStatus(msg, 'success', statusEl);
        } else {
            showStatus('No valid symbols found. Please check the symbol format.', 'error', statusEl);
        }
        
        if (result.invalid.length > 0) {
            console.warn('Invalid symbols:', result.invalid);
        }
    } catch (error) {
        showStatus(`Validation error: ${error.message}`, 'error', statusEl);
        console.error('Validation error:', error);
    }
}

/**
 * Switch between manual entry and dropdown selection tabs
 */
function switchStockSelectionTab(event) {
    const tabName = event.target.getAttribute('data-tab');
    
    // Update active button
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    if (tabName === 'manual') {
        document.getElementById('manual-tab').classList.add('active');
    } else if (tabName === 'dropdown') {
        document.getElementById('dropdown-tab').classList.add('active');
    }
}

/**
 * Load all stocks from API
 */
async function loadAllStocks() {
    try {
        const response = await fetch('/api/get-stock-list');
        const stocksData = await response.json();
        
        // Store globally for later use
        window.allStocks = stocksData;
        console.log('✓ Loaded stock list');
    } catch (error) {
        console.error('Error loading stocks:', error);
    }
}

/**
 * Load stocks for selected category
 */
function loadStocksForCategory(event) {
    const category = event.target.value;
    const stockDropdown = document.getElementById('stock-dropdown');
    
    // Clear existing options
    stockDropdown.innerHTML = '<option value="">Choose stocks...</option>';
    
    if (!category || !window.allStocks || !window.allStocks[category]) {
        return;
    }
    
    // Add stocks for selected category
    window.allStocks[category].forEach(stock => {
        const option = document.createElement('option');
        option.value = stock.symbol;
        option.textContent = `${stock.symbol} - ${stock.name}`;
        stockDropdown.appendChild(option);
    });
}

/**
 * Add selected stocks from dropdown to textarea
 */
function addStocksFromDropdown() {
    const stockDropdown = document.getElementById('stock-dropdown');
    const selectedOptions = Array.from(stockDropdown.selectedOptions);
    
    if (selectedOptions.length === 0) {
        showStatus('Please select at least one stock', 'warning', document.getElementById('status-message'));
        return;
    }
    
    const selectedSymbols = selectedOptions.map(opt => opt.value);
    const textarea = document.getElementById('stock-symbols');
    const existingText = textarea.value.trim();
    
    // Add new symbols, avoiding duplicates
    const existingSymbols = existingText ? existingText.split(',').map(s => s.trim()) : [];
    const allSymbols = [...new Set([...existingSymbols, ...selectedSymbols])];
    
    textarea.value = allSymbols.join(', ');
    
    // Clear dropdown selection
    stockDropdown.value = '';
    
    showStatus(`✓ Added ${selectedSymbols.length} stock(s)`, 'success', document.getElementById('status-message'));
}

/**
 * Main analysis function
 */
async function analyzeRisk() {
    const symbolsInput = document.getElementById('stock-symbols').value.trim();
    const investmentAmount = parseFloat(document.getElementById('investment-amount').value);
    const daysAhead = parseInt(document.getElementById('days-ahead').value);
    const numSimulations = parseInt(document.getElementById('num-simulations').value);
    const statusEl = document.getElementById('status-message');
    const loadingEl = document.getElementById('loading');
    const resultsEl = document.getElementById('results');
    const emptyStateEl = document.getElementById('empty-state');
    
    // Validation
    if (!symbolsInput) {
        showStatus('Please enter at least one stock symbol', 'error', statusEl);
        return;
    }
    
    if (isNaN(investmentAmount) || investmentAmount <= 0) {
        showStatus('Please enter a valid investment amount', 'error', statusEl);
        return;
    }
    
    try {
        // Show loading state
        loadingEl.classList.remove('hidden');
        resultsEl.classList.add('hidden');
        emptyStateEl.classList.add('hidden');
        showStatus('Starting OPTIMIZED analysis... Should finish in 5-15 seconds!', 'info', statusEl);
        
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                symbols: symbolsInput,
                investment_amount: investmentAmount,
                days_ahead: daysAhead,
                num_simulations: numSimulations
            })
        });
        
        if (!response.ok) {
            let errorMsg = 'Analysis failed';
            try {
                const error = await response.json();
                errorMsg = error.error || errorMsg;
            } catch (e) {
                errorMsg = `Server error (status ${response.status})`;
            }
            throw new Error(errorMsg);
        }
        
        const data = await response.json();
        analysisData = data;
        
        // Hide loading
        loadingEl.classList.add('hidden');
        
        // Display results
        displayResults(data);
        renderCharts(data);
        
        showStatus('✓ Analysis completed successfully!', 'success', statusEl);
        
    } catch (error) {
        loadingEl.classList.add('hidden');
        showStatus(`Error: ${error.message}`, 'error', statusEl);
        console.error('Analysis error:', error);
    }
}

/**
 * Display analysis results
 */
function displayResults(data) {
    const resultsEl = document.getElementById('results');
    const emptyStateEl = document.getElementById('empty-state');
    
    // Hide empty state
    emptyStateEl.classList.add('hidden');
    
    // Show results
    resultsEl.classList.remove('hidden');
    
    // Display stock statistics
    displayStockStatistics(data);
    
    // Display risk metrics
    displayRiskMetrics(data);
    
    // Display portfolio optimization results
    displayPortfolioResults(data);
    
    // Display summary
    displaySummary(data);
}

/**
 * Display stock statistics
 */
function displayStockStatistics(data) {
    const container = document.getElementById('stock-stats-container');
    container.innerHTML = '';
    
    Object.entries(data.stock_analysis).forEach(([symbol, stats]) => {
        const card = document.createElement('div');
        card.className = 'stat-card';
        
        const basicStats = stats.basic_statistics;
        
        card.innerHTML = `
            <h3>${symbol}</h3>
            <div class="stat-row">
                <span class="stat-label">Current Price:</span>
                <span class="stat-value">$${(stats.current_price ?? 0).toFixed(2)}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Annual Return:</span>
                <span class="stat-value ${(basicStats.expected_annual_return ?? 0) > 0 ? 'positive' : 'negative'}">
                    ${((basicStats.expected_annual_return ?? 0) * 100).toFixed(2)}%
                </span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Annual Volatility:</span>
                <span class="stat-value warning">${((basicStats.annual_volatility ?? 0) * 100).toFixed(2)}%</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Sharpe Ratio:</span>
                <span class="stat-value">${(stats.risk_metrics.sharpe_ratio ?? 0).toFixed(3)}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Skewness:</span>
                <span class="stat-value">${(basicStats.skewness ?? 0).toFixed(3)}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Kurtosis:</span>
                <span class="stat-value">${(basicStats.kurtosis ?? 0).toFixed(3)}</span>
            </div>
        `;
        
        container.appendChild(card);
    });
}

/**
 * Display risk metrics
 */
function displayRiskMetrics(data) {
    const container = document.getElementById('risk-metrics-container');
    container.innerHTML = '';
    
    Object.entries(data.stock_analysis).forEach(([symbol, stats]) => {
        const metrics = stats.risk_metrics;
        const basicStats = stats.basic_statistics;
        
        const card = document.createElement('div');
        card.className = 'metric-card';
        card.style.background = `linear-gradient(135deg, ${getGradientColor(metrics.risk_level)} 0%, ${getGradientColor(metrics.risk_level, 2)} 100%)`;
        
        card.innerHTML = `
            <h3>${symbol} - Risk Assessment</h3>
            <div class="metric-value">${metrics.risk_level}</div>
            <div class="metric-description">${metrics.risk_description}</div>
            <div style="margin-top: 15px; font-size: 12px; opacity: 0.9;">
                <div>VaR (95%): ${((metrics.var_annual ?? 0) * 100).toFixed(2)}%</div>
                <div>CVaR (Daily): ${((metrics.cvar_daily ?? 0) * 100).toFixed(2)}%</div>
            </div>
        `;
        
        container.appendChild(card);
    });
}

/**
 * Display portfolio optimization results
 */
function displayPortfolioResults(data) {
    const strategies = data.portfolio_optimization.strategies;
    
    Object.entries(strategies).forEach(([strategyKey, strategy]) => {
        const tabId = getTabIdFromStrategy(strategyKey);
        const content = document.getElementById(tabId);
        
        if (content) {
            content.innerHTML = renderPortfolioAllocation(strategy);
        }
    });
}

/**
 * Render portfolio allocation details
 */
function renderPortfolioAllocation(strategy) {
    let html = `
        <div class="portfolio-stats">
            <div class="portfolio-stat">
                <h4>Expected Return</h4>
                <div class="value">${(strategy.expected_return_percentage ?? 0).toFixed(2)}%</div>
            </div>
            <div class="portfolio-stat">
                <h4>Annual Volatility</h4>
                <div class="value">${(strategy.portfolio_volatility_percentage ?? 0).toFixed(2)}%</div>
            </div>
            <div class="portfolio-stat">
                <h4>Sharpe Ratio</h4>
                <div class="value">${(strategy.sharpe_ratio ?? 0).toFixed(3)}</div>
            </div>
        </div>
        
        <h3>Portfolio Allocation</h3>
        <table class="allocation-table">
            <thead>
                <tr>
                    <th>Stock</th>
                    <th>Weight</th>
                    <th>Allocation</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    Object.entries(strategy.allocation).forEach(([symbol, alloc]) => {
        const percentage = alloc.weight_percentage ?? 0;
        html += `
            <tr>
                <td><strong>${symbol}</strong></td>
                <td>${percentage.toFixed(2)}%</td>
                <td>
                    <div class="allocation-bar" style="width: ${percentage}%">
                        ${percentage > 5 ? percentage.toFixed(1) + '%' : ''}
                    </div>
                </td>
            </tr>
        `;
    });
    
    html += `
            </tbody>
        </table>
    `;
    
    return html;
}

/**
 * Display summary statistics
 */
function displaySummary(data) {
    const container = document.getElementById('summary-stats');
    
    const timestamp = new Date(data.timestamp).toLocaleString();
    const numStocks = data.num_symbols;
    const numSims = data.num_simulations;
    
    // Calculate average metrics
    let avgReturn = 0;
    let avgVolatility = 0;
    let avgSharpe = 0;
    
    Object.values(data.stock_analysis).forEach(stats => {
        avgReturn += stats.basic_statistics.expected_annual_return;
        avgVolatility += stats.basic_statistics.annual_volatility;
        avgSharpe += stats.risk_metrics.sharpe_ratio;
    });
    
    avgReturn /= numStocks;
    avgVolatility /= numStocks;
    avgSharpe /= numStocks;
    
    const maxStrategy = data.portfolio_optimization?.strategies?.['Max Sharpe Ratio'];
    
    container.innerHTML = `
        <div class="summary-item">
            <strong>Analysis Timestamp</strong>
            <span>${timestamp}</span>
        </div>
        <div class="summary-item">
            <strong>Stocks Analyzed</strong>
            <span>${numStocks} securities</span>
        </div>
        <div class="summary-item">
            <strong>MC Simulations</strong>
            <span>${numSims} paths</span>
        </div>
        <div class="summary-item">
            <strong>Avg Annual Return</strong>
            <span>${((avgReturn ?? 0) * 100).toFixed(2)}%</span>
        </div>
        <div class="summary-item">
            <strong>Avg Annual Volatility</strong>
            <span>${((avgVolatility ?? 0) * 100).toFixed(2)}%</span>
        </div>
        <div class="summary-item">
            <strong>Avg Sharpe Ratio</strong>
            <span>${(avgSharpe ?? 0).toFixed(3)}</span>
        </div>
        ${maxStrategy ? `<div class="summary-item">
            <strong>Optimal Strategy Return</strong>
            <span>${(maxStrategy.expected_return_percentage ?? 0).toFixed(2)}%</span>
        </div>
        <div class="summary-item">
            <strong>Optimal Strategy Risk</strong>
            <span>${(maxStrategy.portfolio_volatility_percentage ?? 0).toFixed(2)}%</span>
        </div>` : ''}
    `;
}

/**
 * Render all charts
 */
function renderCharts(data) {
    const symbols = data.symbols;
    
    Charts.renderPriceChart(data, symbols);
    Charts.renderReturnsChart(data, symbols);
    Charts.renderMonteCarloChart(data, symbols);
    Charts.renderEfficientFrontier(data);
}

/**
 * Switch between chart tabs
 */
function switchChartTab(e) {
    const tab = e.target.dataset.tab;
    
    // Update active button
    document.querySelectorAll('.chart-tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    e.target.classList.add('active');
    
    // Update active content
    document.querySelectorAll('.chart-tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(tab).classList.add('active');
}

/**
 * Switch between optimization tabs
 */
function switchOptimizationTab(e) {
    const tab = e.target.dataset.tab;
    
    // Update active button
    document.querySelectorAll('.opt-tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    e.target.classList.add('active');
    
    // Update active content
    document.querySelectorAll('.opt-tab').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(tab).classList.add('active');
}

/**
 * Show status message
 */
function showStatus(message, type, element) {
    element.textContent = message;
    element.className = `status-message show ${type}`;
    
    // Auto-hide after 5 seconds
    if (type === 'success') {
        setTimeout(() => {
            element.classList.remove('show');
        }, 5000);
    }
}

/**
 * Get gradient color based on risk level
 */
function getGradientColor(riskLevel, variant = 1) {
    const colors = {
        'Low Risk': ['#27ae60', '#229954'],
        'Medium Risk': ['#f39c12', '#e67e22'],
        'High Risk': ['#e74c3c', '#c0392b']
    };
    
    return colors[riskLevel] ? colors[riskLevel][variant] : '#3498db';
}

/**
 * Map strategy names to tab IDs
 */
function getTabIdFromStrategy(strategy) {
    const mapping = {
        'Min Variance': 'min-variance',
        'Maximum Sharpe Ratio': 'sharpe',
        'Max Return': 'max-return',
        'Maximum Sharpe Ratio (Sharpe)': 'sharpe',
        'Equal Weight': 'equal'
    };
    return mapping[strategy] || 'min-variance';
}

/**
 * Initialize app on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('📊 Financial Risk Analyzer loaded');
    initializeEventListeners();
    
    // Show empty state initially
    document.getElementById('empty-state').classList.remove('hidden');
});

/**
 * Handle keyboard shortcuts
 */
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to analyze
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        analyzeRisk();
    }
});
