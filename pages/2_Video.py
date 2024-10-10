import os
import logging
from pathlib import Path
from typing import NamedTuple, List

import cv2
import numpy as np
import streamlit as st

# Deep learning framework
from ultralytics import YOLO

# Import functions from model.py
from model import get_pt_files_from_s3, check_and_download_model

# Streamlit page configuration
st.set_page_config(
    page_title="🚧 Road Damage Detection - Video 📹",
    page_icon="📹",
    layout="wide",  # Wide layout for a better user experience
    initial_sidebar_state="expanded"
)

# Path and logging setup
HERE = Path(__file__).parent
ROOT = HERE.parent
logger = logging.getLogger(__name__)

# Model configuration
MODELS_DIR = ROOT / "models"
CLASSES = [
    'Alligator Crack', 'Vertical Crack', 'Potholes', 
    'Raveling', 'Shoving', 'Horizontal Crack'
]

# Function to load the selected model
@st.cache_resource
def load_model(model_path):
    return YOLO(model_path)

# Sidebar: Model selection
st.sidebar.header("🔧 Settings")
st.sidebar.subheader("Model Selection")

# Get available models from the GitHub repository
available_models = get_pt_files_from_s3()

# Display a dropdown for model selection without the .pt extension
model_options = [model.replace('.pt', '') for model in available_models]
selected_model_name = st.sidebar.selectbox("Select a model:", model_options)

# Get the selected model's full file name with .pt extension
full_model_name = f"{selected_model_name}.pt"
selected_model_path = MODELS_DIR / full_model_name

# Check if the selected model is downloaded
if not selected_model_path.exists():
    with st.spinner(f"Downloading {full_model_name}... Please wait."):
        # Download the selected model
        selected_model = next(model for model in available_models if model == full_model_name)
        check_and_download_model(selected_model)

    st.sidebar.success(f"{full_model_name} downloaded successfully!")

# Load the selected model
MODEL_LOCAL_PATH = str(selected_model_path)
net = load_model(MODEL_LOCAL_PATH)

# Detection named tuple
class Detection(NamedTuple):
    class_id: int
    label: str
    score: float
    box: np.ndarray

# Create temporary folder for saving videos
TEMP_DIR = Path('./temp')
TEMP_DIR.mkdir(exist_ok=True)

temp_file_input = TEMP_DIR / "video_input.mp4"
temp_file_output = TEMP_DIR / "video_output.mp4"

# Initialize processing state
st.session_state.setdefault('processing', False)

def save_uploaded_file(file_path: Path, file_bytes) -> None:
    """Saves the uploaded file to the specified path."""
    with open(file_path, "wb") as f:
        f.write(file_bytes.getbuffer())

def process_video(video_path: Path, output_path: Path, threshold: float) -> None:
    """Performs damage detection on the uploaded video."""
    video_capture = cv2.VideoCapture(str(video_path))

    if not video_capture.isOpened():
        st.error('🚨 Error opening video file. Please upload a valid video.')
        return

    # Video properties
    width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = video_capture.get(cv2.CAP_PROP_FPS)
    frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

    # Display video properties
    st.write(f"**Video Properties:** {_format_duration(frame_count/fps)}, {width}x{height} @ {fps:.2f} FPS")

    # Setup video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

    # Processing loop
    progress_bar = st.progress(0, text="⏳ Processing video...")
    for frame_idx in range(frame_count):
        ret, frame = video_capture.read()
        if not ret:
            break

        # Perform inference on the frame
        detections, annotated_frame = _detect_and_annotate(frame, threshold)

        # Save the processed frame
        video_writer.write(cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR))

        # Update progress
        progress_bar.progress((frame_idx + 1) / frame_count, text=f"Processing frame {frame_idx + 1} of {frame_count}")

    # Finalize processing
    video_capture.release()
    video_writer.release()
    progress_bar.empty()
    st.success("✅ Video processing completed!")

def _detect_and_annotate(frame: np.ndarray, threshold: float):
    """Runs the YOLO model on the frame and annotates it with detection results."""
    resized_frame = cv2.resize(frame, (640, 640))
    results = net.predict(resized_frame, conf=threshold)

    # Extract detections
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

    # Annotate frame
    annotated_frame = results[0].plot()
    annotated_frame = cv2.resize(annotated_frame, (frame.shape[1], frame.shape[0]))
    return detections, annotated_frame

def _format_duration(duration: float) -> str:
    """Formats duration in seconds into a human-readable format."""
    minutes, seconds = divmod(int(duration), 60)
    return f"{minutes}m {seconds}s"

# Sidebar: Detection parameters
st.sidebar.subheader("Detection Parameters")
threshold = st.sidebar.slider("Confidence Threshold", 0.0, 1.0, 0.5, 0.05, help="Adjust detection sensitivity")

# Main interface
st.title("🚧 Road Damage Detection - Video 📹")
st.markdown(
    """
    <style>
        .description-text {
            font-size: 15px;
        }
    </style>
    """, unsafe_allow_html=True
)
st.markdown('<div class="description-text">Upload a video to detect road damage, including various types of cracks, potholes, and other issues. The system will process the video and annotate detected damage.</div>', unsafe_allow_html=True)

# Video file upload
st.markdown("### 📤 Upload Video (.mp4)")
video_file = st.file_uploader("Drag and drop or browse to upload", type=["mp4"], disabled=st.session_state.processing)

if video_file:
    save_uploaded_file(temp_file_input, video_file)

    if st.button("🚀 Start Detection", disabled=st.session_state.processing):
        st.session_state.processing = True
        process_video(temp_file_input, temp_file_output, threshold)
        st.session_state.processing = False

        # Download link for the processed video
        with open(temp_file_output, "rb") as f:
            st.download_button("📥 Download Processed Video", f, file_name="road_damage_output.mp4", mime="video/mp4")

        # Restart option
        if st.button("🔄 Restart Application"):
            st.experimental_rerun()
else:
    st.info("⚠️ Please upload a video file to start processing.")