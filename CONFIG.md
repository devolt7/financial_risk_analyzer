# Configuration Guide

## Environment Variables

Create `.env` file in project root (optional):

```
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_APP=app.py

# Data Configuration
DATA_PERIOD=1y
DATA_SOURCE=yfinance

# Optimization
RISK_FREE_RATE=0.02
CONFIDENCE_LEVEL=0.95

# Limits
MAX_STOCKS=10
MAX_DAYS=500
MAX_SIMULATIONS=5000
MIN_SIMULATIONS=100

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=5000
```

## Application Settings

### In `app.py`

```python
# Data period (default: 1 year)
data_handler = DataHandler(period='1y')

# Options: '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'max'
```

### In `utils/statistical_analysis.py`

```python
# Confidence level for VaR calculation (default: 95%)
self.confidence_level = 0.95

# Change to 0.99 for 99% confidence, 0.90 for 90%, etc.
```

### In `utils/portfolio_optimizer.py`

```python
# Risk-free rate for Sharpe Ratio (default: 2% annual)
def optimize_sharpe_ratio(self, risk_free_rate=0.02):
    # Adjust for current economic conditions
    # Example: 0.04 for 4% risk-free rate
```

## Flask Configuration Options

### Development Mode
```python
if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)
```

### Production Mode
```python
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
    # Use gunicorn in production: gunicorn app:app
```

### CORS Configuration (if needed)
```python
from flask_cors import CORS
CORS(app)
```

## Performance Tuning

### Reduce Analysis Time

```python
# In app.py, reduce number of simulations
num_simulations = 500  # Instead of 1000
```

### Increase Accuracy

```python
# Use more simulations
num_simulations = 2000
```

### Cache Results

```python
# Add basic caching
from functools import lru_cache

@app.route('/api/analyze', methods=['POST'])
@lru_cache(maxsize=100)
def analyze():
    # Caches last 100 analyses
```

## Database Configuration (Future)

For storing historical analyses:

```python
# SQLite
SQLALCHEMY_DATABASE_URI = 'sqlite:///analyses.db'

# PostgreSQL
SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost:5432/risk_analyzer'
```

## Logging Configuration

```python
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

## Security Settings

### For Production

```python
# HTTPS only
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True

# Disable debug mode
app.config['DEBUG'] = False

# Add CORS restrictions
CORS(app, resources={r"/api/*": {"origins": "https://yourdomain.com"}})
```

## Data Source Configuration

### Change from Yahoo Finance

```python
# In utils/data_handler.py
# Use Alpha Vantage (needs API key)
import alpha_vantage

# Or use IEX Cloud
import iex
```

## Monte Carlo Settings

```python
# In utils/monte_carlo.py
# Adjust number of time steps
dt = 1/252  # Daily steps (default)
dt = 1/252/4  # For intra-daily analysis

# Number of days to simulate
days_ahead = 252  # 1 year
days_ahead = 504  # 2 years
```

---

## Example: Custom Configuration

Create `config.py`:

```python
class Config:
    """Base configuration"""
    DEBUG = False
    TESTING = False
    DATA_PERIOD = '1y'
    RISK_FREE_RATE = 0.02
    CONFIDENCE_LEVEL = 0.95
    
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
```

Use in `app.py`:

```python
import os
from config import DevelopmentConfig, ProductionConfig

if os.getenv('FLASK_ENV') == 'production':
    app.config.from_object(ProductionConfig)
else:
    app.config.from_object(DevelopmentConfig)
```

---

## Deployment Checklist

- [ ] Set `DEBUG = False`
- [ ] Use strong `SECRET_KEY`
- [ ] Enable HTTPS
- [ ] Set up logging to files
- [ ] Configure environment variables
- [ ] Test with production data
- [ ] Use production WSGI server (gunicorn, uWSGI)
- [ ] Set up monitoring and alerts
- [ ] Backup historical data
- [ ] Document API endpoints

---

For more configuration options, see Flask documentation: https://flask.palletsprojects.com/
