# 🚀 Deployment Guide

Deploy **Crypto Correlation Analyzer** ke cloud gratis!

---

## 📋 Overview Arsitektur

```
User → Vercel (Frontend React)
            ↓
      API Calls
            ↓
    Render (Backend FastAPI)
            ↓
      CoinGecko API
```

---

## 🎯 Step 1: Deploy Backend ke Render

### 1.1 Buat Akun Render
• Buka https://render.com
• Sign up dengan GitHub account

### 1.2 New Web Service
• Click **"New +"** → **"Web Service"**
• Connect GitHub repo: `kilyfa-agentai/crypto-correlation`
• Pilih branch: `main`

### 1.3 Configure Service
| Setting | Value |
|---------|-------|
| Name | `crypto-correlation-api` |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app:app --host 0.0.0.0 --port 10000` |
| Root Directory | `backend` |
| Plan | Free |

### 1.4 Deploy
• Click **"Create Web Service"**
• Tunggu 2-3 menit
• Dapatkan URL: `https://crypto-correlation-api.onrender.com`

**Simpan URL ini!** Nanti dipakai di Vercel.

---

## 🎯 Step 2: Deploy Frontend ke Vercel

### 2.1 Buat Akun Vercel
• Buka https://vercel.com
• Sign up dengan GitHub account

### 2.2 Import Project
• Click **"Add New Project"**
• Import GitHub repo: `kilyfa-agentai/crypto-correlation`

### 2.3 Configure Project
| Setting | Value |
|---------|-------|
| Framework | Create React App |
| Root Directory | `frontend` |
| Build Command | `npm run build` |
| Output Directory | `build` |

### 2.4 Environment Variables
Click **"Environment Variables"** lalu tambah:

```
REACT_APP_API_URL=https://crypto-correlation-api.onrender.com
```

**Ganti URL** dengan URL backend Render kamu!

### 2.5 Deploy
• Click **"Deploy"**
• Tunggu 1-2 menit
• Dapatkan URL: `https://crypto-correlation.vercel.app`

---

## ✅ Testing

Buka URL Vercel di browser:
• Frontend: `https://crypto-correlation.vercel.app` ✅
• API: `https://crypto-correlation-api.onrender.com/docs` ✅

---

## 🔧 Troubleshooting

### CORS Error
Kalau frontend error "CORS", tambahkan di `backend/app.py`:
```python
allow_origins=["https://crypto-correlation.vercel.app"]
```

### API Timeout
Render free tier sleep setelah 15 menit idle.
• First request akan lambat (30 detik)
• Request selanjutnya cepat

### Rate Limit CoinGecko
Kalau banyak user, bisa kena rate limit.
Solusi: Implementasi caching (nanti)

---

## 📊 Cost

| Service | Cost | Limit |
|---------|------|-------|
| Render | Free | 750 hours/month, sleep after 15 min idle |
| Vercel | Free | 100 GB bandwidth, unlimited requests |
| **Total** | **$0** | - |

---

## 🎉 Done!

Website live di internet! Share link ke teman-teman 🚀

Ada masalah saat deploy? Saya bisa bantu debug! 🦊
