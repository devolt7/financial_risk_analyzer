# 🚀 Quick Start Guide

## Installation (60 seconds)

### Windows
```bash
# 1. Open Command Prompt in the project folder
cd financial_risk_analyzer

# 2. Run setup (creates virtual environment + installs packages)
setup.bat

# 3. Run the application
run.bat

# 4. Open browser to http://localhost:5000
```

### macOS / Linux
```bash
# 1. Navigate to project folder
cd financial_risk_analyzer

# 2. Make scripts executable
chmod +x setup.sh run.sh

# 3. Run setup
./setup.sh

# 4. Run the application
./run.sh

# 5. Open http://localhost:5000 in browser
```

## Manual Installation (if scripts don't work)

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run Flask app
python app.py
```

---

## First Time Usage

### Step 1: Add Stock Symbols
In the left panel, enter stock symbols separated by commas:
```
RELIANCE.NS, TCS.NS, INFY.NS
```

**Stock Symbol Formats:**
- Indian stocks: `RELIANCE.NS`, `TCS.NS`, `WIPRO.NS`
- US stocks: `AAPL`, `MSFT`, `GOOGL`
- Other: Use full ticker with exchange code

### Step 2: Click "Validate Symbols"
This checks if symbols are correct before running analysis.

### Step 3: Adjust Parameters (Optional)
- **Investment Amount**: Starting capital (default: $100,000)
- **Days to Simulate**: Prediction period (default: 252 = 1 year)
- **Monte Carlo Simulations**: Number of simulated paths (default: 1000)

### Step 4: Click "Analyze Risk"
Wait for analysis to complete (usually 5-30 seconds).

### Step 5: Review Results
- **Statistics**: Mean, volatility, Sharpe ratio
- **Risk Metrics**: VaR, CVaR, risk classification
- **Charts**: Price trends, distributions, simulations
- **Optimization**: Recommended portfolio allocations

---

## Understanding the Output

### Statistics Panel
| Metric | What It Means |
|--------|---------------|
| Expected Annual Return | Average yearly profit potential |
| Annual Volatility | How much returns fluctuate (risk) |
| Sharpe Ratio | Risk-adjusted return (higher is better) |
| Skewness | Whether large gains/losses are more likely |

### Risk Assessment
| Level | Volatility | Meaning |
|-------|-----------|---------|
| **Low** | < 10% | Conservative, stable returns |
| **Medium** | 10-20% | Moderate risk, balanced |
| **High** | > 20% | Aggressive, volatile |

### Monte Carlo Chart
- **Red line**: Worst-case scenario
- **Blue line**: Expected outcome
- **Green line**: Best-case scenario
- **Shaded area**: 90% confidence band

### Portfolio Optimization
- **Minimum Variance**: Lowest risk allocation
- **Max Sharpe Ratio**: Best risk-adjusted returns (RECOMMENDED)
- **Maximum Return**: Highest expected return (risky)
- **Equal Weight**: Simple 1/N distribution

---

## Common Tasks

### Analyze Single Stock
Just enter one symbol:
```
RELIANCE.NS
```

### Compare Two Stocks
```
AAPL, MSFT
```

### Find Best Allocation for 5 Stocks
```
RELIANCE.NS, TCS.NS, INFY.NS, WIPRO.NS, SBIN.NS
```
Then look at "Max Sharpe Ratio" portfolio (best risk-adjusted).

### Test Different Time Periods
- 1 month prediction: Set "Days to Simulate" = 21
- 3 months: 63
- 6 months: 126
- 1 year: 252
- 2 years: 504

### Adjust Risk Tolerance
- **Conservative**: Use "Minimum Variance" allocation
- **Balanced**: Use "Max Sharpe Ratio" allocation
- **Aggressive**: Use "Maximum Return" allocation

---

## Troubleshooting

### "No data found for symbol"
- ❌ Wrong format: `RELIANCE` (missing exchange)
- ✅ Correct format: `RELIANCE.NS`

Check [list of supported symbols](https://finance.yahoo.com/lookup)

### Browser shows "Cannot connect"
- Check if Flask is running (should see message in terminal)
- Try: http://localhost:5000
- If stuck, restart with: `Ctrl+C` then run again

### Simulations running slowly
- Reduce simulations: use 500 instead of 1000
- Reduce days: use 126 instead of 252
- Use fewer stocks: analyze 2-3 instead of 5

### "ModuleNotFoundError: No module named 'flask'"
```bash
# Reinstall packages
pip install -r requirements.txt

