# 📊 Financial Risk Analysis Model using Statistical Methods and Linear Programming

A comprehensive, production-level system for evaluating financial risk using advanced statistical analysis, probability modeling, Monte Carlo simulation, and linear programming optimization.

## 🎯 Overview

This system provides:

- **Statistical Analysis**: Mean, Variance, Standard Deviation, Skewness, Kurtosis
- **Probability & Risk Modeling**: Normal distribution fitting, Value at Risk (VaR), Conditional VaR
- **Monte Carlo Simulation**: 1000+ simulated price paths using Geometric Brownian Motion
- **Portfolio Optimization**: Linear programming for optimal asset allocation
- **Interactive Dashboard**: Real-time visualization and analysis

## 🏗️ Project Structure

```
financial_risk_analyzer/
├── app.py                          # Flask backend application
├── requirements.txt                # Python dependencies
├── utils/                          # Core analysis modules
│   ├── __init__.py
│   ├── data_handler.py            # Stock data fetching & processing
│   ├── statistical_analysis.py    # Statistics & risk metrics
│   ├── monte_carlo.py             # Monte Carlo simulation
│   └── portfolio_optimizer.py     # Linear programming optimization
├── templates/
│   └── index.html                 # Main dashboard interface
└── static/
    ├── style.css                  # CSS styling
    ├── script.js                  # Frontend JavaScript
    └── charts.js                  # Chart rendering
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd /path/to/financial_risk_analyzer
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app.py
```

The server will start at: **http://localhost:5000**

### 3. Use the Dashboard

- Enter stock symbols (e.g., `RELIANCE.NS, TCS.NS, INFY.NS`)
- Click "Analyze Risk"
- Review statistics, simulations, and optimal portfolios

## 📚 Key Features

### 1. Data Handling (`utils/data_handler.py`)

```python
# Fetch real-world data using yfinance
handler = DataHandler(period='1y')
data = handler.fetch_stock_data(['RELIANCE.NS', 'TCS.NS'])
returns = handler.calculate_returns(['RELIANCE.NS', 'TCS.NS'])
```

**Functions:**
- `fetch_stock_data()`: Download historical OHLCV data
- `calculate_returns()`: Compute daily percentage returns
- `get_stock_info()`: Retrieve company information
- `validate_symbols()`: Check if symbols exist

---

### 2. Statistical Analysis (`utils/statistical_analysis.py`)

```python
# Calculate risk metrics
analyzer = StatisticalAnalyzer()
stats = analyzer.calculate_basic_statistics(returns['RELIANCE.NS'])
var = analyzer.calculate_var(returns['RELIANCE.NS'], confidence=0.95)
sharpe = analyzer.calculate_sharpe_ratio(returns['RELIANCE.NS'])
```

**Implemented Metrics:**

| Metric | Formula | Interpretation |
|--------|---------|-----------------|
| **Mean** | μ = Σx/n | Expected daily return |
| **Variance** | σ² = Σ(x-μ)²/n | Measure of volatility |
| **Std Dev** | σ = √σ² | Risk measurement |
| **VaR (95%)** | F⁻¹(0.05) | Max loss with 95% confidence |
| **Sharpe Ratio** | (R - Rf)/σ | Risk-adjusted return |

---

### 3. Normal Distribution Fitting

The system fits returns to a normal distribution:

$$X \sim N(\mu, \sigma^2)$$

- Tests normality using Shapiro-Wilk test
- Calculates probability of loss
- Generates distribution curves

---

### 4. Monte Carlo Simulation (`utils/monte_carlo.py`)

Uses **Geometric Brownian Motion (GBM)** to simulate future prices:

$$dS = \mu S \, dt + \sigma S \, dW$$

Where:
- S = Stock price
- μ = Expected return (drift)
- σ = Volatility (diffusion)
- dW = Random shock from N(0,1)

```python
# Run simulations
simulator = MonteCarloSimulator()
paths = simulator.simulate_paths(
    current_prices={'RELIANCE.NS': 2500},
    returns_stats={'RELIANCE.NS': {'mean_daily': 0.0005, 'std_dev_daily': 0.02}},
    days_ahead=252,
    num_simulations=1000
)
stats = simulator.get_simulation_statistics(1000)
```

