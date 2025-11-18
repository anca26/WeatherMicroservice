# weather_server/server.py
import os
import grpc
from concurrent import futures
from datetime import datetime, timezone
from dotenv import load_dotenv
import requests

from generated import weather_pb2, weather_pb2_grpc  
from server.repository import WeatherRepository
from server.interceptors import ApiKeyInterceptor

load_dotenv()
GRPC_HOST = os.getenv("GRPC_HOST")
GRPC_PORT = int(os.getenv("GRPC_PORT"))
OWM_API_KEY = os.getenv("OWM_API_KEY")
OWM_URL = "http://api.openweathermap.org/data/2.5/weather"

repo = WeatherRepository()

# WeatherService implementation 
class WeatherService(
    weather_pb2_grpc.WeatherServiceServicer
):
    def GetWeather(self, request, context):
            city = request.city.strip()
            print(f"[Info] Received request for city: {city}")
            if not city:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("city must not be empty")
                return weather_pb2.WeatherResponse(error="city must not be empty")
            try: #weather fetching from OWM
                print(f"[Info] Fetching weather data for {city}...")
                r = requests.get(
                    OWM_URL,
                    params = {"q": city, "appid": OWM_API_KEY, "units": "metric"},
                    timeout=10,
                )
                if r.status_code == 404:
                    return weather_pb2.WeatherResponse(city=city, error=f"City '{city}' not found")
                r.raise_for_status()
                j = r.json()
                
                print(f"[Info] Weather data for {city} fetched")
                response = weather_pb2.WeatherResponse(
                    city=j.get("name", city),
                    temperature_c=float(j["main"]["temp"]),
                    description=j["weather"][0]["description"],
                    humidity=int(j["main"]["humidity"]),
                    wind_speed_ms=float(j.get("wind", {}).get("speed", 0.0)),
                )
                
                try: #saving weather data to MongoDB
                    print(f"[Info] Sending weather data for saving ({response.city})...")
                    repo.save_weather_data(
                        city=response.city,
                        temperature_c=response.temperature_c,
                        description=response.description,
                        humidity=response.humidity,
                        wind_speed_ms=response.wind_speed_ms,
                    )
                except Exception as e:
                    print(f"[Warning] Mongo DB save failed: {e}")
                
                return response
            
            except requests.HTTPError as e:
                return weather_pb2.WeatherResponse(city=city, error=f"HTTP error: {e}")
            except Exception as e:
                return weather_pb2.WeatherResponse(city=city, error=f"Error: {e}")

#multithreading server setup
def serve():
    print("[Info] Starting gRPC server...")
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=[ApiKeyInterceptor()],
    )
    print("[Info] Registering WeatherService...")
    weather_pb2_grpc.add_WeatherServiceServicer_to_server(WeatherService(), server)
    server.add_insecure_port(f"{GRPC_HOST}:{GRPC_PORT}")
    print(f"[Info] Listening on {GRPC_HOST}:{GRPC_PORT}")
    server.start()
    server.wait_for_termination()
    
if __name__ == "__main__":
    
    try:
        serve()
    except KeyboardInterrupt:
        print("[Shutdown] Server stopped by user")