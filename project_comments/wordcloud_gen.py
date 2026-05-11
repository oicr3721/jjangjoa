# wordcloud_gen.py
import pandas as pd
import sqlite3
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def generate_wordclouds(db_file="steam_comments.db"):
    conn = sqlite3.connect(db_file)
    df = pd.read_sql("SELECT * FROM comments_sentiment", conn)
    conn.close()

    # 감성별 텍스트 합치기
    positive_text = " ".join(df[df["sentiment"]=="positive"]["comment"].astype(str))
    negative_text = " ".join(df[df["sentiment"]=="negative"]["comment"].astype(str))
    neutral_text  = " ".join(df[df["sentiment"]=="neutral"]["comment"].astype(str))

    plt.figure(figsize=(18,6))

    # 긍정
    if positive_text.strip():
        wc_positive = WordCloud(font_path="malgun.ttf", background_color="white").generate(positive_text)
        plt.subplot(1,3,1)
        plt.imshow(wc_positive, interpolation="bilinear")
        plt.axis("off")
        plt.title("긍정 댓글 워드클라우드")
    else:
        print("⚠️ 긍정 댓글 없음 → 워드클라우드 건너뜀")

    # 부정
    if negative_text.strip():
        wc_negative = WordCloud(font_path="malgun.ttf", background_color="white").generate(negative_text)
        plt.subplot(1,3,2)
        plt.imshow(wc_negative, interpolation="bilinear")
        plt.axis("off")
        plt.title("부정 댓글 워드클라우드")
    else:
        print("⚠️ 부정 댓글 없음 → 워드클라우드 건너뜀")

    # 중립
    if neutral_text.strip():
        wc_neutral = WordCloud(font_path="malgun.ttf", background_color="white").generate(neutral_text)
        plt.subplot(1,3,3)
        plt.imshow(wc_neutral, interpolation="bilinear")
        plt.axis("off")
        plt.title("중립 댓글 워드클라우드")
    else:
        print("⚠️ 중립 댓글 없음 → 워드클라우드 건너뜀")

    plt.show()


if __name__ == "__main__":
    generate_wordclouds()
