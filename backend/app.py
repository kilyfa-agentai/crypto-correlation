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

# Cache for coins list
_coins_cache = {
    "coins": None,
    "last_fetched": None
}

# Coin symbol mapping (coin_id -> Binance/Bitget symbol)
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

def get_binance_coins_list() -> List[Dict]:
    """Fetch all available coins from Binance API"""
    try:
        url = "https://api.binance.com/api/v3/exchangeInfo"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            symbols = data.get("symbols", [])
            
            # Filter USDT pairs that are actively trading
            coins_set = set()
            for symbol_info in symbols:
                if (symbol_info.get("quoteAsset") == "USDT" and 
                    symbol_info.get("status") == "TRADING"):
                    base_asset = symbol_info.get("baseAsset", "").lower()
                    if base_asset:
                        coins_set.add(base_asset)
            
            # Convert to list with metadata
            coins_list = []
            for coin in sorted(coins_set):
                # Map common symbols to readable names
                coin_name = get_coin_display_name(coin)
                coins_list.append({
                    "id": coin,
                    "symbol": coin.upper(),
                    "name": coin_name
                })
            
            print(f"✓ Loaded {len(coins_list)} coins from Binance")
            return coins_list
    except Exception as e:
        print(f"Error fetching Binance coins: {e}")
    
    return []

def get_coin_display_name(coin_id: str) -> str:
    """Get display name for coin ID"""
    # Comprehensive mapping of coin IDs to names
    name_map = {
        "btc": "Bitcoin",
        "eth": "Ethereum",
        "sol": "Solana",
        "ada": "Cardano",
        "dot": "Polkadot",
        "avax": "Avalanche",
        "matic": "Polygon",
        "link": "Chainlink",
        "xlm": "Stellar",
        "atom": "Cosmos",
        "algo": "Algorand",
        "near": "NEAR Protocol",
        "apt": "Aptos",
        "sui": "Sui",
        "arb": "Arbitrum",
        "op": "Optimism",
        "uni": "Uniswap",
        "aave": "Aave",
        "bnb": "BNB",
        "xrp": "XRP",
        "doge": "Dogecoin",
        "shib": "Shiba Inu",
        "trx": "TRON",
        "ltc": "Litecoin",
        "bch": "Bitcoin Cash",
        "etc": "Ethereum Classic",
        "xmr": "Monero",
        "usdc": "USD Coin",
        "usdt": "Tether",
        "dai": "Dai",
        "wbtc": "Wrapped Bitcoin",
        "steth": "Lido Staked Ether",
        "pepe": "Pepe",
        "wif": "dogwifhat",
        "bonk": "Bonk",
        "inj": "Injective",
        "sei": "Sei",
        "tia": "Celestia",
        "jto": "Jito",
        "pyth": "Pyth Network",
        "rune": "THORChain",
        "ftm": "Fantom",
        "one": "Harmony",
        "vet": "VeChain",
        "grt": "The Graph",
        "sand": "The Sandbox",
        "mana": "Decentraland",
        "axs": "Axie Infinity",
        "imx": "Immutable X",
        "ape": "ApeCoin",
        "ldo": "Lido DAO",
        "mkr": "Maker",
        "comp": "Compound",
        "snx": "Synthetix",
        "crv": "Curve DAO",
        "1inch": "1inch",
        "sushi": "SushiSwap",
        "cake": "PancakeSwap",
    }
    
    coin_lower = coin_id.lower()
    if coin_lower in name_map:
        return name_map[coin_lower]
    
    # Default: capitalize first letter
    return coin_id.upper() if len(coin_id) <= 4 else coin_id.capitalize()

def get_historical_prices(coin_id: str, days: int = 30) -> List[float]:
    """Fetch historical prices with fallback order: Binance → CoinGecko → Bitget"""
    
    # 1. Try Binance first (most reliable, free)
    try:
        print(f"[1/3] Trying Binance for {coin_id}...")
        return get_binance_prices(coin_id, days)
    except Exception as e:
        print(f"❌ Binance failed: {e}")
    
    # 2. Fallback to CoinGecko
    try:
        print(f"[2/3] Trying CoinGecko for {coin_id}...")
        return get_coingecko_prices(coin_id, days)
    except Exception as e:
        print(f"❌ CoinGecko failed: {e}")
    
    # 3. Last resort - Bitget
    try:
        print(f"[3/3] Trying Bitget for {coin_id}...")
        return get_bitget_prices(coin_id, days)
    except Exception as e:
        print(f"❌ Bitget failed: {e}")
        raise HTTPException(
            status_code=400, 
            detail=f"Failed to fetch data for {coin_id} from all sources (Binance, CoinGecko, Bitget)"
        )