**Output includes:**
- Best case scenario
- Worst case scenario
- Mean prediction with confidence bands
- Probability of profit

---

### 5. Portfolio Optimization (`utils/portfolio_optimizer.py`)

Uses **Sequential Least Squares Programming (SLSQP)** for linear optimization.

#### Strategy 1: Minimize Risk (Minimum Variance)

**Objective:** Minimize portfolio variance

$$\min \quad w^T \Sigma w$$

**Constraints:**
- $\sum w_i = 1$ (fully invested)
- $w_i \geq 0$ (no short selling)

---

#### Strategy 2: Maximize Sharpe Ratio

**Objective:** Maximize risk-adjusted returns

$$\max \quad \frac{R_p - R_f}{\sigma_p}$$

**Constraints:**
- $\sum w_i = 1$
- $w_i \geq 0$

---

#### Strategy 3: Maximize Return

**Objective:** Maximize expected return subject to risk constraint

$$\max \quad w^T \mu$$

**Constraints:**
- $\sum w_i = 1$
- $\sigma_p \leq \sigma_{max}$
- $w_i \geq 0$

---

#### Optimization Example

```python
# Set up optimizer
optimizer = PortfolioOptimizer()
optimizer.set_parameters(['RELIANCE.NS', 'TCS.NS'], returns_dict)

# Get optimal portfolios
min_var = optimizer.optimize_risk_minimization()
sharpe_max = optimizer.optimize_sharpe_ratio()
max_return = optimizer.optimize_return_maximization()

# Get efficient frontier
frontier = optimizer.get_efficient_frontier(num_points=50)
```

---

## 🎨 API Endpoints

### `/` (GET)
Main dashboard page

### `/api/analyze` (POST)
Perform complete financial analysis

**Request:**
```json
{
    "symbols": "RELIANCE.NS,TCS.NS",
    "investment_amount": 100000,
    "days_ahead": 252,
    "num_simulations": 1000
}
```

**Response:**
```json
{
    "success": true,
    "symbols": ["RELIANCE.NS", "TCS.NS"],
    "stock_analysis": {
        "RELIANCE.NS": {
            "current_price": 2645.50,
            "basic_statistics": {...},
            "risk_metrics": {...},
            "distribution": {...}
        }
    },
    "monte_carlo": {
        "statistics": {...},
        "price_corridors": {...}
    },
    "portfolio_optimization": {
        "strategies": {...},
        "efficient_frontier": [...]
    }
}
```

### `/api/validate-symbols` (POST)
Validate stock symbols before analysis

### `/api/stock-info` (POST)
Get basic information about a stock

### `/api/health` (GET)
Health check endpoint

---

## 📊 Visualization Examples

### 1. Price Trend Chart
- Current prices for all stocks
- Bar chart visualization

### 2. Return Distribution
- Histogram of daily returns
- Normal distribution curve overlay
- Tests for normality

### 3. Monte Carlo Simulation
- 100 sample paths
- Best case, worst case, mean
- 90% confidence band (5th-95th percentile)

### 4. Efficient Frontier
- Risk vs Return trade-off
- All optimal portfolio allocations
- Color-coded by risk level

---

## 🔧 Configuration

### Data Period
Edit in `app.py`:
```python
data_handler = DataHandler(period='1y')  # Options: '1mo', '3mo', '6mo', '1y', '2y'
```

### Risk-Free Rate
Edit in `utils/portfolio_optimizer.py`:
```python
def optimize_sharpe_ratio(self, risk_free_rate=0.02):  # 2% annual rate
```

### Simulation Parameters
Adjust in dashboard or code:
- Days Ahead: 30-1000 (default: 252)
- Simulations: 100-5000 (default: 1000)

---

## 💡 Examples & Use Cases

### Example 1: Analyze Indian Tech Stocks

```python
# Input: RELIANCE.NS,TCS.NS,INFY.NS
# Output:
# - Expected returns: RELIANCE (22%), TCS (18%), INFY (25%)
# - Risk: RELIANCE (28%), TCS (22%), INFY (30%)
# - Optimal allocation: RELIANCE (30%), TCS (40%), INFY (30%)
```

