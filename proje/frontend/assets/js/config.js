const CONFIG = {
  API_BASE_URL: '/api/v1',
  WS_BASE_URL: (window.location.protocol === 'https:' ? 'wss://' : 'ws://') + window.location.host + '/ws',
  
  POPULAR_STOCKS: [
    { symbol: 'THYAO', name: 'Türk Hava Yolları' },
    { symbol: 'GARAN', name: 'Garanti BBVA' },
    { symbol: 'AKBNK', name: 'Akbank' },
    { symbol: 'SISE', name: 'Şişecam' },
    { symbol: 'ASELS', name: 'Aselsan' },
    { symbol: 'EREGL', name: 'Ereğli Demir Çelik' },
    { symbol: 'KCHOL', name: 'Koç Holding' },
    { symbol: 'TUPRS', name: 'Tüpraş' },
    { symbol: 'SAHOL', name: 'Sabancı Holding' },
    { symbol: 'BIMAS', name: 'BİM Mağazaları' },
  ],
  
  CHART_PERIODS: [
    { label: '1H', period: '5d', interval: '1h' },
    { label: '1G', period: '1mo', interval: '1d' },
    { label: '3A', period: '3mo', interval: '1d' },
    { label: '6A', period: '6mo', interval: '1d' },
    { label: '1Y', period: '1y', interval: '1wk' },
  ],
  
  REFRESH_INTERVAL: 10000,
};
