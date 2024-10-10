import logging
import queue
from pathlib import Path
from typing import List, NamedTuple
import av
import cv2
import numpy as np
import streamlit as st
from streamlit_webrtc import WebRtcMode, webrtc_streamer
from ultralytics import YOLO
from get_stun_server import get_stun_server

# Import functions from model.py
from model import get_pt_files_from_github, check_and_download_model

# Configure Streamlit page
st.set_page_config(
    page_title="🚧 Realtime Road Damage Detection 📹",
    page_icon="📹",
    layout="wide",  # Wide layout for better visual presentation
    initial_sidebar_state="expanded"
)

# Paths and logging setup
HERE = Path(__file__).parent
ROOT = HERE.parent
logger = logging.getLogger(__name__)

# Model configuration
MODELS_DIR = ROOT / "models"
CLASSES = [
    'Alligator Crack', 'Vertical Crack', 'Potholes', 
    'Raveling', 'Shoving', 'Horizontal Crack'
]

# STUN server setup for WebRTC
STUN_SERVER = [{"urls": ["stun:" + get_stun_server()]}]

# Function to load the selected model
@st.cache_resource
def load_model(model_path):
    return YOLO(model_path)

# Sidebar: Model selection
st.sidebar.header("🔧 Settings")
st.sidebar.subheader("Model Selection")

# Get available models from the GitHub repository
available_models = get_pt_files_from_github()

# Display a dropdown for model selection without the .pt extension
model_options = [model['name'].replace('.pt', '') for model in available_models]
selected_model_name = st.sidebar.selectbox("Select a model:", model_options)

# Get the selected model's full file name with .pt extension
full_model_name = f"{selected_model_name}.pt"
selected_model_path = MODELS_DIR / full_model_name

# Check if the selected model is downloaded
if not selected_model_path.exists():
    with st.spinner(f"Downloading {full_model_name}... Please wait."):
        # Download the selected model
        selected_model = next(model for model in available_models if model['name'] == full_model_name)
        check_and_download_model(selected_model)

    st.sidebar.success(f"{full_model_name} downloaded successfully!")

# Load the selected model
MODEL_LOCAL_PATH = str(selected_model_path)
net = load_model(MODEL_LOCAL_PATH)

# Detection result named tuple
class Detection(NamedTuple):
    class_id: int
    label: str
    score: float
    box: np.ndarray

# Main interface
st.title("🚧 Road Damage Detection - Realtime 📹")
st.markdown(
    """
    <style>
        .description {
            font-size: 15px;
        }
    </style>
    """, unsafe_allow_html=True
)
st.markdown(
    '<div class="description">Monitor road conditions in real-time using a USB webcam. The system will detect various types of road damage and annotate them on the video feed. Adjust the confidence threshold below for better accuracy.</div>',
    unsafe_allow_html=True
)

# Sidebar configuration for detection sensitivity
st.sidebar.subheader("Detection Sensitivity")
score_threshold = st.sidebar.slider(
    "Confidence Threshold",
    min_value=0.0, max_value=1.0, value=0.5, step=0.05,
    help="Lowering the threshold may increase sensitivity but also false positives."
)

# Queue for processing results
result_queue: "queue.Queue[List[Detection]]" = queue.Queue()

def video_frame_callback(frame: av.VideoFrame) -> av.VideoFrame:
    """Processes each video frame and performs inference."""
    image = frame.to_ndarray(format="bgr24")
    original_height, original_width = image.shape[:2]

    # Resize the frame for YOLO model
    resized_image = cv2.resize(image, (640, 640), interpolation=cv2.INTER_AREA)
    results = net.predict(resized_image, conf=score_threshold)

    # Extract detections and store in the queue
    detections = []
    for result in results:
        for box in result.boxes.cpu().numpy():
            detection = Detection(
                class_id=int(box.cls),
                label=CLASSES[int(box.cls)],
                score=float(box.conf),
                box=box.xyxy[0].astype(int)
            )
            detections.append(detection)
    result_queue.put(detections)

    # Annotate the frame with detection results
    annotated_frame = results[0].plot()
    annotated_frame = cv2.resize(annotated_frame, (original_width, original_height), interpolation=cv2.INTER_AREA)

    return av.VideoFrame.from_ndarray(annotated_frame, format="bgr24")

# WebRTC streamer for real-time video processing
webrtc_ctx = webrtc_streamer(
    key="road-damage-detection",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration={"iceServers": STUN_SERVER},
    video_frame_callback=video_frame_callback,
    media_stream_constraints={
        "video": {
            "width": {"ideal": 1280, "min": 800},
        },
        "audio": False
    },
    async_processing=True,
)

# Divider for better visual separation
st.markdown("---")

# Display predictions in a table
st.subheader("📊 Detection Results")
st.markdown("Enable the checkbox below to view real-time detection results in tabular format.")

if st.checkbox("Show Detection Results", value=True):
    if webrtc_ctx.state.playing:
        labels_placeholder = st.empty()
        while True:
            detections = result_queue.get()
            if detections:
                # Display detection details in a more visually appealing table
                detection_data = [
                    {
                        "Damage Type": det.label,
                        "Confidence (%)": f"{det.score * 100:.1f}",
                        "Location (x1, y1, x2, y2)": f"{det.box}"
                    }
                    for det in detections
                ]
                labels_placeholder.table(detection_data)