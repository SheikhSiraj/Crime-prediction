document.addEventListener("DOMContentLoaded", function() {
  // Prediction form handler
  document.getElementById('predictBtn').addEventListener('click', function() {
      const hour = document.getElementById('hourSelect').value;
      const day = document.getElementById('daySelect').value;
      const month = document.getElementById('monthSelect').value;
      
      // Show loading state
      const predictBtn = document.getElementById('predictBtn');
      const originalText = predictBtn.innerHTML;
      predictBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Predicting...';
      predictBtn.disabled = true;
      
      fetch('/predict', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify({
              hour: hour,
              day: day,
              month: month
          })
      })
      .then(response => {
          if (!response.ok) {
              throw new Error('Network response was not ok');
          }
          return response.json();
      })
      .then(data => {
          if (data.error) {
              throw new Error(data.error);
          }
          
          const resultElement = document.getElementById('predictionResult');
          resultElement.innerHTML = `
              <div class="alert alert-${data.risk_level.toLowerCase()}" role="alert">
                  <h4 class="alert-heading">${data.message}</h4>
                  <div class="progress mt-2" style="height: 20px;">
                      <div class="progress-bar bg-${data.risk_level.toLowerCase()}" 
                           role="progressbar" 
                           style="width: ${data.prediction * 100}%;" 
                           aria-valuenow="${data.prediction * 100}" 
                           aria-valuemin="0" 
                           aria-valuemax="100">
                          ${(data.prediction * 100).toFixed(1)}%
                      </div>
                  </div>
              </div>
          `;
      })
      .catch(error => {
          console.error('Error:', error);
          document.getElementById('predictionResult').innerHTML = `
              <div class="alert alert-danger" role="alert">
                  <i class="fas fa-exclamation-triangle me-2"></i>
                  ${error.message || 'Error making prediction'}
              </div>
          `;
      })
      .finally(() => {
          predictBtn.innerHTML = originalText;
          predictBtn.disabled = false;
      });
  });
});