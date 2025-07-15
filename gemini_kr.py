import streamlit as st
import os
import json
import base64
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
import datetime
from google import genai
from google.genai import types

# Load environment variables from .env file
load_dotenv()

# Updated Korean prompt for table format
COMP_PROMPT = """제공된 두 도면(첫 번째는 변경 전, 두 번째는 변경 후)을 분석하여 지반공학 및 토공 전문가의 관점에서 다음 항목들의 차이점을 **표 형식으로** 분석해 주세요.

다음과 같은 **마크다운 표 형식**으로 응답해 주세요:

| 구분 | 변경 전 | 변경 후 | 변경 사항 설명 |
|------|---------|---------|----------------|
| 위치 및 형상 | [변경 전 내용] | [변경 후 내용] | [변경사항 상세 설명] |
| 벽체 공법 | [변경 전 내용] | [변경 후 내용] | [변경사항 상세 설명] |
| 지보 공법 | [변경 전 내용] | [변경 후 내용] | [변경사항 상세 설명] |
| 굴착 레벨(EL) | [변경 전 내용] | [변경 후 내용] | [변경사항 상세 설명] |
| 구조 부재 사양 | [변경 전 내용] | [변경 후 내용] | [변경사항 상세 설명] |
| 시공 순서 | [변경 전 내용] | [변경 후 내용] | [변경사항 상세 설명] |
| 기타 변경사항 | [변경 전 내용] | [변경 후 내용] | [변경사항 상세 설명] |

**분석할 주요 항목들:**

1. **위치 및 형상 변화**
   - 위치 변화 (공간, 경계선으로부터의 거리 등)
   - 형상 변화 (곡선 → 직선, 벽체 연결부 변화 등)

2. **벽체 공법 변화**
   - CIP, 흙막이판, SCW, 연속벽 등의 공법 변화

3. **지보 공법 변화**
   - RAKER, Anchor, Strut 등의 지보 공법 변화

4. **굴착 레벨(EL) 변화**
   - 굴착 레벨 값 변화 (예: EL(-) 12.0 → EL(-) 13.0)
   - 표기 위치 및 추가/삭제

5. **구조 부재 사양 변화**
   - H-PILE 사양 변화 (예: H-300x300x10x15 (C.T.C1800) → H-300x200x9x14 (C.T.C900))
   - WALE 사양 변화
   - Anchor 규격 및 간격
   - Raker 간격 등

6. **시공 순서 계획 변화**
   - 공법 변화 (예: SGR → ESG, 실리카계 등)

7. **기타 도면 변화**
   - 기호 위치 변경, 범례 및 주석 추가/삭제 등

변경사항이 없는 항목의 경우 "변화 없음"으로 표기해 주세요. 모든 응답은 한국어로 작성해 주세요."""

