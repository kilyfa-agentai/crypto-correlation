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
  const [aiInsights, setAiInsights] = useState("");
  const [aiLoading, setAiLoading] = useState(false);
  const [aiQuestion, setAiQuestion] = useState("");

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

  const parseMarkdown = (text) => {
    if (!text) return null;

    // Split by lines
    const lines = text.split("\n");

    return lines.map((line, lineIndex) => {
      // Handle bold **text**
      let content = line.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");

      // Handle italic *text*
      content = content.replace(/\*(.+?)\*/g, "<em>$1</em>");

      // Handle inline code `text`
      content = content.replace(/`(.+?)`/g, "<code>$1</code>");

      // Check if it's a list item
      if (line.trim().startsWith("- ")) {
        const listContent = content.replace(/^- /, "");
        return <li key={lineIndex} dangerouslySetInnerHTML={{ __html: listContent }} />;
      }

      // Check if it's a numbered list
      if (/^\d+\.\s/.test(line.trim())) {
        const listContent = content.replace(/^\d+\.\s/, "");
        return <li key={lineIndex} dangerouslySetInnerHTML={{ __html: listContent }} />;
      }

      // Regular paragraph
      if (line.trim()) {
        return <p key={lineIndex} dangerouslySetInnerHTML={{ __html: content }} />;
      }

      // Empty line
      return <br key={lineIndex} />;
    });
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

  const getAIInsights = async (question = "") => {
    if (!matrix) {
      setAiInsights("⚠️ No correlation data available yet. Please wait for the correlation matrix to load.");
      return;
    }

    setAiLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/ai/insights`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          coins,
          matrix,
          days,
          question,
        }),
      });

      if (!response.ok) throw new Error("Failed to get AI insights");

      const data = await response.json();
      setAiInsights(data.insights);
      setAiQuestion("");
    } catch (err) {
      setAiInsights(`❌ Error: ${err.message}\n\nPlease make sure the backend is running and the Gemini API key is configured.`);
    }
    setAiLoading(false);
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

      <div className="main-layout">
        {/* 3:1 Layout */}
        {/* Left side - Correlation Analysis (75%) */}
        <div className="correlation-section">
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
        {/* End correlation-section */}

        {/* Right side - AI Insights (25%) */}
        <div className="ai-section">
          <div className="ai-header">
            <h2>🤖 AI Insights</h2>
            <p>Powered by Gemini</p>
          </div>

          <div className="ai-controls">
            <button onClick={() => getAIInsights()} disabled={!matrix || aiLoading} className="btn-ai-analyze">
              {aiLoading ? "Analyzing..." : "Analyze Correlations"}
            </button>

            <div className="ai-question-box">
              <input
                type="text"
                value={aiQuestion}
                onChange={(e) => setAiQuestion(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && getAIInsights(aiQuestion)}
                placeholder="Ask AI about the data..."
                className="ai-question-input"
                disabled={!matrix || aiLoading}
              />
              <button onClick={() => getAIInsights(aiQuestion)} disabled={!matrix || aiLoading || !aiQuestion} className="btn-ai-ask">
                Ask
              </button>
            </div>
          </div>

          <div className="ai-insights-box">
            {aiLoading && (
              <div className="ai-loading">
                <div className="spinner"></div>
                <p>AI is analyzing your data...</p>
              </div>
            )}

            {!aiLoading && aiInsights && <div className="ai-content">{parseMarkdown(aiInsights)}</div>}

            {!aiLoading && !aiInsights && (
              <div className="ai-empty">
                <p>Click "Analyze Correlations" to get AI-powered insights about your cryptocurrency correlations.</p>
                <p className="ai-hint">Or ask a specific question about the data!</p>
              </div>
            )}
          </div>
        </div>
        {/* End ai-section */}
      </div>
      {/* End main-layout */}

      <footer className="footer">
        <p>Data from CoinGecko API • Built with React + FastAPI + Gemini AI</p>
      </footer>
    </div>
  );
}

export default App;
