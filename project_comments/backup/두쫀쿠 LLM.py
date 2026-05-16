# =============================================================================
# Imports
# =============================================================================
import pandas as pd
import numpy as np
import json
import time
import matplotlib.pyplot as plt
from openai import OpenAI

# 한글 폰트 설정 (Windows 기준)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# =============================================================================
# 1. 설정 (API 키 및 파일 경로)
# =============================================================================
# [주의] 본인의 OpenAI API 키를 여기에 입력하세요
API_KEY = "sk-"  
client = OpenAI(api_key=API_KEY)

# 데이터 로드 (CSV 파일 경로를 맞춰주세요)
file_path = "두쫀쿠공짜.csv"  # 예: "C:/data/두쫀쿠공짜.csv"
df1 = pd.read_csv(file_path)

print(f"데이터 로드 완료: {len(df1)}개 댓글")

# =============================================================================
# 2. 데이터 전처리
# =============================================================================
# 필요한 컬럼만 선택 및 결측치 제거
# (유튜브 데이터 형식에 따라 컬럼명이 다를 수 있으니 확인 필요: textOriginal 또는 display_text)
target_col = 'textOriginal' if 'textOriginal' in df1.columns else 'display_text'
df_main = df1.dropna(subset=[target_col]).copy()
texts = df_main[target_col].tolist()

# 날짜 형식 변환 (updatedAt이 없으면 publishedAt 사용)
if 'updatedAt' not in df_main.columns:
    df_main['updatedAt'] = df_main['publishedAt']

df_main['updatedAt'] = pd.to_datetime(df_main['updatedAt'], errors='coerce')
df_main['date'] = df_main['updatedAt'].dt.date

# =============================================================================
# 3. LLM 분류 함수 (프롬프트 수정됨)
# =============================================================================
def classify_dujjonku_sentiment(comments):
    prompt = f"""
    다음은 '두쫀쿠(두바이 쫀득 쿠키)를 주면 헌혈하겠다'는 이벤트 관련 유튜브 댓글들입니다.
    
    각 댓글을 읽고 **가장 주된 대상(Subject)**과 **감정(Sentiment)**을 분류해주세요.
    단어 매칭이 아니라, **문맥상 누구를 지칭하는지** 파악해야 합니다.

    [핵심 가이드: 비꼬기와 반어법 주의!]
    1. "대단하다", "지극정성이다", "한국인 종특" -> 칭찬이 아니라 **비꼬는(부정)** 표현일 가능성이 높음.
    2. 욕설이 있어도 내용을 봐야 함. 
       - 예: "개소리 마라, 헌혈하는 게 어디냐" -> 욕설은 있지만 헌혈자를 **옹호(긍정)**하는 것임.
    3. "피 빨리러 가네 ㅋㅋ" -> 자조적 유머일 수도 있지만, 문맥상 헌혈 행위를 희화화한다면 **부정**에 가까움.

    [1. Subject 분류 기준]
    - "기획자(공급)": 헌혈의 집, 적십자사, **아이디어 낸 사람**, 마케팅 담당자, 두쫀쿠(쿠키 자체), 이벤트 시스템
      (예: "머리 진짜 좋다", "이거 기획한 사람 승진시켜라", "재고 관리 똑바로 해라")
      
    - "참여자(수요)": 헌혈자, **유행 쫓는 사람**, 오픈런 하는 대중, 한국인들의 종특, 줄 서는 사람들
      (예: "이거 먹으려고 피까지 뽑네", "군중 심리 무섭다", "좋은 일도 하고 쿠키도 먹고 일석이조")
      
    - "기타": 위 두 가지에 해당하지 않거나 구분이 모호한 경우

    [2. Sentiment 분류 기준]
    - "긍정": 칭찬, 인정, 재밌다, 맛있다, 훈훈하다, 응원
    - "부정": 비판, 우려, 비꼬기(매혈, 냄비근성, 그지근성), 맛없다, 혐오
    - "중립": 단순 사실 언급, 질문, 감정 판단 불가

    [댓글 목록]
    {chr(10).join([f"{i+1}. {c[:150]}" for i, c in enumerate(comments)])}

    JSON 형식으로 답해주세요 (키는 번호 문자열):
    {{"1": {{"subject": "헌혈자", "sentiment": "긍정"}}, "2": {{"subject": "헌혈의 집", "sentiment": "부정"}}, ...}}
    """

    try:
        response = client.chat.completions.create(
            model="o4-mini", # 가성비 모델
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=1 # 일관된 분석을 위해 0 설정
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"API 호출 에러: {e}")
        return "{}"

