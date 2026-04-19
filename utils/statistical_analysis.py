"""
Statistical Analysis Module
Implements various statistical and risk metrics
"""

import numpy as np
import pandas as pd
from scipy import stats


class StatisticalAnalyzer:
    """
    Performs statistical analysis on stock returns and calculates risk metrics
    """
    
    def __init__(self):
        """Initialize the analyzer"""
        self.stats = {}
        self.confidence_level = 0.95  # 95% for VaR
    
    def calculate_basic_statistics(self, returns):
        """
        Calculate fundamental statistical measures
        
        Args:
            returns (pd.Series): Series of daily returns
            
        Returns:
            dict: Dictionary containing mean, variance, std_dev
        """
        # Expected Return (Mean of daily returns, annualized)
        mean_daily = returns.mean()
        mean_annual = mean_daily * 252  # 252 trading days per year
        
        # Variance (measure of volatility)
        variance_daily = returns.var()
        variance_annual = variance_daily * 252
        
        # Standard Deviation (Risk measurement - how much returns deviate)
        std_dev_daily = returns.std()
        std_dev_annual = std_dev_daily * np.sqrt(252)
        
        # Handle NaN/Inf values
        def safe_float(val):
            if val is None or np.isnan(val) or np.isinf(val):
                return 0.0
            return float(val)
        
        stats_dict = {
            'mean_daily': safe_float(mean_daily),
            'mean_annual': safe_float(mean_annual),
            'variance_daily': safe_float(variance_daily),
            'variance_annual': safe_float(variance_annual),
            'std_dev_daily': safe_float(std_dev_daily),
            'std_dev_annual': safe_float(std_dev_annual),
            'min_return': safe_float(returns.min()),
            'max_return': safe_float(returns.max()),
            'median': safe_float(returns.median()),
            'skewness': safe_float(returns.skew()),  # Asymmetry of distribution
            'kurtosis': safe_float(returns.kurtosis())  # Tail heaviness
        }
        
        return stats_dict
    
    def fit_normal_distribution(self, returns):
        """
        Fit returns data to a normal distribution and calculate parameters
        
        Returns should approximately follow N(μ, σ²) distribution
        
        Args:
            returns (pd.Series): Series of daily returns
            
        Returns:
            dict: Normal distribution parameters
        """
        # Fit normal distribution
        mu, sigma = stats.norm.fit(returns)
        
        # Perform normality test (Shapiro-Wilk test)
        if len(returns) > 5000:
            # For large samples, use Anderson-Darling
            statistic, critical_values, significance_level = stats.anderson(returns)
            normal_test_p_value = None
        else:
            # Shapiro-Wilk test
            statistic, p_value = stats.shapiro(returns)
            normal_test_p_value = p_value
        
        normal_dist = {
            'mu': mu,
            'sigma': sigma,
            'normality_test_p_value': normal_test_p_value,
            'is_normal': normal_test_p_value > 0.05 if normal_test_p_value else True
        }
        
        return normal_dist
    
    def calculate_var(self, returns, confidence=0.95):
        """
        Calculate Value at Risk (VaR)
        
        VaR is the maximum loss expected with a given confidence level
        VaR at 95% means: there's 5% chance of losing more than VaR amount
        
        Args:
            returns (pd.Series): Series of daily returns
            confidence (float): Confidence level (default: 0.95 for 95%)
            
        Returns:
            dict: VaR metrics
        """
        # Historical VaR (non-parametric)
        var_historical = np.percentile(returns, (1 - confidence) * 100)
        
        # Parametric VaR (using normal distribution)
        mu = returns.mean()
        sigma = returns.std()
        z_score = stats.norm.ppf(1 - confidence)
        var_parametric = mu + (z_score * sigma)
        
        # Conditional VaR (CVaR) - average of losses beyond VaR
        losses = returns[returns <= var_historical]
        cvar = losses.mean() if len(losses) > 0 else var_historical
        
        # Annualized VaR (for daily returns)
        var_annual = var_parametric * np.sqrt(252)
        
        # Handle NaN values
        cvar = float(cvar) if not (np.isnan(cvar) or np.isinf(cvar)) else 0.0
        var_annual = float(var_annual) if not (np.isnan(var_annual) or np.isinf(var_annual)) else 0.0
        
        var_metrics = {
            'var_daily_historical': float(var_historical),
            'var_daily_parametric': float(var_parametric),
            'var_annual': var_annual,
            'cvar_daily': cvar,
            'confidence_level': confidence
        }
        
        return var_metrics
    
    def calculate_sharpe_ratio(self, returns, risk_free_rate=0.02):
        """
        Calculate Sharpe Ratio (risk-adjusted return metric)
        
        Sharpe Ratio = (Return - Risk-Free Rate) / Volatility
        Higher is better
        
        Args:
            returns (pd.Series): Series of daily returns
            risk_free_rate (float): Annual risk-free rate (default: 2%)
            
        Returns:
            float: Sharpe Ratio
        """
        annual_return = returns.mean() * 252
        annual_volatility = returns.std() * np.sqrt(252)
        
        # Avoid division by zero
        if annual_volatility == 0 or np.isclose(annual_volatility, 0):
            return 0.0
        
        sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility
        
        # Handle NaN/Inf values
        if np.isnan(sharpe_ratio) or np.isinf(sharpe_ratio):
            return 0.0
        
        return float(sharpe_ratio)
    
    def classify_risk(self, std_dev):
        """
        Classify risk level based on standard deviation
        
        Args:
            std_dev (float): Standard deviation of returns
            
        Returns:
            tuple: (risk_level, description)
        """
        # Annualized volatility
        annual_vol = std_dev * np.sqrt(252)
        
        if annual_vol < 0.10:
            return "Low Risk", f"Volatility: {annual_vol*100:.2f}%"
        elif annual_vol < 0.20:
            return "Medium Risk", f"Volatility: {annual_vol*100:.2f}%"
        else:
            return "High Risk", f"Volatility: {annual_vol*100:.2f}%"
    
    def get_distribution_data(self, returns, bins=50):
        """
        Get histogram data for visualization
        
        Args:
            returns (pd.Series): Series of daily returns
            bins (int): Number of bins for histogram
            
        Returns:
            dict: Histogram data and statistics
        """
        counts, bin_edges = np.histogram(returns, bins=bins)
        
        # Generate normal distribution curve
        mu = returns.mean()
        sigma = returns.std()
        
        # Handle edge case where sigma is 0
        if sigma == 0 or np.isclose(sigma, 0):
            sigma = 0.001  # Use small value to avoid division issues
        
        x = np.linspace(returns.min(), returns.max(), 100)
        normal_curve = stats.norm.pdf(x, mu, sigma)
        
        # Replace NaN/Inf with 0
        normal_curve = np.where(np.isnan(normal_curve) | np.isinf(normal_curve), 0, normal_curve)
        
        dist_data = {
            'counts': counts.tolist(),
            'bin_edges': bin_edges.tolist(),
            'x_normal': x.tolist(),
            'normal_curve': normal_curve.tolist(),
            'mu': float(mu),
            'sigma': float(sigma)
        }
        
        return dist_data
