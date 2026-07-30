const App = {
  currentSymbol: null,
  currentPeriod: '6mo',
  currentInterval: '1d',

  async init() {
    lucide.createIcons();
    
    this.setupEventListeners();
    this.renderChartPeriods();
    
    ChartManager.init('chart-container');
    
    this.loadIndices();
    await this.loadStock('THYAO');
  },
  
  setupEventListeners() {
    const searchInput = document.getElementById('stock-search');
    searchInput.addEventListener('input', (e) => this.handleSearch(e.target.value));
    searchInput.addEventListener('focus', () => {
      if(searchInput.value) this.handleSearch(searchInput.value);
    });
    searchInput.addEventListener('blur', () => UI.hideSearchResults());

    const btnAi = document.getElementById('btn-ai-analysis');
    btnAi.addEventListener('click', () => this.runAIAnalysis());
  },

  renderChartPeriods() {
    const container = document.getElementById('chart-periods');
    container.innerHTML = CONFIG.CHART_PERIODS.map((p, i) => `
      <button class="period-btn ${p.period === this.currentPeriod ? 'active' : ''}" 
              onclick="App.handleChartPeriodChange('${p.period}', '${p.interval}')">
        ${p.label}
      </button>
    `).join('');
  },

  async loadIndices() {
    const res = await API.fetchIndices();
    if(!res.error && res.length > 0) {
      // API 'XU100.IS' döndürüyor, bunu eşleştir
      const bist100 = res.find(r => r.symbol === 'XU100.IS' || r.symbol === 'XU100');
      if(bist100) UI.updateBist100(bist100.last_price, bist100.change_percent);
    }
  },

  async loadStock(symbol) {
    this.currentSymbol = symbol;
    document.getElementById('stock-search').value = symbol;
    UI.hideSearchResults();
    UI.hideAnalysis();
    
    API.disconnectWebSocket();
    UI.showLoadingState();

    const [stockRes, histRes, quickRes] = await Promise.all([
      API.fetchStockData(symbol),
      API.fetchStockHistory(symbol, this.currentPeriod, this.currentInterval),
      API.requestQuickAnalysis(symbol)
    ]);

    UI.hideLoadingState();

    if(!stockRes.error) {
      UI.updatePriceCard(stockRes);
      UI.updateIndicators(stockRes);
      
      API.connectWebSocket(symbol, (msg) => {
        UI.updatePriceCard({
          symbol: msg.symbol,
          last_price: msg.price,
          change_percent: msg.change_percent,
          high: msg.high,
          low: msg.low
        });
        ChartManager.updateLastCandle(msg);
      });
    }

    if(!histRes.error) {
      ChartManager.updateData(histRes);
    }

    if(!quickRes.error) {
      UI.updateQuickSignal(quickRes);
    }
  },

  async runAIAnalysis() {
    if(!this.currentSymbol) return;
    
    const btn = document.getElementById('btn-ai-analysis');
    const loader = btn.querySelector('.btn-loader');
    btn.disabled = true;
    loader.classList.remove('hidden');
    
    UI.showAnalysisLoading();
    
    const res = await API.requestFullAnalysis(this.currentSymbol);
    
    if(!res.error) {
      setTimeout(() => {
        UI.renderFullAnalysis(res);
      }, 500); // Artificial slight delay for animation effect
    }
    
    btn.disabled = false;
    loader.classList.add('hidden');
  },

  handleSearch(query) {
    if(!query) {
      UI.hideSearchResults();
      return;
    }
    const q = query.toLowerCase();
    const matches = CONFIG.POPULAR_STOCKS.filter(s => 
      s.symbol.toLowerCase().includes(q) || s.name.toLowerCase().includes(q)
    );
    if(matches.length > 0) {
      UI.showSearchResults(matches);
    } else {
      UI.hideSearchResults();
    }
  },

  handleChartPeriodChange(period, interval) {
    this.currentPeriod = period;
    this.currentInterval = interval;
    this.renderChartPeriods();
    this.loadStock(this.currentSymbol);
  }
};

document.addEventListener('DOMContentLoaded', () => App.init());
