"""
Financial Risk Analyzer - Flask Backend
Main application file that handles API endpoints and orchestrates analysis
"""

from flask import Flask, request, jsonify, render_template
import json
import traceback
from datetime import datetime
import numpy as np

# Helper function to convert NaN/Inf to None (null in JSON)
def convert_to_json_serializable(obj):
    """Recursively convert NaN, Inf, and numpy types to JSON-serializable values"""
    if isinstance(obj, dict):
        return {k: convert_to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_json_serializable(item) for item in obj]
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.generic):
        return float(obj.item())
    elif isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return None  # Convert NaN/Inf to None which becomes null in JSON
        return obj
    elif isinstance(obj, (np.integer, np.floating)):
        return float(obj)
    elif isinstance(obj, bool):
        return bool(obj)
    return obj


# Custom JSON Encoder to handle NaN and Inf values
class NaNEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles NaN, Inf, and -Inf"""
    def default(self, obj):
        """Handle numpy types and special float values"""
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        if isinstance(obj, float):
            if np.isnan(obj) or np.isinf(obj):
                return None  # Return None for NaN/Inf which becomes null in JSON
        return super(NaNEncoder, self).default(obj)


# Import utility modules
from utils.data_handler import DataHandler
from utils.statistical_analysis import StatisticalAnalyzer
from utils.monte_carlo import MonteCarloSimulator
from utils.portfolio_optimizer import PortfolioOptimizer

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['REQUEST_TIMEOUT'] = 60  # 60 second timeout for Vercel
app.config['PROPAGATE_EXCEPTIONS'] = True

# Override Flask's JSON encoder to handle NaN values
def configure_json_encoder():
    """Configure Flask to use our NaN-aware JSON encoder"""
    from flask.json.provider import DefaultJSONProvider
    
    class NaNAwareJSONProvider(DefaultJSONProvider):
        def default(self, o):
            if isinstance(o, np.ndarray):
                return o.tolist()
            if isinstance(o, (np.integer, np.floating)):
                return float(o)
            if isinstance(o, float):
                if np.isnan(o) or np.isinf(o):
                    return None
            if isinstance(o, (np.bool_)):
                return bool(o)
            return super().default(o)
    
    app.json = NaNAwareJSONProvider(app)

try:
    configure_json_encoder()
except:
    # Fallback for older Flask versions
    app.json_encoder = NaNEncoder

# Override jsonify to ensure NaN handling
_original_jsonify = jsonify
def safe_jsonify(*args, **kwargs):
    return _original_jsonify(convert_to_json_serializable(args[0] if args else kwargs))

# Global objects for analysis
data_handler = DataHandler(period='1y')
stats_analyzer = StatisticalAnalyzer()
mc_simulator = MonteCarloSimulator()
portfolio_optimizer = PortfolioOptimizer()


@app.route('/')
def index():
    """Render the main HTML page"""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Main API endpoint for financial risk analysis
    
    Expected JSON input:
    {
        "symbols": ["RELIANCE.NS", "TCS.NS"],
        "investment_amount": 100000,
        "days_ahead": 252,
        "num_simulations": 500
    }
    
    Returns: Comprehensive analysis with all metrics and visualizations
    """
    try:
        # Get input data
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Invalid request body'}), 400
            
        symbols_str = data.get('symbols', '').strip()
        investment_amount = float(data.get('investment_amount', 100000))
        days_ahead = int(data.get('days_ahead', 252))
        num_simulations = int(data.get('num_simulations', 500))  # Reduced from 1000 for speed
        
        # Cap simulations for performance
        if num_simulations > 2000:
            num_simulations = 2000
        if num_simulations < 100:
            num_simulations = 100
        
        # Parse and validate symbols
        symbols = [s.strip().upper() for s in symbols_str.split(',') if s.strip()]
        
        if not symbols:
            return jsonify({'success': False, 'error': 'Please provide at least one stock symbol'}), 400
        
        if len(symbols) > 10:
            return jsonify({'success': False, 'error': 'Maximum 10 stocks allowed for analysis'}), 400
        
        print(f"\n{'='*60}")
        print(f"Starting analysis for: {symbols}")
        print(f"Simulations: {num_simulations}, Days: {days_ahead}")
        print(f"{'='*60}\n")
        
        # Step 1: Validate symbols and fetch data
        print("Step 1: Validating symbols and fetching data...")
        stock_data = data_handler.fetch_stock_data(symbols)
        
        if not stock_data:
            return jsonify({'success': False, 'error': 'Could not fetch data for any symbols'}), 400
        
        valid_symbols = list(stock_data.keys())
        
        # Step 2: Calculate returns
        print("Step 2: Calculating daily returns...")
        returns_data = data_handler.calculate_returns(valid_symbols)
        
        # Step 3: Statistical Analysis
        print("Step 3: Performing statistical analysis...")
        stock_stats = {}
        current_prices = {}
        returns_dict = {}
        
        for symbol in valid_symbols:
            if symbol in returns_data:
                # Get current price (last closing price) - handle both Series and DataFrame
                try:
                    price_data = stock_data[symbol]['Close'].iloc[-1]
                    # If it's a Series, get the scalar value; if scalar, use as-is
                    if hasattr(price_data, 'item'):
                        current_prices[symbol] = float(price_data.item())
                    else:
                        current_prices[symbol] = float(price_data)
                except (TypeError, AttributeError):
                    # Fallback if extraction fails
                    current_prices[symbol] = float(stock_data[symbol]['Close'].values[-1])
                
                # Calculate statistics
                returns_series = returns_data[symbol]
                returns_dict[symbol] = returns_series
                
                # Basic statistics
                basic_stats = stats_analyzer.calculate_basic_statistics(returns_series)
                
                # Normal distribution fit
                normal_dist = stats_analyzer.fit_normal_distribution(returns_series)
                
                # Value at Risk (95% confidence)
                var_metrics = stats_analyzer.calculate_var(returns_series, confidence=0.95)
                
                # Sharpe Ratio
                sharpe_ratio = stats_analyzer.calculate_sharpe_ratio(returns_series)
                
                # Risk Classification
                risk_level, risk_description = stats_analyzer.classify_risk(basic_stats['std_dev_daily'])
                
                # Distribution data for histogram
                dist_histogram = stats_analyzer.get_distribution_data(returns_series)
                
                stock_stats[symbol] = {
                    'current_price': current_prices[symbol],
                    'basic_statistics': {
                        'expected_daily_return': float(basic_stats['mean_daily']),
                        'expected_annual_return': float(basic_stats['mean_annual']),
                        'daily_volatility': float(basic_stats['std_dev_daily']),
                        'annual_volatility': float(basic_stats['std_dev_annual']),
                        'variance_annual': float(basic_stats['variance_annual']),
                        'min_return': float(basic_stats['min_return']),
                        'max_return': float(basic_stats['max_return']),
                        'median': float(basic_stats['median']),
                        'skewness': float(basic_stats['skewness']),
                        'kurtosis': float(basic_stats['kurtosis'])
                    },
                    'normal_distribution': {
                        'mu': float(normal_dist['mu']),
                        'sigma': float(normal_dist['sigma']),
                        'is_normal': bool(normal_dist['is_normal'])
                    },
                    'risk_metrics': {
                        'var_daily_parametric': float(var_metrics['var_daily_parametric']),
                        'var_annual': float(var_metrics['var_annual']),
                        'cvar_daily': float(var_metrics['cvar_daily']),
                        'sharpe_ratio': float(sharpe_ratio),
                        'risk_level': risk_level,
                        'risk_description': risk_description
                    },
                    'distribution': dist_histogram
                }
        
        # Step 4: Monte Carlo Simulation
        print("Step 4: Running Monte Carlo simulation...")
        mc_simulator.simulate_paths(
            current_prices,
            {s: {'mean_daily': stock_stats[s]['basic_statistics']['expected_daily_return'],
                 'std_dev_daily': stock_stats[s]['basic_statistics']['daily_volatility']}
             for s in valid_symbols},
            days_ahead=days_ahead,
            num_simulations=num_simulations
        )
        
        # Get simulation statistics
        simulation_stats = mc_simulator.get_simulation_statistics(num_simulations)
        price_corridor = mc_simulator.get_price_corridor()
        sample_paths = mc_simulator.get_sample_paths(num_paths_to_plot=100)
        
        # Step 5: Portfolio Optimization
        print("Step 5: Optimizing portfolio allocation...")
        portfolio_optimizer.set_parameters(valid_symbols, returns_dict)
        
        # Get all optimization strategies
        portf_strategies = portfolio_optimizer.compare_strategies()
        
        # Get efficient frontier
        efficient_frontier = portfolio_optimizer.get_efficient_frontier(num_points=50)
        
        # Step 6: Compile results
        print("Step 6: Compiling results...")
        analysis_result = {
            'timestamp': datetime.now().isoformat(),
            'symbols': valid_symbols,
            'num_symbols': len(valid_symbols),
            'investment_amount': investment_amount,
            'analysis_period': f"{days_ahead} days",
            'num_simulations': num_simulations,
            'stock_analysis': stock_stats,
            'monte_carlo': {
                'statistics': simulation_stats,
                'price_corridors': price_corridor,
                'sample_paths': sample_paths
            },
            'portfolio_optimization': {
                'strategies': portf_strategies,
                'efficient_frontier': efficient_frontier
            },
            'success': True
        }
        
        print(f"✓ Analysis completed successfully!")
        print(f"{'='*60}\n")
        
        # Convert NaN/Inf values to JSON-serializable format
        clean_result = convert_to_json_serializable(analysis_result)
        return _original_jsonify(clean_result)
    
    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        print(traceback.format_exc())
        # Always return JSON, even on error
        try:
            error_response = {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc() if app.debug else None
            }
            return jsonify(error_response), 500
        except:
            # Ultimate fallback - return minimal JSON
            return jsonify({'success': False, 'error': 'Internal server error'}), 500


