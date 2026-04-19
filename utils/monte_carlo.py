"""
Monte Carlo Simulation Module
Simulates future stock price paths based on statistical properties
"""

import numpy as np
import pandas as pd


class MonteCarloSimulator:
    """
    Performs Monte Carlo simulation for future price prediction
    Uses Geometric Brownian Motion (GBM) model
    """
    
    def __init__(self):
        """Initialize the simulator"""
        self.simulations = None
        self.final_prices = None
    
    def simulate_paths(self, current_prices, returns_stats, days_ahead=252, num_simulations=1000):
        """
        Simulate future stock price paths using Geometric Brownian Motion
        
        GBM Formula: dS = μ*S*dt + σ*S*dW
        Where:
            S = Stock Price
            μ = Expected return
            σ = Volatility (std dev)
            dt = Time step
            dW = Random shock from normal distribution
        
        Args:
            current_prices (dict): Current price for each stock
            returns_stats (dict): Statistics (mean, std_dev) for each stock
            days_ahead (int): Number of days to simulate
            num_simulations (int): Number of simulation paths
            
        Returns:
            dict: Dictionary containing simulations for each stock
        """
        simulations = {}
        
        for symbol, current_price in current_prices.items():
            if symbol not in returns_stats:
                continue
            
            # Get stock statistics
            mu = returns_stats[symbol]['mean_daily']  # Daily drift
            sigma = returns_stats[symbol]['std_dev_daily']  # Daily volatility
            
            # Initialize array to store simulated prices
            # Shape: (num_simulations, days_ahead + 1) - +1 for current day
            price_paths = np.zeros((num_simulations, days_ahead + 1))
            price_paths[:, 0] = current_price  # Set initial price
            
            # Time step (1 day)
            dt = 1 / 252
            
            # Monte Carlo simulation
            for t in range(1, days_ahead + 1):
                # Generate random shocks from normal distribution
                # Shape: (num_simulations,)
                random_shocks = np.random.randn(num_simulations)
                
                # Calculate price movement using GBM
                # Price_t = Price_{t-1} * exp((μ - σ²/2)*dt + σ*sqrt(dt)*Z)
                drift = (mu - 0.5 * sigma ** 2) * dt
                diffusion = sigma * np.sqrt(dt) * random_shocks
                
                price_paths[:, t] = price_paths[:, t - 1] * np.exp(drift + diffusion)
            
            simulations[symbol] = price_paths
        
        self.simulations = simulations
        return simulations
    
    def get_simulation_statistics(self, num_simulations=1000):
        """
        Extract statistics from simulation results
        
        Args:
            num_simulations (int): Number of simulations performed
            
        Returns:
            dict: Statistics for each stock
        """
        statistics = {}
        
        for symbol, paths in self.simulations.items():
            # Get final prices from all simulations
            final_prices = paths[:, -1]
            
            return_pct = ((final_prices - paths[0, 0]) / paths[0, 0]) * 100
            
            stats = {
                'symbol': symbol,
                'initial_price': paths[0, 0],
                'mean_final_price': np.mean(final_prices),
                'std_final_price': np.std(final_prices),
                'best_case': np.max(final_prices),
                'worst_case': np.min(final_prices),
                'percentile_5': np.percentile(final_prices, 5),  # 5th percentile
                'percentile_25': np.percentile(final_prices, 25),  # 25th percentile (Q1)
                'median': np.median(final_prices),  # 50th percentile (Q2)
                'percentile_75': np.percentile(final_prices, 75),  # 75th percentile (Q3)
                'percentile_95': np.percentile(final_prices, 95),  # 95th percentile
                'best_case_return': np.max(return_pct),
                'worst_case_return': np.min(return_pct),
                'mean_return': np.mean(return_pct),
                'prob_profit': np.sum(final_prices > paths[0, 0]) / num_simulations * 100
            }
            
            statistics[symbol] = stats
        
        return statistics
    
    def get_percentile_prices(self, percentile=95):
        """
        Get price paths for specific percentiles
        Useful for visualizing confidence bands
        
        Args:
            percentile (int): Percentile value (0-100)
            
        Returns:
            dict: Percentile prices over time for each stock
        """
        percentile_data = {}
        
        for symbol, paths in self.simulations.items():
            # Calculate percentile at each time step
            percentile_path = np.percentile(paths, percentile, axis=0)
            percentile_data[symbol] = percentile_path.tolist()
        
        return percentile_data
    
    def get_price_corridor(self):
        """
        Get the price corridor (min, mean, max) for each time step
        Used for visualization
        
        Returns:
            dict: Price corridors for visualization
        """
        corridors = {}
        
        for symbol, paths in self.simulations.items():
            corridor = {
                'best': np.max(paths, axis=0).tolist(),
                'worst': np.min(paths, axis=0).tolist(),
                'mean': np.mean(paths, axis=0).tolist(),
                'percentile_5': np.percentile(paths, 5, axis=0).tolist(),
                'percentile_95': np.percentile(paths, 95, axis=0).tolist(),
                'median': np.median(paths, axis=0).tolist()
            }
            corridors[symbol] = corridor
        
        return corridors
    
    def get_sample_paths(self, num_paths_to_plot=100):
        """
        Get sample paths for visualization
        
        Args:
            num_paths_to_plot (int): Number of sample paths to return
            
        Returns:
            dict: Sample paths for visualization
        """
        sample_paths = {}
        
        for symbol, paths in self.simulations.items():
            # Randomly select sample paths
            num_paths = min(num_paths_to_plot, paths.shape[0])
            indices = np.random.choice(paths.shape[0], num_paths, replace=False)
            
            sample_paths[symbol] = paths[indices, :].tolist()
        
        return sample_paths
