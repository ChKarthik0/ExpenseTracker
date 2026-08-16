document.addEventListener("DOMContentLoaded", () => {
  // Parse data from Flask/Jinja2 (ensure these are set in the template)
  const categoryLabels = JSON.parse(document.getElementById('categoryChartData')?.dataset.labels || '[]');
  const categoryData = JSON.parse(document.getElementById('categoryChartData')?.dataset.data || '[]');
  const trendLabels = JSON.parse(document.getElementById('trendChartData')?.dataset.labels || '[]');
  const trendData = JSON.parse(document.getElementById('trendChartData')?.dataset.data || '[]');

  // Generate random colors for each category
  const generateColors = (num) => {
    const colors = [];
    for (let i = 0; i < num; i++) {
      colors.push(`hsl(${(i * 360 / num)}, 70%, 60%)`);
    }
    return colors;
  };

  // PIE CHART: Spending by Category
  const pieCtx = document.getElementById('categoryChart');
  if (pieCtx && categoryLabels.length > 0) {
    new Chart(pieCtx, {
      type: 'pie',
      data: {
        labels: categoryLabels,
        datasets: [{
          label: 'Spending by Category',
          data: categoryData,
          backgroundColor: generateColors(categoryLabels.length),
          borderColor: '#fff',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'bottom'
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                const value = context.parsed;
                return `${context.label}: ₹${value.toFixed(2)}`;
              }
            }
          }
        }
      }
    });
  }

  // LINE CHART: Monthly Trend
  const lineCtx = document.getElementById('trendChart');
  if (lineCtx && trendLabels.length > 0) {
    new Chart(lineCtx, {
      type: 'line',
      data: {
        labels: trendLabels,
        datasets: [{
          label: 'Monthly Spending',
          data: trendData,
          fill: false,
          borderColor: 'rgba(54, 162, 235, 1)',
          backgroundColor: 'rgba(54, 162, 235, 0.2)',
          tension: 0.3,
          pointRadius: 4,
          pointHoverRadius: 6
        }]
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: function (value) {
                return `₹${value}`;
              }
            },
            title: {
              display: true,
              text: 'Spending (₹)'
            }
          }
        },
        plugins: {
          tooltip: {
            callbacks: {
              label: function (context) {
                return `₹${context.parsed.y.toFixed(2)}`;
              }
            }
          }
        }
      }
    });
  }
});
