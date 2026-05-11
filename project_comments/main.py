import sqlite3
from crawler import crawl_comments
from sentiment_analysis import analyze_sentiments
from wordcloud_gen import generate_wordclouds

def check_table_exists(db_file, table_name):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
        (table_name,)
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None

def main():
    db_file = "steam_comments.db"

    # Step 1: DB에 comments 테이블이 있는지 확인
    if not check_table_exists(db_file, "comments"):
        print("DB에 comments 테이블이 없음 → 크롤링 실행")
        crawl_comments()
        print("크롤링 완료, steam_comments.db 저장됨")
    else:
        print("DB에 comments 테이블 존재 → 크롤링 건너뜀")

    # Step 2: 감성 분석
    print("\n=== Step 2: 감성 분석 시작 ===")
    analyze_sentiments()
    print("감성 분석 완료, DB에 comments_sentiment 테이블 저장됨")

    # Step 3: 워드 클라우드 생성
    print("\n=== Step 3: 워드 클라우드 생성 ===")
    generate_wordclouds()
    print("긍정/부정/중립 워드 클라우드 시각화 완료")

if __name__ == "__main__":
    main()
