# repos_python/OBJECT_reg/test_iros_manual.py
# (2026-09-08 신규 — 사용자 요청) iros_document_issue.py를 exe 빌드·배포·크롬 없이 바로 실행해서
# print() 디버깅 메시지를 터미널에서 즉시 볼 수 있게 하는 재사용 가능한 수동 테스트 스크립트.
# VSCode에서 이 파일을 열고, 아래 설정값만 바꿔서 F5(또는 터미널에서 직접 실행)하면 된다.
#
# [필수] VSCode 파이썬 인터프리터를 아래 경로로 지정해야 selenium을 찾는다(시스템 파이썬엔 없음):
#   D:\241103_nsk98\Documents\repos_python\OBJECT_reg\myenv\Scripts\python.exe

import sys
import json
import urllib.request
import urllib.parse

sys.path.insert(0, r'D:\241103_nsk98\Documents\repos_python\OBJECT_reg')
sys.path.insert(0, r'D:\241103_nsk98\Documents\repos_python')

import iros_document_issue

# ── 여기만 바꿔서 테스트하세요 ──────────────────────────────────────────────
OBJECT_CODE_NEW = '994214'          # 테스트할 새홈매물번호
SERVER = 'https://obangtest.cafe24.com'  # 데이터를 가져올 서버(테섭/본섭)

# document_issue_request.php는 관리자 로그인 세션이 있어야 응답한다 — 브라우저에서 SERVER에
# 로그인한 상태로 개발자도구(F12) → Application/네트워크 탭 → 쿠키에서 PHPSESSID 값을 복사해 넣는다.
# 형식: 'PHPSESSID=여기에_값'
SESSION_COOKIE = ''  # 실제 값은 git에 올리지 않는다 — 로컬에서만 채워 쓸 것(세션 쿠키는 로그인 자격과 같다)

LOOKUP_ONLY = True        # True면 조회만(결제 안 함) — 안전하게 검색 단계만 확인할 때
HEADLESS = False          # False면 크롬 창이 실제로 보임(디버깅 중엔 보는 게 낫다)
AUTO_CONFIRM = False      # LOOKUP_ONLY=False일 때만 의미 있음 — False면 결제 버튼을 직접 눌러야 진행
CLOSE_WHEN_DONE = False   # 끝나고 창을 닫을지
STOP_BEFORE_VIEW = True   # LOOKUP_ONLY=False일 때, 결제까지만 하고 열람 전에 멈출지(안전장치)
# ─────────────────────────────────────────────────────────────────────────


def fetch_payload(server, object_code_new):
    """document_issue_request.php의 payload 계산 로직을 그대로 재사용 — 주소·동/호수 등을 손으로
    다시 입력하지 않기 위함(예전에 수동으로 입력하다 오타로 헤맨 적이 있어서, 실서비스가 실제로
    계산하는 값을 그대로 가져온다). 이 엔드포인트는 관리자 로그인 세션이 있어야 응답하므로,
    브라우저에서 로그인된 세션의 쿠키(SESSION_COOKIE)를 그대로 실어 보낸다."""
    data = urllib.parse.urlencode({
        'mode': 'payload',
        'document_type': 'real_estate_register',
        'object_code_new': object_code_new,
        'give_code': '',
    }).encode('utf-8')
    # SESSION_COOKIE에 'PHPSESSID=' 없이 값만 붙여넣는 경우가 흔해서(쿠키창엔 값만 표시되므로),
    # '='가 없으면 이름을 자동으로 붙여준다.
    cookie_header = SESSION_COOKIE if '=' in SESSION_COOKIE else f'PHPSESSID={SESSION_COOKIE}'
    req = urllib.request.Request(f'{server}/web/_shared/document_issue_request.php', data=data,
                                  headers={'Cookie': cookie_header})
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode('utf-8'))
    if not res.get('ok'):
        raise RuntimeError(f'payload 조회 실패: {res}')
    return res['payload']


# core/config.php의 $CFG['local_helper']['service_token'], local_helper/main.py의
# IROS_SERVICE_TOKEN과 반드시 같은 값이어야 한다 — 하나를 바꾸면 셋 다 같이 바꿀 것.
IROS_SERVICE_TOKEN = '51b5f2f355a2e3958e6d5e9a744ab00b53cd181c3a9864ac'


def fetch_credentials(server):
    """등기소 로그인/선불전자지급수단 정보 — LOOKUP_ONLY=False일 때만 필요하다."""
    data = urllib.parse.urlencode({'fn': 'getirosservicecredentials', 'service_token': IROS_SERVICE_TOKEN}).encode('utf-8')
    req = urllib.request.Request(f'{server}/api/get_api_lib.php', data=data)
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode('utf-8'))
    if not res.get('ok'):
        raise RuntimeError(f'계정정보 조회 실패: {res}')
    return res['data']


if __name__ == '__main__':
    print(f'=== {OBJECT_CODE_NEW} payload 조회 중 ({SERVER}) ===')
    payload = fetch_payload(SERVER, OBJECT_CODE_NEW)
    print('payload:', json.dumps(payload, ensure_ascii=False, indent=2))

    options = {
        'headless': HEADLESS,
        'auto_confirm': AUTO_CONFIRM,
        'close_when_done': CLOSE_WHEN_DONE,
        'lookup_only': LOOKUP_ONLY,
        'stop_before_view': STOP_BEFORE_VIEW,
    }

    if LOOKUP_ONLY:
        credentials = {}
    else:
        print('=== 등기소 계정정보 조회 중 ===')
        credentials = fetch_credentials(SERVER)

    print('=== issue_real_estate_register() 시작 ===')
    result = iros_document_issue.issue_real_estate_register(payload, credentials, options)
    print('=== 결과 ===')
    print(json.dumps(result, ensure_ascii=False, indent=2))
