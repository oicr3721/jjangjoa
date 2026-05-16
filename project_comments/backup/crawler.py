# crawler.py
import requests
from bs4 import BeautifulSoup
# import pandas as pd
import sqlite3
def crawl_comments(game_id):
    # Chapter 1: 공지 링크들 따기 start
    # 스팀 이벤트&공지에 대한 페이지
    # game_id는 스팀 페이지의 고유 게임 id. 예시로 스팀 공지 링크 보면 https://steamcommunity.com/app/367520/eventcomments/ 이렇게 되어있는데 3번째꺼. 다른 게임 가져올거면 game_id만 바꾸면 됨
    url_official = "https://steamcommunity.com/app/"+str(game_id)+"/eventcomments/?fp="
    fp = 1 # fp = 이벤트&공지 페이지 수. 나중에 공지 긁는 기간을 늘리려면 ctp 조정했던 것 처럼 fp 조정으로 가능. fp 변수를 url_official에 붙이려 해봤는데 나중에 url 바뀔 때마다 url을 재정의해야해서 오히려 귀찮아짐. 나중에 게임 여러개 크롤링할 때는 game_id 도 fp처럼 따로 빼야할 듯

    res_official = requests.get(url_official+str(fp)) # url을 불러옴, fp 는 몇번째 페이지인지를 나타내기에 나중에 여러 페이지를 불러온다면? 을 생각해서 일단 만들어 놓음
    soup_official = BeautifulSoup(res_official.text, "html.parser")

    # 공지 페이지 수 계산
    official_count = soup_official.find("div", class_="forum_paging_summary ellipsis")
    official_max = official_count.text.strip()
    official_page = int(official_max.split()[3])//15 + 1 # comment_max.split()[3] = 21 은 문자열

    news_steam = soup_official.select_one(".forum_topics").select("a") # div 클래스 forum_topics 를 불러오고 그 안의 a 태그를 가져옴

    official_links = []

    # 공지사항 제목과 링크 가져오기
    for a in news_steam:
        link = a.get("href") # a 태그 안의 href 링크를 가져옴
        if link: # 링크가 존재한다면
            official_links.append(link) # 링크를 리스트에 추가

    # Chapter 1: 공지 링크들 따기 end
    # Chapter 2: 공지 제목과 내용 따기 start

    data = []

    for links in official_links: # official_links 리스트 안의 링크들 하나씩 불러와서 링크들을 전부 호출하면 반복문 종료
        # 스팀 이벤트에 대한 댓글 페이지. 공지 링크가 바뀔 때마다 재정의
        url_unit = links + "?ctp="
        ctp = 1 # ctp = 댓글 페이지 수

        res_unit = requests.get(url_unit+str(ctp)) # 얘는 댓글 추출용으로 공지 내용이 간소화된 페이지
        soup_unit = BeautifulSoup(res_unit.text, "html.parser")

        detail_link = soup_unit.find("a",class_="bb_link").get("href") # 상세 페이지 진입을 위한 href 링크가 들어있는 a 태그를 불러오고 href 링크를 가져오고 저장
        res_detail = requests.get(detail_link) # 얘는 공지 내용 추출용으로 상세 공지 내용이 적힌 페이지
        soup_detail = BeautifulSoup(res_detail.text, "html.parser")

        title_raw = soup_detail.find("title").text # 결과 ex) Steam :: Hollow Knight :: Patch Version 1.5.12620 Now Live
        title_parts = title_raw.split("::") # :: 기준으로 쪼개면 3개의 요소가 있는 리스트가 만들어짐
        if len(title_parts) >= 3:
            title_detail = title_parts[2].strip() # 리스트의 두번째 인덱스인 제목을 값으로 저장
        else:
            title_detail = title_detail.strip()

        meta_desc = soup_detail.find("meta", {"name": "Description"})
        if meta_desc:
            content_detail = meta_desc.get("content")
        else:
            content_detail = ""  # 없으면 빈 문자열이나 기본값 # 공지 내용은 메타 태그로 저장되어 있음. 페이지 소스 보기로 확인 가능

    # Chapter 2: 공지 제목과 내용 따기 end
    # Chapter 3: 댓글 따기 start

        # 댓글 페이지 수 계산
        comment_count = soup_unit.find("div", class_="forum_paging_summary ellipsis")
        comment_max = comment_count.text.strip()
        comment_page = int(comment_max.split()[3])//15 + 1 # comment_max.split()[3] = 207은 문자열
        # 스팀 공지 페이지랑 댓글 페이지 보면 공지는 Showing 1-15 of 21 active topics, 댓글은 Showing 1-15 of 214 comments 이런 식으로 공지 수랑 댓글 수가 몇 개인지 보이는데 둘 다 띄어쓰기 기준으로 쪼개면 3번째 인덱스가 최대 갯수임.
        # 한 페이지당 최대 댓글 수가 15개인 걸 이용하여 214/15 이런 식으로 몫을 계산하여 댓글(몫) 페이지 수를 계산, 댓글이 15개보다 적을 경우를 대비해 1을 더해줌-> ctp는 0이 아니라 1부터 시작하기에

        data1 = []
        data2 = []
        data3 = []
        comments = []
        # 댓글 페이지 수 만큼 반복하여 리스트에 댓글 정보를 저장하는 반복문
        for i in range(comment_page):

            comment_comment = soup_unit.find_all("div", class_="commentthread_comment_text")
            comment_name = soup_unit.find_all("bdi")
            comment_date = soup_unit.find_all("div", class_="commentthread_comment_timestamp")

            # 댓글 내용 리스트와 이름 리스트에 각각 저장
            for n in comment_comment:
                    data1.append(n.text.strip())
            for m in comment_name:
                    data2.append(m.text)
            for o in comment_date:
                    data3.append(o.text.strip())

            # 변동되는 ctp에 따라 다시 크롤링 하는 페이지 재정의
            ctp += 1
            res_unit = requests.get(url_unit+str(ctp))
            soup_unit = BeautifulSoup(res_unit.text, "html.parser")
        
        date_detail = data3.pop(0) # 댓글들 날짜 크롤링할 때 첫번째 인덱스는 공지 날짜임, 태그가 같아서 같이 저장되는데 빼서 따로 저장
        
        comment_bundle = list(zip(data1,data2,data3)) # db에 넣기 위해 묶음으로 저장

        comments.append(comment_bundle) # [[(내용1,이름1,날짜1),(내용2,이름2,날짜2)]]
        comments = comments[0] # 리스트 기호가 중첩되는 것 해제 [(내용1,이름1,날짜1),(내용2,이름2,날짜2)]
        
        data_unit = {
            "title": title_detail,
            "content": content_detail,
            "comment": comments
        }
        data.append(data_unit)

    # df = pd.DataFrame(data) # csv 용 데이터프레임화
    #Chapter3 댓글 따기 end
    #Chapter4 db 저장 start
        # 공지와 댓글 db에 저장
        conn = sqlite3.connect("steam_comments_"+str(game_id)+".db")
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS notices (
            notice_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            notice_id INTEGER,
            comment TEXT,
            author TEXT,
            date TEXT,
            FOREIGN KEY (notice_id) REFERENCES notices(notice_id)
        )
        """)

        # 공지 하나 저장
        cur.execute("INSERT INTO notices (title, content) VALUES (?, ?)", (title_detail, content_detail))
        notice_id = cur.lastrowid

        # comments 리스트를 기반으로 DB 저장
        for comment, name, date in comments:
            cur.execute(
                "INSERT INTO comments (notice_id, comment, author, date) VALUES (?, ?, ?, ?)",
                (notice_id, comment, name, date)
            )

        conn.commit()
        conn.close()

if __name__ == "__main__":
    crawl_comments()