# 🏦 BIST Finansal Analiz Motoru — AI Destekli

Borsa İstanbul (BIST) hisse senetlerini analiz eden, **3 Ajanlı Yapay Zeka Mimarisi** ile Al/Sat/Tut kararları üreten full-stack web uygulaması.

## 🏗️ Mimari

```
┌──────────────────────────────────────────────────────┐
│                    FRONTEND (JS)                      │
│   index.html + TradingView Charts + Glassmorphism UI  │
└──────────┬───────────────────────────────┬────────────┘
           │  REST API (fetch)             │  WebSocket
           ▼                               ▼
┌──────────────────────────────────────────────────────┐
│                  BACKEND (FastAPI)                     │
│                                                       │
│  ┌─────────────┐  ┌───────────────┐  ┌─────────────┐│
│  │  yfinance    │  │  pandas-ta    │  │ Claude API  ││
│  │  Veri Çekme  │→ │  İndikatörler │→ │ 3 Ajanlı AI ││
│  └─────────────┘  └───────────────┘  └─────────────┘│
└──────────────────────────────────────────────────────┘
```

### 3 Ajanlı Prompt Mimarisi

1. **🔍 Teknik Analist** — RSI, MACD, SMA, Bollinger yorumlar
2. **📊 Temel Analist** — F/K, PD/DD, piyasa değeri analizi
3. **⚖️ Risk Yöneticisi** — İki ajanın çıktılarını birleştirerek final karar verir

## 🚀 Kurulum

### Gereksinimler
- Python 3.11+
- Node.js (opsiyonel, Live Server için)
- Claude API Key ([console.anthropic.com](https://console.anthropic.com))

### Backend Kurulumu

```bash
cd backend

# Sanal ortam oluştur
python -m venv venv
venv\Scripts\activate   # Windows

# Bağımlılıkları kur
pip install -r requirements.txt

# .env dosyasını oluştur
copy .env.example .env
# .env dosyasını düzenle ve ANTHROPIC_API_KEY değerini gir

# Sunucuyu başlat
python run.py
```

Backend `http://localhost:8000` adresinde çalışacaktır.  
Swagger UI: `http://localhost:8000/docs`

### Frontend Kurulumu

```bash
# VS Code Live Server ile veya herhangi bir HTTP sunucusu ile
cd frontend

# Python ile basit HTTP sunucusu:
python -m http.server 5500
```

Frontend `http://localhost:5500` adresinde açılacaktır.

## 📡 API Endpoints

| Endpoint | Method | Açıklama |
|:---|:---|:---|
| `/api/v1/market/stock/{symbol}` | GET | Hisse fiyatı + teknik indikatörler |
| `/api/v1/market/history/{symbol}` | GET | Geçmiş OHLCV verileri (grafik için) |
| `/api/v1/market/indices` | GET | BIST endeksleri (XU100, XU030) |
| `/api/v1/analysis/full/{symbol}` | POST | 3 Ajanlı AI analizi |
| `/api/v1/analysis/quick/{symbol}` | GET | Algoritmik hızlı sinyal |
| `/ws/ticker/{symbol}` | WebSocket | Canlı fiyat stream'i |

## 🛠️ Teknoloji Stack

| Katman | Teknoloji |
|:---|:---|
| Backend | Python 3.11+, FastAPI, Uvicorn |
| Veri Kaynağı | yfinance (`.IS` suffix) |
| İndikatörler | pandas-ta |
| AI | Claude 3.5 Sonnet (Anthropic) |
| Frontend | HTML5, CSS3, Vanilla JS |
| Grafikler | TradingView Lightweight Charts v4 |
| İkonlar | Lucide Icons |

## ⚠️ Uyarı

Bu uygulama yatırım tavsiyesi değildir. BIST verileri 15 dakika gecikmelidir.
