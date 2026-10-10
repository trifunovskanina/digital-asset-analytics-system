const rows = Array.from(document.querySelectorAll('tbody tr[data-date]'));

new Chart(document.getElementById('priceChart'), {
    type: 'line',
    data: {
        labels: rows.map(row => row.dataset.date),
        datasets: [{
            label: 'Close',
            data: rows.map(row => Number(row.dataset.close)),
            borderWidth: 2,
            tension: 0.1
        }]
    },
    options: {
        plugins: {
            legend: { display: false }
        },
        scales: {
            x: { title: { display: true, text: 'Date' } },
            y: { title: { display: true, text: 'Price' } }
        }
    }
});
