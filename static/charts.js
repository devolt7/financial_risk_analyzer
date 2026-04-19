/**
 * Chart Rendering Module
 * Handles all Plotly chart creation and rendering
 */

const Charts = {
    /**
     * Render historical price chart
     */
    renderPriceChart: function(data, symbols) {
        const traces = [];
        
        symbols.forEach(symbol => {
            if (data.stock_analysis && data.stock_analysis[symbol]) {
                const stats = data.stock_analysis[symbol];
                const price = stats.current_price;
                
                // Create a simple line chart showing current prices
                traces.push({
                    x: symbols,
                    y: symbols.map(s => data.stock_analysis[s].current_price),
                    type: 'bar',
                    name: 'Current Price',
                    marker: {
                        color: symbols.map((_, i) => `rgba(52, 152, 219, ${0.5 + i * 0.1})`),
                        line: { color: '#2c3e50', width: 2 }
                    }
                });
            }
        });
        
        const layout = {
            title: '<b>📈 Current Stock Prices</b>',
            xaxis: { title: 'Stock Symbol' },
            yaxis: { title: 'Price ($)' },
            hovermode: 'closest',
            plot_bgcolor: '#f8f9fa',
            paper_bgcolor: '#ffffff'
        };
        
        Plotly.newPlot('price-chart', traces, layout, { responsive: true });
    },

    /**
     * Render returns distribution histogram with normal curve
     */
    renderReturnsChart: function(data, symbols) {
        const layout = {
            title: '<b>📊 Return Distribution (Daily Returns %)</b>',
            xaxis: { title: 'Daily Return (%)' },
            yaxis: { title: 'Frequency' },
            barmode: 'overlay',
            hovermode: 'closest',
            plot_bgcolor: '#f8f9fa',
            paper_bgcolor: '#ffffff'
        };
        
        const traces = [];
        
        symbols.forEach((symbol, idx) => {
            if (data.stock_analysis && data.stock_analysis[symbol]) {
                const dist = data.stock_analysis[symbol].distribution;
                
                // Histogram
                const binWidth = (dist.bin_edges[1] - dist.bin_edges[0]) * 100;
                const binCenters = dist.bin_edges.slice(0, -1).map((edge, i) => 
                    (edge + dist.bin_edges[i + 1]) / 2 * 100
                );
                
                traces.push({
                    x: binCenters,
                    y: dist.counts,
                    name: `${symbol} (Actual)`,
                    type: 'bar',
                    opacity: 0.6,
                    marker: { color: `rgba(52, 152, 219, 0.7)` }
                });
                
                // Normal distribution curve
                traces.push({
                    x: dist.x_normal.map(v => v * 100),
                    y: dist.normal_curve,
                    name: `${symbol} (Normal Dist)`,
                    type: 'scatter',
                    mode: 'lines',
                    line: { color: '#e74c3c', width: 3, dash: 'solid' },
                    yaxis: 'y2'
                });
            }
        });
        
        layout.yaxis2 = {
            title: 'Density',
            overlaying: 'y',
            side: 'right'
        };
        
        Plotly.newPlot('returns-chart', traces, layout, { responsive: true });
    },

    /**
     * Render Monte Carlo simulation paths
     */
    renderMonteCarloChart: function(data, symbols) {
        const traces = [];
        
        symbols.forEach((symbol, idx) => {
            if (data.monte_carlo && data.monte_carlo.price_corridors && data.monte_carlo.price_corridors[symbol]) {
                const corridor = data.monte_carlo.price_corridors[symbol];
                const days = Array.from({length: corridor.best.length}, (_, i) => i);
                
                // Best and Worst cases
                traces.push({
                    x: days, y: corridor.best,
                    name: `${symbol} - Best Case`,
                    type: 'scatter', mode: 'lines',
                    line: { color: '#27ae60', width: 2, dash: 'dash' }
                });
                
                traces.push({
                    x: days, y: corridor.worst,
                    name: `${symbol} - Worst Case`,
                    type: 'scatter', mode: 'lines',
                    line: { color: '#e74c3c', width: 2, dash: 'dash' }
                });
                
                traces.push({
                    x: days, y: corridor.mean,
                    name: `${symbol} - Mean`,
                    type: 'scatter', mode: 'lines',
                    line: { color: '#3498db', width: 3 }
                });
                
                // Confidence bands (95%)
                traces.push({
                    x: [...days, ...days.reverse()],
                    y: [...corridor.percentile_5, ...corridor.percentile_95.reverse()],
                    fill: 'toself',
                    name: `${symbol} - 90% Confidence Band`,
                    fillcolor: 'rgba(52, 152, 219, 0.2)',
                    line: { color: 'transparent' }
                });
            }
        });
        
        const layout = {
            title: '<b>🎲 Monte Carlo Simulation - Price Paths</b>',
            xaxis: { title: 'Days Ahead' },
            yaxis: { title: 'Predicted Price ($)' },
            hovermode: 'x unified',
            plot_bgcolor: '#f8f9fa',
            paper_bgcolor: '#ffffff',
            showlegend: true
        };
        
        Plotly.newPlot('mc-chart', traces, layout, { responsive: true });
    },

    /**
     * Render efficient frontier
     */
    renderEfficientFrontier: function(data) {
        const frontier = data.portfolio_optimization.efficient_frontier;
        
        const trace = {
            x: frontier.map(p => p.volatility_percentage),
            y: frontier.map(p => p.return_percentage),
            mode: 'markers+lines',
            type: 'scatter',
            name: 'Efficient Frontier',
            marker: {
                size: 8,
                color: frontier.map((_, i) => i),
                colorscale: 'Viridis',
                showscale: true,
                colorbar: { title: 'Risk Level' },
                line: { color: '#2c3e50', width: 1 }
            },
            line: { color: '#3498db', width: 2 }
        };
        
        const layout = {
            title: '<b>📊 Efficient Frontier - Risk vs Return</b>',
            xaxis: { title: 'Risk (Annual Volatility %)' },
            yaxis: { title: 'Expected Return (% p.a.)' },
            hovermode: 'closest',
            plot_bgcolor: '#f8f9fa',
            paper_bgcolor: '#ffffff'
        };
        
        Plotly.newPlot('efficient-frontier', [trace], layout, { responsive: true });
    }
};