def get_binance_prices(coin_id: str, days: int = 30) -> List[float]:
    """Primary source: Binance API"""
    # Build symbol - try direct uppercase first
    symbol = f"{coin_id.upper()}USDT"
    
    # Check if we have a custom mapping
    if coin_id.lower() in COIN_SYMBOLS:
        symbol = COIN_SYMBOLS[coin_id.lower()]
    
    url = "https://api.binance.com/api/v3/klines"
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
    
    response = requests.get(url, params=params, headers=headers, timeout=20)
    print(f"✓ Binance: {symbol} - Status {response.status_code}")
    
    if response.status_code != 200:
        raise Exception(f"HTTP {response.status_code}")
    
    data = response.json()
    if not data:
        raise Exception("Empty response")
    
    # Binance klines: [openTime, open, high, low, close, volume, ...]
    prices = [float(candle[4]) for candle in data]
    return prices

def get_coingecko_prices(coin_id: str, days: int = 30) -> List[float]:
    """Fallback #2: CoinGecko API"""
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
    
    response = requests.get(url, params=params, headers=headers, timeout=20)
    print(f"✓ CoinGecko: {coin_id} - Status {response.status_code}")
    
    if response.status_code != 200:
        raise Exception(f"HTTP {response.status_code}")
    
    data = response.json()
    prices = [price[1] for price in data["prices"]]
    return prices

def get_bitget_prices(coin_id: str, days: int = 30) -> List[float]:
    """Fallback #3: Bitget API V2"""
    symbol = COIN_SYMBOLS.get(coin_id.lower())
    if not symbol:
        raise Exception(f"Coin not supported on Bitget: {coin_id}")
    
    url = f"{BITGET_API}/api/v2/spot/market/candles"
    end_time = int(datetime.now().timestamp() * 1000)
    start_time = end_time - (days * 24 * 60 * 60 * 1000)
    
    params = {
        "symbol": symbol,
        "granularity": "1D",
        "startTime": str(start_time),
        "endTime": str(end_time),
        "limit": str(days)
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, params=params, headers=headers, timeout=20)
    print(f"✓ Bitget: {symbol} - Status {response.status_code}")
    
    if response.status_code != 200:
        raise Exception(f"HTTP {response.status_code}")
    
    data = response.json()
    if data.get("code") != "00000":
        raise Exception(f"API error: {data.get('msg')}")
    
    candles = data.get("data", [])
    if not candles:
        raise Exception("Empty response")
    
    # Bitget V2 format: [timestamp, open, high, low, close, volume, quoteVolume]
    prices = [float(candle[4]) for candle in candles]
    prices.reverse()  # Oldest first
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

@app.get("/api/coins")
def get_available_coins():
    """
    Get list of available coins - try Bitget first, fallback to static
    """
    try:
        # Try to fetch from Bitget V2 API
        url = f"{BITGET_API}/api/v2/spot/public/coins"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == "00000" and data.get("data"):
                coins_data = data.get("data", [])
                available_coins = []
                
                for coin in coins_data:
                    coin_id = coin.get("coinId", "").lower()
                    coin_name = coin.get("coinName", "").lower()
                    
                    # Only include coins with USDT pair
                    if coin_id:
                        symbol = f"{coin_id.upper()}USDT"
                        # Update mapping
                        if coin_id not in COIN_SYMBOLS:
                            COIN_SYMBOLS[coin_id] = symbol
                        available_coins.append(coin_id)
                
                if available_coins:
                    return {
                        "coins": available_coins[:200],  # Return top 200
                        "source": "bitget_api",
                        "count": len(available_coins)
                    }
        
        # If API call fails, return static list + some extras
        extended_list = list(COIN_SYMBOLS.keys()) + [
            'sui', 'sei', 'blur', 'pepe', 'floki', 'bonk', 'wld',
            'pendle', 'ondo', 'bera', 'taiko', 'zksync', 'scroll',
            'eigenlayer', 'bittensor', 'render', 'injective',
            'celestia', 'dymension', 'manta', 'blast', 'mode'
        ]
        
        return {
            "coins": list(set(extended_list)),  # Remove duplicates
            "source": "extended_static_list",
            "count": len(set(extended_list))
        }
        
    except Exception as e:
        print(f"Error fetching coins: {e}")
        # Fallback to static list
        return {
            "coins": list(COIN_SYMBOLS.keys()),
            "source": "static_fallback",
            "count": len(COIN_SYMBOLS)
        }

# Cache for Bitget coins list
_bitget_coins_cache = {
    "coins": [],
    "last_fetched": None
}

