const canvas = document.getElementById('sentimentChart');

const sentimentBar = (label, count, fill, border) => ({
    label: label,
    data: [Number(count)],
    backgroundColor: fill,
    borderColor: border,
    borderWidth: 1
});

new Chart(canvas.getContext('2d'), {
    type: 'bar',
    data: {
        labels: ['SENTIMENT'],
        datasets: [
            sentimentBar('POSITIVE', canvas.dataset.positive, 'rgba(0,255,6, 0.2)', 'rgba(0,147,3,0.5)'),
            sentimentBar('NEGATIVE', canvas.dataset.negative, 'rgba(255,0,0, 0.2)', 'rgba(121,0,13,0.5)')
        ]
    },
    options: {
        maintainAspectRatio: false,
        layout: {
            padding: {
                bottom: 15
            }
        },
        scales: {
            x: {
                grid: { display: false },
                ticks: {
                    padding: 12
                }
            },
            y: {
                beginAtZero: true,
                grid: {
                    color: '#e6e9ef'
                },
                ticks: {
                    precision: 0,
                    stepSize: 1,
                    padding: 10
                }
            }
        }
    }
});