@app.route('/api/get-stock-list', methods=['GET'])
def get_stock_list():
    """Get list of popular stocks for dropdown menu"""
    try:
        # Popular Indian and US stocks
        stocks = {
            'Indian Stocks': [
                {'symbol': 'RELIANCE.NS', 'name': 'Reliance Industries'},
                {'symbol': 'TCS.NS', 'name': 'Tata Consultancy Services'},
                {'symbol': 'INFY.NS', 'name': 'Infosys'},
                {'symbol': 'HDFCBANK.NS', 'name': 'HDFC Bank'},
                {'symbol': 'SBIN.NS', 'name': 'State Bank of India'},
                {'symbol': 'WIPRO.NS', 'name': 'Wipro'},
                {'symbol': 'LT.NS', 'name': 'Larsen & Toubro'},
                {'symbol': 'MARUTI.NS', 'name': 'Maruti Suzuki'},
                {'symbol': 'BAJAJ-AUTO.NS', 'name': 'Bajaj Auto'},
                {'symbol': 'ICICIBANK.NS', 'name': 'ICICI Bank'},
                {'symbol': 'BHARTIARTL.NS', 'name': 'Bharti Airtel'},
                {'symbol': 'KOTAKBANK.NS', 'name': 'Kotak Mahindra Bank'},
                {'symbol': 'ADANIPORTS.NS', 'name': 'Adani Ports'},
                {'symbol': 'POWERGRID.NS', 'name': 'Power Grid'},
                {'symbol': 'JSWSTEEL.NS', 'name': 'JSW Steel'},
            ],
            'US Stocks': [
                {'symbol': 'AAPL', 'name': 'Apple Inc.'},
                {'symbol': 'MSFT', 'name': 'Microsoft Corporation'},
                {'symbol': 'GOOGL', 'name': 'Alphabet Inc.'},
                {'symbol': 'AMZN', 'name': 'Amazon.com Inc.'},
                {'symbol': 'TESLA', 'name': 'Tesla Inc.'},
                {'symbol': 'META', 'name': 'Meta Platforms'},
                {'symbol': 'NVDA', 'name': 'NVIDIA Corporation'},
                {'symbol': 'JPM', 'name': 'JPMorgan Chase'},
                {'symbol': 'V', 'name': 'Visa Inc.'},
                {'symbol': 'JNJ', 'name': 'Johnson & Johnson'},
                {'symbol': 'PG', 'name': 'Procter & Gamble'},
                {'symbol': 'DIS', 'name': 'The Walt Disney Company'},
                {'symbol': 'BA', 'name': 'Boeing'},
                {'symbol': 'INTC', 'name': 'Intel Corporation'},
                {'symbol': 'AMD', 'name': 'Advanced Micro Devices'},
            ]
        }
        return jsonify(stocks), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/validate-symbols', methods=['POST'])
