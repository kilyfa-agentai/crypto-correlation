from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import requests
from datetime import datetime, timedelta
from typing import List, Dict
import os

app = FastAPI(title="Crypto Correlation API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

COINGECKO_API = "https://api.coingecko.com/api/v3"

def get_historical_prices(coin_id: str, days: int = 30) -> List[float]:
    """Fetch historical prices from CoinGecko"""
    url = f"{COINGECKO_API}/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
        "interval": "daily"
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Failed to fetch data for {coin_id}")
    
    data = response.json()
    prices = [price[1] for price in data["prices"]]
    return prices

def calculate_returns(prices: List[float]) -> List[float]:
    """Calculate percentage returns"""
    returns = []
    for i in range(1, len(prices)):
        ret = (prices[i] - prices[i-1]) / prices[i-1] * 100
        returns.append(ret)
    return returns

def pearson_correlation(returns_a: List[float], returns_b: List[float]) -> float:
    """Calculate Pearson correlation coefficient"""
    if len(returns_a) != len(returns_b):
        raise ValueError("Returns arrays must have same length")
    
    n = len(returns_a)
    mean_a = sum(returns_a) / n
    mean_b = sum(returns_b) / n
    
    numerator = sum((a - mean_a) * (b - mean_b) for a, b in zip(returns_a, returns_b))
    denom_a = sum((a - mean_a) ** 2 for a in returns_a)
    denom_b = sum((b - mean_b) ** 2 for b in returns_b)
    
    if denom_a == 0 or denom_b == 0:
        return 0.0
    
    correlation = numerator / np.sqrt(denom_a * denom_b)
    return round(correlation, 4)

def rolling_correlation(returns_a: List[float], returns_b: List[float], window: int = 7) -> List[Dict]:
    """Calculate rolling correlation"""
    correlations = []
    
    for i in range(window, len(returns_a)):
        slice_a = returns_a[i-window:i]
        slice_b = returns_b[i-window:i]
        
        corr = pearson_correlation(slice_a, slice_b)
        correlations.append({
            "day": i,
            "correlation": corr
        })
    
    return correlations

def calculate_beta(coin_returns: List[float], btc_returns: List[float]) -> float:
    """Calculate beta coefficient relative to BTC"""
    covariance = np.cov(coin_returns, btc_returns)[0][1]
    btc_variance = np.var(btc_returns)
    
    if btc_variance == 0:
        return 0.0
    
    beta = covariance / btc_variance
    return round(beta, 4)

@app.get("/")
def root():
    return {"message": "Crypto Correlation API", "version": "1.0"}

@app.get("/api/correlation-matrix")
def get_correlation_matrix(coins: str = "bitcoin,ethereum,solana", days: int = 30):
    """
    Get correlation matrix for selected coins
    Example: /api/correlation-matrix?coins=bitcoin,ethereum,solana&days=30
    """
    coin_list = coins.split(",")
    
    # Fetch prices for all coins
    prices_data = {}
    returns_data = {}
    
    for coin in coin_list:
        prices = get_historical_prices(coin, days)
        prices_data[coin] = prices
        returns_data[coin] = calculate_returns(prices)
    
    # Calculate correlation matrix
    matrix = {}
    for coin_a in coin_list:
        matrix[coin_a] = {}
        for coin_b in coin_list:
            corr = pearson_correlation(returns_data[coin_a], returns_data[coin_b])
            matrix[coin_a][coin_b] = corr
    
    return {
        "coins": coin_list,
        "days": days,
        "matrix": matrix,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/rolling-correlation")
def get_rolling_correlation(coin_a: str = "ethereum", coin_b: str = "bitcoin", days: int = 30, window: int = 7):
    """
    Get rolling correlation between two coins
    Example: /api/rolling-correlation?coin_a=ethereum&coin_b=bitcoin&days=30&window=7
    """
    prices_a = get_historical_prices(coin_a, days)
    prices_b = get_historical_prices(coin_b, days)
    
    returns_a = calculate_returns(prices_a)
    returns_b = calculate_returns(prices_b)
    
    rolling_corr = rolling_correlation(returns_a, returns_b, window)
    
    return {
        "coin_a": coin_a,
        "coin_b": coin_b,
        "days": days,
        "window": window,
        "rolling_correlations": rolling_corr
    }

@app.get("/api/beta")
def get_beta_coefficient(coins: str = "ethereum,solana", days: int = 30):
    """
    Get beta coefficient for coins relative to BTC
    Example: /api/beta?coins=ethereum,solana,cardano&days=30
    """
    coin_list = coins.split(",")
    
    # Fetch BTC prices as benchmark
    btc_prices = get_historical_prices("bitcoin", days)
    btc_returns = calculate_returns(btc_prices)
    
    betas = {}
    for coin in coin_list:
        prices = get_historical_prices(coin, days)
        returns = calculate_returns(prices)
        
        beta = calculate_beta(returns, btc_returns)
        betas[coin] = beta
    
    return {
        "benchmark": "bitcoin",
        "days": days,
        "betas": betas,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
