# Dockerized LSTM Forecasting Web App

A containerized time-series prediction demo with a Flask backend, React frontend, Nginx reverse proxy, and committed model/scaler artifacts.

## Architecture

- **Frontend:** React served by Nginx on port 3000
- **Backend:** Flask/Gunicorn on port 5000
- **API routing:** browser requests `/api/predict`; Nginx proxies to `backend:5000/predict`
- **Model artifacts:** `backend/model.pkl` and `backend/scaler.pkl`

## Run with Docker Compose

```bash
git clone https://github.com/rahimizadeh/Dockerized-LSTM-Forecasting-Web-App.git
cd Dockerized-LSTM-Forecasting-Web-App
docker compose up --build
```

Open:

```text
http://localhost:3000
```

Backend health check:

```bash
curl http://localhost:5000/health
```

## Test the prediction endpoint directly

Use a numeric CSV compatible with the scaler/model input shape:

```bash
curl -X POST http://localhost:5000/predict \
  -F "file=@timeseries_data.csv"
```

The response contains a prediction array plus a base64-encoded PNG plot.

## Safety/robustness behavior

- only `.csv` uploads are accepted
- uploads are limited to 5 MB
- CSV columns must be numeric
- temporary upload files are deleted after each request
- matplotlib figures are explicitly closed after rendering
- backend error details are surfaced by the frontend

## Local backend syntax check

```bash
python -m py_compile backend/app.py backend/train_lstm.py
```

## Frontend build check

```bash
cd frontend
npm install
npm run build
```

## Docker checks

```bash
docker compose config
docker compose build
docker compose up
```

Then verify both `http://localhost:3000` and `http://localhost:5000/health`.
