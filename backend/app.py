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

BITGET_API = "https://api.bitget.com"

# Coin symbol mapping (coin_id -> Bitget symbol)
COIN_SYMBOLS = {
    'bitcoin': 'BTCUSDT',
    'ethereum': 'ETHUSDT',
    'solana': 'SOLUSDT',
    'cardano': 'ADAUSDT',
    'polkadot': 'DOTUSDT',
    'avalanche': 'AVAXUSDT',
    'polygon': 'MATICUSDT',
    'chainlink': 'LINKUSDT',
    'stellar': 'XLMUSDT',
    'cosmos': 'ATOMUSDT',
    'algorand': 'ALGOUSDT',
    'near': 'NEARUSDT',
    'aptos': 'APTUSDT',
    'sui': 'SUIUSDT',
    'arbitrum': 'ARBUSDT',
    'optimism': 'OPUSDT',
    'uniswap': 'UNIUSDT',
    'aave': 'AAVEUSDT',
    'binancecoin': 'BNBUSDT',
    'ripple': 'XRPUSDT',
    'dogecoin': 'DOGEUSDT',
    'shiba-inu': 'SHIBUSDT',
    'tron': 'TRXUSDT',
    'litecoin': 'LTCUSDT',
}

def get_bitget_symbol(coin_id: str) -> str:
    """Convert coin ID to Bitget symbol"""
    coin_id = coin_id.lower().replace(' ', '-')
    if coin_id in COIN_SYMBOLS:
        return COIN_SYMBOLS[coin_id]
    # Try common patterns
    return f"{coin_id.upper()}USDT"

def get_historical_prices(coin_id: str, days: int = 30) -> List[float]:
    """Fetch historical prices - Binance as primary"""
    
    # Try Binance first (most reliable)
    try:
        return get_binance_prices(coin_id, days)
    except Exception as e:
        print(f"Binance failed: {e}")
    
    # Fallback to CoinGecko
    try:
        return get_coingecko_prices(coin_id, days)
    except Exception as e:
        print(f"CoinGecko failed: {e}")
    
    # Last resort - Bitget
    try:
        return get_bitget_prices(coin_id, days)
    except Exception as e:
        print(f"Bitget failed: {e}")
        raise HTTPException(
            status_code=400, 
            detail=f"Failed to fetch data for {coin_id} from all sources"
        )

