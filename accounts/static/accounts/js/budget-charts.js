// budget-charts.js - Updated version for card layout

document.addEventListener('DOMContentLoaded', function() {
    // Function to create a budget progress chart
    function createBudgetChart(canvasId, spent, total, status, options = {}) {
        const canvas = document.getElementById(canvasId);
        
        if (!canvas) return; // Skip if canvas doesn't exist
        
        // Calculate percentage
        let percentage = (spent / total) * 100;
        if (percentage > 100) percentage = 100;
        
        // Determine colors based on status
        let progressColor, remainingColor;
        
        switch(status) {
            case 'exceeded':
                progressColor = '#f56565'; // Red
                remainingColor = '#fed7d7';
                break;
            case 'warning':
                progressColor = '#ed8936'; // Orange
                remainingColor = '#feebc8';
                break;
            default: // normal
                progressColor = '#48bb78'; // Green
                remainingColor = '#c6f6d5';
        }
        
        // Default options
        const defaultOptions = {
            cutout: '75%',      // Doughnut thickness
            showPercentage: true, // Show percentage in center
            fontSize: 1.0,      // Font size multiplier
            rotation: -90,      // Start from top
            showText: true      // Whether to show text in the center
        };
        
        // Merge provided options with defaults
        const chartOptions = {...defaultOptions, ...options};
        
        // Create chart
        new Chart(canvas, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [percentage, 100 - percentage],
                    backgroundColor: [progressColor, remainingColor],
                    borderWidth: 0,
                    cutout: chartOptions.cutout
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                circumference: 360,
                rotation: chartOptions.rotation,
                plugins: {
                    tooltip: {
                        enabled: false
                    },
                    legend: {
                        display: false
                    }
                },
                animation: {
                    animateRotate: true,
                    animateScale: true,
                    duration: 1000
                }
            },
            plugins: chartOptions.showText ? [{
                id: 'centerText',
                beforeDraw: function(chart) {
                    if (!chartOptions.showPercentage) return;
                    
                    const width = chart.width;
                    const height = chart.height;
                    const ctx = chart.ctx;
                    
                    ctx.restore();
                    
                    // Display percentage in the center
                    const fontSize = (height / 110 * chartOptions.fontSize).toFixed(2);
                    ctx.font = fontSize + 'em sans-serif';
                    ctx.textBaseline = 'middle';
                    ctx.fillStyle = status === 'exceeded' ? '#f56565' : (status === 'warning' ? '#ed8936' : '#4a5568');
                    
                    const text = percentage.toFixed(0) + '%';
                    const textX = Math.round((width - ctx.measureText(text).width) / 2);
                    const textY = height / 2;
                    
                    ctx.fillText(text, textX, textY);
                    ctx.save();
                }
            }] : []
        });
    }
    
    // Create the overall budget chart if it exists
    const overallBudgetCanvas = document.getElementById('overallBudgetChart');
    if (overallBudgetCanvas) {
        const spent = parseFloat(overallBudgetCanvas.getAttribute('data-spent'));
        const total = parseFloat(overallBudgetCanvas.getAttribute('data-total'));
        const status = overallBudgetCanvas.getAttribute('data-status');
        
        createBudgetChart('overallBudgetChart', spent, total, status, {
            cutout: '70%',
            fontSize: 1.4
        });
    }
    
    // Create charts for each category budget
    document.querySelectorAll('.category-budget-chart').forEach(function(canvas) {
        const spent = parseFloat(canvas.getAttribute('data-spent'));
        const total = parseFloat(canvas.getAttribute('data-total'));
        const status = canvas.getAttribute('data-status');
        
        createBudgetChart(canvas.id, spent, total, status, {
            cutout: '75%',
            fontSize: 0.9
        });
    });
});