# =============================================================================
# 4. 배치 처리 및 분석 실행
# =============================================================================
batch_size = 20
results_classify = []

print("🚀 LLM 분석 시작...")
start_time = time.time()

for i in range(0, len(texts), batch_size):
    batch = texts[i:i+batch_size]
    result = classify_dujjonku_sentiment(batch)
    results_classify.append(result)
    
    # 진행 상황 출력
    if (i + batch_size) % 100 == 0:
        print(f"  - {min(i+batch_size, len(texts))}/{len(texts)} 완료")

print(f"✅ 분석 종료 (소요시간: {time.time() - start_time:.1f}초)")

# =============================================================================
# 5. 결과 파싱 및 데이터프레임 병합
# =============================================================================
subjects = []
sentiments = []

for i, result in enumerate(results_classify):
    try:
        parsed = json.loads(result)
        batch_len = min(batch_size, len(texts) - i*batch_size)
        
        for j in range(1, batch_len + 1):
            key = str(j)
            if key in parsed and isinstance(parsed[key], dict):
                subjects.append(parsed[key].get('subject', '기타'))
                sentiments.append(parsed[key].get('sentiment', '중립'))
            else:
                subjects.append('기타')
                sentiments.append('중립')
    except json.JSONDecodeError:
        # 에러 시 해당 배치만큼 '기타/중립' 채움
        batch_len = min(batch_size, len(texts) - i*batch_size)
        subjects.extend(['기타'] * batch_len)
        sentiments.extend(['중립'] * batch_len)

df_main['subject'] = subjects
df_main['sentiment'] = sentiments

# 결과 저장
df_main.to_csv("두쫀쿠_분석결과_o4-mini.csv", index=False, encoding='utf-8-sig')
print("\n=== 대상별 분포 ===")
print(df_main['subject'].value_counts())

# =============================================================================
# 6. 시각화: '헌혈의 집' vs '헌혈자' 긍부정 비교
# =============================================================================
fig, axes = plt.subplots(2, 1, figsize=(12, 10))

# [그래프 1] 대상별 감정 비율 (100% Stacked Bar)
cross_tab = pd.crosstab(df_main['subject'], df_main['sentiment'], normalize='index') * 100
# 컬럼 순서 고정
cols = [c for c in ['긍정', '부정', '중립'] if c in cross_tab.columns]
cross_tab = cross_tab[cols]
colors = {'긍정': '#4CAF50', '부정': '#F44336', '중립': '#9E9E9E'}

cross_tab.plot(kind='barh', stacked=True, color=[colors[c] for c in cols], ax=axes[0], alpha=0.8)
axes[0].set_title('대상별 감정 반응 비율 (헌혈의 집 vs 헌혈자)', fontsize=14, fontweight='bold')
axes[0].set_xlabel('비율 (%)')
axes[0].set_ylabel('대상')

plt.tight_layout()
plt.show()
# =============================================================================
# 7. 핵심 댓글 추출 (인사이트 용)
# =============================================================================
print("\n🔥 [헌혈의 집] 관련 가장 핫한 긍정 댓글 (Best Positive):")
top_neg_center = df_main[(df_main['subject']=='헌혈의 집') & (df_main['sentiment']=='긍정')].nlargest(3, 'likeCount')
for i, row in top_neg_center.iterrows():
    print(f"- ({row['likeCount']}❤) {row[target_col][:80]}...")

print("\n🔥 [헌혈의 집] 관련 가장 핫한 부정 댓글 (Best Negative):")
top_neg_center = df_main[(df_main['subject']=='헌혈의 집') & (df_main['sentiment']=='부정')].nlargest(3, 'likeCount')
for i, row in top_neg_center.iterrows():
    print(f"- ({row['likeCount']}❤) {row[target_col][:80]}...")

print("\n✨ [헌혈자] 관련 가장 핫한 긍정 댓글 (Best Positive):")
top_pos_donor = df_main[(df_main['subject']=='헌혈자') & (df_main['sentiment']=='긍정')].nlargest(3, 'likeCount')
for i, row in top_pos_donor.iterrows():
    print(f"- ({row['likeCount']}❤) {row[target_col][:80]}...")

print("\n✨ [헌혈자] 관련 가장 핫한 부정 댓글 (Best Negative):")
top_pos_donor = df_main[(df_main['subject']=='헌혈자') & (df_main['sentiment']=='부정')].nlargest(3, 'likeCount')
for i, row in top_pos_donor.iterrows():
    print(f"- ({row['likeCount']}❤) {row[target_col][:80]}...")