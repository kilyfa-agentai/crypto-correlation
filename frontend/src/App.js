import React, { useState, useEffect, useCallback, useRef } from "react";
import "./App.css";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

function App() {
  const [coins, setCoins] = useState(["bitcoin", "ethereum", "solana"]);
  const [days, setDays] = useState(30);
  const [matrix, setMatrix] = useState(null);
  const [loading, setLoading] = useState(false);
  const [newCoin, setNewCoin] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [error, setError] = useState(null);
  const [showCoinList, setShowCoinList] = useState(false);
  const [allCoins, setAllCoins] = useState([]);
  const [searchResults, setSearchResults] = useState(null);
  const searchRef = useRef(null);

  // Fetch all available coins on mount
  useEffect(() => {
    const fetchCoins = async () => {
      try {
        const response = await fetch(`${API_URL}/api/coins`);
        const data = await response.json();
        const coins = data.coins || [];
        setAllCoins(coins);
        console.log(`Loaded ${coins.length} coins from ${data.source}`);
      } catch (err) {
        console.error("Failed to fetch coins:", err);
        // Fallback to extended list
        setAllCoins([
          "bitcoin",
          "ethereum",
          "solana",
          "cardano",
          "polkadot",
          "avalanche",
          "polygon",
          "chainlink",
          "stellar",
          "cosmos",
          "algorand",
          "near",
          "aptos",
          "sui",
          "arbitrum",
          "optimism",
          "uniswap",
          "aave",
          "binancecoin",
          "ripple",
          "dogecoin",
          "shiba-inu",
          "tron",
          "litecoin",
        ]);
      }
    };
    fetchCoins();
  }, []);

  const fetchCorrelationMatrix = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/correlation-matrix?coins=${coins.join(",")}&days=${days}`);
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to fetch data");
      }
      const data = await response.json();
      setMatrix(data.matrix);
    } catch (error) {
      console.error("Error fetching data:", error);
      setError(error.message || "Network error. Please check your connection.");
    }
    setLoading(false);
  }, [coins, days]);

  useEffect(() => {
    fetchCorrelationMatrix();
  }, [fetchCorrelationMatrix]);

  // Google-style search with API
  useEffect(() => {
    const fetchSearchResults = async () => {
      if (newCoin.length > 0) {
        try {
          const response = await fetch(`${API_URL}/api/search?query=${encodeURIComponent(newCoin)}`);
          const data = await response.json();
          setSearchResults(data);

          // Combine all recommendations
          const allSuggestions = [...(data.categories?.exact_match || []), ...(data.categories?.similar || []), ...(data.recommendations || [])];

          // Remove duplicates and already selected coins
          const uniqueSuggestions = [...new Set(allSuggestions)].filter((coin) => !coins.includes(coin)).slice(0, 8);

          setSuggestions(uniqueSuggestions);
          setShowSuggestions(uniqueSuggestions.length > 0);
        } catch (err) {
          // Fallback to local filtering
          const filtered = allCoins
            .filter((coin) => coin.toLowerCase().includes(newCoin.toLowerCase()))
            .filter((coin) => !coins.includes(coin))
            .slice(0, 8);
          setSuggestions(filtered);
          setShowSuggestions(filtered.length > 0);
        }
      } else {
        setSuggestions([]);
        setShowSuggestions(false);
        setSearchResults(null);
      }
    };

    const timeoutId = setTimeout(fetchSearchResults, 300); // Debounce 300ms
    return () => clearTimeout(timeoutId);
  }, [newCoin, allCoins, coins]);

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setShowSuggestions(false);
        setShowCoinList(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const addCoin = (coin) => {
    let targetCoin = coin;

    // If entered via keyboard/button without specific coin, find best match
    if (!targetCoin) {
      if (searchResults?.exact_match) {
        targetCoin = searchResults.exact_match;
      } else if (suggestions.length > 0) {
        // Prefer exact match from suggestions if available (e.g. typing "bitcoi")
        const exactMatch = suggestions.find((s) => s.toLowerCase() === newCoin.toLowerCase());
        targetCoin = exactMatch || suggestions[0];
      } else {
        targetCoin = newCoin;
      }
    }

    if (!targetCoin) return;

    const coinId = targetCoin.toLowerCase().trim();
    if (!coinId) return;

    if (coins.includes(coinId)) {
      setError(`"${targetCoin}" is already in your list!`);
      // Don't clear input on error so user can fix it
    } else {
      setCoins([...coins, coinId]);
      setNewCoin("");
      setShowSuggestions(false);
    }
  };

  const removeCoin = (coin) => {
    setCoins(coins.filter((c) => c !== coin));
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      addCoin();
    }
  };

  const getCorrelationColor = (value) => {
    if (value >= 0.8) return "#10b981";
    if (value >= 0.5) return "#f59e0b";
    if (value >= 0) return "#f97316";
    return "#ef4444";
  };

  const getCorrelationLabel = (value) => {
    if (value >= 0.8) return "Strong";
    if (value >= 0.5) return "Moderate";
    if (value >= 0) return "Weak";
    return "Negative";
  };

  return (
    <div className="App">
      {/* Error Popup */}
      {error && (
        <div className="error-overlay" onClick={() => setError(null)}>
          <div className="error-popup" onClick={(e) => e.stopPropagation()}>
            <div className="error-icon">⚠️</div>
            <h3>Error</h3>
            <p>{error}</p>
            <button onClick={() => setError(null)}>Close</button>
          </div>
        </div>
      )}

      {/* Hero Section */}
      <header className="hero">
        <div className="hero-content">
          <h1>📊 Crypto Correlation Analyzer</h1>
          <p className="subtitle">Discover how cryptocurrencies move together. Track correlations, analyze trends, and make smarter trading decisions.</p>
        </div>
        <div className="hero-stats">
          <div className="stat">
            <span className="stat-value">{coins.length}</span>
            <span className="stat-label">Coins</span>
          </div>
          <div className="stat">
            <span className="stat-value">{days}d</span>
            <span className="stat-label">Timeframe</span>
          </div>
        </div>
      </header>

      {/* Controls Section */}
      <div className="controls-card">
        <div className="search-section" ref={searchRef}>
          <label className="section-label">🔍 Add Cryptocurrency</label>
          <div className="search-container">
            <input
              type="text"
              value={newCoin}
              onChange={(e) => setNewCoin(e.target.value)}
              onKeyDown={handleKeyDown}
              onFocus={() => newCoin.length === 0 && setShowCoinList(true)}
              placeholder="Type to search (e.g., stellar, cardano)..."
              className="search-input"
            />
            <button onClick={() => addCoin()} className="add-btn" disabled={!newCoin}>
              + Add
            </button>
          </div>

          {/* Google-style Autocomplete Suggestions */}
          {showSuggestions && (
            <div className="suggestions-dropdown">
              {searchResults?.categories?.exact_match && searchResults.categories.exact_match.length > 0 && (
                <div className="suggestion-category">
                  <div className="category-label">🎯 Exact Match</div>
                  {searchResults.categories.exact_match
                    .filter((coin) => !coins.includes(coin))
                    .slice(0, 3)
                    .map((coin) => (
                      <div key={`exact-${coin}`} className="suggestion-item exact-match" onClick={() => addCoin(coin)}>
                        <span className="coin-icon">🎯</span>
                        <span className="coin-name">{coin.charAt(0).toUpperCase() + coin.slice(1)}</span>
                        <span className="match-badge">Exact</span>
                      </div>
                    ))}
                </div>
              )}

              {searchResults?.categories?.similar && searchResults.categories.similar.length > 0 && (
                <div className="suggestion-category">
                  <div className="category-label">💡 Similar Results</div>
                  {searchResults.categories.similar
                    .filter((coin) => !coins.includes(coin))
                    .map((coin) => (
                      <div key={`similar-${coin}`} className="suggestion-item" onClick={() => addCoin(coin)}>
                        <span className="coin-icon">🪙</span>
                        <span className="coin-name">{coin.charAt(0).toUpperCase() + coin.slice(1)}</span>
                      </div>
                    ))}
                </div>
              )}

              {suggestions.length > 0 && (!searchResults?.categories?.exact_match || searchResults.categories.exact_match.length === 0) && (!searchResults?.categories?.similar || searchResults.categories.similar.length === 0) && (
                <div className="suggestion-category">
                  <div className="category-label">🔍 Suggestions</div>
                  {suggestions.map((coin) => (
                    <div key={coin} className="suggestion-item" onClick={() => addCoin(coin)}>
                      <span className="coin-icon">🪙</span>
                      <span className="coin-name">{coin.charAt(0).toUpperCase() + coin.slice(1)}</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Bitget Recommended */}
              {searchResults?.categories?.bitget_recommended && searchResults.categories.bitget_recommended.length > 0 && (
                <div className="suggestion-category">
                  <div className="category-label">⚡ Recommended from Bitget</div>
                  {searchResults.categories.bitget_recommended
                    .filter((coin) => !coins.includes(coin))
                    .slice(0, 5)
                    .map((coin) => (
                      <div key={`bitget-${coin}`} className="suggestion-item bitget-recommended" onClick={() => addCoin(coin)}>
                        <span className="coin-icon">💎</span>
                        <span className="coin-name">{coin.charAt(0).toUpperCase() + coin.slice(1)}</span>
                        <span className="source-badge">Bitget</span>
                      </div>
                    ))}
                </div>
              )}
            </div>
          )}

          {/* Full Coin List */}
          {showCoinList && (
            <div className="suggestions-dropdown">
              <div className="suggestions-header">📋 Available Coins ({allCoins.length})</div>
              <div className="coin-grid">
                {allCoins.map((coin) => (
                  <div key={coin} className={`coin-chip ${coins.includes(coin) ? "selected" : ""}`} onClick={() => !coins.includes(coin) && addCoin(coin)}>
                    {coin.charAt(0).toUpperCase() + coin.slice(1)}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Selected Coins */}
        <div className="selected-coins">
          <label className="section-label">✅ Selected Coins</label>
          <div className="coin-tags">
            {coins.map((coin) => (
              <span key={coin} className="coin-tag">
                <span className="tag-icon">🪙</span>
                {coin.charAt(0).toUpperCase() + coin.slice(1)}
                <button onClick={() => removeCoin(coin)} className="remove-btn">
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>

        {/* Days Selector */}
        <div className="days-section">
          <label className="section-label">📅 Timeframe</label>
          <div className="days-buttons">
            {[7, 30, 90].map((d) => (
              <button key={d} onClick={() => setDays(d)} className={`day-btn ${days === d ? "active" : ""}`}>
                {d} Days
              </button>
            ))}
          </div>
          <button onClick={fetchCorrelationMatrix} disabled={loading} className="update-btn">
            {loading ? (
              <>
                <span className="spinner">↻</span> Loading...
              </>
            ) : (
              "🔄 Update Data"
            )}
          </button>
        </div>
      </div>

      {/* Correlation Matrix */}
      {matrix && (
        <div className="matrix-card">
          <h2>📈 Correlation Matrix</h2>
          <p className="matrix-description">Values range from -1 (opposite movement) to +1 (perfect correlation)</p>

          <div className="matrix-table-wrapper">
            <table className="matrix-table">
              <thead>
                <tr>
                  <th>Coin</th>
                  {coins.map((coin) => (
                    <th key={coin}>{coin.charAt(0).toUpperCase() + coin.slice(1)}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {coins.map((coinA) => (
                  <tr key={coinA}>
                    <td className="row-header">{coinA.charAt(0).toUpperCase() + coinA.slice(1)}</td>
                    {coins.map((coinB) => {
                      const value = matrix[coinA][coinB];
                      return (
                        <td
                          key={`${coinA}-${coinB}`}
                          className="matrix-cell"
                          style={{
                            backgroundColor: getCorrelationColor(value),
                            color: value > 0.3 ? "white" : "#1f2937",
                          }}
                          title={`${getCorrelationLabel(value)} correlation: ${value.toFixed(3)}`}
                        >
                          <span className="cell-value">{value.toFixed(2)}</span>
                          <span className="cell-label">{getCorrelationLabel(value)}</span>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Legend */}
          <div className="legend">
            <h3>📊 Legend</h3>
            <div className="legend-grid">
              {[
                { color: "#10b981", label: "Strong (0.8-1.0)", desc: "Move together" },
                { color: "#f59e0b", label: "Moderate (0.5-0.8)", desc: "Somewhat related" },
                { color: "#f97316", label: "Weak (0.0-0.5)", desc: "Weak relationship" },
                { color: "#ef4444", label: "Negative (-1.0-0.0)", desc: "Opposite movement" },
              ].map((item) => (
                <div key={item.label} className="legend-item">
                  <div className="legend-color" style={{ backgroundColor: item.color }}></div>
                  <div className="legend-text">
                    <strong>{item.label}</strong>
                    <span>{item.desc}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!matrix && !loading && !error && (
        <div className="empty-state">
          <div className="empty-icon">📊</div>
          <h3>No Data Yet</h3>
          <p>Add coins and click "Update Data" to see correlation matrix</p>
        </div>
      )}

      {/* Footer */}
      <footer className="footer">
        <p>📡 Data from CoinGecko API • Built with React + FastAPI</p>
      </footer>
    </div>
  );
}

export default App;