### Example 2: Risk vs Return Trade-off

The efficient frontier shows that:
- **Low Risk Portfolio**: 5% return, 10% volatility
- **Balanced Portfolio**: 15% return, 18% volatility
- **Aggressive Portfolio**: 25% return, 35% volatility

---

## 🎓 Mathematical Foundations

### 1. Value at Risk (VaR)

**Parametric VaR (Normal Distribution):**

$$\text{VaR}_\alpha = \mu + z_{1-\alpha} \cdot \sigma$$

Where:
- $z_{1-\alpha}$ = Z-score at confidence level
- For 95% confidence: $z = -1.645$

**Example:** If VaR at 95% = -2%, there's only 5% chance of losing more than 2%

### 2. Sharpe Ratio

$$\text{Sharpe Ratio} = \frac{R_p - R_f}{\sigma_p}$$

Where:
- $R_p$ = Portfolio return
- $R_f$ = Risk-free rate (2%)
- $\sigma_p$ = Portfolio volatility

Higher Sharpe Ratio = Better risk-adjusted returns

### 3. Geometric Brownian Motion

$$S_t = S_0 \exp\left[\left(\mu - \frac{\sigma^2}{2}\right)t + \sigma\sqrt{t}Z\right]$$

Where:
- Z ~ N(0,1) = Random normal variable
- Simulations show plausible future paths

---

## 🧪 Testing

Run the application with sample data:

```bash
# Start the server
python app.py

# In browser, enter:
# Symbols: RELIANCE.NS,TCS.NS,INFY.NS
# Investment: 100000
# Days: 252
# Simulations: 1000
```

---

## 📈 Performance Tips

1. **Reduce simulations** for faster analysis (use 500 instead of 1000)
2. **Limit stocks** to 5-7 for portfolio optimization
3. **Use 6 months data** instead of 1 year for faster processing
4. **Cache results** for repeated analyses

---

## ⚠️ Important Notes

1. **Past performance ≠ Future results** - Simulations based on historical volatility
2. **Assumes normal distribution** - Real returns may have fat tails
3. **No transaction costs** included - Add ~0.5% for realistic scenarios
4. **No maximum constraints** - May suggest >100% weighting in exotic scenarios
5. **Use for educational purposes** - Not investment advice

---

## 🔐 Security Considerations

- Run on localhost only for local development
- Never expose API keys if using real brokerage APIs
- Validate all user inputs
- Use HTTPS in production
- Implement rate limiting

---

## 📦 Dependencies

| Package | Purpose | Version |
|---------|---------|---------|
| Flask | Web framework | 2.3.3 |
| Pandas | Data manipulation | 2.0.3 |
| NumPy | Numerical computing | 1.24.3 |
| yfinance | Stock data API | 0.2.28 |
| SciPy | Scientific computing | 1.11.1 |
| Matplotlib | Data visualization | 3.7.2 |
| Plotly | Interactive charts | 5.15.0 |
| scikit-learn | Machine learning | 1.3.0 |
| PuLP | Linear programming | 2.7.0 |

---

## 🐛 Troubleshooting

### Issue: "No data found for symbol"
- Verify symbol format (e.g., `RELIANCE.NS` not `RELIANCE`)
- Check if market is open
- Stock might be delisted

### Issue: "Simulation takes too long"
- Reduce number of simulations
- Use fewer stocks
- Reduce prediction period

### Issue: "Module not found errors"
- Reinstall requirements: `pip install -r requirements.txt`
- Use virtual environment: `python -m venv venv`

---

## 📞 Support & Contributions

For issues, suggestions, or contributions:
1. Check existing solutions
2. Enable debug mode in `app.py`
3. Review console logs for errors

---

## 📝 License

Educational & Research Use

---

## 🎯 Learning Outcomes

After using this system, you'll understand:

✅ Statistical risk measurement (variance, std dev, VaR)
✅ Probability distributions and hypothesis testing
✅ Monte Carlo simulation techniques
✅ Portfolio optimization and linear programming
✅ Full-stack web development (Python, JavaScript, Flask)
✅ Data visualization and financial concepts

---

**Happy analyzing! 📊**
