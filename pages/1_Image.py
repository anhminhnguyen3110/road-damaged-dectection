import logging
from typing import NamedTuple, List
from pathlib import Path
import numpy as np
import cv2
from ultralytics import YOLO
import streamlit as st
from io import BytesIO
from PIL import Image
import os

# Import functions from model.py
from model import get_pt_files_from_s3, check_and_download_model

# Configure Streamlit page settings
st.set_page_config(
    page_title="🚧 Road Damage Detection 🛣️",
    page_icon="🛣️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paths and logging setup
HERE = Path(__file__).parent
ROOT = HERE.parent
logger = logging.getLogger(__name__)

# Model configuration
MODELS_DIR = ROOT / "models"
CLASSES = [
    'Alligator Crack',
    'Vertical Crack',
    'Potholes',
    'Raveling',
    'Shoving',
    'Horizontal Crack'
]

# Function to load the selected model
@st.cache_resource
def load_model(model_path):
    return YOLO(model_path)

# Sidebar configuration for model selection
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

# Sidebar for detection parameters
st.sidebar.subheader("Detection Parameters")
score_threshold = st.sidebar.slider(
    "Confidence Threshold",
    min_value=0.0,
    max_value=1.0,
    value=0.5,
    step=0.05,
    help="Adjust to filter predictions by confidence."
)

st.sidebar.write(
    "🔍 **Tip**: Lowering the threshold may help detect subtle damage, but could increase false positives."
)

# Main title and description
st.title("🚧 Road Damage Detection System")
st.markdown(
    """
    <style>
        .description {
            font-size: 15px;
        }
    </style>
    """, unsafe_allow_html=True
)
st.markdown('<div class="description">Upload an image of a road to detect various types of damage, including Alligator Cracks, Potholes, and more. The system will analyze the image and highlight detected damage.</div>', unsafe_allow_html=True)

# File uploader
st.markdown("### 📸 Upload an Image")
image_file = st.file_uploader(
    "Accepted formats: PNG, JPG, JPEG",
    type=['png', 'jpg', 'jpeg'],
    help="Upload an image file to begin detection."
)

def predict_damage(image: Image.Image, model, threshold: float) -> List[Detection]:
    """Run the YOLO model to detect damage in the image."""
    _image = np.array(image)
    original_size = _image.shape[:2]

    # Resize image for prediction
    resized_image = cv2.resize(_image, (640, 640), interpolation=cv2.INTER_AREA)
    results = model.predict(resized_image, conf=threshold)

    # Extract detections
    detections = []
    for result in results:
        boxes = result.boxes.cpu().numpy()
        for box in boxes:
            detection = Detection(
                class_id=int(box.cls),
                label=CLASSES[int(box.cls)],
                score=float(box.conf),
                box=box.xyxy[0].astype(int)
            )
            detections.append(detection)

    # Annotate results back to original image size
    annotated_frame = results[0].plot()
    output_image = cv2.resize(annotated_frame, original_size[::-1], interpolation=cv2.INTER_AREA)

    return detections, output_image

if image_file:
    # Display original image
    st.image(image_file, caption="Uploaded Image", use_column_width=True)
    image = Image.open(image_file)

    # Perform detection with a progress indicator
    with st.spinner("🔍 Detecting road damage... Please wait."):
        detections, annotated_image = predict_damage(image, net, score_threshold)
    
    # Display results in two columns
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🖼️ Original Image")
        st.image(image, use_column_width=True)
    
    with col2:
        st.subheader("📍 Detected Damage")
        st.image(annotated_image, use_column_width=True)

        # Allow downloading the prediction image
        buffer = BytesIO()
        prediction_image = Image.fromarray(annotated_image)
        prediction_image.save(buffer, format="PNG")
        st.download_button(
            label="📥 Download Prediction Image",
            data=buffer.getvalue(),
            file_name="road_damage_prediction.png",
            mime="image/png"
        )

    # Display detection details
    st.markdown("### 📊 Detection Details")
    if detections:
        st.write(f"**Total Detections:** {len(detections)}")
        for detection in detections:
            st.markdown(f"- **{detection.label}** detected with a confidence of `{detection.score:.2f}` at `{detection.box}`")
    else:
        st.info("No damage detected. Try adjusting the confidence threshold.")
else:
    st.info("Please upload an image to start the detection process.")