# Or manually install Flask
pip install Flask pandas numpy yfinance scipy matplotlib plotly
```

---

## Example Analyses

### Analysis 1: Beginner
**Goal**: Understand basic stock metrics

```
Symbols: INFY.NS
Investment: 50000
Days: 252
Simulations: 500

Output: Individual stock risk/return profile
```

### Analysis 2: Intermediate
**Goal**: Compare two tech stocks

```
Symbols: TCS.NS, INFY.NS
Investment: 100000
Days: 252
Simulations: 1000

Output: Which has better risk-adjusted returns?
```

### Analysis 3: Advanced
**Goal**: Build optimal portfolio from 5 stocks

```
Symbols: RELIANCE.NS, TCS.NS, INFY.NS, WIPRO.NS, SBIN.NS
Investment: 500000
Days: 504
Simulations: 1000

Output: Recommended allocation % for each stock
```

---

## Tips for Best Results

✅ **Use 1 year of data**: More historical context = better accuracy
✅ **Include 3-5 stocks**: Enough diversity, but not too many
✅ **Run 1000+ simulations**: Better statistical reliability
✅ **Use Max Sharpe Ratio**: Balances risk and return
✅ **Validate symbols first**: Catch errors before full analysis

❌ **Don't use too many stocks**: > 10 becomes slow
❌ **Don't assume past = future**: Markets change constantly
❌ **Don't ignore transaction costs**: Add ~0.5% to real trades
❌ **Don't trade on recommendation alone**: Do your own research!

---

## Understanding Monte Carlo Results

### Interpretation Example
```
Initial Price: $100
Mean Final: $115
Best Case: $145 (+45%)
Worst Case: $88 (-12%)
Probability of Profit: 72%
```

**Means:**
- Stock expected to reach $115 in 1 year (average)
- Best scenario: $145 profit
- Worst scenario: $12 loss
- 72% chance of making profit

---

## API Usage (Advanced)

Use the REST API for programmatic access:

```python
import requests
import json

url = "http://localhost:5000/api/analyze"

data = {
    "symbols": "RELIANCE.NS,TCS.NS",
    "investment_amount": 100000,
    "days_ahead": 252,
    "num_simulations": 1000
}

response = requests.post(url, json=data)
results = response.json()

print(f"Expected Return: {results['portfolio_optimization']['strategies']['Max Sharpe Ratio']['expected_return_percentage']}%")
```

---

## Performance Notes

| Parameter | Affects | Speed |
|-----------|---------|-------|
| Number of stocks | Analysis time | Slow with > 5 |
| Days ahead | Calculation | Minimal impact |
| Simulations | MC accuracy | Big impact |

**Typical Times:**
- 1-2 stocks, 1000 sims: 5-10 seconds
- 3-4 stocks, 1000 sims: 10-20 seconds
- 5+ stocks, slow computer: 30+ seconds

---

## Next Steps

1. **Try different stock combinations**
2. **Compare with market indices** (use ^NSEI for India, ^GSPC for S&P500)
3. **Test different time horizons** (3 months, 6 months, 1 year)
4. **Study the mathematics** in `utils/` modules
5. **Customize the code** for your needs

---

## Resources

📚 **Learn More:**
- [Modern Portfolio Theory](https://en.wikipedia.org/wiki/Modern_portfolio_theory)
- [Monte Carlo Simulation](https://en.wikipedia.org/wiki/Monte_Carlo_method)
- [Value at Risk](https://en.wikipedia.org/wiki/Value_at_risk)
- [Statistical Analysis](https://en.wikipedia.org/wiki/Statistical_inference)

🔗 **Data Source:**
- [Yahoo Finance API](https://finance.yahoo.com)
- [Stock Symbol Lookup](https://finance.yahoo.com/lookup)

---

**Happy analyzing! 📊**

For detailed documentation, see `README.md`
