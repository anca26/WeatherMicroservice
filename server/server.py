# weather_server/server.py
import os
import grpc
from concurrent import futures
from datetime import datetime, timezone
from dotenv import load_dotenv
import requests

from generated import weather_pb2, weather_pb2_grpc  

load_dotenv()
GRPC_HOST = os.getenv("GRPC_HOST")
GRPC_PORT = int(os.getenv("GRPC_PORT"))
OWM_API_KEY = os.getenv("OWM_API_KEY")
GRPC_API_KEY = os.getenv("GRPC_API_KEY")
OWM_URL = "http://api.openweathermap.org/data/2.5/weather"


# gRPC Interceptor for API key authentication
class ApiKeyInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        md = dict(handler_call_details.invocation_metadata or [])
        if md.get("x-api-key") != GRPC_API_KEY:
            def deny(request, context):
                context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid API key")
            return grpc.unary_unary_rpc_method_handler(deny)
        return continuation(handler_call_details)


# WeatherService implementation 
class WeatherService(
    weather_pb2_grpc.WeatherServiceServicer
):
    def GetWeather(self, request, context):
            city = request.city.strip()
            if not city:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("city must not be empty")
                return weather_pb2.WeatherResponse(error="city must not be empty")
            try:
                r = requests.get(
                    OWM_URL,
                    params = {"q": city, "appid": OWM_API_KEY, "units": "metric"},
                    timeout=10,
                )
                if r.status_code == 404:
                    return weather_pb2.WeatherResponse(city=city, error=f"City '{city}' not found")
                r.raise_for_status()
                j = r.json()
                
                return weather_pb2.WeatherResponse(
                    city=j.get("name", city),
                    temperature_c=float(j["main"]["temp"]),
                    description=j["weather"][0]["description"],
                    humidity=int(j["main"]["humidity"]),
                    wind_speed_ms=float(j.get("wind", {}).get("speed", 0.0)),
                )
            except requests.HTTPError as e:
                return weather_pb2.WeatherResponse(city=city, error=f"HTTP error: {e}")
            except Exception as e:
                return weather_pb2.WeatherResponse(city=city, error=f"Error: {e}")

#multithreading server setup
def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=[ApiKeyInterceptor()],
    )
    weather_pb2_grpc.add_WeatherServiceServicer_to_server(WeatherService(), server)
    server.add_insecure_port(f"{GRPC_HOST}:{GRPC_PORT}")
    print(f"listening on {GRPC_HOST}:{GRPC_PORT}")
    server.start()
    server.wait_for_termination()
    
if __name__ == "__main__":
    serve()

