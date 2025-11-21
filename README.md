# WeatherMicroservice

A microservice-based weather dashboard using Flask (UI), gRPC (Python), and MongoDB.  
Fetches current weather data from OpenWeatherMap and displays historical temperature charts.

---

## Features

- **Flask UI**: Search for a city, view temperature history, and fetch current weather.
- **gRPC Server**: Handles weather data fetching and MongoDB storage.
- **MongoDB**: Stores weather observations.
- **Dockerized**: Easy to run all services with Docker Compose.
- **Tests**: Includes unit tests for UI, server, and repository.

---

## Quick Start

### 1. Clone the repository

```sh
git clone <your-repo-url>
cd WeatherMicroservice
```

### 2. Set up environment variables

Copy `.env.example` to `.env` and fill in your API keys (or edit `.env` directly):

```env
OWM_API_KEY=your_openweathermap_api_key
GRPC_API_KEY=your_grpc_api_key
MONGO_URI=mongodb://root:example@mongo:27017/
MONGO_DB=weather_db
MONGO_COLLECTION=weather_data
GRPC_HOST=0.0.0.0
GRPC_PORT=50051
FLASK_HOST=0.0.0.0
FLASK_PORT=8080
FLASK_KEY=your_flask_secret_key
```

### 3. Build and run with Docker Compose

```sh
docker-compose up --build
```

- Flask UI: [http://localhost:8080](http://localhost:8080)
- gRPC server: `localhost:50051`
- MongoDB: `localhost:27017`

---

## Development

### Run tests

```sh
pip install -r requirements-dev.txt
set PYTHONPATH=.
pytest
```

## Project Structure

```
.
├── client/           # CLI client for gRPC server
├── generated/        # gRPC/protobuf generated code
├── protobufs/        # .proto files
├── server/           # gRPC server and MongoDB repository
├── ui/               # Flask UI app (templates, static, app.py)
├── tests/            # Unit tests
├── docker-compose.yml
├── dockerfile-server
├── dockerfile-ui
├── requirements.txt
├── requirements-dev.txt
└── .env
```

---

## API Keys

- **OpenWeatherMap:** [Get a free API key](https://openweathermap.org/api)
- **gRPC API Key:** Set any string, but must match between UI and server.

---

