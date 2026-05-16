import pandas as pd
import sqlite3
import torch
from transformers import BertTokenizer, BertForSequenceClassification
import os

tokenizer = BertTokenizer.from_pretrained("monologg/kobert")
model = BertForSequenceClassification.from_pretrained("monologg/kobert", num_labels=3)

# pnn 폴더 준비
PNN_DIR = "pnn"
os.makedirs(PNN_DIR, exist_ok=True)

def load_keywords():
    keywords = {"positive": set(), "negative": set(), "neutral": set()}
    for label in keywords.keys():
        file_path = os.path.join(PNN_DIR, f"{label}.txt")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    keywords[label].add(line.strip())
    return keywords

def save_keyword(label, word):
    file_path = os.path.join(PNN_DIR, f"{label}.txt")
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(word + "\n")
    print(f"새로운 키워드 추가: '{word}' → {label}.txt")

def predict_sentiment(text, keywords):
    # 사전 우선 적용
    for label, words in keywords.items():
        for w in words:
            if w in text:
                return label

    # 사전에 없으면 모델로 예측
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    outputs = model(**inputs)
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    label_idx = torch.argmax(probs).item()
    label = ["negative", "neutral", "positive"][label_idx]

    # 새로운 키워드 업데이트 (간단히 단어 단위로 추가)
    for word in text.split():
        if word not in keywords[label]:
            save_keyword(label, word)
            keywords[label].add(word)

    return label

def analyze_sentiments(game_id):
    db_file = f"steam_comments_{game_id}.db"
    conn = sqlite3.connect(db_file)
    df = pd.read_sql("SELECT * FROM comments", conn)
    conn.close()

    keywords = load_keywords()
    df["sentiment"] = df["comment"].apply(lambda x: predict_sentiment(str(x), keywords))

    sentiment_counts = df["sentiment"].value_counts(normalize=True) * 100
    print("댓글 감성 비율:")
    print(sentiment_counts)

    conn = sqlite3.connect(db_file)
    df.to_sql("comments_sentiment", conn, if_exists="replace", index=False)
    conn.close()

    print(f"✅ DB 저장 완료: comments_sentiment 테이블 ({db_file})")
    return df
