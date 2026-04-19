"""
Sample Data Generator
Creates realistic mock data for testing when Yahoo Finance is rate-limited
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class SampleDataGenerator:
    """Generate realistic sample data for testing"""
    
    @staticmethod
    def generate_stock_prices(symbol, days=252, start_price=100, volatility=0.02, trend=0.0001):
        """
        Generate realistic stock price data using geometric Brownian motion
        
        Args:
            symbol (str): Stock symbol
            days (int): Number of days of data
            start_price (float): Starting price
            volatility (float): Daily volatility (std dev of returns)
            trend (float): Daily drift/trend
            
        Returns:
            pd.DataFrame: DataFrame with OHLCV data
        """
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        # Generate returns using geometric Brownian motion
        np.random.seed(hash(symbol) % 2**32)  # Deterministic seed per symbol
        returns = np.random.normal(trend, volatility, days)
        
        # Generate prices from returns
        prices = start_price * np.exp(np.cumsum(returns))
        
        # Create realistic OHLCV data
        data = {
            'Open': prices * (1 + np.random.uniform(-0.01, 0.01, days)),
            'High': prices * (1 + np.abs(np.random.normal(0, 0.005, days))),
            'Low': prices * (1 - np.abs(np.random.normal(0, 0.005, days))),
            'Close': prices,
            'Volume': np.random.randint(1000000, 100000000, days),
            'Adj Close': prices
        }
        
        df = pd.DataFrame(data, index=dates)
        
        # Ensure High >= Close >= Low
        df['High'] = df[['Open', 'High', 'Close']].max(axis=1)
        df['Low'] = df[['Open', 'Low', 'Close']].min(axis=1)
        
        return df[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']]
    
    @staticmethod
    def get_sample_data(symbols=None):
        """
        Get sample data for common stocks
        
        Args:
            symbols (list): List of symbols to generate data for
            
        Returns:
            dict: Dictionary of symbol -> DataFrame
        """
        if symbols is None:
            symbols = ['AAPL', 'MSFT', 'GOOGL', 'RELIANCE.NS', 'TCS.NS']
        
        # Predefined parameters for realistic data
        params = {
            'AAPL': {'start': 150, 'volatility': 0.018, 'trend': 0.0003},
            'MSFT': {'start': 300, 'volatility': 0.015, 'trend': 0.0002},
            'GOOGL': {'start': 100, 'volatility': 0.020, 'trend': 0.0003},
            'RELIANCE.NS': {'start': 2500, 'volatility': 0.025, 'trend': 0.0001},
            'TCS.NS': {'start': 3500, 'volatility': 0.022, 'trend': 0.0002},
            'INFY.NS': {'start': 1800, 'volatility': 0.020, 'trend': 0.0002},
            'TSLA': {'start': 200, 'volatility': 0.035, 'trend': 0.0004},
            'AMZN': {'start': 140, 'volatility': 0.025, 'trend': 0.0003},
        }
        
        data = {}
        for symbol in symbols:
            if symbol in params:
                p = params[symbol]
                data[symbol] = SampleDataGenerator.generate_stock_prices(
                    symbol,
                    start_price=p['start'],
                    volatility=p['volatility'],
                    trend=p['trend']
                )
            else:
                # Generate with default parameters for unknown symbols
                data[symbol] = SampleDataGenerator.generate_stock_prices(symbol)
        
        return data


# Quick test
if __name__ == '__main__':
    gen = SampleDataGenerator()
    sample = gen.get_sample_data(['AAPL', 'RELIANCE.NS'])
    for symbol, df in sample.items():
        print(f"\n{symbol}:")
        print(df.head())
        print(f"Shape: {df.shape}")
        print(f"Latest Close: {df['Close'].iloc[-1]:.2f}")
