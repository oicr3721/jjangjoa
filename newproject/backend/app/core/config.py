from dotenv import load_dotenv
import os

load_dotenv()

KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")
KAKAO_JS_KEY= os.getenv("KAKAO_JS_KEY")
GROQ_API_KEY= os.getenv("GROQ_API_KEY")