def get_bitget_coins_list() -> List[str]:
    """Fetch and cache coins list from Bitget API"""
    import time
    
    # Check cache (refresh every 5 minutes)
    if _bitget_coins_cache["coins"] and _bitget_coins_cache["last_fetched"]:
        if time.time() - _bitget_coins_cache["last_fetched"] < 300:
            return _bitget_coins_cache["coins"]
    
    try:
        url = f"{BITGET_API}/api/v2/spot/public/coins"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == "00000" and data.get("data"):
                coins_data = data.get("data", [])
                available_coins = []
                
                for coin in coins_data:
                    # In Bitget V2, coinName is usually the ticker (BTC, ETH)
                    # coinId might be internal ID or same as ticker depending on endpoint version
                    coin_ticker = coin.get("coinName", "").lower()
                    
                    # Fallback to symbol if coinName is empty, strips USDT if present
                    if not coin_ticker:
                         symbol = coin.get("symbol", "").lower()
                         coin_ticker = symbol.replace("usdt", "")

                    if coin_ticker:
                        available_coins.append(coin_ticker)
                        # Update symbol mapping
                        symbol = f"{coin_ticker.upper()}USDT"
                        if coin_ticker not in COIN_SYMBOLS:
                            COIN_SYMBOLS[coin_ticker] = symbol
                
                _bitget_coins_cache["coins"] = available_coins
                _bitget_coins_cache["last_fetched"] = time.time()
                return available_coins
    except Exception as e:
        print(f"Error fetching Bitget coins: {e}")
    
    # Fallback to static list
    return list(COIN_SYMBOLS.keys())

@app.get("/api/coins/all")
def get_all_coins():
    """
    Get complete list of all available coins with metadata
    Cached for 1 hour - frontend will search client-side
    """
    import time
    
    # Check cache (refresh every 1 hour)
    if _coins_cache["coins"] and _coins_cache["last_fetched"]:
        if time.time() - _coins_cache["last_fetched"] < 3600:
            return {
                "coins": _coins_cache["coins"],
                "total": len(_coins_cache["coins"]),
                "cache_duration": 3600,
                "source": "cache"
            }
    
    # Try Binance first (most reliable and comprehensive)
    binance_coins = get_binance_coins_list()
    
    if binance_coins:
        # Add category metadata
        for coin in binance_coins:
            coin["category"] = get_coin_category(coin["id"])
        
        _coins_cache["coins"] = binance_coins
        _coins_cache["last_fetched"] = time.time()
        
        return {
            "coins": binance_coins,
            "total": len(binance_coins),
            "cache_duration": 3600,
            "source": "binance"
        }
    
    # Fallback to static list if Binance fails
    print("Binance coins fetch failed, using static list")
    static_coins = []
    for coin_id in COIN_SYMBOLS.keys():
        static_coins.append({
            "id": coin_id,
            "name": get_coin_display_name(coin_id),
            "symbol": coin_id.upper(),
            "category": get_coin_category(coin_id)
        })
    
    return {
        "coins": static_coins,
        "total": len(static_coins),
        "cache_duration": 3600,
        "source": "static"
    }

def get_coin_category(coin_id: str) -> str:
    """Categorize coins"""
    layer1 = ["btc", "eth", "sol", "ada", "avax", "algo", "near", "apt", "sui", "trx", "ftm", "one"]
    layer2 = ["matic", "arb", "op", "imx"]
    layer0 = ["dot", "atom"]
    defi = ["uni", "aave", "mkr", "comp", "snx", "crv", "1inch", "sushi", "cake", "ldo"]
    oracle = ["link", "pyth"]
    payment = ["xlm", "xrp", "ltc", "bch"]
    meme = ["doge", "shib", "pepe", "wif", "bonk"]
    stablecoin = ["usdc", "usdt", "dai"]
    
    coin_lower = coin_id.lower()
    if coin_lower in layer1:
        return "Layer 1"
    elif coin_lower in layer2:
        return "Layer 2"
    elif coin_lower in layer0:
        return "Layer 0"
    elif coin_lower in defi:
        return "DeFi"
    elif coin_lower in oracle:
        return "Oracle"
    elif coin_lower in payment:
        return "Payment"
    elif coin_lower in meme:
        return "Meme"
    elif coin_lower in stablecoin:
        return "Stablecoin"
    else:
        return "Other"

@app.get("/api/search")
def search_coins(query: str = ""):
    """
    DEPRECATED: Use /api/coins/all instead and search client-side
    Kept for backward compatibility
    """
    bitget_coins = get_bitget_coins_list()
    
    return {
        "query": query,
        "recommendations": bitget_coins[:20],
        "deprecated": True,
        "message": "Please use /api/coins/all and implement client-side search"
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
