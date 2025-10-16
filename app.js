
document.getElementById('analyze-form').addEventListener('submit', async function(e) {
  e.preventDefault();
  const videoId = document.getElementById('videoId').value.trim();
  document.getElementById('results').innerHTML = 'Processing...';

  // Replace the URL below with your backend server endpoint
  fetch('http://localhost:5000/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ videoId })
  })
  .then(response => response.json())
  .then(data => {
    let html = '';
    data.forEach(item => {
      html += `<div><b>Comment:</b> ${item.comment} <br>
                 <b>Sentiment:</b> ${item.sentiment} <br>
                 <b>Probabilities:</b> Negative: ${item.prob_negative}, Neutral: ${item.prob_neutral}, Positive: ${item.prob_positive}
               </div><hr>`;
    });
    document.getElementById('results').innerHTML = html;
  })
  .catch(err => {
    document.getElementById('results').innerHTML = 'Error: ' + err;
  });
});