def get_binance_prices(coin_id: str, days: int = 30) -> List[float]:
    """Primary: Binance API"""
    # Map coin_id to Binance symbol
    symbol_map = {
        'bitcoin': 'BTCUSDT',
        'ethereum': 'ETHUSDT',
        'solana': 'SOLUSDT',
        'cardano': 'ADAUSDT',
        'polkadot': 'DOTUSDT',
        'avalanche': 'AVAXUSDT',
        'polygon': 'MATICUSDT',
        'chainlink': 'LINKUSDT',
        'stellar': 'XLMUSDT',
        'cosmos': 'ATOMUSDT',
        'algorand': 'ALGOUSDT',
        'near': 'NEARUSDT',
        'aptos': 'APTUSDT',
        'sui': 'SUIUSDT',
        'arbitrum': 'ARBUSDT',
        'optimism': 'OPUSDT',
        'uniswap': 'UNIUSDT',
        'aave': 'AAVEUSDT',
        'binancecoin': 'BNBUSDT',
        'ripple': 'XRPUSDT',
        'dogecoin': 'DOGEUSDT',
        'shiba-inu': 'SHIBUSDT',
        'tron': 'TRXUSDT',
        'litecoin': 'LTCUSDT',
    }
    
    symbol = symbol_map.get(coin_id.lower())
    if not symbol:
        raise Exception(f"Unknown coin: {coin_id}")
    
    url = "https://api.binance.com/api/v3/klines"
    
    # Calculate start time (milliseconds)
    end_time = int(datetime.now().timestamp() * 1000)
    start_time = end_time - (days * 24 * 60 * 60 * 1000)
    
    params = {
        "symbol": symbol,
        "interval": "1d",
        "startTime": start_time,
        "endTime": end_time,
        "limit": days
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    response = requests.get(url, params=params, headers=headers, timeout=10)
    
    print(f"Binance API: {symbol}, Status: {response.status_code}")
    
    if response.status_code != 200:
        raise Exception(f"Binance error: {response.status_code}")
    
    data = response.json()
    if not data:
        raise Exception("No data from Binance")
    
    # Binance klines: [openTime, open, high, low, close, volume, ...]
    prices = [float(candle[4]) for candle in data]  # Close price
    return prices

def get_coingecko_prices(coin_id: str, days: int = 30) -> List[float]:
    """Fallback 1: CoinGecko API"""
    COINGECKO_API = "https://api.coingecko.com/api/v3"
    url = f"{COINGECKO_API}/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
        "interval": "daily"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    response = requests.get(url, params=params, headers=headers, timeout=10)
    
    print(f"CoinGecko API: {coin_id}, Status: {response.status_code}")
    
    if response.status_code != 200:
        raise Exception(f"CoinGecko error: {response.status_code}")
    
    data = response.json()
    prices = [price[1] for price in data["prices"]]
    return prices

def get_bitget_prices(coin_id: str, days: int = 30) -> List[float]:
    """Fallback 2: Bitget API V2"""
    symbol = COIN_SYMBOLS.get(coin_id.lower())
    if not symbol:
        raise Exception(f"Unknown coin for Bitget: {coin_id}")
    
    # Bitget V2 API endpoint
    url = f"{BITGET_API}/api/v2/spot/market/candles"
    
    end_time = int(datetime.now().timestamp() * 1000)
    start_time = end_time - (days * 24 * 60 * 60 * 1000)
    
    params = {
        "symbol": symbol,
        "granularity": "1D",  # V2 uses granularity, not period
        "startTime": str(start_time),
        "endTime": str(end_time),
        "limit": str(days)
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, params=params, headers=headers, timeout=10)
    
    print(f"Bitget V2 API: {symbol}, Status: {response.status_code}")
    
    if response.status_code != 200:
        raise Exception(f"Bitget error: {response.status_code}")
    
    data = response.json()
    if data.get("code") != "00000":
        raise Exception(f"Bitget API error: {data.get('msg')}")
    
    candles = data.get("data", [])
    if not candles:
        raise Exception("No data from Bitget")
    
    # Bitget V2 candles format: [timestamp, open, high, low, close, volume, quoteVolume]
    prices = [float(candle[4]) for candle in candles]  # Close price
    prices.reverse()  # Oldest first
    return prices

def get_coingecko_prices(coin_id: str, days: int = 30) -> List[float]:
    """Fallback to CoinGecko API"""
    COINGECKO_API = "https://api.coingecko.com/api/v3"
    url = f"{COINGECKO_API}/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
        "interval": "daily"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        print(f"CoinGecko API Request: {url}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 429:
            # Rate limited - try Binance
            print("CoinGecko rate limited, trying Binance...")
            return get_binance_prices(coin_id, days)
        
        if response.status_code != 200:
            return get_binance_prices(coin_id, days)
        
        data = response.json()
        prices = [price[1] for price in data["prices"]]
        return prices
    except Exception as e:
        print(f"CoinGecko error: {e}")
        return get_binance_prices(coin_id, days)

def get_binance_prices(coin_id: str, days: int = 30) -> List[float]:
    """Fallback to Binance API"""
    # Map coin_id to Binance symbol
    symbol_map = {
        'bitcoin': 'BTCUSDT',
        'ethereum': 'ETHUSDT',
        'solana': 'SOLUSDT',
        'cardano': 'ADAUSDT',
        'polkadot': 'DOTUSDT',
        'avalanche': 'AVAXUSDT',
        'polygon': 'MATICUSDT',
        'chainlink': 'LINKUSDT',
        'stellar': 'XLMUSDT',
        'cosmos': 'ATOMUSDT',
        'algorand': 'ALGOUSDT',
        'near': 'NEARUSDT',
        'aptos': 'APTUSDT',
        'sui': 'SUIUSDT',
        'arbitrum': 'ARBUSDT',
        'optimism': 'OPUSDT',
        'uniswap': 'UNIUSDT',
        'aave': 'AAVEUSDT',
        'binancecoin': 'BNBUSDT',
        'ripple': 'XRPUSDT',
        'dogecoin': 'DOGEUSDT',
        'shiba-inu': 'SHIBUSDT',
        'tron': 'TRXUSDT',
        'litecoin': 'LTCUSDT',
    }
    
    symbol = symbol_map.get(coin_id.lower(), f"{coin_id.upper()}USDT")
    
    url = "https://api.binance.com/api/v3/klines"
    
    # Calculate start time
    end_time = int(datetime.now().timestamp() * 1000)
    start_time = end_time - (days * 24 * 60 * 60 * 1000)
    
    params = {
        "symbol": symbol,
        "interval": "1d",
        "startTime": start_time,
        "endTime": end_time,
        "limit": days
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        print(f"Binance API Request: {url}")
        print(f"Symbol: {symbol}")
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to fetch data for {coin_id} from all sources (Bitget, CoinGecko, Binance)"
            )
        
        data = response.json()
        # Binance klines: [openTime, open, high, low, close, volume, ...]
        prices = [float(candle[4]) for candle in data]  # Close price
        return prices
        
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Failed to fetch data for {coin_id}: {str(e)}"
        )

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

@app.get("/api/coins")
def get_available_coins():
    """
    Get list of available coins from Bitget
    """
    try:
        url = f"{BITGET_API}/api/v2/spot/public/coins"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            # Fallback to static list if API fails
            return {
                "coins": list(COIN_SYMBOLS.keys()),
                "source": "static_fallback",
                "count": len(COIN_SYMBOLS)
            }
        
        data = response.json()
        if data.get("code") != "00000":
            return {
                "coins": list(COIN_SYMBOLS.keys()),
                "source": "static_fallback",
                "count": len(COIN_SYMBOLS)
            }
        
        # Parse coins from Bitget
        coins_data = data.get("data", [])
        available_coins = []
        
        for coin in coins_data:
            coin_name = coin.get("coinName", "").lower()
            coin_id = coin.get("coinId", "").lower()
            if coin_name and coin_id:
                # Add to our mapping if not exists
                symbol = f"{coin_id.upper()}USDT"
                if coin_id not in COIN_SYMBOLS:
                    COIN_SYMBOLS[coin_id] = symbol
                available_coins.append(coin_id)
        
        return {
            "coins": available_coins[:100],  # Limit to top 100
            "source": "bitget_api",
            "count": len(available_coins)
        }
        
    except Exception as e:
        # Fallback to static list
        return {
            "coins": list(COIN_SYMBOLS.keys()),
            "source": "static_fallback",
            "count": len(COIN_SYMBOLS)
        }

@app.get("/api/search")
def search_coins(query: str = ""):
    """
    Search coins with recommendations like Google
    Example: /api/search?query=ste
    """
    query = query.lower().strip()
    
    if not query:
        return {
            "query": query,
            "exact_match": None,
            "recommendations": list(COIN_SYMBOLS.keys())[:10],
            "categories": {
                "popular": ["bitcoin", "ethereum", "solana", "cardano", "polkadot"],
                "defi": ["uniswap", "aave", "compound", "maker"],
                "layer1": ["ethereum", "solana", "avalanche", "near", "aptos"]
            }
        }
    
    # Find exact or partial matches
    exact_matches = []
    partial_matches = []
    
    for coin_id in COIN_SYMBOLS.keys():
        if coin_id == query:
            exact_matches.append(coin_id)
        elif query in coin_id:
            partial_matches.append(coin_id)
    
    # Also check by common names
    common_names = {
        "btc": "bitcoin",
        "eth": "ethereum", 
        "sol": "solana",
        "ada": "cardano",
        "dot": "polkadot",
        "avax": "avalanche",
        "matic": "polygon",
        "link": "chainlink",
        "xlm": "stellar",
        "atom": "cosmos",
        "uni": "uniswap",
        "aave": "aave",
        "bnb": "binancecoin",
        "xrp": "ripple",
        "doge": "dogecoin",
        "shib": "shiba-inu",
        "trx": "tron",
        "ltc": "litecoin",
    }
    
    if query in common_names:
        exact_matches.append(common_names[query])
    
    # Remove duplicates and combine
    all_matches = list(dict.fromkeys(exact_matches + partial_matches))
    
    return {
        "query": query,
        "exact_match": exact_matches[0] if exact_matches else None,
        "recommendations": all_matches[:10],
        "categories": {
            "exact_match": exact_matches[:3],
            "similar": partial_matches[:5],
            "popular": ["bitcoin", "ethereum", "solana"],
            "may_related": [c for c in COIN_SYMBOLS.keys() if c not in all_matches][:5]
        }
    }

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
