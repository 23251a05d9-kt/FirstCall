import os
import math
import asyncio
import pickle
import torch
import numpy as np
import cv2

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from torchvision.models.video import r3d_18
import torch.nn as nn

from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")

twilio_client = Client(TWILIO_SID, TWILIO_AUTH)


from feature_extractor import VideoFeatureExtractor

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# LOAD MODELS
# =====================================================

rf_bundle = pickle.load(open("models/accident_detector.pkl", "rb"))
rf_model = rf_bundle["model"]
scaler = rf_bundle["scaler"]
feature_extractor = rf_bundle["feature_extractor"]

device = torch.device("cpu")

crime_model = r3d_18(weights=None)
crime_model.fc = nn.Sequential(
    nn.Dropout(p=0.5),
    nn.Linear(crime_model.fc.in_features, 4)
)

crime_model.load_state_dict(
    torch.load("models/best_crime_model2.pth", map_location=device)
)
crime_model.eval()

# =====================================================
# SYSTEM STATE
# =====================================================

system_state = {
    "state": "IDLE",
    "incident_type": None,
    "nearest_police": None,
    "nearest_hospital": None
}

# =====================================================
# CAMERA LOCATIONS
# =====================================================

cameras = {
    "CAM1": (17.3850, 78.4867),
    "CAM2": (17.4000, 78.5000),
    "CAM3": (17.3700, 78.4700)
}

# =====================================================
# POLICE + HOSPITAL DATA
# =====================================================

police_stations = [
    {"name": "Police A", "lat": 17.3900, "lon": 78.4800, "phone": "+917981214838"},
    {"name": "Police B", "lat": 17.4100, "lon": 78.5100, "phone": "+918555866952"},
    {"name": "Police C", "lat": 17.3600, "lon": 78.4600, "phone": "+918978369131"},
]

hospitals = [
    {"name": "Hospital A", "lat": 17.3880, "lon": 78.4820, "phone": "+916281466649"},
    {"name": "Hospital B", "lat": 17.4020, "lon": 78.4950, "phone": "+917981214838"},
    {"name": "Hospital C", "lat": 17.3720, "lon": 78.4750, "phone": "+918555866952"},
]

# =====================================================
# HAVERSINE
# =====================================================

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)

    a = (
        math.sin(dLat/2)**2 +
        math.cos(math.radians(lat1)) *
        math.cos(math.radians(lat2)) *
        math.sin(dLon/2)**2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c


def find_nearest(camera_id):
    cam_lat, cam_lon = cameras[camera_id]

    nearest_police = min(
        police_stations,
        key=lambda p: haversine(cam_lat, cam_lon, p["lat"], p["lon"])
    )

    nearest_hospital = min(
        hospitals,
        key=lambda h: haversine(cam_lat, cam_lon, h["lat"], h["lon"])
    )

    return nearest_police, nearest_hospital

# =====================================================
# R3D PREPROCESS
# =====================================================

def preprocess_for_r3d(video_path):

    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    indices = np.linspace(0, total_frames - 1, 16).astype(int)
    frames = []

    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (112, 112))
        frames.append(frame)

    cap.release()

    frames = np.array(frames) / 255.0

    mean = np.array([0.43216, 0.394666, 0.37645])
    std = np.array([0.22803, 0.22145, 0.216989])

    frames = (frames - mean) / std
    frames = np.transpose(frames, (3, 0, 1, 2))

    tensor = torch.tensor(frames, dtype=torch.float32).unsqueeze(0)

    return tensor

# =====================================================
# MAIN PIPELINE
# =====================================================

