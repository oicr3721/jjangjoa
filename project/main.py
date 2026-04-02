from sites import SITE_CONFIG
from list_crawler import crawl_list
from database import init_db, save_notice


def crawl_all():

    init_db()

    for site_name, config in SITE_CONFIG.items():

        notices = crawl_list(site_name, config)

        for notice in notices:

            save_notice(notice)


if __name__ == "__main__":

    crawl_all()

    print("크롤링 완료")