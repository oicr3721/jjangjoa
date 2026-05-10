import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "notices.db"

conn = sqlite3.connect(DB_PATH)


st.set_page_config(
    page_title="게임 공지 대시보드",
    layout="wide"
)


query = """
SELECT *
FROM notices
ORDER BY id DESC
"""


df = pd.read_sql_query(query, conn)


st.title("게임 공지 요약 대시보드")


if df.empty:
    st.warning("공지 데이터가 없습니다.")
    st.stop()


games = df["game"].unique()

selected_game = st.selectbox(
    "게임 선택",
    ["전체"] + list(games)
)


keyword = st.text_input("공지 검색")


filtered = df


if selected_game != "전체":
    filtered = filtered[
        filtered["game"] == selected_game
    ]


if keyword:
    filtered = filtered[
        filtered["title"].str.contains(
            keyword,
            case=False,
            na=False
        )
    ]


st.write(f"총 {len(filtered)}개의 공지")


for _, row in filtered.iterrows():

    with st.container(border=True):

        st.subheader(row["title"])

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"게임: {row['game']}")

        with col2:
            st.write(f"날짜: {row['date']}")

        st.markdown("### AI 요약")

        st.write(row.get("summary", "요약 없음"))

        st.link_button(
            "공지 바로가기",
            row["url"]
        )