async def run_model(camera_id, video_path):

    system_state["state"] = "ANALYZING"
    await asyncio.sleep(np.random.uniform(2, 4))

    # ----- Accident Detection -----

    rf_features = feature_extractor.extract_video_features(video_path)
    rf_features_scaled = scaler.transform([rf_features])
    accident_pred = rf_model.predict(rf_features_scaled)[0]

    if accident_pred == 1:
        system_state["state"] = "DETECTED"
        system_state["incident_type"] = "TRAFFIC"
        await asyncio.sleep(2)
        await trigger_alerts(camera_id)
        return

    # ----- Crime Classification -----

    tensor = preprocess_for_r3d(video_path)

    with torch.no_grad():
        output = crime_model(tensor)
        pred = torch.argmax(output, dim=1).item()

    mapping = {
        0: "VIOLENT",
        1: "PROPERTY",
        2: "DESTRUCTIVE",
        3: "NORMAL"
    }

    category = mapping[pred]

    if category == "NORMAL":
        await asyncio.sleep(2)
        system_state["state"] = "COMPLETED"
        system_state["incident_type"] = "NORMAL"
        return

    system_state["state"] = "DETECTED"
    system_state["incident_type"] = category

    await asyncio.sleep(2)
    await trigger_alerts(camera_id)

# =====================================================
# ALERT HANDLER
# =====================================================

# async def trigger_alerts(camera_id):

#     system_state["state"] = "CALLING"

#     nearest_police, nearest_hospital = find_nearest(camera_id)

#     system_state["nearest_police"] = nearest_police["name"]
#     system_state["nearest_hospital"] = nearest_hospital["name"]

#     incident = system_state["incident_type"]

#     incident_readable = {
#         "VIOLENT": "Violent Crime",
#         "PROPERTY": "Property Crime",
#         "DESTRUCTIVE": "Destructive Activity",
#         "TRAFFIC": "Traffic Accident",
#         "NORMAL": "Normal Activity"
#     }.get(incident, incident)

#     # 📍 Get camera coordinates
#     cam_lat, cam_lon = cameras[camera_id]

#     # 📍 Google Maps link
#     maps_link = f"https://www.google.com/maps?q={cam_lat},{cam_lon}"

#     message_body = (
#         f"🚨 Emergency Detected!\n\n"
#         f"Camera ID: {camera_id}\n"
#         f"Incident: {incident_readable}\n\n"
#         f"Location:\n{maps_link}"
#     )

#     police_twiml = f"""
#     <Response>
#         <Say voice="alice" rate="85%">
#             Emergency detected.
#             Incident type: {incident_readable}.
#             Camera ID: {camera_id}.
#             Please check your message for exact location.
#         </Say>
#     </Response>
#     """

#     hospital_twiml = f"""
#     <Response>
#         <Say voice="alice" rate="85%">
#             Emergency detected.
#             Incident type: {incident_readable}.
#             Camera ID: {camera_id}.
#             Please check your message for exact location.
#         </Say>
#     </Response>
#     """

#     try:
#         # Call Police
#         twilio_client.calls.create(
#             to=nearest_police["phone"],
#             from_=TWILIO_NUMBER,
#             twiml=police_twiml
#         )

#         # Call Hospital
#         twilio_client.calls.create(
#             to=nearest_hospital["phone"],
#             from_=TWILIO_NUMBER,
#             twiml=hospital_twiml
#         )

#         # SMS Police
#         twilio_client.messages.create(
#             body=message_body,
#             from_=TWILIO_NUMBER,
#             to=nearest_police["phone"]
#         )

#         # SMS Hospital
#         twilio_client.messages.create(
#             body=message_body,
#             from_=TWILIO_NUMBER,
#             to=nearest_hospital["phone"]
#         )

#     except Exception as e:
#         print("Twilio error:", e)

#     await asyncio.sleep(3)

#     system_state["state"] = "ALERT_SENT"


# =====================================================
# API ENDPOINTS
# =====================================================

@app.post("/start-monitoring")
async def start_monitoring(camera_id: str = Form(...), video: UploadFile = File(...)):

    if camera_id not in cameras:
        return {"error": "Invalid camera ID"}

    os.makedirs("temp", exist_ok=True)
    file_path = f"temp/{video.filename}"

    with open(file_path, "wb") as f:
        f.write(await video.read())

    system_state["state"] = "MONITORING"
    system_state["incident_type"] = None
    system_state["nearest_police"] = None
    system_state["nearest_hospital"] = None

    asyncio.create_task(run_model(camera_id, file_path))

    return {"message": "Monitoring started"}


@app.get("/status")
def get_status():
    return system_state
