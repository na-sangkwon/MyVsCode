# fileName: ai_utils.py
import os
import urllib.request
import json
import time # 👈 [신설] 429 제한 시간 버퍼용 내장 라이브러리 추가
from dotenv import load_dotenv

# [2026-09-02 수정] API 키가 코드에 그대로 박혀 있어 공개 GitHub 저장소에 노출돼있었다 —
# 이 파일과 같은 폴더의 .env(git 미추적)에서 읽어오도록 바꿨다. .env 파일이 없거나 값이
# 비어있으면 CONFIG_API_KEY는 빈 문자열이 되고, ask_openrouter()가 이를 감지해 안내 메시지를
# 찍고 None을 반환한다(기존 방어 로직 그대로 유지).
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

# ⚙️ 중앙 집중 관리용 공용 설정값
CONFIG_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
CONFIG_MODEL = "openai/gpt-oss-120b:free"
# openai/gpt-oss-120b:free 
# google/gemma-4-26b-a4b-it:free
# z-ai/glm-4.5-air:free

def ask_openrouter(system_prompt, user_prompt, api_key=CONFIG_API_KEY, model=CONFIG_MODEL, temperature=0.5, max_tokens=100):
    if not api_key or api_key.strip() == "":
        print("⚠️  [AI 공용 모듈] API 키가 설정되지 않았습니다.")
        return None

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Realty Shared Module"
    }
    print(f"사용된 AI모델:{model}")
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    for attempt in range(1, 4):
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=5.0) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                content = res_data["choices"][0]["message"]["content"].strip()
                return content.replace('"', '').replace("'", "").strip()
                
        except urllib.error.HTTPError as http_err:
            if http_err.code == 429 and attempt < 3:
                print(f"⏳ [AI 동시성 429 에러 감지] 1.5초 후 자동으로 우회 재시도합니다... ({attempt}/3)")
                time.sleep(1.5)
                continue
            print(f"⚠️ [AI 공용 모듈 오류] API 통신 최종 실패: {http_err}")
            return None
        except Exception as e:
            print(f"⚠️ [AI 공용 모듈 오류] API 통신 예외 발생: {e}")
            return None
    return None
# def ask_openrouter(system_prompt, user_prompt, api_key=CONFIG_API_KEY, model=CONFIG_MODEL, temperature=0.5, max_tokens=2000):
#     """
#     OpenRouter API를 호출하여 결과 문자열만 깔끔하게 반환하는 공용 함수.
#     api_key, model 등이 생략되면 상단에 정의된 공용 설정값을 자동으로 사용합니다.
#     """
#     if not api_key or api_key.strip() == "":
#         print("⚠️  [AI 공용 모듈] API 키가 설정되지 않았습니다.")
#         return None

#     url = "https://openrouter.ai/api/v1/chat/completions"
#     headers = {
#         "Authorization": f"Bearer {api_key}",
#         "Content-Type": "application/json",
#         "HTTP-Referer": "http://localhost:8000",
#         "X-Title": "Realty Shared Module"
#     }
#     print(f"사용된 AI모델:{model}")
#     payload = {
#         "model": model,
#         "messages": [
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_prompt}
#         ],
#         "temperature": temperature,
#         "max_tokens": max_tokens
#     }
#     try:
#         req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
#         with urllib.request.urlopen(req, timeout=3.5) as response:
#             res_data = json.loads(response.read().decode("utf-8"))
#             content = res_data["choices"][0]["message"]["content"].strip()
#             return content.replace('"', '').replace("'", "").strip()
#     except Exception as e:
#         print(f"⚠️ [AI 공용 모듈 오류] API 통신 실패: {e}")
#         return None