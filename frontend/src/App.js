import React, { useState, useEffect, useCallback } from "react";
import "./App.css";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

function App() {
  const [coins, setCoins] = useState(["bitcoin", "ethereum", "solana"]);
  const [days, setDays] = useState(30);
  const [matrix, setMatrix] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [error, setError] = useState(null);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [allCoins, setAllCoins] = useState([]); // Cache all coins here

  // Fetch ALL coins once on mount
  useEffect(() => {
    const fetchAllCoins = async () => {
      try {
        const response = await fetch(`${API_URL}/api/coins/all`);
        const data = await response.json();
        setAllCoins(data.coins || []);
        console.log(`✓ Loaded ${data.total} coins from cache`);
      } catch (err) {
        console.error("Failed to load coins:", err);
        // Fallback to empty array
        setAllCoins([]);
      }
    };
    fetchAllCoins();
  }, []); // Only run once on mount

  const fetchCorrelationMatrix = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/correlation-matrix?coins=${coins.join(",")}&days=${days}`);
      if (!response.ok) throw new Error("Failed to fetch data");
      const data = await response.json();
      setMatrix(data.matrix);
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  }, [coins, days]);

  useEffect(() => {
    fetchCorrelationMatrix();
  }, [fetchCorrelationMatrix]);

  // Client-side search - NO API CALLS!
  useEffect(() => {
    if (searchTerm.length >= 2 && allCoins.length > 0) {
      const query = searchTerm.toLowerCase();

      // Search in id, name, and symbol
      const matches = allCoins
        .filter((coin) => {
          const id = coin.id.toLowerCase();
          const name = coin.name.toLowerCase();
          const symbol = coin.symbol.toLowerCase();

          return id.includes(query) || name.includes(query) || symbol.includes(query);
        })
        .filter((coin) => !coins.includes(coin.id)) // Exclude already selected
        .slice(0, 10); // Limit to 10 results

      // Format for display
      const formattedSuggestions = matches.map((coin) => ({
        id: coin.id,
        name: coin.name,
        symbol: coin.symbol,
        category: coin.category,
      }));

      setSuggestions(formattedSuggestions);
      setShowSuggestions(true);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  }, [searchTerm, coins, allCoins]); // Re-run when searchTerm changes

  const addCoin = (coin) => {
    const coinId = typeof coin === "object" ? coin.id : coin || searchTerm;
    if (coinId && !coins.includes(coinId.toLowerCase())) {
      setCoins([...coins, coinId.toLowerCase()]);
      setSearchTerm("");
      setSuggestions([]);
      setShowSuggestions(false);
    }
  };

  const removeCoin = (coin) => {
    setCoins(coins.filter((c) => c !== coin));
  };

  const getColor = (value) => {
    if (value >= 0.7) return "#10b981";
    if (value >= 0.4) return "#f59e0b";
    if (value >= 0) return "#ef4444";
    return "#dc2626";
  };

  const getLabel = (value) => {
    if (value >= 0.7) return "Strong";
    if (value >= 0.4) return "Moderate";
    if (value >= 0) return "Weak";
    return "Negative";
  };

  return (
    <div className="app">
      <header className="header">
        <h1>Crypto Correlation Analyzer</h1>
        <p>Analyze price correlations between cryptocurrencies</p>
      </header>

      {error && (
        <div className="alert alert-error" onClick={() => setError(null)}>
          {error}
        </div>
      )}

      <div className="container">
        <div className="control-panel">
          <div className="search-box">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  if (suggestions.length > 0) {
                    addCoin(suggestions[0]);
                  } else {
                    addCoin();
                  }
                }
              }}
              onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
              onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
              placeholder={allCoins.length === 0 ? "Loading coins..." : "Search cryptocurrency..."}
              className="search-input"
              disabled={allCoins.length === 0}
            />
            <button onClick={() => addCoin()} disabled={!searchTerm} className="btn-add">
              Add
            </button>
            {showSuggestions && suggestions.length > 0 && (
              <div className="suggestions">
                {suggestions.map((suggestion) => (
                  <div key={suggestion.id} className="suggestion-item" onClick={() => addCoin(suggestion)}>
                    <div className="suggestion-icon">
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <circle cx="12" cy="12" r="10" />
                        <path d="M12 6v6l4 2" />
                      </svg>
                    </div>
                    <div className="suggestion-content">
                      <div className="suggestion-title">
                        <span className="coin-name">{suggestion.name}</span>
                        <span className="coin-symbol">({suggestion.symbol})</span>
                      </div>
                      <div className="suggestion-category">{suggestion.category}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="selected-coins">
            {coins.map((coin) => (
              <div key={coin} className="coin-badge">
                {coin}
                <button onClick={() => removeCoin(coin)} className="btn-remove">
                  ×
                </button>
              </div>
            ))}
          </div>

          <div className="timeframe">
            <label>Timeframe:</label>
            <div className="btn-group">
              {[7, 30, 90].map((d) => (
                <button key={d} onClick={() => setDays(d)} className={`btn-day ${days === d ? "active" : ""}`}>
                  {d} days
                </button>
              ))}
            </div>
          </div>

          <button onClick={fetchCorrelationMatrix} disabled={loading} className="btn-update">
            {loading ? "Loading..." : "Update Data"}
          </button>
        </div>

        {matrix && (
          <div className="matrix-container">
            <h2>Correlation Matrix</h2>
            <div className="matrix-wrapper">
              <table className="matrix-table">
                <thead>
                  <tr>
                    <th></th>
                    {coins.map((coin) => (
                      <th key={coin}>{coin}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {coins.map((coinA) => (
                    <tr key={coinA}>
                      <td className="row-label">{coinA}</td>
                      {coins.map((coinB) => {
                        const value = matrix[coinA]?.[coinB];
                        // Handle missing data
                        if (value === undefined || value === null) {
                          return (
                            <td key={`${coinA}-${coinB}`} className="matrix-cell matrix-cell-loading" title="Loading...">
                              -
                            </td>
                          );
                        }
                        return (
                          <td key={`${coinA}-${coinB}`} className="matrix-cell" style={{ backgroundColor: getColor(value) }} title={`${getLabel(value)}: ${value.toFixed(3)}`}>
                            {value.toFixed(2)}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="legend">
              <div className="legend-item">
                <span className="legend-color" style={{ backgroundColor: "#10b981" }}></span>
                <span>Strong (0.7+)</span>
              </div>
              <div className="legend-item">
                <span className="legend-color" style={{ backgroundColor: "#f59e0b" }}></span>
                <span>Moderate (0.4-0.7)</span>
              </div>
              <div className="legend-item">
                <span className="legend-color" style={{ backgroundColor: "#ef4444" }}></span>
                <span>Weak (0-0.4)</span>
              </div>
              <div className="legend-item">
                <span className="legend-color" style={{ backgroundColor: "#dc2626" }}></span>
                <span>Negative (&lt;0)</span>
              </div>
            </div>
          </div>
        )}
      </div>

      <footer className="footer">
        <p>Data from CoinGecko API • Built with React + FastAPI</p>
      </footer>
    </div>
  );
}

export default App;
