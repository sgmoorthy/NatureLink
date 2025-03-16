from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, List

from .bhuvan_api import BhuvanAPI
from .bhuvan_services import BhuvanServices
from .data_processor import DataProcessor
from .model import CropYieldPredictor, ModelTrainer
import os
from dotenv import load_dotenv

app = FastAPI(title="NatureLink API", description="API for agricultural satellite data analysis")

# Mount static files
app.mount("/static", StaticFiles(directory="NatureLink/src/static"), name="static")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
load_dotenv()

# Initialize components
bhuvan_api = BhuvanAPI()
bhuvan_services = BhuvanServices(os.getenv('BHUVAN_API_KEY'), os.getenv('BHUVAN_API_BASE_URL'))
data_processor = DataProcessor()
model = CropYieldPredictor()
trainer = ModelTrainer(model)

class LocationData(BaseModel):
    latitude: float
    longitude: float
    date: str
    soil_type: str = None

class TimeSeriesData(BaseModel):
    latitude: float
    longitude: float
    start_date: str
    end_date: str

@app.get("/")
async def root():
    return {"message": "Welcome to NatureLink API - Your Agricultural Decision Support System"}

@app.post("/vegetation-indices")
async def get_vegetation_indices(data: LocationData):
    try:
        indices = bhuvan_api.get_vegetation_indices(data.latitude, data.longitude, data.date)
        return indices
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/soil-moisture")
async def get_soil_moisture(data: LocationData):
    try:
        moisture = bhuvan_api.get_soil_moisture(data.latitude, data.longitude, data.date)
        return {"moisture": moisture}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/lulc")
async def get_lulc(data: LocationData):
    try:
        lulc_data = bhuvan_services.get_lulc_data(data.latitude, data.longitude)
        return {
            "timestamp": datetime.now().isoformat(),
            "location": {"latitude": data.latitude, "longitude": data.longitude},
            "lulc_data": lulc_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/weather")
async def get_weather(data: LocationData):
    try:
        weather_data = bhuvan_services.get_weather_forecast(data.latitude, data.longitude)
        return {
            "timestamp": datetime.now().isoformat(),
            "location": {"latitude": data.latitude, "longitude": data.longitude},
            "weather_forecast": weather_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/crop-recommendations")
async def get_recommendations(data: LocationData):
    try:
        recommendations = bhuvan_services.get_crop_recommendations(
            data.latitude,
            data.longitude,
            data.soil_type
        )
        return {
            "timestamp": datetime.now().isoformat(),
            "location": {"latitude": data.latitude, "longitude": data.longitude},
            "recommendations": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ndvi-timeseries")
async def get_ndvi_series(data: TimeSeriesData):
    try:
        ndvi_data = bhuvan_services.get_ndvi_timeseries(
            data.latitude,
            data.longitude,
            data.start_date,
            data.end_date
        )
        return {
            "timestamp": datetime.now().isoformat(),
            "location": {"latitude": data.latitude, "longitude": data.longitude},
            "ndvi_timeseries": ndvi_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
async def analyze_location(data: LocationData):
    try:
        # Fetch satellite data
        satellite_data = bhuvan_api.get_satellite_data(
            data.latitude,
            data.longitude,
            data.date
        )
        
        # Process data
        processed_data = data_processor.process_satellite_data(satellite_data)
        features = data_processor.extract_features(processed_data)
        
        # Make prediction
        prediction = trainer.predict(features)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "location": {
                "latitude": data.latitude,
                "longitude": data.longitude
            },
            "vegetation_indices": bhuvan_api.get_vegetation_indices(
                data.latitude,
                data.longitude,
                data.date
            ),
            "soil_moisture": bhuvan_api.get_soil_moisture(
                data.latitude,
                data.longitude,
                data.date
            ),
            "yield_prediction": float(prediction[0])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))