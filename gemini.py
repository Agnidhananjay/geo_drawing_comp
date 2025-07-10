import streamlit as st
from openai import OpenAI
import os
import json
import base64
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
from prompts import COMP_PROMPT
import datetime
from google import genai
from google.genai import types
# Load environment variables from .env file
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Geotechnical Drawing Comparison",
    page_icon="🏗️",
    layout="wide"
)

# Custom CSS for better table rendering
st.markdown("""
<style>
    /* Improve table styling */
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 20px 0;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    th {
        background-color: #f2f2f2;
        font-weight: bold;
    }
    tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    /* Style for comparison results container */
    .comparison-results {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
    }
    /* Improve heading styles */
    h2 {
        color: #1f4788;
        margin-top: 25px;
    }
    h3 {
        color: #2d5aa0;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'comparison_result' not in st.session_state:
    st.session_state.comparison_result = None
if 'comparison_timestamp' not in st.session_state:
    st.session_state.comparison_timestamp = None

# Get OpenAI API Key from environment variable
# 
api_key = st.secrets["GEMINI_API_KEY"]
if not api_key:
    st.error("Please set your GEMINI_API_KEY in the .env file")
    st.stop()

client = genai.Client(api_key=api_key)

# Function to encode image to base64
def encode_image(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# Function to compare the drawings using OpenAI API
def compare_drawings(previous_image, current_image):
    try:
        contents = [COMP_PROMPT]
        contents.append(previous_image)
        contents.append(current_image)


        response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=contents,
        )
        response = json.loads(response.text)
        return response
    except Exception as e:
        return f"Error occurred: {str(e)}"

# Function to save comparison result to file
def save_comparison_to_file(content, timestamp):
    filename = f"comparison_result_{timestamp.strftime('%Y%m%d_%H%M%S')}.md"
    return filename, content

# Main UI
st.title("🏗️ Geotechnical Drawing Comparison Tool")
st.markdown("Compare previous and current versions of geotechnical drawings with AI-powered analysis")

# Create two columns for file uploaders
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Previous Version")
    previous_image = st.file_uploader(
        "Upload Previous Drawing",
        type=["jpg", "png", "jpeg"],
        key="prev_upload"
    )

with col2:
    st.subheader("📄 Current Version")
    current_image = st.file_uploader(
        "Upload Current Drawing",
        type=["jpg", "png", "jpeg"],
        key="curr_upload"
    )

# Display uploaded images if available
if previous_image and current_image:
    col1, col2 = st.columns(2)
    
    previous_image_pil = Image.open(previous_image)
    current_image_pil = Image.open(current_image)
    
    with col1:
        st.image(previous_image_pil, caption="Previous Version", use_container_width=True)
    
    with col2:
        st.image(current_image_pil, caption="Current Version", use_container_width=True)
    
    # Encode images to base64
    # previous_image_base64 = encode_image(previous_image_pil)
    # current_image_base64 = encode_image(current_image_pil)
    
    # Comparison button
    if st.button("🔍 Start Comparison", type="primary", use_container_width=True):
        with st.spinner("Analyzing drawings... This may take a moment..."):
            comparison_result = compare_drawings(previous_image_pil, current_image_pil)
            st.session_state.comparison_result = comparison_result
            st.session_state.comparison_timestamp = datetime.datetime.now()
        
        st.success("✅ Comparison completed successfully!")

# Display comparison results if available
if st.session_state.comparison_result:
    st.markdown("---")
    st.header("📊 Comparison Results")
    
    if st.session_state.comparison_timestamp:
        st.caption(f"Generated on: {st.session_state.comparison_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create a container for the results with custom styling
    results_container = st.container()
    with results_container:
        # Use markdown to properly render the formatted content
        st.markdown('<div class="comparison-results">', unsafe_allow_html=True)
        st.markdown(st.session_state.comparison_result)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Download button for the results
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        filename, content = save_comparison_to_file(
            st.session_state.comparison_result,
            st.session_state.comparison_timestamp
        )
        st.download_button(
            label="📥 Download Results (Markdown)",
            data=content,
            file_name=filename,
            mime="text/markdown"
        )
    
    with col2:
        # Also provide as plain text
        st.download_button(
            label="📥 Download Results (Text)",
            data=content,
            file_name=filename.replace('.md', '.txt'),
            mime="text/plain"
        )

# Sidebar for additional options
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This tool compares geotechnical drawings and identifies:
    - Changes in location & shape
    - Wall construction methods
    - Support methods
    - Excavation levels
    - Material specifications
    - Construction sequences
    - Other drawing changes
    """)
    
    st.header("🔧 Settings")
    if st.button("Clear Comparison Results"):
        st.session_state.comparison_result = None
        st.session_state.comparison_timestamp = None
        st.rerun()
    
    st.header("📝 Tips")
    st.markdown("""
    - Upload high-quality images for best results
    - Ensure drawings are properly oriented
    - Check that text is legible in the images
    """)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #888;'>Powered by Gemini-2.5-pro Vision</p>",
    unsafe_allow_html=True
)