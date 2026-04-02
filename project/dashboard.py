import streamlit as st
import pandas as pd
import sqlite3


conn = sqlite3.connect("notices.db")


df = pd.read_sql_query("""

SELECT *
FROM notices

""", conn)


st.title("게임 공지 모음")


# 게임 선택

games = df["game"].unique()

selected_game = st.selectbox(

    "게임 선택",

    ["전체"] + list(games)

)


# 검색

keyword = st.text_input("공지 검색")


filtered = df


if selected_game != "전체":

    filtered = filtered[filtered["game"] == selected_game]


if keyword:

    filtered = filtered[
        filtered["title"].str.contains(keyword, case=False)
    ]


st.write(f"{len(filtered)}개의 공지")


for _, row in filtered.iterrows():

    st.markdown(f"""

### {row['title']}

게임: {row['game']}  
날짜: {row['date']}  

[공지 바로가기]({row['url']})

---

""")