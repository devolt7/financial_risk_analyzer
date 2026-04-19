"""
Portfolio Optimizer Module
Uses Linear Programming to optimize portfolio allocation
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize, LinearConstraint, Bounds
import warnings
warnings.filterwarnings('ignore')


class PortfolioOptimizer:
    """
    Optimizes portfolio allocation using linear programming and optimization techniques
    """
    
    def __init__(self):
        """Initialize the optimizer"""
        self.num_assets = None
        self.expected_returns = None
        self.covariance_matrix = None
        self.symbols = None
    
    def set_parameters(self, symbols, returns_dict):
        """
        Set portfolio parameters
        
        Args:
            symbols (list): List of stock symbols
            returns_dict (dict): Dictionary with returns for each symbol
        """
        self.symbols = symbols
        self.num_assets = len(symbols)
        
        # Calculate expected annual returns and covariance matrix
        returns_data = []
        
        for symbol in symbols:
            if symbol in returns_dict:
                # Annualize daily returns
                daily_return = returns_dict[symbol].mean()
                annual_return = daily_return * 252
                # Convert to float scalar to avoid Series issues
                annual_return = float(annual_return) if not (np.isnan(annual_return) or np.isinf(annual_return)) else 0.0
                returns_data.append(annual_return)
        
        self.expected_returns = np.array(returns_data)
        
        # Calculate correlation matrix between stocks
        returns_df = pd.DataFrame({
            symbol: returns_dict[symbol] 
            for symbol in symbols 
            if symbol in returns_dict
        })
        
        # Covariance matrix (annualized)
        cov_matrix = returns_df.cov() * 252
        
        # Replace NaN/Inf values in covariance matrix with 0 to prevent optimization errors
        cov_matrix = cov_matrix.fillna(0)
        cov_matrix = cov_matrix.replace([np.inf, -np.inf], 0)
        
        # Convert to numpy array to avoid Series ambiguity errors in optimization
        self.covariance_matrix = cov_matrix.values
    
    def optimize_risk_minimization(self):
        """
        Optimize portfolio to MINIMIZE RISK (variance) for a given return level
        
        Objective: Minimize portfolio variance
        Constraints:
            - Sum of weights = 1 (fully invested)
            - Each weight ≥ 0 (no short selling)
        
        Returns:
            dict: Optimal weights and portfolio statistics
        """
        def portfolio_variance(weights):
            """Calculate portfolio variance"""
            return np.dot(weights, np.dot(self.covariance_matrix, weights))
        
        # Initial guess: equal weights
        x0 = np.array([1.0 / self.num_assets] * self.num_assets)
        
        # Constraints: weights sum to 1
        constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
        
        # Bounds: 0 ≤ weight ≤ 1 (no short selling)
        bounds = tuple((0, 1) for _ in range(self.num_assets))
        
        # Optimize
        result = minimize(
            portfolio_variance,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if not result.success:
            print(f"Optimization warning: {result.message}")
        
        return self._compute_portfolio_stats(result.x, "Minimum Variance")
    
    def optimize_return_maximization(self, max_volatility=None):
        """
        Optimize portfolio to MAXIMIZE RETURN subject to risk constraint
        
        Objective: Maximize portfolio expected return
        Constraints:
            - Sum of weights = 1
            - Portfolio volatility ≤ max_volatility (if specified)
            - Each weight ≥ 0
        
        Args:
            max_volatility (float): Maximum allowed portfolio volatility
        
        Returns:
            dict: Optimal weights and portfolio statistics
        """
        def negative_return(weights):
            """We minimize negative return (= maximize positive return)"""
            return -np.dot(weights, self.expected_returns)
        
        def portfolio_volatility(weights):
            """Calculate portfolio volatility (std dev)"""
            return np.sqrt(np.dot(weights, np.dot(self.covariance_matrix, weights)))
        
        # Initial guess: equal weights
        x0 = np.array([1.0 / self.num_assets] * self.num_assets)
        
        # Constraints
        constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
        
        # Add volatility constraint if specified
        if max_volatility is not None:
            constraints.append({
                'type': 'ineq',
                'fun': lambda w: max_volatility - portfolio_volatility(w)
            })
        
        # Bounds
        bounds = tuple((0, 1) for _ in range(self.num_assets))
        
        # Optimize
        result = minimize(
            negative_return,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if not result.success:
            print(f"Optimization warning: {result.message}")
        
        return self._compute_portfolio_stats(result.x, "Maximum Return")
    
    def optimize_sharpe_ratio(self, risk_free_rate=0.02):
        """
        Optimize portfolio to MAXIMIZE SHARPE RATIO
        
        Sharpe Ratio = (Portfolio Return - Risk-Free Rate) / Portfolio Volatility
        
        This is the best risk-adjusted portfolio
        
        Args:
            risk_free_rate (float): Annual risk-free rate
        
        Returns:
            dict: Optimal weights and portfolio statistics
        """
        def negative_sharpe_ratio(weights):
            """Minimize negative Sharpe ratio (= maximize Sharpe ratio)"""
            p_return = np.dot(weights, self.expected_returns)
            p_volatility = np.sqrt(np.dot(weights, np.dot(self.covariance_matrix, weights)))
            
            if p_volatility == 0:
                return float('inf')
            
            return -(p_return - risk_free_rate) / p_volatility
        
        # Initial guess: equal weights
        x0 = np.array([1.0 / self.num_assets] * self.num_assets)
        
        # Constraints: weights sum to 1
        constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
        
        # Bounds: 0 ≤ weight ≤ 1
        bounds = tuple((0, 1) for _ in range(self.num_assets))
        
        # Optimize
        result = minimize(
            negative_sharpe_ratio,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if not result.success:
            print(f"Optimization warning: {result.message}")
        
        return self._compute_portfolio_stats(result.x, "Maximum Sharpe Ratio")
    
    def _compute_portfolio_stats(self, weights, strategy_name):
        """
        Calculate portfolio statistics for given weights
        
        Args:
            weights (np.array): Portfolio weights
            strategy_name (str): Name of optimization strategy
        
        Returns:
            dict: Portfolio statistics and allocation
        """
        # Expected portfolio return
        portfolio_return = np.dot(weights, self.expected_returns)
        
        # Portfolio variance and volatility
        portfolio_variance = np.dot(weights, np.dot(self.covariance_matrix, weights))
        portfolio_volatility = np.sqrt(portfolio_variance)
        
        # Build allocation dictionary
        allocation = {}
        for i, symbol in enumerate(self.symbols):
            allocation[symbol] = {
                'weight': float(weights[i]),
                'weight_percentage': float(weights[i] * 100)
            }
        
        result = {
            'strategy': strategy_name,
            'optimal_weights': weights.tolist(),
            'allocation': allocation,
            'expected_return': float(portfolio_return),
            'expected_return_percentage': float(portfolio_return * 100),
            'portfolio_variance': float(portfolio_variance),
            'portfolio_volatility': float(portfolio_volatility),
            'portfolio_volatility_percentage': float(portfolio_volatility * 100),
            'sharpe_ratio': float((portfolio_return - 0.02) / portfolio_volatility) if float(portfolio_volatility) > 0 else 0.0
        }
        
        return result
    
    def get_efficient_frontier(self, num_points=50):
        """
        Generate the efficient frontier (risk-return trade-off)
        
        Returns a set of optimal portfolios for different risk levels
        
        Args:
            num_points (int): Number of points on the frontier
        
        Returns:
            list: Points on the efficient frontier
        """
        
        # Find minimum and maximum volatility
        min_vol_portfolio = self.optimize_risk_minimization()
        min_volatility = min_vol_portfolio['portfolio_volatility']
        
        # For max volatility, try equally weighted portfolio
        equal_weights = np.array([1.0 / self.num_assets] * self.num_assets)
        equal_vol = np.sqrt(np.dot(equal_weights, np.dot(self.covariance_matrix, equal_weights)))
        max_volatility = equal_vol * 1.5
        
        frontier = []
        volatilities = np.linspace(min_volatility, max_volatility, num_points)
        
        for target_vol in volatilities:
            portfolio = self.optimize_return_maximization(max_volatility=target_vol)
            frontier.append({
                'volatility': portfolio['portfolio_volatility'],
                'return': portfolio['expected_return'],
                'return_percentage': portfolio['expected_return_percentage'],
                'volatility_percentage': portfolio['portfolio_volatility_percentage']
            })
        
        return frontier
    
    def compare_strategies(self):
        """
        Compare different optimization strategies
        
        Returns:
            dict: Comparison of all strategies
        """
        strategies = {
            'Min Variance': self.optimize_risk_minimization(),
            'Max Sharpe Ratio': self.optimize_sharpe_ratio(),
            'Max Return': self.optimize_return_maximization(),
            'Equal Weight': self._equal_weight_portfolio()
        }
        
        return strategies
    
    def _equal_weight_portfolio(self):
        """Calculate statistics for equal weight portfolio"""
        weights = np.array([1.0 / self.num_assets] * self.num_assets)
        return self._compute_portfolio_stats(weights, "Equal Weight")
