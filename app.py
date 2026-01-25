import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="도서관 메이커스페이스 통합 관리 시스템", layout="wide")

# 구글 스프레드시트 연결
conn = st.connection("gsheets", type=GSheetsConnection)
#df = conn.read(worksheet="maker_data_sheets", ttl=0)
df = conn.read(ttl=0)

# 누적인원 재계산 함수
def recalculate_cumulative(dataframe):
    if dataframe.empty: return dataframe
    dataframe = dataframe.reset_index(drop=True)
    dataframe['누적인원'] = dataframe['금회합계'].cumsum()
    return dataframe

st.title("🏛️ 메이커스페이스 연도별 실적 관리 시스템")

# --- [사이드바: 입력창에 년도 추가] ---
with st.sidebar:
    st.header("📝 실적 등록")
    
    with st.expander("➕ 데이터 입력", expanded=True):
        # [추가] 년도 선택 (현재 연도 기준 전후 선택 가능)
        current_year = datetime.now().year
        selected_year = st.selectbox("운영 년도 *", [current_year - 1, current_year, current_year + 1], index=1)
        
        main_cat = st.selectbox("구분 *", ["선택하세요", "외부", "자체", "기관", "공모", "기타"])
        
        # (중략: 하위분류 및 학교명 입력 로직...)
        sub_cat = st.text_input("세부 분류 *")
        program_name = st.text_input("강좌/행사명 *")
        month = st.slider("운영 월", 1, 12, 1)
        
        # [데이터 저장 로직 수정]
        if st.button("🚀 실적 저장"):
            if main_cat != "선택하세요" and program_name:
                # 인원 합산 등 기존 로직 수행...
                new_row = pd.DataFrame([{
                    '년도': f"{selected_year}년", # 연도 필드 추가
                    '구분(탭)': main_cat, '하위분류': sub_cat,
                    '대상': "청소년", '강좌/행사명': program_name, '월': f"{month}월",
                    '금회합계': 10, '누적인원': 0 
                }])
                df = pd.concat([df, new_row], ignore_index=True)
                df = recalculate_cumulative(df)
                conn.update(worksheet="Sheet1", data=df)
                st.success(f"{selected_year}년 실적이 저장되었습니다.")
                st.rerun()

# --- [메인 화면: 연도 포함 다중 필터] ---
st.subheader("🔍 연도별 다중 분석 필터")

if not df.empty:
    # 연도 필터 추가를 위해 5개 컬럼으로 확장
    f0, f1, f2, f3, f4 = st.columns(5)
    
    with f0:
        # [추가] 년도 다중 선택 필터
        options_year = sorted(df['년도'].unique())
        c1, c2 = st.columns(2)
        if c1.button("전체 선택", key="y_all"): st.session_state.s_year = options_year
        if c2.button("전체 해제", key="y_none"): st.session_state.s_year = []
        sel_year = st.multiselect("📅 년도", options=options_year, key="s_year", default=options_year)

    # (중략: 기존 월, 구분, 대상, 강좌명 필터 로직...)
    # ... 필터링 코드에 sel_year 조건 추가 ...
    filtered_df = df[df['년도'].isin(sel_year)] # 연도 필터 적용


    st.dataframe(filtered_df, use_container_width=True)

