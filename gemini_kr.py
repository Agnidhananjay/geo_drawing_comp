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

# Original Korean prompt for table format (Architecture & Engineering)
COMP_PROMPT_ARCH = """제공된 두 도면(첫 번째는 변경 전, 두 번째는 변경 후)을 분석하여 지반공학 및 토공 전문가의 관점에서 다음 항목들의 차이점을 **표 형식으로** 분석해 주세요.

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

# New prompt for Energy & Construction Technology
COMP_PROMPT_ENERGY = """제공된 두 도면(첫 번째는 변경 전, 두 번째는 변경 후)을 분석하여 발전분야 및 화공분야 VP(Vendor Print) 전문가의 관점에서 다음 항목들의 차이점을 **표 형식으로** 분석해 주세요.

**[발전분야 VP(Vendor Print) 비교 분석]**

다음과 같은 **마크다운 표 형식**으로 응답해 주세요:

| 구분 | 변경 전 | 변경 후 | 변경 사항 설명 |
|------|---------|---------|----------------|
| 기준점 좌표 | [변경 전 내용] | [변경 후 내용] | [변경사항 상세 설명] |
| Foundation Size | [변경 전 내용] | [변경 후 내용] | [변경사항 상세 설명] |
| Weight | [변경 전 내용] | [변경 후 내용] | [변경사항 상세 설명] |
| Top of Concrete Level | [변경 전 내용] | [변경 후 내용] | [변경사항 상세 설명] |
| Grouting 유무 및 두께 | [변경 전 내용] | [변경 후 내용] | [변경사항 상세 설명] |
| Anchor Bolt 사양 | [변경 전 내용] | [변경 후 내용] | [변경사항 상세 설명] |
| Box-out 유무 및 상세 | [변경 전 내용] | [변경 후 내용] | [변경사항 상세 설명] |
| 하중 정보 | [변경 전 내용] | [변경 후 내용] | [변경사항 상세 설명] |
| NOTE 영역 변경사항 | [변경 전 내용] | [변경 후 내용] | [변경사항 상세 설명] |

**[화공분야 VP(Vendor Print) 비교 분석]**

| 구분 | 변경 전 | 변경 후 | 변경 사항 설명 |
|------|---------|---------|----------------|
| Key Plan 정보 | [변경 전 내용] | [변경 후 내용] | [변경사항 상세 설명] |
| Equipment Dimension | [변경 전 내용] | [변경 후 내용] | [변경사항 상세 설명] |
| Base Elevation | [변경 전 내용] | [변경 후 내용] | [변경사항 상세 설명] |
| Anchor Bolt 정보 | [변경 전 내용] | [변경 후 내용] | [변경사항 상세 설명] |
| Fixed/Sliding Side | [변경 전 내용] | [변경 후 내용] | [변경사항 상세 설명] |
| Weight 정보 | [변경 전 내용] | [변경 후 내용] | [변경사항 상세 설명] |
| 관련 주석/Note | [변경 전 내용] | [변경 후 내용] | [변경사항 상세 설명] |

**분석할 주요 항목들:**

**1. [발전분야 VP 분석 항목]**
   - **NOTE 텍스트 영역**: OCR 및 자연어처리 기반 인식 후 설계 기준 항목 비교 (Grouting 기준, 기준 Elevation, Anchor 설치 조건 등)
   - **Anchor Bolt 정보**: 위치 좌표(X,Y), 치수 정보, Grid 기준 위치, 중심좌표(mm), Foundation 외곽 치수, 개수, 배치 치수(Projection/Embed 길이) 등
   - **설계 핵심사항**: 기준점 좌표, Foundation Size(mm), Weight(ton), Top of Concrete Level(FL 기준), Grouting 두께(mm), Box-out 치수, 하중(Dead/Live/Wind/Seismic Load)

**2. [화공분야 VP 분석 항목]**
   - **장비 정보**: Key Plan 정보, Equipment Dimension(장비 외형 치수), Base Elevation(FL 기준 높이)
   - **Anchor Bolt**: 개수, 크기, 간격, 배치 변경사항
   - **고정/이동**: Fixed Side/Sliding Side 위치 변경
   - **하중 정보**: Empty, Erection, Operating, Test 각 하중값 변화
   - **주석 변경**: 관련 주석/Note 사항의 추가/삭제/수정

