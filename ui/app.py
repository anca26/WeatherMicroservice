import os
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient, errors
import grpc

from generated import weather_pb2, weather_pb2_grpc


load_dotenv()

GRPC_HOST = os.getenv("GRPC_HOST")
GRPC_PORT = int(os.getenv("GRPC_PORT"))
GRPC_API_KEY = os.getenv("GRPC_API_KEY")

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

FLASK_HOST = os.getenv("FLASK_HOST")
FLASK_PORT = int(os.getenv("FLASK_PORT"))
FLASK_KEY = os.getenv("FLASK_KEY")


app = Flask(__name__)
app.secret_key = FLASK_KEY

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
coll = db[MONGO_COLLECTION]

def fetch_data(city):
     with grpc.insecure_channel(f"{GRPC_HOST}:{GRPC_PORT}") as channel:
        stub = weather_pb2_grpc.WeatherServiceStub(channel)
        api_key_metadata = [('x-api-key', GRPC_API_KEY)]
        
        try:
            response = stub.GetWeather(
                weather_pb2.WeatherRequest(city=city),
                metadata=api_key_metadata
            )
            if response.error:
                return None, response.error 
            
            return response, None

        except grpc.RpcError as e:
            error_msg = f"gRPC Error: {e.code()} - {e.details()}"
            return None, error_msg

def solve_range_params(): 
    now = datetime.now(timezone.utc)

    r = (request.args.get('range') or "1d").lower()
    
    presets = {
            "1d": timedelta(days=1),
            "3d": timedelta(days=3),
            "5d": timedelta(days=5),
            "7d": timedelta(days=7),        
        }
        
    time = presets.get(r, presets["1d"])

        
    start_time = now - time
    end_time = now
    
    labels = {
        "1d": "Last day",
        "3d": "Last 3 days",
        "5d": "Last 5 days",
        "7d": "Last 7 days",
    }
    
    return start_time, end_time, labels.get(r, "Last day"),r

@app.get("/")
def index():
    city = request.args.get("city") or "Iasi"
    start_time, end_time, range_label, range_param = solve_range_params()
    
    documents = list(
        coll.find({"city":city, 
                   "timestamp":{"$gte": start_time, "$lte": end_time}})
            .sort("timestamp", 1)
    )
    
    labels = []
    temperatures = []
    
    for doc in documents:
        try:
            ts = doc.get("timestamp")
            labels.append(ts.strftime('%m-%d %H:%M'))
            temperatures.append(doc.get("temperature_c"))
        except Exception as e:
            print(f"[Error] Unexpected error while processing document: {e}")
            
    return render_template(
        "index.html",
        city=city,
        labels=labels,
        temps=temperatures,
        range_label=range_label,
        selected=range_param,
    )
    

@app.post("/fetch")
def fetch():
    city = request.form.get("city").strip()
    range = (request.form.get("range") or "1d").lower()
    
    if not city:
        return redirect(url_for("index", city="Iasi", range=range)) 
    
    data, error = fetch_data(city)
    if error:
        print(f"[Error] {error}")
        return redirect(url_for("index", city="Iasi", range=range))
    
    return redirect(url_for("index", city=city, range=range))

if __name__ == "__main__":
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=True)