def validate_symbols():
    """
    Validate stock symbols before full analysis
    
    Returns: List of valid and invalid symbols
    """
    try:
        data = request.get_json()
        symbols_str = data.get('symbols', '').strip()
        
        symbols = [s.strip().upper() for s in symbols_str.split(',') if s.strip()]
        
        if not symbols:
            return jsonify({'valid': [], 'invalid': []})
        
        valid, invalid = data_handler.validate_symbols(symbols)
        
        return jsonify({
            'valid': valid,
            'invalid': invalid,
            'valid_count': len(valid),
            'invalid_count': len(invalid)
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'valid': [],
            'invalid': []
        }), 500


@app.route('/api/stock-info', methods=['POST'])
def get_stock_info():
    """Get basic information about a stock"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').strip().upper()
        
        if not symbol:
            return jsonify({'error': 'Symbol required'}), 400
        
        info = data_handler.get_stock_info(symbol)
        clean_info = convert_to_json_serializable(info)
        return _original_jsonify(clean_info)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'app': 'Financial Risk Analyzer',
        'timestamp': datetime.now().isoformat()
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Financial Risk Analyzer - Starting Server")
    print("="*60)
    print("Server running at: http://localhost:5000")
    print("Dashboard: http://localhost:5000/")
    print("="*60 + "\n")
    
    # Run Flask app in debug mode (change to False in production)
    app.run(debug=True, host='0.0.0.0', port=5000)
