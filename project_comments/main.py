import sqlite3
import sys
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
    # ✅ 명령줄 인자로 game_id 받기
    if len(sys.argv) < 2:
        print("사용법: python main.py <game_id>")
        sys.exit(1)

    game_id = sys.argv[1]
    db_file = f"steam_comments_{game_id}.db"

    # Step 1: DB에 comments 테이블 확인
    if not check_table_exists(db_file, "comments"):
        print(f"DB에 comments 테이블 없음 → 크롤링 실행 (game_id={game_id})")
        crawl_comments(game_id)  # crawler.py 내부에서 game_id를 동일하게 맞춰야 함
        print(f"크롤링 완료, {db_file} 저장됨")
    else:
        print(f"DB에 comments 테이블 존재 → 크롤링 건너뜀 (game_id={game_id})")

    # Step 2: 감성 분석
    print("\n=== Step 2: 감성 분석 시작 ===")
    analyze_sentiments(game_id)
    print("감성 분석 완료")

    # Step 3: 워드 클라우드 생성
    print("\n=== Step 3: 워드 클라우드 생성 ===")
    generate_wordclouds(game_id)
    print("워드 클라우드 시각화 완료")

if __name__ == "__main__":
    main()
