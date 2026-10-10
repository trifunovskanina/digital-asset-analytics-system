const futureRows = Array.from(document.querySelectorAll('tbody tr[data-price]'));
const validationRows = Array.from(document.querySelectorAll('tbody tr[data-actual]'));

const values = (rows, key) => rows.map(row => Number(row.dataset[key]));
const titledAxis = text => ({ title: { display: true, text: text } });

function lineChart(canvasId, labels, datasets, xTitle) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    new Chart(canvas, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets.map(dataset => ({ borderWidth: 2, tension: 0.25, ...dataset }))
        },
        options: {
            scales: {
                x: titledAxis(xTitle),
                y: titledAxis('Price')
            }
        }
    });
}

lineChart(
    'forecastChart',
    futureRows.map(row => row.dataset.date),
    [{ label: 'Predicted Closing Price', data: values(futureRows, 'price'), pointRadius: 2 }],
    'Date'
);

lineChart(
    'validationChart',
    validationRows.map((_, i) => i + 1),
    [
        { label: 'Actual', data: values(validationRows, 'actual'), pointRadius: 0 },
        { label: 'Predicted', data: values(validationRows, 'predicted'), pointRadius: 0 }
    ],
    'Validation step'
);