# Page configuration
st.set_page_config(
    page_title="지반공학 도면 비교",
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
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 12px 8px;
        text-align: left;
        vertical-align: top;
    }
    th {
        background-color: #f2f2f2;
        font-weight: bold;
        color: #333;
    }
    tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    tr:hover {
        background-color: #f5f5f5;
    }
    /* Style for comparison results container */
    .comparison-results {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* Improve heading styles */
    h1 {
        color: #1f4788;
        text-align: center;
    }
    h2 {
        color: #1f4788;
        margin-top: 25px;
    }
    h3 {
        color: #2d5aa0;
        margin-top: 20px;
    }
    /* Korean font support */
    * {
        font-family: 'Segoe UI', 'Malgun Gothic', 'Apple Gothic', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'comparison_result' not in st.session_state:
    st.session_state.comparison_result = None
if 'comparison_timestamp' not in st.session_state:
    st.session_state.comparison_timestamp = None

# Get Gemini API Key from environment variable
api_key = st.secrets["GEMINI_API_KEY"]
if not api_key:
    st.error("환경 변수에서 GEMINI_API_KEY를 설정해 주세요")
    st.stop()

client = genai.Client(api_key=api_key)

# Function to convert PIL Image to base64 for Gemini
def pil_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# Function to compare the drawings using Gemini API
def compare_drawings(previous_image, current_image):
    try:
        # Convert PIL images to base64
        prev_base64 = pil_to_base64(previous_image)
        curr_base64 = pil_to_base64(current_image)
        
        # Create content with text and images
        contents = [
            COMP_PROMPT,
            {
                "mime_type": "image/jpeg",
                "data": prev_base64
            },
            {
                "mime_type": "image/jpeg", 
                "data": curr_base64
            }
        ]

        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=contents,
        )
        
        resp_text = response.text.strip()
        if resp_text.startswith("```"):
            resp_text = resp_text.replace("```", "").strip()
            if resp_text.lower().startswith("json"):
                resp_text = resp_text[4:].strip()
        return resp_text
    except Exception as e:
        return f"오류가 발생했습니다: {str(e)}"

# Function to save comparison result to file
def save_comparison_to_file(content, timestamp):
    filename = f"도면비교결과_{timestamp.strftime('%Y%m%d_%H%M%S')}.md"
    return filename, content

# Main UI
st.title("🏗️ 지반공학 도면 비교 도구")
st.markdown("AI 기반 분석으로 지반공학 도면의 이전 버전과 현재 버전을 비교합니다")

# Create two columns for file uploaders
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 변경 전 도면")
    previous_image = st.file_uploader(
        "변경 전 도면 업로드",
        type=["jpg", "png", "jpeg"],
        key="prev_upload"
    )

with col2:
    st.subheader("📄 변경 후 도면")
    current_image = st.file_uploader(
        "변경 후 도면 업로드",
        type=["jpg", "png", "jpeg"],
        key="curr_upload"
    )

# Display uploaded images if available
if previous_image and current_image:
    col1, col2 = st.columns(2)
    
    previous_image_pil = Image.open(previous_image)
    current_image_pil = Image.open(current_image)
    
    with col1:
        st.image(previous_image_pil, caption="변경 전 도면", use_container_width=True)
    
    with col2:
        st.image(current_image_pil, caption="변경 후 도면", use_container_width=True)
    
    # Comparison button
    if st.button("🔍 비교 분석 시작", type="primary", use_container_width=True):
        with st.spinner("도면을 분석하고 있습니다... 잠시만 기다려 주세요..."):
            comparison_result = compare_drawings(previous_image_pil, current_image_pil)
            st.session_state.comparison_result = comparison_result
            st.session_state.comparison_timestamp = datetime.datetime.now()
        
        st.success("✅ 비교 분석이 성공적으로 완료되었습니다!")

# Display comparison results if available
if st.session_state.comparison_result:
    st.markdown("---")
    st.header("📊 비교 분석 결과")
    
    if st.session_state.comparison_timestamp:
        st.caption(f"생성 시간: {st.session_state.comparison_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
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
            label="📥 결과 다운로드 (Markdown)",
            data=content,
            file_name=filename,
            mime="text/markdown"
        )
    
    with col2:
        # Also provide as plain text
        st.download_button(
            label="📥 결과 다운로드 (Text)",
            data=content,
            file_name=filename.replace('.md', '.txt'),
            mime="text/plain"
        )

# Sidebar for additional options
with st.sidebar:
    st.header("ℹ️ 정보")
    st.markdown("""
    이 도구는 지반공학 도면을 비교하여 다음 항목들을 분석합니다:
    - 위치 및 형상 변화
    - 벽체 공법 변화
    - 지보 공법 변화
    - 굴착 레벨 변화
    - 구조 부재 사양 변화
    - 시공 순서 변화
    - 기타 도면 변화사항
    """)
    
    st.header("🔧 설정")
    if st.button("비교 결과 초기화"):
        st.session_state.comparison_result = None
        st.session_state.comparison_timestamp = None
        st.rerun()
    
    st.header("📝 사용 팁")
    st.markdown("""
    - 최상의 결과를 위해 고품질 이미지를 업로드하세요
    - 도면이 올바르게 방향이 맞춰져 있는지 확인하세요
    - 이미지의 텍스트가 선명하게 읽힐 수 있는지 확인하세요
    """)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #888;'>Google Gemini 2.0 Flash 기반</p>",
    unsafe_allow_html=True
)