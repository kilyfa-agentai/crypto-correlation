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

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Step 1: Clone Repository
```bash
git clone https://github.com/kilyfa-agentai/crypto-correlation.git
cd crypto-correlation
```

### Step 2: Setup Backend
```bash
cd backend

# Create virtual environment (optional tapi direkomendasikan)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# atau: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run backend server
python app.py
```

Backend akan jalan di: **http://localhost:8000**

API Documentation (Swagger UI): **http://localhost:8000/docs**

### Step 3: Setup Frontend (Terminal Baru)
```bash
cd frontend

# Install dependencies
npm install

# Run React development server
npm start
```

Frontend akan jalan di: **http://localhost:3000**

### Step 4: Open Browser
Buka **http://localhost:3000** untuk melihat aplikasi.

---

## 📊 Cara Pakai

### 1. Correlation Matrix
• Buka http://localhost:3000
• Default coins: Bitcoin, Ethereum, Solana
• Click "Update" untuk generate matrix
• Warna hijau = korelasi kuat, merah = lemah/negatif

### 2. Tambah Coin Baru
• Ketik nama coin di input (contoh: `cardano`, `polkadot`)
• Click "Add Coin"
• Click "Update" untuk recalculate

### 3. Ganti Timeframe
• Pilih 7 days / 30 days / 90 days
• Click "Update"

---

## 🔌 API Endpoints (Untuk Testing)

### Correlation Matrix
```bash
curl "http://localhost:8000/api/correlation-matrix?coins=bitcoin,ethereum,solana&days=30"
```

### Rolling Correlation
```bash
curl "http://localhost:8000/api/rolling-correlation?coin_a=ethereum&coin_b=bitcoin&days=30&window=7"
```

### Beta Coefficient
```bash
curl "http://localhost:8000/api/beta?coins=ethereum,solana,cardano&days=30"
```

---

## ⚠️ Catatan Penting

### Rate Limiting
• CoinGecko Free API: 10-30 calls per menit
• Untuk 1 user (kamu doang): Aman ✅
• Jangan spam click "Update" berkali-kali

### Tips
• Tunggu 1-2 detik setelah click Update
• Kalau error, coba refresh page
• Backend harus jalan dulu sebelum frontend

---

## 🛠️ Tech Stack Details

| Komponen | Teknologi |
|----------|-----------|
| Backend | Python 3.8+ + FastAPI |
| Frontend | React 18 + Chart.js |
| Data API | CoinGecko (Free) |
| No Database | Direct API calls (simple) |

## API Endpoints

- `GET /api/correlation-matrix` - Get correlation matrix for selected coins
- `GET /api/rolling-correlation` - Get time-varying correlation
- `GET /api/beta` - Get beta coefficient for coins

## License

MIT
