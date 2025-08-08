# COMP_PROMPT = """In the future, if I provide the drawings before and after the change( the first one is befor and the second one is after), you are the world's best geotechnical and 
# earthwork experts, and by analyzing the differences between the two drawings based on the following matters. (Example: cip → slope)  
#  -Changes: Location (spaces, distance from borderline, etc.), shape (curve → straight line, change of wall connections, etc.) -Dosing
#    method: CIP, earth plate, SCW, diaphragm wall, etc.     2. Check the changes in the climax method. (Example: RAKER → Anchor, etc.) 
#        -Dosing method of earthenware: RAKER, Anchor, Strut, etc.     3. Compare the excavation level (EL) change (notation position and
#          additional, level value, etc.).   -Changes: Excavation level value change (e.g. el (-) 12.0 → EL (-) 13.0)     4. Check the 
#          changes in the soil component elements (for example, H-PILE, WALE, ANCHOR, RAKER, etc.).   -Changes: H-PILE 
#          specifications (for example, H-300x300x10x15 (C.T.C1800) → H-300x200x9x14 (C.T.C900)), WALE specifications 
#          (e.g. H-300x300x10x15/H-300x305x15x15 → 2H-300x9x914), Anchor standards and spacing, raker spacing, etc.    
#            5. Check the order plan change.   -Changes: In addition to changing the order method (e.g. SGR → ESG, Silica series, etc.) 
#            -Type of ordering method: SGR, ESG, ASG, Silica -based ordering method, etc.     6. Check the changes in other drawings.
#              (Example: Motor Position Change, Legends and Note Additional Materials, etc.)  
#             -Changes: Moving or adding new positions, fertilization or omission of legend symbols, additional or deletion, cross -sectional or section change"""


COMP_PROMPT = """I provided the drawings before and after the change( the first one is befor and the second one is after), you are the world's best geotechnical and 
earthwork experts, and by analyzing the differences between the two drawings based on the following matters. (Example: cip → slope)  
 -Changes: Location (spaces, distance from borderline, etc.), shape (curve → straight line, change of wall connections, etc.) -Dosing
   method: CIP, earth plate, SCW, diaphragm wall, etc.     2. Check the changes in the climax method. (Example: RAKER → Anchor, etc.) 
       -Dosing method of earthenware: RAKER, Anchor, Strut, etc.     3. Compare the excavation level (EL) change (notation position and
         additional, level value, etc.).   -Changes: Excavation level value change (e.g. el (-) 12.0 → EL (-) 13.0)     4. Check the 
         changes in the soil component elements (for example, H-PILE, WALE, ANCHOR, RAKER, etc.).   -Changes: H-PILE 
         specifications (for example, H-300x300x10x15 (C.T.C1800) → H-300x200x9x14 (C.T.C900)), WALE specifications 
         (e.g. H-300x300x10x15/H-300x305x15x15 → 2H-300x9x914), Anchor standards and spacing, raker spacing, etc.    
           5. Check the order plan change.   -Changes: In addition to changing the order method (e.g. SGR → ESG, Silica series, etc.) 
           -Type of ordering method: SGR, ESG, ASG, Silica -based ordering method, etc.     6. Check the changes in other drawings.
             (Example: Motor Position Change, Legends and Note Additional Materials, etc.)  
            -Changes: Moving or adding new positions, fertilization or omission of legend symbols, additional or deletion, cross -sectional or section change"""
comp_prompt = """[발전분야 VP(Vendor Print)]
1. 다음 설비 도면에서 아래의 정보를 추출해주세요. AI 기반 객체 인식과 텍스트 추론 기능을 모두 활용하여 구조적 데이터로 정리해주시기 바랍니다.
① [NOTE 텍스트 영역 인식 및 해석]
- 도면 내 Note 영역을 OCR 및 자연어처리 기반으로 인식 후,
- 설계 기준이 되는 항목을 요약 정리해주세요. (예: Grouting 기준, 기준 Elevation, Anchor 설치 조건 등)
② [Anchor Bolt 위치 및 치수 정보 추출]
- 도면에 나타난 Anchor Bolt의 위치 좌표 (X, Y)와 치수 정보를 표 형태로 정리해주세요.
- 변경 도면 비교를 위해 다음 항목 포함:
    • Grid 기준 위치 
    • 중심좌표 (mm)
    • Foundation 외곽 치수 (mm x mm)
    • Anchor Bolt 유무 및 개수
    • Anchor Bolt 배치 치수 (Projection/Embed 길이, 개소수 등)
③ [설계 필요 핵심사항 추출]
- 아래 항목별로 도면 및 연결 문서(예: Loading Data PDF 등)에서 확인되는 값을 추출해주세요. 
| 1 | 기준점 좌표 | 도면 내 기준 Grid 또는 중심점 |
| 2 | Foundation Size | mm 단위 치수 (예: 2100 x 2100) |
| 3 | Weight | ton 단위 (연결된 하중 문서 참고) |
| 4 | Top of Concrete Level | FL 기준 Elevation (mm 또는 m) |
| 5 | Grouting 유무 및 두께 | 존재 여부 및 Thickness (mm) |
| 6 | Anchor Bolt | Type / Projection Length / Embedded Length / 개소수 / Bolt간 거리 |
| 7 | Box-out 유무 및 상세 | Box out 존재 여부 및 치수 (mm x mm) |
| 8 | 하중 | Dead Load / Live Load / Wind Load / Seismic Load (단위 포함) |
출력은 Table로 정리해 주세요.
2️. 변경 도면 비교 분석
초도 도면 대비 2차 도면에서 변경된 부분을 비교해 주세요.
**출력 형식:**
- 변경 사항 비교 Table (Before / After / 변경내용)
[화공분야 VP(Vendor Print)]
1. 초도 도면 분석
다음 항목을 도면에서 인식하여 설계 기준이 되는 내용으로 요약 정리해주세요.
- Key Plan 정보
- Equipment Dimension (장비 외형 치수)
- Base Elevation (FL 기준 높이)
- Anchor Bolt 정보 (개수, 크기, 간격)
- Fixed Side / Sliding Side 위치
- Weight 정보 (Empty, Erection, Operating, Test 각 하중)
- 관련 주석/Note 사항
**출력 형식:**
- 항목별 Table
- 도면 내 위치 표시 가능 시, 위치 좌표 또는 Grid 기준 포함
2️. 변경 도면 비교 분석
초도 도면 대비 2차 도면에서 변경된 부분을 비교해 주세요.
**중점 비교 항목:**
- 외형 치수 변경 여부
- Base Elevation의 변동 여부
- Anchor Bolt 개수/간격/사이즈 변경 여부
- Fixed/Sliding Side 위치 변경 여부
- Weight 값 변경 여부
- 기타 주석 및 Detail 상의 추가/삭제/수정사항
**출력 형식:**
- 변경 사항 비교 Table (Before / After / 변경내용)
"""