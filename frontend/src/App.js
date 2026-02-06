import React, { useState, useEffect } from 'react';
import { Line, Scatter } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import './App.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [coins, setCoins] = useState(['bitcoin', 'ethereum', 'solana']);
  const [days, setDays] = useState(30);
  const [matrix, setMatrix] = useState(null);
  const [loading, setLoading] = useState(false);
  const [newCoin, setNewCoin] = useState('');

  const fetchCorrelationMatrix = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/correlation-matrix?coins=${coins.join(',')}&days=${days}`);
      const data = await response.json();
      setMatrix(data.matrix);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchCorrelationMatrix();
  }, []);

  const addCoin = () => {
    if (newCoin && !coins.includes(newCoin)) {
      setCoins([...coins, newCoin]);
      setNewCoin('');
    }
  };

  const removeCoin = (coin) => {
    setCoins(coins.filter(c => c !== coin));
  };

  const getCorrelationColor = (value) => {
    if (value >= 0.8) return '#22c55e'; // Green - strong
    if (value >= 0.5) return '#eab308'; // Yellow - moderate
    if (value >= 0) return '#f97316';   // Orange - weak
    return '#ef4444';                    // Red - negative
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>📊 Crypto Correlation Analyzer</h1>
        <p>Track how cryptocurrencies move together</p>
      </header>

      <div className="controls">
        <div className="coin-input">
          <input
            type="text"
            value={newCoin}
            onChange={(e) => setNewCoin(e.target.value)}
            placeholder="Add coin (e.g., cardano)"
          />
          <button onClick={addCoin}>Add Coin</button>
        </div>

        <div className="coin-list">
          {coins.map(coin => (
            <span key={coin} className="coin-tag">
              {coin}
              <button onClick={() => removeCoin(coin)}>×</button>
            </span>
          ))}
        </div>

        <div className="days-selector">
          <label>Days: </label>
          <select value={days} onChange={(e) => setDays(Number(e.target.value))}>
            <option value={7}>7 days</option>
            <option value={30}>30 days</option>
            <option value={90}>90 days</option>
          </select>
          <button onClick={fetchCorrelationMatrix} disabled={loading}>
            {loading ? 'Loading...' : 'Update'}
          </button>
        </div>
      </div>

      {matrix && (
        <div className="matrix-container">
          <h2>Correlation Matrix</h2>
          <table className="correlation-table">
            <thead>
              <tr>
                <th>Coin</th>
                {coins.map(coin => <th key={coin}>{coin}</th>)}
              </tr>
            </thead>
            <tbody>
              {coins.map(coinA => (
                <tr key={coinA}>
                  <td><strong>{coinA}</strong></td>
                  {coins.map(coinB => (
                    <td
                      key={`${coinA}-${coinB}`}
                      style={{
                        backgroundColor: getCorrelationColor(matrix[coinA][coinB]),
                        color: matrix[coinA][coinB] > 0.5 ? 'white' : 'black'
                      }}
                    >
                      {matrix[coinA][coinB].toFixed(2)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="legend">
        <h3>Correlation Guide:</h3>
        <div className="legend-item">
          <span className="color-box" style={{background: '#22c55e'}}></span>
          <span>Strong (0.8-1.0) - Move together</span>
        </div>
        <div className="legend-item">
          <span className="color-box" style={{background: '#eab308'}}></span>
          <span>Moderate (0.5-0.8) - Somewhat related</span>
        </div>
        <div className="legend-item">
          <span className="color-box" style={{background: '#f97316'}}></span>
          <span>Weak (0.0-0.5) - Weak relationship</span>
        </div>
        <div className="legend-item">
          <span className="color-box" style={{background: '#ef4444'}}></span>
          <span>Negative (-1.0-0.0) - Move opposite</span>
        </div>
      </div>
    </div>
  );
}

export default App;
