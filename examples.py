"""
Example Usage - Financial Risk Analyzer
Demonstrates how to use the system programmatically
"""

# ==============================================================
# EXAMPLE 1: Basic Statistical Analysis
# ==============================================================

from utils.data_handler import DataHandler
from utils.statistical_analysis import StatisticalAnalyzer

# Initialize
handler = DataHandler(period='1y')
analyzer = StatisticalAnalyzer()

# Fetch data for stocks
symbols = ['RELIANCE.NS', 'TCS.NS']
stock_data = handler.fetch_stock_data(symbols)

# Calculate returns
returns_data = handler.calculate_returns(symbols)

# Analyze RELIANCE stock
reliance_returns = returns_data['RELIANCE.NS']

# Calculate statistics
stats = analyzer.calculate_basic_statistics(reliance_returns)
print(f"RELIANCE Expected Annual Return: {stats['mean_annual']*100:.2f}%")
print(f"RELIANCE Annual Volatility: {stats['std_dev_annual']*100:.2f}%")

# Fit to normal distribution
normal_dist = analyzer.fit_normal_distribution(reliance_returns)
print(f"Normal Distribution - μ={normal_dist['mu']:.4f}, σ={normal_dist['sigma']:.4f}")

# Calculate Value at Risk
var = analyzer.calculate_var(reliance_returns, confidence=0.95)
print(f"VaR (95%): {var['var_daily_parametric']*100:.2f}%")
print(f"VaR Annual: {var['var_annual']*100:.2f}%")

# Calculate Sharpe Ratio
sharpe = analyzer.calculate_sharpe_ratio(reliance_returns)
print(f"Sharpe Ratio: {sharpe:.3f}")


# ==============================================================
# EXAMPLE 2: Monte Carlo Simulation
# ==============================================================

from utils.monte_carlo import MonteCarloSimulator

# Initialize simulator
simulator = MonteCarloSimulator()

# Prepare current prices and statistics
current_prices = {
    'RELIANCE.NS': stock_data['RELIANCE.NS']['Close'].iloc[-1],
    'TCS.NS': stock_data['TCS.NS']['Close'].iloc[-1]
}

returns_stats = {}
for symbol in symbols:
    stats = analyzer.calculate_basic_statistics(returns_data[symbol])
    returns_stats[symbol] = {
        'mean_daily': stats['mean_daily'],
        'std_dev_daily': stats['std_dev_daily']
    }

# Run simulations
paths = simulator.simulate_paths(
    current_prices=current_prices,
    returns_stats=returns_stats,
    days_ahead=252,
    num_simulations=1000
)

# Get statistics
sim_stats = simulator.get_simulation_statistics(1000)

for symbol, stats in sim_stats.items():
    print(f"\n{symbol} - Monte Carlo Results:")
    print(f"  Initial Price: ${stats['initial_price']:.2f}")
    print(f"  Mean Final Price: ${stats['mean_final_price']:.2f}")
    print(f"  Best Case: ${stats['best_case']:.2f}")
    print(f"  Worst Case: ${stats['worst_case']:.2f}")
    print(f"  Probability of Profit: {stats['prob_profit']:.1f}%")


# ==============================================================
# EXAMPLE 3: Portfolio Optimization
# ==============================================================

from utils.portfolio_optimizer import PortfolioOptimizer

# Initialize optimizer
optimizer = PortfolioOptimizer()

# Set parameters
optimizer.set_parameters(symbols, returns_data)

# Get different optimization strategies
min_var = optimizer.optimize_risk_minimization()
sharpe_max = optimizer.optimize_sharpe_ratio()
max_return = optimizer.optimize_return_maximization()

print("\n=== PORTFOLIO OPTIMIZATION RESULTS ===\n")

print("1. MINIMUM VARIANCE PORTFOLIO")
print(f"   Expected Return: {min_var['expected_return_percentage']:.2f}%")
print(f"   Volatility: {min_var['portfolio_volatility_percentage']:.2f}%")
print("   Allocation:")
for symbol, alloc in min_var['allocation'].items():
    print(f"     {symbol}: {alloc['weight_percentage']:.2f}%")

print("\n2. MAXIMUM SHARPE RATIO PORTFOLIO")
print(f"   Expected Return: {sharpe_max['expected_return_percentage']:.2f}%")
print(f"   Volatility: {sharpe_max['portfolio_volatility_percentage']:.2f}%")
print(f"   Sharpe Ratio: {sharpe_max['sharpe_ratio']:.4f}")
print("   Allocation:")
for symbol, alloc in sharpe_max['allocation'].items():
    print(f"     {symbol}: {alloc['weight_percentage']:.2f}%")

print("\n3. MAXIMUM RETURN PORTFOLIO")
print(f"   Expected Return: {max_return['expected_return_percentage']:.2f}%")
print(f"   Volatility: {max_return['portfolio_volatility_percentage']:.2f}%")
print("   Allocation:")
for symbol, alloc in max_return['allocation'].items():
    print(f"     {symbol}: {alloc['weight_percentage']:.2f}%")

# Get efficient frontier
frontier = optimizer.get_efficient_frontier(num_points=20)
print("\n=== EFFICIENT FRONTIER ===")
print("Volatility (%) | Return (%)")
for point in frontier:
    print(f"{point['volatility_percentage']:6.2f}      | {point['return_percentage']:6.2f}")


# ==============================================================
# EXAMPLE 4: Risk Classification
# ==============================================================

print("\n=== RISK ASSESSMENT ===\n")

for symbol in symbols:
    stats = analyzer.calculate_basic_statistics(returns_data[symbol])
    risk_level, risk_desc = analyzer.classify_risk(stats['std_dev_daily'])
    
    print(f"{symbol}:")
    print(f"  Risk Level: {risk_level}")
    print(f"  {risk_desc}")


# ==============================================================
# EXAMPLE 5: Symbol Validation
# ==============================================================

print("\n=== SYMBOL VALIDATION ===\n")

test_symbols = ['RELIANCE.NS', 'TCS.NS', 'INVALID.NS', 'AAPL']
valid, invalid = handler.validate_symbols(test_symbols)

print(f"Valid Symbols: {valid}")
print(f"Invalid Symbols: {invalid}")


# ==============================================================
# EXAMPLE 6: Stock Information
# ==============================================================

print("\n=== STOCK INFORMATION ===\n")

for symbol in ['RELIANCE.NS', 'TCS.NS']:
    info = handler.get_stock_info(symbol)
    print(f"{symbol}:")
    print(f"  Name: {info['name']}")
    print(f"  Sector: {info['sector']}")
    print(f"  Current Price: ${info['current_price']}")


print("\n" + "="*50)
print("Examples completed! Check output above.")
print("="*50)
