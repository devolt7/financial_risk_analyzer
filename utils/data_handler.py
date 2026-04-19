"""
Data Handler Module
Handles fetching and processing real-world stock data using yfinance API
Falls back to sample data when rate-limited
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import warnings
from utils.sample_data import SampleDataGenerator

# Suppress yfinance warnings
warnings.filterwarnings('ignore')


class DataHandler:
    """
    Fetches and processes historical stock data
    """
    
    def __init__(self, period='1y'):
        """
        Initialize DataHandler with default period
        
        Args:
            period (str): Historical data period (default: '1y' for 1 year)
        """
        self.period = period
        self.data = {}
        self.returns = {}
    
    def fetch_stock_data(self, symbols):
        """
        Fetch historical closing prices for given stock symbols with retry logic
        Using batch download for efficiency
        
        Args:
            symbols (list): List of stock symbols (e.g., ['RELIANCE.NS', 'TCS.NS'])
            
        Returns:
            dict: Dictionary containing DataFrames for each symbol
        """
        try:
            if not symbols:
                return self.data
            
            print(f"Fetching data for {len(symbols)} symbols...")
            print(f"Symbols: {', '.join(symbols)}")
            
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    print(f"\nAttempt {retry_count + 1}/{max_retries}...")
                    
                    # Try batch download first (more efficient)
                    print("Using batch download (more efficient)...")
                    hist = yf.download(
                        tickers=' '.join(symbols),
                        period=self.period,
                        progress=False,
                        threads=False  # Disable threading to avoid rate limits
                    )
                    
                    if hist.empty:
                        print("⚠ Batch download returned empty data")
                        raise Exception("Empty data from batch download")
                    
                    # Process batch results
                    if len(symbols) == 1:
                        # Single symbol - reshape to match expected format
                        self.data[symbols[0]] = hist[['Close']].copy()
                        print(f"✓ Successfully fetched {len(hist)} records for {symbols[0]}")
                    else:
                        # Multiple symbols
                        for symbol in symbols:
                            if symbol in hist.columns and 'Close' in hist.columns:
                                # Multi-level columns
                                self.data[symbol] = hist['Close'][[symbol]].copy()
                                self.data[symbol].columns = ['Close']
                                print(f"✓ Successfully fetched {len(hist)} records for {symbol}")
                            elif symbol.lower() in hist.columns:
                                # Sometimes yfinance uses lowercase
                                self.data[symbol] = hist[[symbol.lower()]].copy()
                                self.data[symbol].columns = ['Close']
                                print(f"✓ Successfully fetched {len(hist)} records for {symbol}")
                    
                    if self.data:
                        print("\n✓ Batch download successful!")
                        return self.data
                    
                except Exception as batch_err:
                    print(f"⚠ Batch download failed: {str(batch_err)}")
                    print("Falling back to individual symbol downloads...")
                    
                    # Fallback: try individual downloads
                    for idx, symbol in enumerate(symbols):
                        try:
                            # Add delay between requests
                            if idx > 0:
                                wait_time = 1
                                print(f"  Waiting {wait_time}s before next request...")
                                time.sleep(wait_time)
                            
                            print(f"  Fetching {symbol}...")
                            ticker = yf.Ticker(symbol)
                            hist = ticker.history(period=self.period)
                            
                            if hist.empty:
                                print(f"  ⚠ No data for {symbol} - invalid symbol or delisted")
                                continue
                            
                            self.data[symbol] = hist[['Close']].copy()
                            print(f"  ✓ {symbol}: {len(hist)} records")
                            
                        except Exception as symbol_err:
                            print(f"  ✗ Failed to fetch {symbol}: {str(symbol_err)}")
                            continue
                    
                    if self.data:
                        return self.data
                    
                    # If still no data, retry
                    retry_count += 1
                    if retry_count < max_retries:
                        wait_time = 5 * retry_count
                        print(f"\n⏳ No data fetched yet. Waiting {wait_time}s before retry {retry_count + 1}...\n")
                        time.sleep(wait_time)
            
            if not self.data:
                print("\n" + "="*60)
                print("⚠ FAILED TO FETCH REAL DATA - USING SAMPLE DATA")
                print("="*60)
                print("\nReason: Yahoo Finance rate limiting or connectivity issue")
                print("\nSolution:")
                print("  • Wait 10-15 minutes and try again")
                print("  • Or use a VPN to get a new IP address")
                print("\n📊 Using SAMPLE DATA for demonstration:")
                print("="*60 + "\n")
                
                # Fall back to sample data
                try:
                    generator = SampleDataGenerator()
                    self.data = generator.get_sample_data(symbols)
                    print(f"\n✓ Generated sample data for: {', '.join(self.data.keys())}")
                    print("Note: This is realistic mock data for testing purposes only")
                    return self.data
                except Exception as fallback_err:
                    print(f"✗ Also failed to generate sample data: {str(fallback_err)}")
                    raise Exception("Could not fetch data for any symbols after retries and sample data generation failed")
            
            return self.data
            
        except Exception as e:
            print(f"✗ Error in fetch_stock_data: {str(e)}")
            raise Exception(f"Error fetching stock data: {str(e)}")
    
    def calculate_returns(self, symbols):
        """
        Calculate daily returns from closing prices
        
        Returns = (Price_today - Price_yesterday) / Price_yesterday
        
        Args:
            symbols (list): List of stock symbols
            
        Returns:
            dict: Daily returns for each symbol
        """
        try:
            for symbol in symbols:
                if symbol not in self.data:
                    print(f"Skipping {symbol} - no data available")
                    continue
                
                # Calculate daily percentage returns
                self.returns[symbol] = self.data[symbol]['Close'].pct_change().dropna()
                
            return self.returns
            
        except Exception as e:
            raise Exception(f"Error calculating returns: {str(e)}")
    
    def get_stock_info(self, symbol):
        """
        Get basic information about a stock
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            dict: Stock information
        """
        try:
            ticker = yf.Ticker(symbol)
            info = {
                'name': ticker.info.get('longName', symbol),
                'currency': ticker.info.get('currency', 'USD'),
                'sector': ticker.info.get('sector', 'N/A'),
                'current_price': ticker.info.get('currentPrice', None)
            }
            return info
        except:
            return {'name': symbol, 'currency': 'USD', 'sector': 'N/A', 'current_price': None}
    
    def validate_symbols(self, symbols):
        """
        Validate if symbols are accessible
        
        Args:
            symbols (list): List of stock symbols
            
        Returns:
            tuple: (valid_symbols, invalid_symbols)
        """
        valid = []
        invalid = []
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                if ticker.history(period='1d').empty:
                    invalid.append(symbol)
                else:
                    valid.append(symbol)
            except:
                invalid.append(symbol)
        
        return valid, invalid
