from sites import SITE_CONFIG
from list_crawler import crawl_list
from content_crawler import crawl_content
from cleaner import html_to_clean_text
from summarizer import summarize_text
from database import init_db, save_notice


def crawl_all():

    init_db()

    for site_name, config in SITE_CONFIG.items():

        print(f"\n===== {site_name} 크롤링 시작 =====")

        notices = crawl_list(site_name, config)

        for notice in notices:

            try:

                print(f"\n[NOTICE] {notice['title']}")

                # 1. 본문 HTML 가져오기
                content_html = crawl_content(notice["url"], config)

                if not content_html:
                    print("  → 본문 HTML 없음, 스킵")
                    continue

                # 2. HTML → 정제된 텍스트
                content = html_to_clean_text(content_html)
                print(f"  → 정제 텍스트 길이: {len(content)}자")

                if not content.strip():
                    print("  → 정제 후 텍스트 없음, 스킵")
                    continue

                print(f"  → 미리보기: {content[:80].replace(chr(10), ' ')}...")

                # 3. Gemini 요약
                summary = summarize_text(content)
                print(f"\n[SUMMARY]\n{summary}")

                # 4. DB 저장
                notice["content"] = content
                notice["summary"] = summary
                save_notice(notice)
                print("  → 저장 완료")

            except Exception as e:
                print(f"  [ERROR] {notice['title']}: {e}")
                continue


if __name__ == "__main__":
    crawl_all()
    print("\n✅ 크롤링 완료")
