import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [plot, setPlot] = useState('');
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!file) {
      setError('Please choose a CSV file first.');
      return;
    }

    setLoading(true);
    setError('');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('/api/predict', formData);
      setPlot(`data:image/png;base64,${response.data.plot}`);
      setPredictions(response.data.predictions || []);
    } catch (err) {
      const message = err.response?.data?.error || err.message;
      setError(message);
      setPlot('');
      setPredictions([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>Time Series Predictor</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="file"
          accept=".csv,text/csv"
          onChange={(event) => setFile(event.target.files?.[0] || null)}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Processing...' : 'Predict'}
        </button>
      </form>

      {error && <p role="alert">{error}</p>}
      {plot && <img src={plot} alt="Forecast plot" style={{ maxWidth: '100%' }} />}

      {predictions.length > 0 && (
        <div>
          <h2>Results</h2>
          <pre>{JSON.stringify(predictions, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