**3. [공통 분석 항목]**
   - 도면 번호 및 리비전 변경사항
   - 치수 및 좌표 변경 (mm 단위 정밀 분석)
   - 범례 및 기호 변경사항
   - 상세도 추가/삭제/수정사항

변경사항이 없는 항목의 경우 "변화 없음"으로 표기해 주세요. 
AI 기반 객체 인식과 텍스트 추론 기능을 모두 활용하여 구조적 데이터로 정리해주시기 바랍니다.
모든 응답은 한국어로 작성해 주세요."""

# Page configuration
st.set_page_config(
    page_title="지반공학 도면 비교",
    page_icon="🏗️",
    layout="wide"
)

# Custom CSS for better table rendering
st.markdown("""
<style>
    /* Improve table styling - subtle and integrated */
    .stMarkdown table {
        border-collapse: collapse !important;
        width: 100% !important;
        margin: 15px 0 !important;
        font-family: 'Segoe UI', 'Malgun Gothic', 'Apple Gothic', sans-serif !important;
        background-color: transparent !important;
        border-radius: 8px !important;
        overflow: hidden !important;
    }
    .stMarkdown th, .stMarkdown td {
        border: 1px solid rgba(250, 250, 250, 0.1) !important;
        padding: 10px 12px !important;
        text-align: left !important;
        vertical-align: top !important;
        color: inherit !important;
        background-color: rgba(255, 255, 255, 0.02) !important;
    }
    .stMarkdown th {
        background-color: rgba(255, 255, 255, 0.08) !important;
        font-weight: 600 !important;
        color: inherit !important;
        border-bottom: 2px solid rgba(250, 250, 250, 0.15) !important;
    }
    .stMarkdown tr:nth-child(even) td {
        background-color: rgba(255, 255, 255, 0.04) !important;
    }
    .stMarkdown tr:hover td {
        background-color: rgba(255, 255, 255, 0.08) !important;
    }
    .stMarkdown tr:hover th {
        background-color: rgba(255, 255, 255, 0.12) !important;
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
    /* Radio button styling */
    .stRadio > div {
        display: flex;
        flex-direction: row;
        gap: 20px;
    }
    .stRadio > div > label {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        padding: 10px 15px;
        border: 1px solid rgba(250, 250, 250, 0.1);
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .stRadio > div > label:hover {
        background-color: rgba(255, 255, 255, 0.1);
        border-color: rgba(250, 250, 250, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'comparison_result' not in st.session_state:
    st.session_state.comparison_result = None
if 'comparison_timestamp' not in st.session_state:
    st.session_state.comparison_timestamp = None
if 'selected_prompt_type' not in st.session_state:
    st.session_state.selected_prompt_type = "Architecture & Engineering"

# Get Gemini API Key from environment variable
api_key = st.secrets["GEMINI_API_KEY"]
if not api_key:
    st.error("환경 변수에서 GEMINI_API_KEY를 설정해 주세요")
    st.stop()

client = genai.Client(api_key=api_key)

# Function to encode image to base64
def encode_image(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# Function to compare the drawings using Gemini API
def compare_drawings(previous_image, current_image, prompt_type):
    try:
        # Select the appropriate prompt based on user selection
        if prompt_type == "Architecture & Engineering":
            selected_prompt = COMP_PROMPT_ARCH
        else:  # Energy & Construction Technology
            selected_prompt = COMP_PROMPT_ENERGY
            
        contents = [selected_prompt]
        contents.append(previous_image)
        contents.append(current_image)

        response = client.models.generate_content(
        model="gemini-2.5-pro",
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
def save_comparison_to_file(content, timestamp, prompt_type):
    prompt_suffix = "arch_eng" if prompt_type == "Architecture & Engineering" else "energy_const"
    filename = f"도면비교결과_{prompt_suffix}_{timestamp.strftime('%Y%m%d_%H%M%S')}.md"
    return filename, content

# Main UI
st.title("🏗️ 지반공학 도면 비교 도구")
st.markdown("AI 기반 분석으로 지반공학 도면의 이전 버전과 현재 버전을 비교합니다")

# Add prompt selection section
st.markdown("### 📋 분석 유형 선택")
prompt_type = st.radio(
    "분석하고자 하는 도면 유형을 선택하세요:",
    options=["Architecture & Engineering", "Energy & Construction Technology"],
    index=0,
    key="prompt_selection",
    help="Architecture & Engineering: 지반공학 및 토공 전문 분석\nEnergy & Construction Technology: 발전/화공분야 VP 분석"
)

# Store selected prompt type in session state
st.session_state.selected_prompt_type = prompt_type

# Display selected analysis type information
if prompt_type == "Architecture & Engineering":
    st.info("🏗️ **지반공학 및 토공 전문 분석**: 위치/형상, 벽체공법, 지보공법, 굴착레벨, 구조부재사양, 시공순서 등을 분석합니다.")
else:
    st.info("⚡ **에너지 & 건설기술 분석**: VP(Vendor Print) 도면의 Anchor Bolt, Foundation, Weight, Elevation 등 발전/화공분야 설비정보를 분석합니다.")

st.markdown("---")

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
    button_text = f"🔍 비교 분석 시작 ({prompt_type})"
    if st.button(button_text, type="primary", use_container_width=True):
        with st.spinner(f"도면을 {prompt_type} 방식으로 분석하고 있습니다... 잠시만 기다려 주세요..."):
            comparison_result = compare_drawings(previous_image_pil, current_image_pil, prompt_type)
            st.session_state.comparison_result = comparison_result
            st.session_state.comparison_timestamp = datetime.datetime.now()
        
        st.success("✅ 비교 분석이 성공적으로 완료되었습니다!")

# Display comparison results if available
if st.session_state.comparison_result:
    st.markdown("---")
    st.header("📊 비교 분석 결과")
    
    if st.session_state.comparison_timestamp:
        st.caption(f"생성 시간: {st.session_state.comparison_timestamp.strftime('%Y-%m-%d %H:%M:%S')} | 분석 유형: {st.session_state.selected_prompt_type}")
    
    # Create a container for the results with custom styling
    results_container = st.container()
    with results_container:
        # Use markdown to properly render the formatted content
        st.markdown(st.session_state.comparison_result)
    
    # Download button for the results
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        filename, content = save_comparison_to_file(
            st.session_state.comparison_result,
            st.session_state.comparison_timestamp,
            st.session_state.selected_prompt_type
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
    
    if st.session_state.selected_prompt_type == "Architecture & Engineering":
        st.markdown("""
        **지반공학 및 토공 전문 분석**
        이 도구는 지반공학 도면을 비교하여 다음 항목들을 분석합니다:
        - 위치 및 형상 변화
        - 벽체 공법 변화
        - 지보 공법 변화
        - 굴착 레벨 변화
        - 구조 부재 사양 변화
        - 시공 순서 변화
        - 기타 도면 변화사항
        """)
    else:
        st.markdown("""
        **에너지 & 건설기술 분석**
        이 도구는 발전/화공분야 VP 도면을 비교하여 다음 항목들을 분석합니다:
        - NOTE 텍스트 영역 인식 및 해석
        - Anchor Bolt 위치 및 치수 정보
        - 설계 필요 핵심사항 추출
        - Equipment Dimension 및 Base Elevation
        - Weight 정보 및 하중 분석
        - Fixed/Sliding Side 위치 분석
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
    - 분석 유형에 맞는 도면을 선택하세요
    """)
    
    st.header("🎯 분석 유형별 특징")
    with st.expander("Architecture & Engineering"):
        st.markdown("""
        - 지반공학 및 토공 전문 분석
        - 벽체/지보 공법 중심
        - 굴착 레벨 및 구조 부재 분석
        - 건축/토목 도면에 최적화
        """)
    
    with st.expander("Energy & Construction Technology"):
        st.markdown("""
        - 발전분야 VP(Vendor Print) 분석
        - Anchor Bolt 및 Foundation 중심
        - 화공분야 장비 도면 분석
        - Weight 및 하중 정보 추출
        """)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #888;'>Google Gemini 2.5 Pro 기반 | 다중 프롬프트 지원</p>",
    unsafe_allow_html=True
)