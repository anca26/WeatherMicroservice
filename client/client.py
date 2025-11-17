import os
import grpc
from dotenv import load_dotenv
from generated import weather_pb2, weather_pb2_grpc

load_dotenv()

GRPC_HOST = os.getenv("GRPC_HOST")
GRPC_PORT = int(os.getenv("GRPC_PORT"))
GRPC_API_KEY = os.getenv("GRPC_API_KEY")

def main():
    with grpc.insecure_channel(f"{GRPC_HOST}:{GRPC_PORT}") as channel:
        stub = weather_pb2_grpc.WeatherServiceStub(channel)
        api_key_metadata = [('x-api-key', GRPC_API_KEY)]
        
        city = input("Enter city name: ").strip()
        
        try:
            response = stub.GetWeather(
                weather_pb2.WeatherRequest(city=city),
                metadata=api_key_metadata
            )
            if response.error:
                print(f"Error: {response.error}")
                return
            
            print(f"Weather in {response.city}:")
            print(f"  Temperature: {response.temperature_c} °C")
            print(f"  Humidity: {response.humidity} %")
            print(f"  Wind Speed: {response.wind_speed_ms} m/s")
            print(f"  Description: {response.description}")
        except grpc.RpcError as e:
            print(f"gRPC Error: {e.code()} - {e.details()}")
        
if __name__ == "__main__":
    main()