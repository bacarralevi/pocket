// dashboard.js - Place this file in your static/accounts/js/ directory

document.addEventListener('DOMContentLoaded', function() {
    // Elements references
    // Toggle buttons
    const monthlyViewBtn = document.getElementById('monthlyViewBtn');
    const yearlyViewBtn = document.getElementById('yearlyViewBtn');
    const chartTitle = document.getElementById('chart-title');
    const pieChartPeriod = document.getElementById('pieChartPeriod');
    
    // Selector groups
    const monthlySelectors = document.getElementById('monthlySelectors');
    const yearlySelectors = document.getElementById('yearlySelectors');
    
    // Date selectors
    const monthSelector = document.getElementById('monthSelector');
    const yearSelectorMonthly = document.getElementById('yearSelectorMonthly');
    const yearSelectorYearly = document.getElementById('yearSelectorYearly');
    const updateMonthlyBtn = document.getElementById('updateMonthlyBtn');
    const updateYearlyBtn = document.getElementById('updateYearlyBtn');
    
    // Loading indicators
    const chartContainer = document.querySelector('.graph-container');
    const loadingIndicator = document.getElementById('chart-loading');
    const pieLoadingIndicator = document.getElementById('pie-chart-loading');
    const noDataMessage = document.getElementById('no-data-message');
    
    // Chart variables
    let currentChart = null;
    let categoryPieChart = null;
    
    // Initialize with current date
    const currentDate = new Date();
    monthSelector.value = currentDate.getMonth() + 1; // JavaScript months are 0-indexed
    
    // Default views
    loadMonthlyData(monthSelector.value, yearSelectorMonthly.value);
    loadCategoryData(monthSelector.value, yearSelectorMonthly.value, 'monthly');
    
    // Event listeners for toggle buttons
    monthlyViewBtn.addEventListener('click', function() {
        if (!this.classList.contains('active')) {
            setActiveButton(monthlyViewBtn);
            setActiveSelectors('monthly');
            loadMonthlyData(monthSelector.value, yearSelectorMonthly.value);
            loadCategoryData(monthSelector.value, yearSelectorMonthly.value, 'monthly');
        }
    });
    
    yearlyViewBtn.addEventListener('click', function() {
        if (!this.classList.contains('active')) {
            setActiveButton(yearlyViewBtn);
            setActiveSelectors('yearly');
            loadYearlyData(yearSelectorYearly.value);
            loadCategoryData(null, yearSelectorYearly.value, 'yearly');
        }
    });
    
    // Event listeners for update buttons
    updateMonthlyBtn.addEventListener('click', function() {
        loadMonthlyData(monthSelector.value, yearSelectorMonthly.value);
        loadCategoryData(monthSelector.value, yearSelectorMonthly.value, 'monthly');
    });
    
    updateYearlyBtn.addEventListener('click', function() {
        loadYearlyData(yearSelectorYearly.value);
        loadCategoryData(null, yearSelectorYearly.value, 'yearly');
    });
    
    // Helper functions
    function setActiveButton(activeButton) {
        // Remove active class from all buttons
        document.querySelectorAll('.toggle-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        // Add active class to selected button
        activeButton.classList.add('active');
    }
    
    function setActiveSelectors(view) {
        if (view === 'monthly') {
            monthlySelectors.style.display = 'flex';
            yearlySelectors.style.display = 'none';
        } else {
            monthlySelectors.style.display = 'none';
            yearlySelectors.style.display = 'flex';
        }
    }
    
    function showLoading(indicator) {
        if (indicator) {
            indicator.style.display = 'flex';
        }
    }
    
    function hideLoading(indicator) {
        if (indicator) {
            indicator.style.display = 'none';
        }
    }
    
    function destroyChart(chart) {
        if (chart) {
            chart.destroy();
            return null;
        }
        return null;
    }
    
    function getMonthName(monthNum) {
        const monthNames = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ];
        return monthNames[monthNum - 1];
    }
    
    // Data loading functions
    function loadMonthlyData(month, year) {
        showLoading(loadingIndicator);
        const monthName = getMonthName(month);
        chartTitle.textContent = `Daily Transactions - ${monthName} ${year}`;
        
        // Use global URL variable defined in the template
        fetch(`${window.chartDataUrl}?view=monthly&month=${month}&year=${year}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(chartData => {
                hideLoading(loadingIndicator);
                
                // Prepare arrays for chart
                const days = chartData.map(item => item.day);
                const incomeData = chartData.map(item => item.income);
                const expenseData = chartData.map(item => item.expenses);
                
                currentChart = destroyChart(currentChart);
                
                const ctx = document.getElementById('financialChart');
                
                currentChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: days,
                        datasets: [
                            {
                                label: 'Income',
                                data: incomeData,
                                backgroundColor: 'rgba(72, 187, 120, 0.7)',
                                borderColor: '#48bb78',
                                borderWidth: 1
                            },
                            {
                                label: 'Expenses',
                                data: expenseData,
                                backgroundColor: 'rgba(245, 101, 101, 0.7)',
                                borderColor: '#f56565',
                                borderWidth: 1
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                title: {
                                    display: true,
                                    text: 'Amount ($)'
                                },
                                grid: {
                                    color: 'rgba(0, 0, 0, 0.05)'
                                }
                            },
                            x: {
                                title: {
                                    display: true,
                                    text: 'Day of Month'
                                },
                                grid: {
                                    display: false
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                position: 'top',
                            },
                            title: {
                                display: false
                            },
                            tooltip: {
                                callbacks: {
                                    title: function(tooltipItems) {
                                        return 'Day ' + tooltipItems[0].label;
                                    },
                                    label: function(context) {
                                        let label = context.dataset.label || '';
                                        if (label) {
                                            label += ': ';
                                        }
                                        label += '$' + context.parsed.y.toFixed(2);
                                        return label;
                                    }
                                }
                            }
                        }
                    }
                });
            })
            .catch(error => {
                console.error("Error loading monthly data:", error);
                
                // Show error message in the graph container
                hideLoading(loadingIndicator);
                if (chartContainer) {
                    loadingIndicator.innerHTML = `<div style="padding: 20px; color: red;">Failed to load chart: ${error.message}</div>`;
                    loadingIndicator.style.display = 'flex';
                }
            });
    }
    
    function loadYearlyData(year) {
        showLoading(loadingIndicator);
        chartTitle.textContent = `Monthly Transactions - ${year}`;
        
        // Use global URL variable defined in the template
        fetch(`${window.chartDataUrl}?view=yearly&year=${year}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(chartData => {
                hideLoading(loadingIndicator);
                
                // Prepare arrays for chart
                const months = chartData.map(item => item.month);
                const incomeData = chartData.map(item => item.income);
                const expenseData = chartData.map(item => item.expenses);
                
                currentChart = destroyChart(currentChart);
                
                const ctx = document.getElementById('financialChart');
                
                currentChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: months,
                        datasets: [
                            {
                                label: 'Income',
                                data: incomeData,
                                backgroundColor: 'rgba(72, 187, 120, 0.7)',
                                borderColor: '#48bb78',
                                borderWidth: 1
                            },
                            {
                                label: 'Expenses',
                                data: expenseData,
                                backgroundColor: 'rgba(245, 101, 101, 0.7)',
                                borderColor: '#f56565',
                                borderWidth: 1
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                title: {
                                    display: true,
                                    text: 'Amount ($)'
                                },
                                grid: {
                                    color: 'rgba(0, 0, 0, 0.05)'
                                }
                            },
                            x: {
                                title: {
                                    display: true,
                                    text: 'Month'
                                },
                                grid: {
                                    display: false
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                position: 'top',
                            },
                            title: {
                                display: false
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        let label = context.dataset.label || '';
                                        if (label) {
                                            label += ': ';
                                        }
                                        label += '$' + context.parsed.y.toFixed(2);
                                        return label;
                                    }
                                }
                            }
                        }
                    }
                });
            })
            .catch(error => {
                console.error("Error loading yearly data:", error);
                
                // Show error message in the graph container
                hideLoading(loadingIndicator);
                if (chartContainer) {
                    loadingIndicator.innerHTML = `<div style="padding: 20px; color: red;">Failed to load chart: ${error.message}</div>`;
                    loadingIndicator.style.display = 'flex';
                }
            });
    }
    
    function loadCategoryData(month, year, viewType) {
        showLoading(pieLoadingIndicator);
        noDataMessage.style.display = 'none';
        
        // Clear any existing legend
        const legendContainer = document.getElementById('pieLegendContainer');
        if (legendContainer) {
            legendContainer.innerHTML = '';
        }
        
        // Use global URL variable defined in the template
        let url = `${window.categoryDataUrl}?year=${year}`;
        let periodLabel = `${year}`;
        
        if (viewType === 'monthly' && month) {
            url += `&month=${month}`;
            const monthName = getMonthName(month);
            periodLabel = `${monthName} ${year}`;
        }
        
        pieChartPeriod.textContent = periodLabel;
        
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(categoryData => {
                hideLoading(pieLoadingIndicator);
                
                // Check if there's any data
                const hasData = categoryData.some(item => item.amount > 0);
                
                if (!hasData) {
                    noDataMessage.style.display = 'flex';
                    categoryPieChart = destroyChart(categoryPieChart);
                    return;
                }
                
                noDataMessage.style.display = 'none';
                
                // Prepare data for pie chart
                const labels = categoryData.map(item => item.category);
                const amounts = categoryData.map(item => item.amount);
                
                // Generate colors for each category
                const backgroundColors = generateColors(categoryData.length);
                
                categoryPieChart = destroyChart(categoryPieChart);
                
                const ctx = document.getElementById('categoryPieChart');
                
                categoryPieChart = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: labels,
                        datasets: [{
                            data: amounts,
                            backgroundColor: backgroundColors,
                            borderColor: 'white',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        cutout: '60%',
                        layout: {
                            padding: {
                                top: 10,
                                bottom: 10,
                                left: 10,
                                right: 10
                            }
                        },
                        plugins: {
                            legend: {
                                display: false // We'll create a custom legend
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        const label = context.label || '';
                                        const value = context.parsed || 0;
                                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                        const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
                                        return `${label}: $${value.toFixed(2)} (${percentage}%)`;
                                    }
                                }
                            }
                        }
                    }
                });
                
                // Create custom legend
                createCustomLegend(labels, backgroundColors, amounts);
            })
            .catch(error => {
                console.error("Error loading category data:", error);
                
                // Show error message
                hideLoading(pieLoadingIndicator);
                noDataMessage.innerHTML = `<i class="fas fa-exclamation-circle"></i><p>Failed to load category data: ${error.message}</p>`;
                noDataMessage.style.display = 'flex';
            });
    }
    
    // Generate colors for pie chart
    function generateColors(count) {
        // Predefined colors for common categories
        const colorPalette = [
            '#FF6384', // red
            '#36A2EB', // blue
            '#FFCE56', // yellow
            '#4BC0C0', // teal
            '#9966FF', // purple
            '#FF9F40', // orange
            '#C9CBCF', // grey
            '#7ED321', // green
            '#50E3C2', // mint
            '#B8E986', // light green
            '#D667CE', // pink
            '#F8E71C'  // bright yellow
        ];
        
        // If we have more categories than colors, generate additional colors
        if (count <= colorPalette.length) {
            return colorPalette.slice(0, count);
        }
        
        const colors = [...colorPalette];
        
        // Generate additional random colors
        for (let i = colorPalette.length; i < count; i++) {
            const r = Math.floor(Math.random() * 200 + 55);
            const g = Math.floor(Math.random() * 200 + 55);
            const b = Math.floor(Math.random() * 200 + 55);
            colors.push(`rgb(${r}, ${g}, ${b})`);
        }
        
        return colors;
    }
    
    // Create custom legend for pie chart
    function createCustomLegend(labels, colors, values) {
        // Get or create the legend container
        let legendContainer = document.getElementById('pieLegendContainer');
        if (!legendContainer) {
            legendContainer = document.createElement('div');
            legendContainer.id = 'pieLegendContainer';
            legendContainer.className = 'chart-legend-container';
            
            // Find the pie container and append the legend
            const pieContainer = document.querySelector('.pie-container');
            pieContainer.appendChild(legendContainer);
        } else {
            legendContainer.innerHTML = '';
        }
        
        // Calculate total for percentages
        const total = values.reduce((a, b) => a + b, 0);
        
        // Create legend items
        labels.forEach((label, index) => {
            const percentage = total > 0 ? Math.round((values[index] / total) * 100) : 0;
            
            const legendItem = document.createElement('div');
            legendItem.className = 'chart-legend-item';
            
            const colorBox = document.createElement('span');
            colorBox.className = 'legend-color';
            colorBox.style.backgroundColor = colors[index];
            
            const labelSpan = document.createElement('span');
            labelSpan.className = 'legend-label';
            labelSpan.textContent = `${label} (${percentage}%)`;
            
            legendItem.appendChild(colorBox);
            legendItem.appendChild(labelSpan);
            legendContainer.appendChild(legendItem);
            
            // Add hover interaction
            legendItem.addEventListener('mouseover', () => {
                const activeSegments = categoryPieChart.getActiveElements();
                categoryPieChart.setActiveElements([{
                    datasetIndex: 0,
                    index: index
                }]);
                categoryPieChart.update();
            });
            
            legendItem.addEventListener('mouseout', () => {
                categoryPieChart.setActiveElements([]);
                categoryPieChart.update();
            });
        });
    }
});