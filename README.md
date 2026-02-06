# Crypto Correlation Analyzer

Track correlations between cryptocurrencies with real-time data analysis.

## Features

- **Correlation Matrix**: Visualize correlations between selected coins
- **BTC Correlation Focus**: Track how altcoins move relative to Bitcoin
- **Rolling Correlation**: See how correlations change over time
- **Custom Coin Selection**: Add any coin from CoinGecko
- **Beta Coefficient**: Measure volatility relative to BTC

## Tech Stack

- **Backend**: Python (FastAPI) + PostgreSQL
- **Frontend**: React + Chart.js
- **Data Source**: CoinGecko API (Free tier)

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## API Endpoints

- `GET /api/correlation-matrix` - Get correlation matrix for selected coins
- `GET /api/rolling-correlation` - Get time-varying correlation
- `GET /api/beta` - Get beta coefficient for coins

## License

MIT
