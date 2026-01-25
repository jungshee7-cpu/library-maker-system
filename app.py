import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="구리시 도서관 메이커스페이스 실적 관리", layout="wide")

st.title("📘 메이커스페이스 실적 관리 시스템")
st.markdown("---")

# 2. 구글 시트 연결
conn = st.connection("gsheets", type=GSheetsConnection)

# 데이터 불러오기
try:
    # 주소에서 직접 읽어오되 시트 이름을 명시적으로 지정
    df = conn.read(worksheet="maker_data_sheets", ttl=0)
    if df.empty:
        df = pd.DataFrame(columns=['년도', '구분(탭)', '하위분류', '대상', '강좌/행사명', '월', '금회합계', '누적인원'])
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    df = pd.DataFrame(columns=['년도', '구분(탭)', '하위분류', '대상', '강좌/행사명', '월', '금회합계', '누적인원'])

# 3. 사이드바: 실적 입력 창 (세부 분류 항목 강화)
st.sidebar.header("➕ 새로운 실적 입력")
with st.sidebar.form("input_form"):
    year = st.selectbox("년도", ["2026", "2025"])
    category = st.selectbox("구분(탭)", ["자체", "협력", "장비운영"])
    
    # 세부 분류를 선택형으로 변경하여 명확하게 표출
    sub_category = st.selectbox("세부 분류(하위분류)", ["장비활용", "메이커교육", "창작활동", "체험행사", "기타"])
    
    target = st.selectbox("대상", ["어린이", "청소년", "성인", "가족", "장애인", "기타"])
    program_name = st.text_input("강좌/행사명 (필수)")
    month = st.selectbox("월", [f"{i}월" for i in range(1, 13)])
    count = st.number_input("금회합계 (명)", min_value=0, step=1)
    
    submit_button = st.form_submit_button(label="🚀 실적 저장")

# 4. 데이터 저장 로직
if submit_button:
    if program_name:
        new_data = pd.DataFrame([{
            "년도": year,
            "구분(탭)": category,
            "하위분류": sub_category,
            "대상": target,
            "강좌/행사명": program_name,
            "월": month,
            "금회합계": count,
            "누적인원": count 
        }])
        
        updated_df = pd.concat([df, new_data], ignore_index=True)
        conn.update(worksheet="maker_data_sheets", data=updated_df)
        
        st.sidebar.success("✅ 실적이 성공적으로 저장되었습니다!")
        st.rerun()
    else:
        st.sidebar.error("⚠️ 강좌명은 필수 입력 사항입니다.")

# 5. 메인 화면: 실적 현황 및 세부 분류별 보기
if not df.empty:
    # 상단 요약 지표
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("총 프로그램 수", len(df))
    with col2:
        st.metric("총 참여 인원", int(df["금회합계"].sum()))
    with col3:
        # 가장 활발한 세부 분류 표시
        top_sub = df['하위분류'].value_counts().idxmax() if '하위분류' in df.columns else "-"
        st.metric("주요 세부 분류", top_sub)

    st.markdown("---")
    st.subheader("📊 실적 상세 내역")
    st.dataframe(df, use_container_width=True)
else:
    st.info("현재 등록된 실적이 없습니다. 왼쪽 사이드바에서 데이터를 입력해 주세요.")
