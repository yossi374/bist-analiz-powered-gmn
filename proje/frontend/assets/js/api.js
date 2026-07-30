const API = {
  wsConnection: null,
  wsSymbol: null,
  wsReconnectTimer: null,
  wsOnMessage: null,

  async fetchStockData(symbol) {
    try {
      const res = await fetch(`${CONFIG.API_BASE_URL}/market/stock/${symbol}`);
      if (!res.ok) throw new Error('Stock data fetch failed');
      return await res.json();
    } catch (err) {
      console.error(err);
      return { error: true, message: err.message };
    }
  },

  async fetchStockHistory(symbol, period, interval) {
    try {
      const res = await fetch(`${CONFIG.API_BASE_URL}/market/history/${symbol}?period=${period}&interval=${interval}`);
      if (!res.ok) throw new Error('History data fetch failed');
      return await res.json();
    } catch (err) {
      console.error(err);
      return { error: true, message: err.message };
    }
  },

  async fetchIndices() {
    try {
      const res = await fetch(`${CONFIG.API_BASE_URL}/market/indices`);
      if (!res.ok) throw new Error('Indices fetch failed');
      return await res.json();
    } catch (err) {
      console.error(err);
      return { error: true, message: err.message };
    }
  },

  async requestFullAnalysis(symbol) {
    try {
      const res = await fetch(`${CONFIG.API_BASE_URL}/analysis/full/${symbol}`, { method: 'POST' });
      if (!res.ok) throw new Error('Analysis request failed');
      return await res.json();
    } catch (err) {
      console.error(err);
      return { error: true, message: err.message };
    }
  },

  async requestQuickAnalysis(symbol) {
    try {
      const res = await fetch(`${CONFIG.API_BASE_URL}/analysis/quick/${symbol}`);
      if (!res.ok) throw new Error('Quick analysis request failed');
      return await res.json();
    } catch (err) {
      console.error(err);
      return { error: true, message: err.message };
    }
  },

  connectWebSocket(symbol, onMessage) {
    this.disconnectWebSocket();
    this.wsSymbol    = symbol;
    this.wsOnMessage = onMessage;
    this._openWS(symbol, onMessage);
  },

  _openWS(symbol, onMessage) {
    try {
      this.wsConnection = new WebSocket(`${CONFIG.WS_BASE_URL}/ticker/${symbol}`);

      this.wsConnection.onopen = () => {
        console.log(`WS connected: ${symbol}`);
        UI.setConnectionStatus(true);
        if (this.wsReconnectTimer) { clearTimeout(this.wsReconnectTimer); this.wsReconnectTimer = null; }
      };

      this.wsConnection.onmessage = (event) => {
        try { onMessage(JSON.parse(event.data)); } catch(e) {}
      };

      this.wsConnection.onerror = (err) => {
        console.warn('WS error', err);
      };

      this.wsConnection.onclose = () => {
        console.log('WS closed, reconnecting in 5s...');
        UI.setConnectionStatus(false);
        // Aynı sembol için 5 saniye sonra yeniden bağlan
        if (this.wsSymbol === symbol) {
          this.wsReconnectTimer = setTimeout(() => {
            if (this.wsSymbol === symbol) this._openWS(symbol, onMessage);
          }, 5000);
        }
      };
    } catch (err) {
      console.error('WS setup failed', err);
    }
  },

  disconnectWebSocket() {
    this.wsSymbol = null;
    if (this.wsReconnectTimer) { clearTimeout(this.wsReconnectTimer); this.wsReconnectTimer = null; }
    if (this.wsConnection) {
      this.wsConnection.onclose = null; // Yeniden bağlanmayı engelle
      this.wsConnection.close();
      this.wsConnection = null;
    }
  }
};
