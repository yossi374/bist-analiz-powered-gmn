const UI = {
  updatePriceCard(data) {
    document.getElementById('hero-symbol').textContent = data.symbol;
    document.getElementById('hero-symbol').classList.remove('skeleton-text');
    
    const stockConfig = CONFIG.POPULAR_STOCKS.find(s => s.symbol === data.symbol);
    if(stockConfig) {
      document.getElementById('hero-name').textContent = stockConfig.name;
    } else {
      document.getElementById('hero-name').textContent = data.symbol + " Hisse Senedi";
    }
    document.getElementById('hero-name').classList.remove('skeleton-text');

    const priceEl = document.getElementById('hero-price');
    priceEl.textContent = data.last_price ? data.last_price.toFixed(2) : '0.00';
    priceEl.classList.remove('skeleton-text');
    
    const changeEl = document.getElementById('hero-change');
    const changeIcon = document.getElementById('hero-change-icon');
    const changeContainer = document.getElementById('hero-change-container');
    
    const changeVal = data.change_percent || 0;
    changeEl.textContent = Math.abs(changeVal).toFixed(2) + '%';
    changeEl.classList.remove('skeleton-text');
    
    changeContainer.className = 'price-change-container';
    if(changeVal > 0) {
      changeContainer.classList.add('color-up');
      changeIcon.setAttribute('data-lucide', 'arrow-up');
    } else if (changeVal < 0) {
      changeContainer.classList.add('color-down');
      changeIcon.setAttribute('data-lucide', 'arrow-down');
    } else {
      changeContainer.classList.add('color-neutral');
      changeIcon.setAttribute('data-lucide', 'minus');
    }
    lucide.createIcons();
    
    // Günlük Yüksek / Düşük — önce daily_high/low, yoksa WS high/low
    const high = data.daily_high || data.high || null;
    const low  = data.daily_low  || data.low  || null;
    if (high && low) {
      const highEl = document.getElementById('hero-high');
      const lowEl  = document.getElementById('hero-low');
      if (highEl) { highEl.textContent = parseFloat(high).toFixed(2); highEl.classList.remove('skeleton-text'); }
      if (lowEl)  { lowEl.textContent  = parseFloat(low).toFixed(2);  lowEl.classList.remove('skeleton-text'); }
      
      // Range bar: fiyatın günlük aralıktaki pozisyonu
      const price = data.last_price || 0;
      if (high !== low) {
        const pct = Math.max(0, Math.min(100, ((price - low) / (high - low)) * 100));
        const bar = document.getElementById('hero-range-bar');
        if (bar) {
          bar.style.left  = '0';
          bar.style.width = pct + '%';
          bar.style.background = pct > 60 ? 'var(--signal-al)' : pct < 40 ? 'var(--signal-sat)' : 'var(--text-muted)';
        }
      }
    }
    
    priceEl.parentElement.classList.remove('price-pulse');
    void priceEl.parentElement.offsetWidth;
    priceEl.parentElement.classList.add('price-pulse');
  },

  updateIndicators(data) {
    if(data.rsi_14 !== undefined) this.updateRSIGauge(data.rsi_14);
    
    const upd = (id, val) => {
      const el = document.getElementById(id);
      if(el && val !== undefined) {
        el.textContent = val.toFixed(2);
        el.classList.remove('skeleton-text');
      }
    };
    
    upd('ind-macd', data.macd);
    upd('ind-sma20', data.sma_20);
    upd('ind-sma50', data.sma_50);
    upd('ind-atr', data.atr_14);
  },

  updateRSIGauge(value) {
    const valEl = document.getElementById('rsi-value');
    valEl.textContent = value.toFixed(1);
    valEl.classList.remove('skeleton-text');
    
    const gauge = document.getElementById('rsi-gauge');
    let color = '#f59e0b'; // yellow 30-70
    if (value < 30) color = '#10b981'; // green overbought/oversold logic ? typically RSI < 30 is oversold (buy signal)
    if (value > 70) color = '#ef4444'; // red
    
    const percent = Math.min(Math.max(value, 0), 100);
    gauge.style.background = `conic-gradient(${color} ${percent}%, var(--bg-tertiary) ${percent}%)`;
  },

  updateQuickSignal(data) {
    const content = document.getElementById('quick-signal-content');
    content.innerHTML = `
      <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
        <span style="font-weight:600; color:var(--text-secondary)">Sinyal:</span>
        ${this.createSignalBadge(data.quick_signal || data.signal || 'TUT')}
      </div>
      <div class="qs-summary">${data.summary || data.macd_signal_text || 'Analiz bekleniyor...'}</div>
    `;
  },

  showAnalysisLoading() {
    const section = document.getElementById('ai-results-section');
    section.classList.remove('hidden');
    
    document.getElementById('agents-grid').innerHTML = `
      <div class="skeleton-box" style="height: 300px; border-radius: 12px;"></div>
      <div class="skeleton-box" style="height: 300px; border-radius: 12px;"></div>
      <div class="skeleton-box" style="height: 300px; border-radius: 12px;"></div>
    `;
    document.getElementById('final-decision-container').innerHTML = `
      <div class="skeleton-box" style="height: 200px; border-radius: 16px;"></div>
    `;
    section.scrollIntoView({ behavior: 'smooth' });
  },

  renderFullAnalysis(data) {
    const grid = document.getElementById('agents-grid');
    const finalContainer = document.getElementById('final-decision-container');
    
    const agents = [
      data.technical_analysis,
      data.fundamental_analysis,
      data.risk_assessment
    ].filter(Boolean);
    
    grid.innerHTML = agents.map(agent => `
      <div class="agent-card">
        <div class="agent-header">
          <div class="agent-name">
            <i data-lucide="cpu"></i> ${agent.agent_name}
          </div>
          ${this.createSignalBadge(agent.signal)}
        </div>
        ${this.createConfidenceBar(agent.confidence)}
        <div class="agent-text">${agent.analysis_text}</div>
        <ul class="agent-points">
          ${(agent.key_points || []).map(p => `<li>${p}</li>`).join('')}
        </ul>
      </div>
    `).join('');
    
    if (data.final_decision) {
      finalContainer.innerHTML = `
        <div class="final-card">
          <div class="final-title">Yapay Zeka Ortak Kararı</div>
          <div style="display:flex; align-items:center; gap:24px;">
             ${this.createSignalBadge(data.final_decision, true)}
             <div style="text-align:left; width: 200px;">
                ${this.createConfidenceBar(data.final_confidence, true)}
             </div>
          </div>
          <p class="final-summary">${data.summary}</p>
        </div>
      `;
    }
    
    lucide.createIcons();
  },

  hideAnalysis() {
    document.getElementById('ai-results-section').classList.add('hidden');
  },

  createSignalBadge(signal, isLarge=false) {
    const sig = signal ? signal.toUpperCase() : 'TUT';
    let cls = 'tut';
    if(sig === 'AL') cls = 'al';
    if(sig === 'SAT') cls = 'sat';
    
    const extra = isLarge ? 'final-badge' : '';
    return `<div class="signal-badge ${cls} ${extra}">${sig}</div>`;
  },

  createConfidenceBar(confidence, showValue=true) {
    const val = ((confidence || 0) * 100).toFixed(0);
    return `
      <div class="confidence-container">
        <div class="confidence-label">
          <span>Güven Skoru</span>
          ${showValue ? `<span>%${val}</span>` : ''}
        </div>
        <div class="confidence-track">
          <div class="confidence-fill" style="width: ${val}%;"></div>
        </div>
      </div>
    `;
  },

  showSearchResults(stocks) {
    const res = document.getElementById('search-results');
    res.innerHTML = stocks.map(s => `
      <div class="search-item" onclick="App.loadStock('${s.symbol}')">
        <span class="search-item-symbol">${s.symbol}</span>
        <span class="search-item-name">${s.name}</span>
      </div>
    `).join('');
    res.classList.remove('hidden');
  },

  hideSearchResults() {
    setTimeout(() => {
      document.getElementById('search-results').classList.add('hidden');
    }, 200);
  },

  setConnectionStatus(connected) {
    const dot = document.querySelector('.status-dot');
    const text = document.querySelector('.status-text');
    if(connected) {
      dot.className = 'status-dot connected';
      text.textContent = 'Canlı Veri';
    } else {
      dot.className = 'status-dot disconnected';
      text.textContent = 'Bağlantı Koptu';
    }
  },

  showLoadingState() {
    document.querySelectorAll('.skeleton-text').forEach(el => {
      el.textContent = '00.00';
    });
    const content = document.getElementById('quick-signal-content');
    content.innerHTML = `<div class="skeleton-box" style="height: 100px; width: 100%; border-radius: 8px;"></div>`;
    
    document.getElementById('chart-container').classList.add('hidden');
    document.getElementById('chart-skeleton').classList.remove('hidden');
  },

  hideLoadingState() {
    document.getElementById('chart-skeleton').classList.add('hidden');
    document.getElementById('chart-container').classList.remove('hidden');
  },

  updateBist100(val, change) {
    const el   = document.querySelector('.index-value');
    const chEl = document.querySelector('.index-change');
    if (!el || val == null) return;
    el.textContent = parseFloat(val).toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    el.classList.remove('skeleton-text');
    if (chEl && change != null) {
      chEl.textContent = (change > 0 ? '+' : '') + parseFloat(change).toFixed(2) + '%';
      chEl.style.color = change > 0 ? 'var(--signal-al)' : 'var(--signal-sat)';
    }
  }
};
