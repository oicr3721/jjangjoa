from urllib.parse import urlparse, parse_qs
from typing import Dict
import math
import re
import unicodedata

from googleapiclient.discovery import build
import pandas as pd


YOUTUBE_API_KEY = "API키_여기에_넣어주세요"


yt = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)


def main():
    print()
    print('================')
    video_url = input("유튜브 영상 url을 입력해주세요: ")

    assert video_url, f'영상 주소를 입력해주셔야 합니다.'

    video_id = extract_video_id(video_url)
    video_title = get_video_title(video_id)

    print()
    print('================')
    print(f'"{video_title}" 영상에서 가져올 댓글 수를 입력해주세요.')
    print(f'(기본값: 10,000개, 100개 단위): ', end='')
    video_comment_count = int(input() or 10000)
    video_comments = list(get_video_comments(video_id, video_comment_count))

    print()
    csv_path = f"({len(video_comments),}개 댓글) {safe_filename(video_title)} ({video_id}).csv"
    df = pd.DataFrame(video_comments)
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print("수집 완료!")


def get_video_title(video_id: str) -> str:
    res = yt.videos().list(
        part="snippet",
        id=video_id
    ).execute()

    items = res.get("items", [])
    if not items:
        return '<Untitled>'

    return items[0]["snippet"]["title"]


def get_video_comments(video_id: str, max_results: int = 10000):
    assert video_id, f"video ID: {video_id}는 올바르지 않습니다."
    step = 100
    max_results = math.ceil(max_results/step)*step
    print(f'{max_results}개의 댓글을 수집할 예정입니다.')

    next_page_token = None
    for results in range(0, max_results, step):
        print(f'up to {results,}개 수집중...')

        try:
            res = yt.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=max_results,
                pageToken=next_page_token
            ).execute()

        except Exception as e:
            print("더 이상 댓글을 가져올 수 없습니다.")
            print("API KEY 쿼터(잔여 사용량)를 확인해보세요.")
            print()
            print(e)
            break

        yield from map(flatten_comment_thread, res['items'])

        next_page_token = res.get("nextPageToken")

        if not next_page_token:
            print("더 이상 가져올 댓글이 없습니다.")
            break


def flatten_comment_thread(item: Dict) -> Dict[str, str]:
    tlc = item["snippet"]["topLevelComment"]["snippet"]
    return {
        # thread level
        "thread_id": item["id"],
        "video_id": item["snippet"]["videoId"],
        "channel_id": item["snippet"]["channelId"],
        "can_reply": item["snippet"]["canReply"],
        "total_reply_count": item["snippet"]["totalReplyCount"],
        "is_public": item["snippet"]["isPublic"],

        # comment level
        "comment_id": item["snippet"]["topLevelComment"]["id"],
        "comment_text": tlc["textOriginal"],
        "author_display_name": tlc["authorDisplayName"],
        "author_channel_url": tlc.get("authorChannelUrl"),
        "author_channel_id": tlc["authorChannelId"]["value"],
        "like_count": tlc["likeCount"],
        "published_at": tlc["publishedAt"],
        "updated_at": tlc["updatedAt"]
    }


def safe_filename(title: str, max_length: int = 100, fallback: str = "untitled") -> str:
    title = unicodedata.normalize("NFC", title)
    title = re.sub(r"[\r\n\t]", " ", title)
    title = re.sub(r'[\\/:*?"<>|]', "", title)
    title = re.sub(r"\s+", " ", title).strip()
    title = title[:max_length].rstrip()
    return title if title else fallback


def extract_video_id(url: str) -> str:
    """유튜브 url에서 영상 ID 만 추출"""
    parsed = urlparse(url)

    # 1. watch?v=...
    if parsed.query:
        qs = parse_qs(parsed.query)
        if "v" in qs:
            return qs["v"][0]

    # 2. /shorts/VIDEO_ID
    if parsed.path.startswith("/shorts/"):
        return parsed.path.split("/shorts/")[1].split("/")[0]

    # 3. youtu.be/VIDEO_ID
    if parsed.netloc == "youtu.be":
        return parsed.path.lstrip("/")

    raise ValueError("비디오 ID를 찾을 수 없습니다.")


main()
