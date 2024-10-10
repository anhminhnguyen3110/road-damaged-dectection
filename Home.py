import streamlit as st

st.set_page_config(
    page_title="Road Damage Detection",
    page_icon="🚧",
    initial_sidebar_state="collapsed",
)

# Apply custom CSS
st.markdown(
    """
    <style>
    .main {
        padding: 20px;
        border-radius: 8px;
    }
    .title {
        font-size: 36px;
        font-weight: bold;
    }
    .subheader {http://localhost:8501/Realtime_Detection
        font-size: 24px;
    }
    .section-title {
        font-size: 20px;
        font-weight: bold;
        margin-top: 20px;
    }
    .bullet-item {
        font-size: 16px;
        margin: 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Title of the app with custom styling
st.markdown('<div class="title">🚧 Road Damage Detection 🚧</div>', unsafe_allow_html=True)

# Engaging introduction with markdown
st.markdown(
    """
    ### 🛣️ Making Roads Safer, One Detection at a Time
    
    Welcome to the **Road Damage Detection App**, your digital companion for improving road safety and infrastructure upkeep. Powered by the cutting-edge **YOLO deep learning model**, this app has been fine-tuned with real-world data from the **Road Damage Tracking Dataset (RDTD)**.
    """,
    unsafe_allow_html=True,
)

# Display a banner image (replace 'path_to_image' with actual image path or URL)
st.image(r'resources/banner.png', use_column_width=True)

# Divide the content into columns for better layout
st.markdown(
    """
    ### 🚦 What Can We Detect?
    The model is trained to recognize six distinct types of road damage:
    - **Vertical Cracks**: Long, straight cracks that extend in a vertical direction along the road, often forming continuous lines that can vary in width and depth, but always following the length of the road.
    - **Horizontal Cracks**: Straight, lateral cracks that cut across the road surface from one side to the other, forming a clear division between sections of pavement, and can grow wider over time.
    - **Alligator Cracks**: A complex network of small, interconnected cracks that resemble the texture of alligator skin, often forming tight, irregular grids. These cracks create a fractured appearance and can cover large areas of the road.
    - **Potholes**: Circular or irregular depressions in the road, characterized by missing chunks of pavement, steep edges, and varying depths. These holes create a rough, uneven driving experience and can cause significant damage to vehicles.
    - **Shoving**: A wavy or bulging area on the road surface where the pavement appears to have been pushed up or shifted, often causing a noticeable bump or ripple effect when driving over it.
    - **Ravelling**: A coarse, loose surface where the top layer of asphalt and small aggregates have been worn away, leaving behind a rough texture with visible gaps between particles. The surface may appear dry and deteriorated, with loose gravel scattered on the pavement.
    """,
    unsafe_allow_html=True,
)

st.divider()

st.markdown('**Vertical Cracks Example**', unsafe_allow_html=True)
st.image(r'resources/vertical_crack.png', caption="Vertical Crack", use_column_width=True, width=200)

st.divider()

st.markdown('**Horizontal Cracks Example**', unsafe_allow_html=True)
st.image(r'resources/horizontal_crack.png', caption="Horizontal Crack", use_column_width=True, width=200)

st.divider()

st.markdown('**Potholes Example**', unsafe_allow_html=True)
st.image(r'resources/pothole.png', caption="Pothole", use_column_width=True, width=200)

st.divider()

st.markdown('**Alligator Cracks Example**', unsafe_allow_html=True)
st.image(r'resources/alligator_crack.png', caption="Alligator Crack", use_column_width=True, width=200)

st.markdown('**Shoving Example**', unsafe_allow_html=True)
st.image(r'resources/shoving.png', caption="Shoving", use_column_width=True, width=200)

st.divider()

st.markdown('**Ravelling Example**', unsafe_allow_html=True)
st.image(r'resources/ravelling.png', caption="Ravelling", use_column_width=True, width=200)

st.markdown("---")


# Behind the Scenes section with a different layout
st.markdown('<div class="section-title">🏎️ Behind the Scenes</div>', unsafe_allow_html=True)
st.markdown(
    """
    This powerful model utilizes the **YOLOv8 architecture**, trained on a dataset from Japan and India, ensuring it’s well-versed in detecting a variety of road conditions.
    """,
    unsafe_allow_html=True,
)

# Add a call to action to get started
st.markdown('<div class="section-title">🚀 Get Started</div>', unsafe_allow_html=True)
st.markdown(
    """
    Choose your input type from the sidebar—whether you want to analyze **real-time webcam footage, videos, or images**—and see the magic happen!
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

# Resources section
st.markdown('<div class="section-title">📚 Resources and More</div>', unsafe_allow_html=True)
st.markdown(
    """
    - 🔗 [GitHub Repository: Explore the Code](https://github.com/anhminhnguyen3110/Road-damaged-dectection)
    - 📊 [Road Damage Tracking Dataset (RDTD)](https://www.kaggle.com/datasets/mersico/road-damage-tracking-dataset-rdtd-v10/data): Dive into the data that powers the detection
    """,
    unsafe_allow_html=True,
)