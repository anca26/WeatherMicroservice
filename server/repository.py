from pymongo import MongoClient, ASCENDING, errors
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

class WeatherRepository:
    def __init__(self, uri=MONGO_URI, db=MONGO_DB, collection=MONGO_COLLECTION):
        print(f"[Info] Connecting to MongoDB at {uri}...")
        try:
            self.client = MongoClient(uri)
            self.col = self.client[db][collection]
        
            self.col.create_index([("city", ASCENDING), ("timestamp", ASCENDING)])
            print(f"[Info] Connected to: {db}, collection: {collection}")
        except errors.ConnectionFailure as e:
            print(f"[Error] Could not connect to MongoDB: {e}")
        except Exception as e:
            print(f"[Error] Unexpected error from MongoDB: {e}")
        
        
    def save_weather_data(self, city, temperature_c, description, humidity, wind_speed_ms):
        print(f"[Info] Saving weather data for city: {city}...")
        data = {
            "city": city,
            "temperature_c": temperature_c,
            "humidity": humidity,
            "description": description,
            "wind_speed_ms": wind_speed_ms,
            "timestamp": datetime.now(timezone.utc) #added just for charts
        }
        
        if data is None:
            print("[Warning] No data to save.")
            return
        
        try:
            self.col.insert_one(data)
            print(f"[Info] Weather data for {city} saved to MongoDB.")
        except errors.DuplicateKeyError:
            print(f"[Warning] Duplicate entry for city: {city} at {data['timestamp']}")
        except errors.OperationFailure as e:
            print(f"[Error] Failed to save data: {e}")
        except Exception as e:
            print(f"[Error] Unexpected error while saving: {e}")
        

    
