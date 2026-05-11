# sentiment_analysis.py
import pandas as pd
import sqlite3
import torch
from transformers import BertTokenizer, BertForSequenceClassification

tokenizer = BertTokenizer.from_pretrained("monologg/kobert")
model = BertForSequenceClassification.from_pretrained("monologg/kobert", num_labels=3)

def predict_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    outputs = model(**inputs)
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    label = torch.argmax(probs).item()
    return ["negative", "neutral", "positive"][label]

def analyze_sentiments(db_file="steam_comments.db"):
    conn = sqlite3.connect(db_file)
    df = pd.read_sql("SELECT * FROM comments", conn)
    conn.close()

    # 감성 분석
    df["sentiment"] = df["comment"].apply(lambda x: predict_sentiment(str(x)))

    # 비율 출력
    sentiment_counts = df["sentiment"].value_counts(normalize=True) * 100
    print("댓글 감성 비율:")
    print(sentiment_counts)

    # 결과 저장
    conn = sqlite3.connect(db_file)
    df.to_sql("comments_sentiment", conn, if_exists="replace", index=False)
    conn.close()

    print("✅ DB 저장 완료: comments_sentiment 테이블")
    return df

if __name__ == "__main__":
    analyze_sentiments()
