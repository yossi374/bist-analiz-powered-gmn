const ChartManager = {
  chart: null,
  candleSeries: null,
  volumeSeries: null,
  smaLines: {},
  bollingerSeries: {},

  init(containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    
    this.chart = LightweightCharts.createChart(container, {
      layout: {
        background: { type: 'solid', color: '#0a0e17' },
        textColor: '#94a3b8',
      },
      grid: {
        vertLines: { color: 'rgba(255, 255, 255, 0.04)' },
        horzLines: { color: 'rgba(255, 255, 255, 0.04)' },
      },
      crosshair: {
        mode: LightweightCharts.CrosshairMode.Normal,
        vertLine: {
          width: 1,
          color: 'rgba(255,255,255,0.3)',
          style: LightweightCharts.LineStyle.Dashed,
        },
        horzLine: {
          width: 1,
          color: 'rgba(255,255,255,0.3)',
          style: LightweightCharts.LineStyle.Dashed,
        },
      },
      rightPriceScale: {
        borderColor: 'rgba(255, 255, 255, 0.08)',
      },
      timeScale: {
        borderColor: 'rgba(255, 255, 255, 0.08)',
        timeVisible: true,
      },
    });

    this.candleSeries = this.chart.addCandlestickSeries({
      upColor: '#10b981',
      downColor: '#ef4444',
      borderVisible: false,
      wickUpColor: '#10b981',
      wickDownColor: '#ef4444'
    });

    this.volumeSeries = this.chart.addHistogramSeries({
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: '',
      scaleMargins: {
        top: 0.8,
        bottom: 0,
      },
    });
    
    window.addEventListener('resize', this.resize.bind(this));
  },

  updateData(historyData) {
    if (!this.chart || !historyData.data) return;

    const candleData = historyData.data.map(d => ({
      time: new Date(d.date).getTime() / 1000,
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
    }));

    const volData = historyData.data.map(d => ({
      time: new Date(d.date).getTime() / 1000,
      value: d.volume,
      color: d.close >= d.open ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)',
    }));

    this.candleSeries.setData(candleData);
    this.volumeSeries.setData(volData);
    this.chart.timeScale().fitContent();

    // Reset lines
    for (const key in this.smaLines) {
      this.chart.removeSeries(this.smaLines[key]);
    }
    this.smaLines = {};

    if (historyData.indicators) {
      if (historyData.indicators.sma_20) {
        this.addSMAOverlay('sma_20', historyData.indicators.sma_20, '#3b82f6');
      }
      if (historyData.indicators.sma_50) {
        this.addSMAOverlay('sma_50', historyData.indicators.sma_50, '#8b5cf6');
      }
    }
  },

  addSMAOverlay(name, data, color) {
    const lineSeries = this.chart.addLineSeries({
      color: color,
      lineWidth: 2,
      crosshairMarkerVisible: false,
    });
    
    const formattedData = data.map(d => ({
      time: new Date(d.date).getTime() / 1000,
      value: d.value,
    }));
    
    lineSeries.setData(formattedData);
    this.smaLines[name] = lineSeries;
  },

  addBollingerOverlay(upper, lower) {
    // Advanced feature, skipped for brevity, could use line series
  },

  updateLastCandle(tickerData) {
    if (!this.candleSeries) return;
    const time = new Date(tickerData.timestamp).getTime() / 1000;
    
    this.candleSeries.update({
      time: time,
      open: tickerData.price, // using current price as simple fallback if real OHL isn't provided perfectly in ws
      high: tickerData.high,
      low: tickerData.low,
      close: tickerData.price,
    });
  },

  resize() {
    if (this.chart) {
      const container = document.getElementById('chart-container');
      this.chart.applyOptions({
        width: container.clientWidth,
        height: container.clientHeight
      });
    }
  },

  destroy() {
    if (this.chart) {
      window.removeEventListener('resize', this.resize.bind(this));
      this.chart.remove();
      this.chart = null;
    }
  }
};
