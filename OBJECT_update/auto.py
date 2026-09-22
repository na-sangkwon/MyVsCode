import os
import json
import time
import random
import datetime
import sys
import platform
import traceback
import pymysql
import tkinter as tk
from tkinter import ttk, messagebox
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# 외부 폴더의 진짜 일꾼 모듈들을 정상적으로 매핑
from workers.obang_worker import ObangAutomationWorker
from workers.carrot_worker import CarrotAutomationWorker

# 🎯 [2026-09-06 통합] 당근 업데이트 사이클 직후 자동 검증(verify_carrot_registration.py)을
# 연결한다. import 자체가 실패해도(예: 파일 누락, selenium 버전 불일치) 오방/당근 업데이트라는
# 본작업까지 막으면 안 되므로, 여기서부터 방어적으로 처리한다 — 로컬 lint만으로는 서버에서의
# import 실패를 못 잡아내기 때문(CLAUDE.md 코드수정 원칙).
try:
    import verify_carrot_registration as carrot_verify
    CARROT_VERIFY_모듈_로드됨 = True
except Exception:
    carrot_verify = None
    CARROT_VERIFY_모듈_로드됨 = False

# 사진 원본 폴더 최상위 경로 — Windows PC에서는 매핑드라이브(Z:), 나스 도커 컨테이너에서는
# "업무자료" 공유폴더를 직접 볼륨마운트한 경로를 쓴다. 두 환경이 같은 코드를 그대로 쓰도록
# 환경변수로 주입받고, 값이 없으면(기존 PC 환경) 지금까지 써온 Z: 드라이브를 기본값으로 둔다.
PHOTO_ROOT_DIR = os.environ.get('PHOTO_ROOT_DIR', 'Z:\\업무자료')

# 매물 카테고리 매핑 테이블
SELE_MAP = {
    '원룸': [11, ['오픈형', '분리형', '통1.5룸', '1.5룸', '1.8룸']],
    '투룸/쓰리룸+': [12, ['투룸', '쓰리룸+']],
    '상가/사무실': [16, ['상가', '사무실']],
    '오피스텔': [13, []],
    '아파트': [14, []],
    '주택/고급빌라': [15, []],
    '공장/창고': [17, []],
    '토지': [18, []],
    '통건물': [19, ['상업용건물','상가주택','다가구주택','다세대주택','오피스텔','단독주택','도시형생활주택','주상복합건물','지식산업센터']],
}

# 글로벌 카운트 변수 유지
complete_count = 0
restart_ok = 0
update_ok = 0
end_ok = 0
skip_count = 0  # 임대료 누락 건너뛰기 전역 카운트
error_count = 0  # 성공/재등록/비공개/건너뜀 어디로도 분류되지 않는 예외 발생 건수

def 작업모드_한글(target_mode):
    # [처리결과 가시화] "작업 모드"를 화면에 보여줘야 할 지점이 두 곳(테스트 대상 확정 로그,
    # run_platform_workers()의 완료 요약)이라 라벨 매핑을 한 곳에 모아 재사용한다.
    return {"all": "전체 실행", "update_only": "신규/수정 업데이트만 실행", "close_only": "거래완료(비공개) 처리만 실행"}.get(target_mode, target_mode)

def process_wait(hour):
    now = datetime.datetime.now()
    end_time = now + datetime.timedelta(hours=hour)

    root = tk.Tk()
    root.title("실시간 남은 시간")
    root.geometry("500x150")

    remaining_time_label = tk.Label(root, text="", font=("Helvetica", 14))
    remaining_time_label.pack(pady=20)

    stop_button = tk.Button(root, text="멈춤", font=("Helvetica", 12), command=root.destroy)
    stop_button.pack(pady=10)

    def update_remaining_time():
        remaining_time = end_time - datetime.datetime.now()
        remaining_time_str = str(remaining_time).split('.')[0]  
        remaining_time_label.configure(text=f"업데이트 개시까지 {remaining_time_str} 남았습니다.")
        if remaining_time.total_seconds() > 0:
            root.after(1000, update_remaining_time)  
        else:
            root.destroy()
            update_start()

    update_remaining_time()
    root.mainloop()

def get_main_settings(prev_settings=None):
    root = tk.Tk()
    root.title("⚙️ 통합 매물 자동화 환경 설정")
    # 🎯 [창 크기 확장] 테스트 입력 프레임이 안착할 버퍼 공간 확보를 위해 세로 높이를 620으로 보정합니다.
    window_width, window_height = 450, 620
    
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = int((screen_width / 2) - (window_width / 2))
    y = int((screen_height / 2) - (window_height / 2))
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    # 🎯 [닫기 경로 통일] X버튼도 '확인'과 마찬가지로 체크박스·라디오버튼 상태를 저장한 뒤 종료한다
    # (close_and_exit는 아래에서 정의 — 클로저라 정의 위치가 이 줄보다 아래여도 문제없음).
    root.protocol("WM_DELETE_WINDOW", lambda: close_and_exit())

    frame_platform = tk.LabelFrame(root, text=" 🌐 대상 플랫폼 선택 ", font=("Malgun Gothic", 10, "bold"), padx=10, pady=10)
    frame_platform.pack(padx=20, pady=10, fill="x")

    # 🎯 [환경설정 영구 저장] 같은 실행 중 재오픈(prev_settings)이 아니라 프로그램을 완전히
    # 새로 켠 경우엔, 지난번 확인 버튼을 눌렀을 때 이 창 전용으로 저장해둔 main_settings.json을
    # 읽어 기본값으로 삼는다. 이 값은 test_memo.txt와 마찬가지로 로컬 파일 전용이며,
    # 나스 무인실행이 쓰는 운영 DB(pr_config, auto_update 그룹)와는 별개다 — 이 창에서 바꾼
    # 값이 나스 자동실행 설정에 영향을 주지 않도록 의도적으로 분리했다.
    if prev_settings:
        init_obang = prev_settings['obang']
        init_carrot = prev_settings['carrot']
        init_day = prev_settings['before_day']
        init_mode = prev_settings['mode']
    else:
        saved_settings = {}
        if os.path.exists("main_settings.json"):
            try:
                with open("main_settings.json", "r", encoding="utf-8") as 설정파일:
                    saved_settings = json.load(설정파일)
            except: pass
        init_obang = saved_settings.get('obang', True)
        init_carrot = saved_settings.get('carrot', True)
        init_day = saved_settings.get('before_day', 1)
        init_mode = saved_settings.get('mode', 'all')
    
    # 🎯 [영구 파일 소환] 메모리(prev_settings)에 세션 기록이 없다면 로컬 디스크의 메모장을 열어 마지막 새홈 테스트 번호를 자동 로딩합니다.
    if prev_settings and 'test_code' in prev_settings:
        init_test_code = prev_settings['test_code']
    else:
        init_test_code = ""
        if os.path.exists("test_memo.txt"):
            try:
                with open("test_memo.txt", "r", encoding="utf-8") as 파일조수:
                    init_test_code = 파일조수.read().strip()
            except: pass
    
    var_obang = tk.BooleanVar(value=init_obang) 
    var_carrot = tk.BooleanVar(value=init_carrot)
    is_custom_mode = init_day not in [0, 1, 3, 7]
    var_period = tk.IntVar(value=-1 if is_custom_mode else init_day)
    var_all = tk.BooleanVar(value=True if init_obang and init_carrot else False)
    
    def toggle_all():
        val = var_all.get()
        var_obang.set(val)
        var_carrot.set(val)

    def update_all_state():
        if var_obang.get() and var_carrot.get():
            var_all.set(True)
        else:
            var_all.set(False)

    tk.Checkbutton(frame_platform, text="전체 선택", variable=var_all, command=toggle_all, font=("Malgun Gothic", 10)).pack(anchor="w")
    tk.Checkbutton(frame_platform, text="오방부동산", variable=var_obang, command=update_all_state, font=("Malgun Gothic", 10)).pack(side="left", padx=20, pady=5)
    tk.Checkbutton(frame_platform, text="당근부동산", variable=var_carrot, command=update_all_state, font=("Malgun Gothic", 10)).pack(side="left", padx=20, pady=5)

    frame_period = tk.LabelFrame(root, text=" 📅 데이터 조회 기간 ", font=("Malgun Gothic", 10, "bold"), padx=10, pady=10)
    frame_period.pack(padx=20, pady=10, fill="x")

    periods = [("오늘 기준", 0), ("1일 전 데이터", 1), ("3일 전 데이터", 3), ("7일 전 데이터", 7)]
    for text, val in periods:
        tk.Radiobutton(frame_period, text=text, variable=var_period, value=val, font=("Malgun Gothic", 10)).pack(anchor="w", pady=2)

    custom_frame = tk.Frame(frame_period)
    custom_frame.pack(anchor="w", pady=2)
    tk.Radiobutton(custom_frame, text="직접 입력 ", variable=var_period, value=-1, font=("Malgun Gothic", 10)).pack(side="left")
    entry_custom = tk.Entry(custom_frame, width=5, font=("Malgun Gothic", 10), justify="center")
    entry_custom.pack(side="left", padx=2)
    entry_custom.insert(0, str(init_day) if is_custom_mode else "14")
    tk.Label(custom_frame, text=" 일 전 데이터", font=("Malgun Gothic", 10)).pack(side="left")

    frame_mode = tk.LabelFrame(root, text=" ⚙️ 작업 모드 선택 ", font=("Malgun Gothic", 10, "bold"), padx=10, pady=10)
    frame_mode.pack(padx=20, pady=10, fill="x")
    
    var_mode = tk.StringVar(value=init_mode)
    tk.Radiobutton(frame_mode, text="전체 자동화 (업데이트 + 비공개 처리)", variable=var_mode, value="all", font=("Malgun Gothic", 10)).pack(anchor="w", pady=2)
    tk.Radiobutton(frame_mode, text="신규/수정 업데이트만 실행", variable=var_mode, value="update_only", font=("Malgun Gothic", 10)).pack(anchor="w", pady=2)
    tk.Radiobutton(frame_mode, text="거래완료(비공개) 처리만 실행", variable=var_mode, value="close_only", font=("Malgun Gothic", 10)).pack(anchor="w", pady=2)

    # 🎯 [신설] 특정 매물번호 테스트 입력을 위한 독립 레이아웃 슬롯 벨트
    frame_test = tk.LabelFrame(root, text=" 🧪 특정 매물번호 단독/다중 테스트 (선택사항) ", font=("Malgun Gothic", 10, "bold"), padx=10, pady=8, fg="#ba264a")
    frame_test.pack(padx=20, pady=5, fill="x")

    # 🎯 [다중화] 쉼표로 여러 새홈 매물번호를 함께 입력할 수 있다는 걸 라벨/입력창 너비로 알 수 있게 한다.
    tk.Label(frame_test, text="새홈 매물번호 입력 (쉼표로 여러 개):", font=("Malgun Gothic", 10)).pack(side="left", padx=5)

    entry_test = tk.Entry(frame_test, width=35, font=("Malgun Gothic", 10, "bold"), justify="center", fg="blue")
    entry_test.pack(side="left", padx=5)
    entry_test.insert(0, init_test_code)

    result_settings = {}

    # 🎯 [환경설정 영구 저장] 확인/취소/X 세 가지 닫기 경로 모두에서 공통으로 호출해,
    # "확인을 눌러야만 저장된다"는 예전 동작 때문에 취소·X로 닫으면 체크박스·라디오버튼
    # 변경이 그냥 사라지던 문제를 근본적으로 없앤다. 직접입력 기간 값이 잘못 들어있어도
    # (확인 버튼과 달리) 경고창으로 종료를 막지 않고, 그 항목만 이전 저장값을 그대로 유지한다.
    def save_current_settings():
        if var_period.get() == -1:
            try:
                직접입력값 = int(entry_custom.get().strip())
                if 직접입력값 < 0: raise ValueError
            except ValueError:
                직접입력값 = init_day
        else:
            직접입력값 = var_period.get()

        try:
            with open("main_settings.json", "w", encoding="utf-8") as 설정파일:
                json.dump({
                    'obang': var_obang.get(),
                    'carrot': var_carrot.get(),
                    'before_day': 직접입력값,
                    'mode': var_mode.get(),
                }, 설정파일, ensure_ascii=False)
        except: pass

        # 🎯 [영구 파일 마킹] 새홈 매물번호 입력값도 확인/취소/X 세 경로 모두에서
        # 동일하게 저장한다 — on_ok() 전용이던 예전 방식으로는 취소·X로 닫을 때
        # 체크박스와 똑같이 유실되던 문제가 있었다.
        테스트_입력값 = entry_test.get().strip()
        try:
            with open("test_memo.txt", "w", encoding="utf-8") as 파일조수:
                파일조수.write(테스트_입력값)
        except: pass

    def close_and_exit():
        save_current_settings()
        sys.exit()

    def on_ok():
        if not var_obang.get() and not var_carrot.get():
            messagebox.showwarning("경고", "최소 하나의 플랫폼은 선택해야 합니다.")
            return

        if var_period.get() == -1:
            try:
                입력값 = int(entry_custom.get().strip())
                if 입력값 < 0: raise ValueError
                result_settings['before_day'] = 입력값
            except ValueError:
                messagebox.showwarning("입력 오류", "조회 기간은 0 이상의 올바른 숫자로만 입력해 주세요.")
                return
        else:
            result_settings['before_day'] = var_period.get()

        result_settings['obang'] = var_obang.get()
        result_settings['carrot'] = var_carrot.get()
        result_settings['mode'] = var_mode.get()
        result_settings['test_code'] = entry_test.get().strip()

        # 🎯 [영구 파일 마킹] 새홈 매물번호를 포함한 실제 파일 저장은 save_current_settings()가
        # 담당한다(확인/취소/X 공통 로직) — 위 result_settings는 이번 실행에 바로 쓸 반환값일 뿐이다.
        save_current_settings()

        root.destroy()

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=15)
    tk.Button(btn_frame, text="확 인", font=("Malgun Gothic", 10, "bold"), bg="#2196F3", fg="white", padx=25, pady=5, command=on_ok).pack(side="left", padx=20)
    tk.Button(btn_frame, text="취 소", font=("Malgun Gothic", 10), bg="#9E9E9E", fg="white", padx=25, pady=5, command=close_and_exit).pack(side="right", padx=20)

    root.mainloop()
    return result_settings

def show_update_preview(data, before_day, user_settings):
    """ 대시보드 그리드 형태로 매물 요약본을 보여주는 프리뷰 윈도우 """
    today = datetime.datetime.now().date()
    start_date = today - datetime.timedelta(days=before_day)

    root = tk.Tk()
    root.title("📊 통합 매물 업데이트 대시보드 프리뷰")
    root.geometry("820x320")
    root.attributes("-topmost", True)

    info_text = f"조회 기준: 최근 {before_day}일 ({start_date} ~ {today})"
    tk.Label(root, text=info_text, font=("Malgun Gothic", 11, "bold"), fg="#333333", pady=10).pack()

    columns = ("platform", "new", "today", "unreg", "fav", "normal", "complete")
    tree = ttk.Treeview(root, columns=columns, show="headings", height=4)
    
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview.Heading", font=("Malgun Gothic", 10, "bold"), background="#EEEEEE")
    style.configure("Treeview", font=("Malgun Gothic", 10), rowheight=28)

    headers = {
        "platform": "플랫폼", "new": "신규등록(기간)", "today": "금일등록", 
        "unreg": "미등록의뢰 🔥", "fav": "관심수정", "normal": "일반수정", "complete": "거래완료"
    }
    for col, text in headers.items():
        tree.heading(col, text=text)
        tree.column(col, width=130 if col == "platform" else 110, anchor="center")

    # [처리결과 가시화] 신규등록/금일등록/미등록의뢰/관심수정/일반수정은 "업데이트" 트랙,
    # 거래완료는 "거래완료" 트랙 결과다 — 작업 모드가 한쪽만 실행하도록 돼 있으면 실행 안 될
    # 트랙의 칸은 실제 값이 아니라 "—"(제외)로 표시한다. 값을 그대로 보여주면 "실제로 0건"인지
    # "이 모드에서는 애초에 안 도는 트랙"인지 구분이 안 돼, 완료 후 결과와 비교할 때 마치
    # 어긋난 것처럼 보인다(147558/691813 테스트에서 실제로 겪은 혼란).
    실행모드 = user_settings.get('mode', 'all')
    업데이트_실행됨 = 실행모드 in ('all', 'update_only')
    거래완료_실행됨 = 실행모드 in ('all', 'close_only')
    제외표시 = "— (모드 제외)"

    # 🔥 [클리닝 패치] 사용자가 체크박스에서 활성화한 플랫폼의 로우(Row)만 프리뷰 표에 인서트합니다!
    if user_settings['obang']:
        tree.insert("", "end", values=(
            "오방부동산",
            len(data.get('신규등록매물', [])) if 업데이트_실행됨 else 제외표시,
            len(data.get('금일등록매물', [])) if 업데이트_실행됨 else 제외표시,
            data.get('미등록의뢰수', 0) if 업데이트_실행됨 else 제외표시,
            len(data.get('업데이트매물_관심', [])) if 업데이트_실행됨 else 제외표시,
            len(data.get('업데이트매물_일반', [])) if 업데이트_실행됨 else 제외표시,
            len(data.get('거래완료매물', [])) if 거래완료_실행됨 else 제외표시,
        ))

    if user_settings['carrot']:
        # 미등록의뢰/관심수정은 당근에는 없는 개념이라 모드와 무관하게 항상 "해당없음"이다
        # (모드 제외와 의미가 겹치지 않도록 별도 표기를 쓴다).
        해당없음 = "— (해당없음)"
        tree.insert("", "end", values=(
            "당근부동산",
            data.get('당근_신규등록', 0) if 업데이트_실행됨 else 제외표시,
            data.get('당근_금일등록', 0) if 업데이트_실행됨 else 제외표시,
            해당없음,
            해당없음,
            data.get('당근_일반수정', 0) if 업데이트_실행됨 else 제외표시,
            data.get('당근_거래완료', 0) if 거래완료_실행됨 else 제외표시,
        ))

    tree.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

    proceed = False
    def on_confirm(): nonlocal proceed; proceed = True; root.destroy()
    def on_cancel(): nonlocal proceed; proceed = False; root.destroy()

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=15)
    tk.Button(btn_frame, text="🚀 이대로 작업 개시", font=("Malgun Gothic", 10, "bold"), bg="#4CAF50", fg="white", padx=15, pady=5, command=on_confirm).pack(side=tk.LEFT, padx=15)
    tk.Button(btn_frame, text="❌ 작업 취소", font=("Malgun Gothic", 10), bg="#F44336", fg="white", padx=15, pady=5, command=on_cancel).pack(side=tk.RIGHT, padx=15)

    root.mainloop()
    return proceed

def obang_data(before_day, 오방_선택=True, 당근_선택=True, 강제_새홈번호_목록=None):
    """
    기존 DB 로직에 당근 데이터 매핑 연동을 결합한 데이터 수집 함수.

    강제_새홈번호_목록: [단독/다중 테스트 모드 전용] 값이 있으면, 아래 3개 후보군 쿼리(당근 광고
    대상 / 오방 업데이트 대상 / 오방 거래완료 대상)가 평소의 "최근 N일 의뢰수정 또는 관심 매물"·
    "광고시작 14일 경과" 조건 대신 이 새홈번호들만을 대상으로 삼는다. 그 뒤(매물 정보 조립,
    오방·당근 매칭, 관심/일반 분류, 반환 구조)는 정상 배치와 완전히 동일한 코드를 그대로 탄다 —
    테스트 전용 조회/조립 로직을 별도로 두지 않기 위함(재사용 원칙, 테스트매물_정보조회() 참고).
    """
    today = datetime.datetime.now().date()
    금일등록매물, 신규등록매물, 미등록의뢰수, img_update = [], [], 0, []
    obang_update, obang_update_fav, obang_update_normal, obang_map = [], [], [], {}          
    obang_update_seen = set()  

    start_date = today - datetime.timedelta(days=before_day)
    today_str, start_date_str = today.strftime("%Y-%m-%d"), start_date.strftime("%Y-%m-%d")
    today_date, start_date_date = today, start_date    

    conn = pymysql.connect(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', charset='utf8')
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('USE obangkr;')

    carrot_map, dang_new_set, dang_today_set, dang_update_set = {}, set(), set(), set()
    if 강제_새홈번호_목록:
        # 테스트 모드: "광고시작 14일 경과" 조건 없이, 지정된 새홈번호의 당근 광고만 후보로 삼는다.
        자리표시자 = ",".join(["%s"] * len(강제_새홈번호_목록))
        c_query = f'SELECT object_code_new, ad_code FROM pr_externalad WHERE ad_site = "당근" AND ad_del = "N" AND object_code_new IN ({자리표시자})'
        cursor.execute(c_query, tuple(강제_새홈번호_목록))
    else:
        c_query = f'SELECT object_code_new, ad_code FROM pr_externalad WHERE ad_site = "당근" AND ad_del = "N" AND CURRENT_DATE >= DATE_ADD(ad_start, INTERVAL 14 DAY)'
        cursor.execute(c_query)

    # 🔥 [DB 실시간 가로채기] 당근 만료 광고 테이블 원본 데이터 출력
    당근_광고_원본목록 = cursor.fetchall()

    for c_row in 당근_광고_원본목록:
        if c_row['object_code_new']: carrot_map[c_row['object_code_new']] = str(c_row['ad_code'])

    # [2026-09-16 수정 — 다른 세션 DB 마이그레이션 반영] pr_request_give/pr_object 둘 다
    # land_code/building_code/room_code 대신 land_group_code/building_group_code/
    # room_group_code를 쓰도록 스키마가 바뀌었다. 여기서는 두 테이블끼리 "같은 위치인지"만
    # 비교하면 되므로(개별 land_code 자체가 필요한 게 아님) 그룹코드로 그대로 바꿔치기하면 된다.
    query = '''SELECT DISTINCT p.request_code, p.land_group_code, p.building_group_code, p.room_group_code FROM pr_request_give AS p
            LEFT JOIN pr_request_fix AS c ON p.request_code = c.request_code WHERE c.fix_del="N"'''
    cursor.execute(query)
    f_res = cursor.fetchall()
    f_codes_arr = []
    for row in f_res:
        o_query = 'SELECT land_group_code,building_group_code,room_group_code,object_code_obang FROM pr_object WHERE object_status="중개요청" AND object_del="N" AND land_group_code = %s AND building_group_code = %s AND room_group_code = %s'
        cursor.execute(o_query, (row['land_group_code'], row['building_group_code'], row['room_group_code']))
        o_res = cursor.fetchall()
        try:
            # [테스트 모드 격리] 이 줄은 원래 관심(즐겨찾기) 매물의 오방코드를 조건 없이
            # 업데이트매물에 바로 얹어둔다 — 테스트 모드에서까지 그대로 두면, 지정한 새홈번호와
            # 무관한 회사 전체의 관심 매물이 몽땅 테스트 대상에 섞여 들어간다(실측으로 확인:
            # 147558/112561 두 건만 지정했는데 관심 매물 14건이 함께 섞여 나왔다). 테스트 모드는
            # 지정된 새홈번호만 대상이어야 하므로 이 줄만 건너뛴다.
            if not 강제_새홈번호_목록 and o_res and o_res[0]['object_code_obang'] != '': obang_update.append(str(o_res[0]['object_code_obang']))
            f_codes_arr.append(row['request_code'])
        except: pass

    f_codes = "','".join(f_codes_arr) if len(f_codes_arr) > 0 else ''
    f_codes = f"'{f_codes}'"

    # 테스트 모드: 날짜/관심 조건 대신, 지정된 새홈번호에 대응하는 request_code만 후보로 삼는다
    # (테스트매물_정보조회()가 새홈번호 -> request_code로 변환 — 관심(f_codes)과 완전히 같은
    # 자리에 꽂아 넣는다). 나머지 필터(내놓기/접수·진행 등)는 정상 배치와 동일하게 유지한다 —
    # 그래야 이미 완료(성공/실패)된 의뢰는 아래 거래완료 후보군 쪽에서만 잡혀 중복되지 않는다.
    테스트_request_codes = 테스트매물_정보조회(강제_새홈번호_목록) if 강제_새홈번호_목록 else []
    if 강제_새홈번호_목록:
        테스트_f_codes = "','".join(테스트_request_codes) if 테스트_request_codes else ''
        후보_조건 = f'p.request_code IN (\'{테스트_f_codes}\')'
    else:
        후보_조건 = f'(p.request_date BETWEEN "{start_date_str}" AND "{today_str}" OR p.request_code IN ({f_codes}))'

    query = f'''SELECT p.request_code, p.tr_target, p.object_type1, p.object_type2, p.admin_name, p.request_date, p.request_udate, p.request_wdate,
        c.land_group_code, c.building_group_code, c.room_group_code, c.request_trading, c.request_deposit1, c.request_deposit2, c.request_deposit3,
        c.request_rent1, c.request_rent2, c.request_rent3, c.request_manager, c.request_mmoney, c.request_mlist, c.tr_memo,
        c.request_area1, c.request_area2, c.request_areatype1, c.request_areatype2, c.first_trade
        FROM pr_request AS p LEFT JOIN pr_request_give AS c ON p.request_code = c.request_code
        WHERE p.request_del="N" AND {후보_조건}
        AND p.request_main != "전체" AND p.tr_type = "내놓기" AND (p.request_status = "접수" OR p.request_status = "진행")
        AND (c.request_deposit1 != "" OR c.request_rent1 != "")'''
    cursor.execute(query)
    recently_res = cursor.fetchall()

    # 1️⃣ 무조건 다 찍던 구형 코드는 삭제하고, 안내 헤더만 담백하게 남깁니다.
    print(f"\n[🔎 DB 실시간 로딩] 의뢰 데이터 수집 완료 (총 {len(recently_res)}건 중 매칭 시작)")
    print("-" * 80)

    for row in recently_res:
        if not row['land_group_code']: continue
        # [2026-09-16 수정 — 다른 세션 DB 마이그레이션 반영] pr_object는 land_group_code만
        # 갖고 있고, 주소 상세(land_do/si/dong/li 등)는 여전히 개별 pr_land에만 있어서 land_code로
        # 한 번 풀어줘야 한다. 그런데 land_group_code 하나가 여러 land_code(필지)를 묶을 수 있어
        # (실측 확인: 최대 16개), "대표 필지" 하나를 골라야 한다 — 이미 web(PHP)쪽
        # core/lib/lib_object.php:getObjectFullInfoDataList()/lib_get.php:getObjectInfo()가
        # 쓰는 것과 동일한 방식(pr_land_group.representing_jibun과 land_jibun이 일치하는 필지,
        # 없으면 가장 먼저 등록된 필지)을 그대로 따른다 — 두 곳 다 고칠 때 반드시 같이 맞출 것.
        # building_group_code/room_group_code는 실측 결과 그룹당 항목이 사실상 항상 1개뿐이라
        # (건물 2452/2452, 호실 11672/11677) 단순 서브쿼리로 충분하다.
        # 기존 컬럼 l.land_jibung/representing_jibun/representing_jimok/representing_purpose는
        # 애초에 pr_land(개별)가 아니라 pr_land_group(그룹)에만 있는 컬럼이라 이 JOIN(l=pr_land)
        # 에서는 원래부터 전부 NULL만 나오고 있었다 — land_jibun만 살리고 나머지는 뺐다(아래
        # land_jibung 코드에서 쓰는 이름과 맞추려고 AS로 별칭만 유지).
        o_query = '''SELECT o.object_code_new, o.land_group_code, o.building_group_code, o.room_group_code, o.object_code_obang, o.object_type, o.object_ttype, o.object_rtype, o.object_del, o.object_ori_img,
            l.land_do, l.land_si, l.land_dong, l.land_li, l.land_main, l.land_jibun AS land_jibung, l.land_address, l.land_totarea, l.land_important, l.land_option, l.land_memo,
            b.building_name, b.building_del, b.building_gate1, b.building_gate2, b.building_parking, b.building_pn, b.building_direction, b.building_bolt, b.building_height, b.building_element, b.building_memo, b.building_important, b.building_option, b.building_purpose, b.building_grndflr, b.building_ugrndflr, b.building_archarea, b.building_totarea, b.building_usedate, b.building_stract, b.building_elvcount,
            r.room_num, r.room_floor, r.room_status, r.room_nmemo, r.room_gate1, r.room_gate2, r.room_memo, r.room_rcount, r.room_bcount, r.r_direction, r.room_direction, r.room_area1, r.room_areatype1, r.room_area2, r.room_areatype2, r.room_important, r.room_option, r.room_purpose
            FROM pr_object AS o
            LEFT JOIN pr_land AS l ON l.land_code = COALESCE(
                    (SELECT li.land_code FROM pr_land_group_item li
                     INNER JOIN pr_land il ON il.land_code = li.land_code AND il.land_del = 'N'
                     WHERE li.land_group_code = o.land_group_code
                       AND il.land_jibun = (SELECT lgr.representing_jibun FROM pr_land_group lgr WHERE lgr.land_group_code = o.land_group_code)
                     LIMIT 1),
                    (SELECT li2.land_code FROM pr_land_group_item li2 WHERE li2.land_group_code = o.land_group_code ORDER BY li2.item_idx ASC LIMIT 1)
                ) AND l.land_del = 'N'
            LEFT JOIN pr_building AS b ON b.building_code = (SELECT bi.building_code FROM pr_building_group_item bi WHERE bi.building_group_code = o.building_group_code LIMIT 1) AND b.building_del = 'N'
            LEFT JOIN pr_room     AS r ON r.room_code     = (SELECT ri.room_code FROM pr_room_group_item ri WHERE ri.room_group_code = o.room_group_code LIMIT 1) AND r.room_del = 'N'
            WHERE o.object_del = 'N' AND o.land_group_code = %s AND o.building_group_code = %s AND o.room_group_code = %s LIMIT 1;'''
        cursor.execute(o_query, (row['land_group_code'], row.get('building_group_code',''), row.get('room_group_code','')))
        o_row = cursor.fetchone()
        if not o_row: continue
        # print(f">>>>>>o_row:\n{o_row}")
        object_code_new = o_row['object_code_new']


        # 2️⃣ [정밀 필터링 선택형 출력] 사장님이 체크박스에 선택한 플랫폼의 진짜 타겟만 골라 찍습니다.
        이동_방식 = []
        출력_여부 = False
        
        # 당근이 선택되었고, 현재 매물이 당근 만료 광고에 존재할 때만 노출 대상 확정
        if 당근_선택 and (object_code_new in carrot_map):
            이동_방식.append(f"당근번호:{carrot_map[object_code_new]}")
            출력_여부 = True
            
        # 오방이 선택되었고, 오방 번호가 존재할 때만 노출 대상 확정
        오방_코드 = str(o_row.get('object_code_obang') or '').strip()
        if 오방_선택 and 오방_코드:
            # 단, 당근만 선택했을 때는 오방 매물이라도 당근 만료 목록에 들어있다면 번호 식별용으로 함께 보여줍니다.
            이동_방식.append(f"오방번호:{오방_코드}")
            if object_code_new in carrot_map:
                출력_여부 = True
            elif 오방_선택:
                출력_여부 = True

        if 출력_여부:
            주소 = o_row.get('land_address', '주소미기재')
            가격 = f"보증금/월세: {row.get('request_deposit1')}/{row.get('request_rent1')}" if row.get('request_rent1') else f"매매가: {row.get('request_trading')}"
            print(f" 🎯 [처리대상 매물 발견] 새홈번호: {object_code_new} | 명찰: {', '.join(이동_방식)} | 주소: {주소} | 금액: {가격}")


        # 🔥 [원형 전수 복원] Z드라이브 물리 폴더 스캔 및 object_ori_img DB 상태 동기화 처리
        tr_target = row['tr_target']
        if tr_target == '층호수' and row.get('room_group_code','') == '':
            print("호실정보없는 층호수의뢰: " + str(row['request_code']))
        else:
            try:
                land_do = o_row.get('land_do') or ''
                if land_do.endswith('도'):
                    if '경상남도' in land_do: land_do = '경남'
                    elif '경상북도' in land_do: land_do = '경북'
                    elif '충청남도' in land_do: land_do = '충남'
                    elif '충청북도' in land_do: land_do = '충북'
                    elif '전라남도' in land_do: land_do = '전남'
                    elif '전라북도' in land_do: land_do = '전북'
                    elif '강원특별자치도' in land_do: land_do = '강원'
                    else: land_do = land_do[:-1]
                elif land_do.endswith('특별시'): land_do = land_do[:-3]

                land_type = '산' if o_row.get('land_type') == '2' else ''
                land_jibung = o_row.get('land_jibung') or ''

                # Windows(\\)와 리눅스(/) 양쪽에서 동일한 코드로 실제 폴더 중첩을 표현하려면
                # 구분자를 하드코딩하지 않고 os.sep을 써야 한다 — 나스 도커(리눅스) 컨테이너에서는
                # 이 sep이 '/'가 되어야 실제 폴더 경로로 인식되고, 그냥 '\\'로 고정해두면
                # 리눅스에서는 역슬래시가 포함된 하나의 파일명으로 오인되어 존재 확인이 항상 실패한다.
                sep = os.sep
                do_path = land_do
                si_path = sep + (o_row.get('land_si') or '') if o_row.get('land_si') else ''
                dong_path = sep + (o_row.get('land_dong') or '') if o_row.get('land_dong') else ''
                li_path = sep + (o_row.get('land_li') or '') if o_row.get('land_li') else ''
                jibun_path = sep + land_jibung if land_jibung else ''

                folderPath = do_path + si_path + dong_path + li_path + land_type + jibun_path
                if tr_target in ['건물', '층호수'] and o_row.get('building_name'):
                    folderPath += sep + o_row['building_name']
                if tr_target == '층호수' and o_row.get('room_floor'):
                    rf = o_row['room_floor']
                    room_floor_str = str(rf) if int(rf) > 0 else '지하' + str(int(rf) * (-1))
                    folderPath += sep + room_floor_str + '층' + sep + (o_row.get('room_num') or '')

                main_dir = os.path.join(PHOTO_ROOT_DIR, '4사진자료&이미지자료(외부유출금지)', '1주거용물건, 상업용물건') + sep
                path_dir = main_dir + folderPath
                if os.path.exists(path_dir):
                    file_list = os.listdir(path_dir)
                    원본사진들 = [f for f in file_list if f.lower().endswith(('.jpeg', '.gif', '.png', '.jpg'))]
                    if 원본사진들 and o_row.get('object_ori_img') == 'N':
                        cursor.execute(f'UPDATE pr_object SET object_ori_img="Y" WHERE object_code_new="{object_code_new}"')
            except: pass

        if o_row.get('object_code_new') in carrot_map:
            dang_code = carrot_map[o_row['object_code_new']]
            dang_update_set.add(dang_code)
            if start_date_date <= row['request_wdate'] <= today_date: dang_new_set.add(dang_code)
            if row['request_wdate'] == today_date: dang_today_set.add(dang_code)

        obang_code = str(o_row.get('object_code_obang') or '').strip()
        if not obang_code: continue

        if start_date_date <= row['request_wdate'] <= today_date:
            if obang_code: 신규등록매물.append(obang_code)
            else: 미등록의뢰수 += 1
        if row['request_wdate'] == today_date and obang_code: 금일등록매물.append(obang_code)

        if obang_code not in obang_update_seen:
            obang_update.append(obang_code)
            if row['request_code'] in f_codes_arr: obang_update_fav.append(obang_code)
            else: obang_update_normal.append(obang_code)
            obang_update_seen.add(obang_code)
        obang_map[obang_code] = {**row, **o_row}

    random.shuffle(obang_update)

    # 거래완료매물 수집 — 테스트 모드일 때는 위에서 이미 구한 테스트_f_codes를 그대로 재사용한다.
    # (지정된 새홈번호의 의뢰가 이미 완료(성공/실패) 상태라면 여기서, 아직 진행 중이면 위
    # recently_res 쪽에서 잡힌다 — 상호 배타적이라 중복 집계될 일이 없다.)
    거래완료_조건 = f'p.request_code IN (\'{테스트_f_codes}\')' if 강제_새홈번호_목록 else f'p.request_date BETWEEN "{start_date_str}" AND "{today_str}"'
    query = f"""SELECT o.object_code_obang, o.object_code_new FROM pr_request AS p
               JOIN pr_request_give AS c ON p.request_code = c.request_code
               JOIN pr_object AS o ON o.object_del = 'N' AND o.land_group_code = c.land_group_code AND o.building_group_code = c.building_group_code AND o.room_group_code = c.room_group_code
               WHERE p.request_del = 'N' AND p.request_main <> '전체' AND p.tr_type = '내놓기' AND p.request_status IN ('성공','실패')
                 AND {거래완료_조건}"""
    cursor.execute(query)
    rows = cursor.fetchall()

    obang_complete = [str(r['object_code_obang']) for r in rows if r['object_code_obang']]
    dang_complete_set = set(carrot_map[r['object_code_new']] for r in rows if r['object_code_new'] in carrot_map)

    cursor.close(); conn.close()
    
    return {
        '금일등록매물': 금일등록매물, '신규등록매물': 신규등록매물, '미등록의뢰수': 미등록의뢰수, 'img_update': img_update,
        '업데이트매물': obang_update, '업데이트매물_관심': obang_update_fav, '업데이트매물_일반': obang_update_normal,
        '거래완료매물': obang_complete, '오방매물정보': obang_map,
        '당근_신규등록': len(dang_new_set), '당근_금일등록': len(dang_today_set), '당근_일반수정': len(dang_update_set), '당근_거래완료': len(dang_complete_set),
        # 🔥 [패치] 일꾼 파일이 루프를 돌릴 수 있도록 순수 매물번호 리스트 형태의 데이터셋 추가 전달
        '당근_업데이트목록': list(dang_update_set),
        '당근_거래완료목록': list(dang_complete_set)
    }


def 테스트매물_정보조회(새홈번호_목록):
    """
    [단독/다중 테스트 모드 전용] obang_data()의 정상 후보군 쿼리는 "최근 N일 의뢰수정" 또는
    "관심(즐겨찾기)" 매물만 대상으로 삼는데, 테스트 모드는 이 범위와 무관하게 지정된 새홈번호들이
    항상 잡혀야 한다. 이 함수는 새홈번호들을 그에 대응하는 request_code로 바꿔주기만 한다 —
    관심(즐겨찾기)이 f_codes를 만들어 recently_res 쿼리의 "OR request_code IN (f_codes)" 자리에
    꽂는 것과 완전히 같은 방식으로, obang_data()가 이 반환값을 그 자리에 대신 꽂아 넣는다.
    주소/가격 등 매물 상세 조회는 여기서 하지 않는다 — obang_data()의 기존 enrichment 루프가
    그대로 재사용되므로 중복 로직을 새로 만들 필요가 없다.
    """
    if not 새홈번호_목록: return []
    conn = pymysql.connect(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', database='obangkr', charset='utf8')
    cursor = conn.cursor()
    자리표시자 = ",".join(["%s"] * len(새홈번호_목록))
    cursor.execute(f'''
        SELECT DISTINCT c.request_code
        FROM pr_object AS o
        JOIN pr_request_give AS c ON o.land_group_code = c.land_group_code
                                   AND o.building_group_code = c.building_group_code
                                   AND o.room_group_code = c.room_group_code
        WHERE o.object_code_new IN ({자리표시자}) AND o.object_del = 'N'
    ''', tuple(새홈번호_목록))
    request_codes = [str(r[0]) for r in cursor.fetchall()]
    cursor.close(); conn.close()
    return request_codes


def 테스트_새홈번호별_오방당근코드_조회(새홈번호_목록):
    """
    [단독/다중 테스트 모드 전용] "당근 1건" 같은 합계만으로는 입력한 새홈번호 중 어느 것이
    실제로 그 플랫폼에 존재하는지 알 수 없다(예: 당근 광고 자체가 없는 매물) — obangData의
    업데이트/거래완료 목록과 대조해 새홈번호별로 어느 트랙에 속하는지 보여주기 위해, 새홈번호별
    오방코드/당근코드만 조회한다(주소/가격 조회는 obang_data()가 이미 하므로 중복하지 않는다).
    """
    if not 새홈번호_목록: return {}, {}
    conn = pymysql.connect(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', database='obangkr', charset='utf8')
    cursor = conn.cursor()
    자리표시자 = ",".join(["%s"] * len(새홈번호_목록))
    cursor.execute(f"SELECT object_code_new, object_code_obang FROM pr_object WHERE object_code_new IN ({자리표시자})", tuple(새홈번호_목록))
    새홈_오방코드 = {str(r[0]): str(r[1] or '').strip() for r in cursor.fetchall()}
    cursor.execute(
        f"SELECT object_code_new, ad_code FROM pr_externalad WHERE ad_site='당근' AND ad_del='N' AND object_code_new IN ({자리표시자})",
        tuple(새홈번호_목록)
    )
    새홈_당근코드 = {str(r[0]): str(r[1]) for r in cursor.fetchall()}
    cursor.close(); conn.close()
    return 새홈_오방코드, 새홈_당근코드


# 🎯 [2026-09-06 통합] 당근 루프 검증 단계 전용 디버그 로그 — auto.py는 GUI 경로에 별도
# 로그파일이 없어서(콘솔 print만 있음), 이 신규 통합 지점만이라도 나중에 원인 추적이 가능하게
# 독립된 로그 파일을 둔다. cwd에 따라 엉뚱한 위치에 생기지 않도록 이 파일 자신의 위치 기준
# 절대경로로 고정한다(과거 main_settings.json이 cwd에 따라 엉뚱한 곳에 생기던 문제 재발 방지).
CARROT_VERIFY_LOOP_DEBUG_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "carrot_loop_verify_debug.log")


def _당근_검증_디버그기록(내용):
    # 디버그 기록 자체의 실패(디스크 문제 등)가 본작업을 막으면 안 된다.
    try:
        with open(CARROT_VERIFY_LOOP_DEBUG_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {내용}\n")
    except Exception:
        pass


def _당근_검증_오류_pr_error_log기록(message, file=None, line=None, stack=None):
    """
    오방홈 오류로그 체계(pr_error_log)에 직접 기록한다. 실제 저장/중복판정 로직은
    obangtest 저장소의 core/lib/lib_error_log.php::recordErrorLog()가 원본이다 — naver.py는
    로컬도우미 HTTP 콜백을 거쳐 그 PHP 함수를 호출하지만(연장등록 예상밖오류 사례), auto.py는
    그 콜백 경로가 없어서(로컬도우미 없이 나스/PC에서 직접 도는 무인 프로세스) 같은 테이블에
    같은 스키마·같은 지문(fingerprint) 규칙으로 파이썬에서 직접 INSERT한다(2026-09-06,
    사용자 지적으로 pr_log 대체 임시조치에서 전환) — 다른 저장소(PHP)는 건드리지 않는다.

    지문 = sha1(source|file|line|message[:300]) — recordErrorLog()와 동일 공식. 같은 지문이면
    새 행 대신 elog_occurrence_count만 늘려서, 반복되는 같은 오류가 로그 테이블을 폭주시키지
    않게 하는 원본의 방어 설계를 그대로 따른다.
    """
    try:
        import hashlib
        # ⚠️ [2026-09-06 실측 발견] elog_source는 varchar(10)이다 — pr_log.log_item과 같은 종류의
        # 함정을 반복하지 않으려고 미리 SHOW CREATE TABLE로 확인했다. 원본 PHP 쪽 관례('php'|'js'|
        # 'ajax')를 넘지 않는 짧은 값을 쓰고, "당근 루프 검증"이라는 구체적 맥락은 길이 제한이
        # 없는 elog_message 쪽에 담는다.
        source = 'python'
        severity = 'Exception'
        message = str(message)[:5000]
        stack = str(stack)[:8000] if stack else None
        지문원본 = f"{source}|{file or ''}|{line or ''}|{message[:300]}"
        fingerprint = hashlib.sha1(지문원본.encode('utf-8')).hexdigest()

        conn = pymysql.connect(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', database='obangkr', charset='utf8')
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO pr_error_log
                   (elog_source, elog_severity, elog_level, elog_message, elog_file, elog_line,
                    elog_stack, elog_url, elog_admin_id, elog_fingerprint, elog_occurrence_count,
                    elog_is_read, elog_first_seen_at, elog_last_seen_at)
               VALUES (%s, %s, 'high', %s, %s, %s, %s, NULL, NULL, %s, 1, 'N', NOW(), NOW())
               ON DUPLICATE KEY UPDATE
                   elog_occurrence_count = elog_occurrence_count + 1,
                   elog_last_seen_at = NOW(),
                   elog_is_read = 'N',
                   elog_stack = %s""",
            (source, severity, message, file, line, stack, fingerprint, stack)
        )
        conn.commit()
        cursor.close(); conn.close()
    except Exception:
        pass


def 당근_루프_검증_안전실행(driver, 당근번호_리스트):
    """
    당근 업데이트 사이클 직후 자동 검증을 실행한다(2026-09-06 통합, 사용자 결정: 사람 승인 없이
    자동 DB 반영). 검증 로직 자체의 버그나 당근 화면 구조 변경으로 이 단계가 실패해도, 방금 끝난
    오방/당근 업데이트라는 본작업 결과에는 절대 영향을 주면 안 되므로 여기서 통째로 방어한다 —
    실패 시 전체 traceback을 로컬 디버그 로그와 pr_error_log(오방홈 오류로그 체계) 둘 다에 남겨
    나중에 추적 가능하게 한다.
    """
    if not CARROT_VERIFY_모듈_로드됨:
        _당근_검증_디버그기록("검증 모듈(verify_carrot_registration) import 실패로 이번 사이클 검증을 건너뜀")
        return None
    if not 당근번호_리스트:
        return None
    try:
        결과 = carrot_verify.당근번호로_검증(driver, 당근번호_리스트, DB반영=True)
        _당근_검증_디버그기록(f"검증 완료: 대상 {당근번호_리스트} -> {결과}")
        return 결과
    except Exception:
        오류내용 = traceback.format_exc()
        _당근_검증_디버그기록(f"검증 중 예외 발생(대상 {당근번호_리스트}):\n{오류내용}")
        # elog_file/elog_line은 실제 예외가 터진 지점(가장 안쪽 프레임)을 가리키게 한다 —
        # recordErrorLog()가 호출부(__FILE__/__LINE__)를 받는 것과 같은 취지.
        마지막프레임 = traceback.extract_tb(sys.exc_info()[2])
        elog_file = 마지막프레임[-1].filename if 마지막프레임 else __file__
        elog_line = 마지막프레임[-1].lineno if 마지막프레임 else None
        _당근_검증_오류_pr_error_log기록(
            f"당근 루프 검증 실패(대상 {당근번호_리스트}): {오류내용.strip().splitlines()[-1] if 오류내용 else ''}",
            file=elog_file, line=elog_line, stack=오류내용
        )
        return None


def run_platform_workers(obangData, target_mode, user_settings, progress_callback, unattended=False):
    """
    크롬 드라이버를 띄우고 오방/당근 워커를 순차 실행해 (성공/재등록/수정/비공개/건너뜀) 누적 카운트를 반환한다.
    사람이 클릭하며 지켜보는 GUI 대시보드(update_start)와, 사람 없이 도는 무인 모드(run_unattended)가
    "실제 업데이트를 수행하는" 이 부분만은 완전히 같은 코드를 타야 한다 — 여기서 갈라지면
    한쪽만 고치고 다른 쪽을 깜빡하는 사고로 이어지기 쉬워서, 진행상황 통지만 progress_callback으로
    분리하고 나머지 로직은 호출부(GUI/무인) 구분 없이 이 함수 하나로 통일했다.
    """
    # [처리결과 가시화] 'error'는 성공/재등록/비공개/건너뜀 어디로도 분류되지 않는 "설명되지
    # 않는 예외" 건수 — 예전엔 이게 집계 자체가 없어 조용히 사라졌다. '오방_요약'/'당근_요약'은
    # 무인모드가 지금까지 오방+당근을 합산해 하나의 숫자로만 보여주던 것을(어느 플랫폼이
    # 문제였는지 구분 불가) 플랫폼별로 나눠 보여줄 수 있도록, 완료 직후 이 함수 안에서
    # 바로 조립해 둔다(GUI 최종화면/무인모드 로그 양쪽이 재사용). 둘 다 처음부터 "선택 안 함"으로
    # 채워두고, 선택된 경우에만 실제 결과로 덮어쓴다 — 플랫폼을 아예 선택 안 한 것과 결과 조립을
    # 깜빡한 것을 구분 못 하는 일이 없게(직접 겪음: "결과가 1개만 보이는데 왜?"라는 질문이 나왔던
    # 이유 중 하나가 당근을 선택 안 했는데도 완료화면에 당근 관련 언급이 아예 없어서였다).
    작업모드_표시 = 작업모드_한글(target_mode)
    counts = {
        'complete': 0, 'restart': 0, 'update': 0, 'end': 0, 'skip': 0, 'error': 0,
        '작업모드': 작업모드_표시,
        '오방_요약': "선택 안 함(스킵됨)", '당근_요약': "선택 안 함(스킵됨)",
    }
    print(f"   [⚙️ 작업 모드] {작업모드_표시} | 오방:{'실행' if user_settings['obang'] else '건너뜀'} 당근:{'실행' if user_settings['carrot'] else '건너뜀'}")

    options = Options()
    profile_path = os.path.join(os.getcwd(), "daangn_profile")
    options.add_argument(f"--user-data-dir={profile_path}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    if platform.system() != 'Windows':
        # 나스 도커 컨테이너(리눅스)에서만 필요한 옵션 — 크롬이 SIGTRAP으로 죽던 문제
        # (2026-08-30 실제로 재현) 대응. 컨테이너는 root로 돌기 때문에 크롬 자체 샌드박스가
        # 거부되고, 도커 기본 /dev/shm(64MB)도 크롬한테 너무 작다. 이미 검증된 윈도우 PC
        # 동작에는 영향이 없도록 리눅스에서만 적용한다.
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # Xvfb에는 창을 관리해주는 윈도우 매니저가 없어서 maximize_window()가 내부적으로
        # 쓰는 CDP 호출(Runtime.evaluate)이 깨진다(2026-08-30 실제로 재현). 창 크기를
        # 미리 인자로 지정해서 창 최대화 자체가 필요 없게 우회한다.
        options.add_argument("--window-size=1600,900")
    options.add_experimental_option('useAutomationExtension', False)
    # [2026-09-02] 이 프로필(daangn_profile)은 원래 당근 로그인 세션 유지용인데 오방
    # 로그인에도 그대로 재사용된다 — 그 결과 크롬 비밀번호 관리자가 오방 로그인 정보를
    # 저장해두고 매 실행마다 비동기로 자동완성을 시도했고, 이 자동완성이 obang_worker.py의
    # 아이디 입력 코드와 타이밍 경쟁을 일으켜 실행마다 성공/실패가 갈리는 원인이었다(실제로
    # 필드에 아이디가 중복 이어붙어 로그인 자체가 거부되는 현상을 재현/확인함). 타이밍에
    # 의존하는 재시도 대신, 이 프로필에서 비밀번호 저장·자동완성 자체를 꺼서 경쟁 조건을
    # 원천 제거한다.
    options.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
    })

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    if platform.system() == 'Windows':
        driver.maximize_window()

    try:
        if user_settings['obang']:
            obang_worker = ObangAutomationWorker(
                driver, obangData, target_mode,
                progress_callback=lambda c, t, txt, mode='determinate': progress_callback('obang', c, t, txt, mode),
                unattended=unattended
            )
            c_count, r_ok, u_ok, e_ok, s_ok, err_ok, nf_ok = obang_worker.run()
            counts['complete'] += c_count; counts['restart'] += r_ok; counts['update'] += u_ok; counts['end'] += e_ok; counts['skip'] += s_ok; counts['error'] += err_ok
            # [처리결과 가시화] "총 N건" 자체를 요약 맨 앞에 적어, 뒤에 나열된 숫자를 더했을 때
            # 이 값과 정확히 같아야 한다는 걸 화면만 보고도 검산할 수 있게 한다(사용자 지침:
            # "각 사이트마다 카운트된 것들의 합은 항상 조회한 매물들의 숫자와 일치해야 한다").
            # restart_ok(재등록)는 update_ok로 이미 집계된 같은 매물의 부가 지표라 총건수에서 제외.
            # "미등록"은 두 가지를 합친 것이다: nf_ok(거래완료 대상인데 검색화면에서 못 찾음)와
            # obangData의 오방_미등록_건수(테스트 모드에서 입력한 새홈번호에 오방코드 자체가 없음)
            # — 사용자 지적대로 "오방에 등록된 상태로 확인 안 됨"이라는 점에서 같은 의미라 하나로
            # 합친다. 일반 배치 실행에서는 오방_미등록_건수가 없어(0) nf_ok만 그대로 쓰인다.
            오방_미등록_합계 = nf_ok + obangData.get('오방_미등록_건수', 0)
            오방_총건수 = u_ok + e_ok + s_ok + err_ok + 오방_미등록_합계
            counts['오방_요약'] = f"총 {오방_총건수}건 — 성공:{u_ok} 재등록:{r_ok} 비공개:{e_ok} 건너뜀:{s_ok} 실패:{err_ok} 미등록:{오방_미등록_합계}"
            progress_callback('obang', 100, 100, f"✅ 오방 업데이트 완료 V \n(총 {오방_총건수}건 - 성공:{u_ok} , 재등록:{r_ok} , 비공개:{e_ok} , 건너뜀:{s_ok} , 실패:{err_ok} , 미등록:{오방_미등록_합계}개)", 'determinate')
        else:
            progress_callback('obang', 0, 100, "⏭️ 오방부동산 스킵됨", 'determinate')

        if user_settings['carrot']:
            carrot_worker = CarrotAutomationWorker(
                driver, obangData, target_mode,
                progress_callback=lambda c, t, txt, mode='determinate': progress_callback('carrot', c, t, txt, mode),
                unattended=unattended
            )
            cc, ro, uo, eo, so, ho, err_c = carrot_worker.run()
            counts['complete'] += cc; counts['restart'] += ro; counts['update'] += uo; counts['end'] += eo; counts['skip'] += so; counts['error'] += err_c
            # [처리결과 가시화] cc(최종완료_개수)와 eo(비공개완료_성공_개수)가 매물 단위의 실제
            # 항목 수이고, ro(끌어올리기)/uo(수정업데이트)/ho(숨김해제)는 cc 안에 이미 포함된
            # 같은 매물의 부가 지표라서 총건수 계산에선 제외한다(오방쪽과 동일한 원칙). 당근_미등록_건수
            # (테스트 모드에서 입력한 새홈번호에 당근 광고 자체가 없는 경우, 예: 691813)도 오방과
            # 동일하게 "미등록"으로 합산한다 — 그래야 총건수가 조회한 새홈번호 수와 정확히 맞는다.
            당근_미등록_건수 = obangData.get('당근_미등록_건수', 0)
            당근_총건수 = cc + eo + so + err_c + 당근_미등록_건수
            counts['당근_요약'] = f"총 {당근_총건수}건 — 끌올:{ro + ho}(일반{ro}/숨김해제{ho}) 수정:{uo} 비공개:{eo} 건너뜀:{so} 실패:{err_c} 미등록:{당근_미등록_건수}"
            progress_callback(
                'carrot', 100, 100,
                f"✅ 당근 업데이트 완료 V \n(총 {당근_총건수}건 - 끌올 {ro + ho}건 [일반 {ro} / 숨김해제 {ho}] , 수정:{uo} , 비공개:{eo} , 건너뜀:{so} , 실패:{err_c} , 미등록:{당근_미등록_건수}개)",
                'determinate'
            )

            # 🎯 [2026-09-06 통합] 방금 처리한 당근매물들이 실제로도 '판매중'으로 반영됐는지
            # 검증하고, 불일치는 자동으로 DB(ad_end)에 반영한다(사용자 결정: 사람 승인 없이
            # 즉시 반영). 이미 로그인된 driver를 그대로 넘겨 새 브라우저를 띄우지 않는다.
            # 검증 실패가 방금 끝난 오방/당근 업데이트 결과에 영향을 주지 않도록 별도 함수
            # 안에서 통째로 방어한다(당근_루프_검증_안전실행 주석 참고).
            검증결과 = 당근_루프_검증_안전실행(driver, obangData.get('당근_업데이트목록', []))
            if 검증결과 and 검증결과['불일치건수'] > 0:
                progress_callback(
                    'carrot', 100, 100,
                    f"🔍 당근 사후검증: 불일치 {검증결과['불일치건수']}건 자동수정 "
                    f"(확인 {검증결과['총건수']}건 중, 확인불가 {검증결과['확인불가건수']}건)",
                    'determinate'
                )
        else:
            progress_callback('carrot', 0, 100, "⏭️ 당근부동산 스킵됨", 'determinate')
    finally:
        # 워커 도중 예외가 나도(예: 로그인 세션 만료) 크롬 프로세스가 좀비로 남지 않도록 항상 종료한다.
        # 무인 모드는 사람이 지켜보지 않으므로 이 보장이 특히 중요하다.
        driver.quit()

    return counts

def update_start():
    global complete_count, restart_ok, update_ok, end_ok, skip_count, error_count
    print(f"업데이트 사이클 시작: {datetime.datetime.now()}")

    # 🎯 루프 밖에서 세팅 보관용 빈 메모리 박스를 먼저 비치해 둡니다.
    user_settings = None 
    
    # 🔥 [무한 루프 벨트 탑재] 사용자가 취소했을 때 설정창으로 부드럽게 되돌아가기 위한 가드 회로
    while True:
        # 🎯 위에서 보정 가공한 함수에 현재의 메모리팩을 밀어 넣어 복원을 지시합니다.
        user_settings = get_main_settings(user_settings)
        before_day = user_settings['before_day']
        target_mode = user_settings['mode']

        # 🎯 [단독/다중 매물 테스트 모드] 입력창에 쉼표로 구분해 적은 새홈번호가 있으면, obang_data()가
        # 정상 배치와 완전히 같은 코드로 "이 번호들만" 후보군으로 삼아 조회하게 한다(obang_data()의
        # 강제_새홈번호_목록 파라미터 참고) — 테스트 전용 별도 조회/조립 로직을 두지 않는다.
        테스트_새홈번호_목록 = [x.strip() for x in user_settings.get('test_code', '').split(',') if x.strip()]
        if 테스트_새홈번호_목록:
            print(f"   [🧪 새홈번호 테스트 모드 가동] {len(테스트_새홈번호_목록)}건 지정: {', '.join(테스트_새홈번호_목록)}")

        obangData = obang_data(
            before_day, user_settings['obang'], user_settings['carrot'],
            강제_새홈번호_목록=테스트_새홈번호_목록 or None
        )

        if 테스트_새홈번호_목록:
            처리대상_전체건수 = (
                len(obangData.get('업데이트매물', [])) + len(obangData.get('거래완료매물', []))
                + len(obangData.get('당근_업데이트목록', [])) + len(obangData.get('당근_거래완료목록', []))
            )
            if 처리대상_전체건수 == 0:
                messagebox.showwarning(
                    "역추적 실패",
                    f"입력하신 새홈 매물번호 [{', '.join(테스트_새홈번호_목록)}]에서 유효한 처리 대상을 "
                    f"찾지 못했습니다.\n(선택된 플랫폼에 등록된 광고/의뢰가 없거나, 번호가 잘못됐을 수 있습니다)"
                )
                user_settings['test_code'] = ""
                continue
            # [처리결과 가시화] 여기 나오는 "확보된 대상"은 업데이트/거래완료 두 트랙을 합친
            # 수치라서, 작업 모드가 한쪽만 실행하도록 돼 있으면 실제 완료 결과의 "총 N건"과
            # 다를 수 있다(예: 업데이트만 실행 모드에서는 거래완료 트랙 건수가 실행되지 않음).
            # 둘이 달라도 되는 정상 상황임을 여기서 미리 밝혀 완료 결과와 비교할 때 헷갈리지 않게 한다.
            오방_업데이트_건수 = len(obangData.get('업데이트매물', []))
            오방_거래완료_건수 = len(obangData.get('거래완료매물', []))
            당근_업데이트_건수 = len(obangData.get('당근_업데이트목록', []))
            당근_거래완료_건수 = len(obangData.get('당근_거래완료목록', []))
            print(f"   [🎯 테스트 대상 확정] 오방 {오방_업데이트_건수 + 오방_거래완료_건수}건(업데이트:{오방_업데이트_건수}/거래완료:{오방_거래완료_건수}) "
                  f"/ 당근 {당근_업데이트_건수 + 당근_거래완료_건수}건(업데이트:{당근_업데이트_건수}/거래완료:{당근_거래완료_건수}) "
                  f"— ※ 작업 모드가 [{작업모드_한글(target_mode)}]이므로, 이 중 해당 트랙만 실제 실행됩니다.")

            # [처리결과 가시화] "당근 1건" 같은 합계만으로는 입력한 번호 중 어느 게 그 플랫폼에
            # 아예 없는지 알 수 없다(691813처럼 당근 광고 자체가 없는 경우가 실제로 있었다) —
            # 새홈번호 하나하나가 각 플랫폼 어느 트랙에 속하는지(또는 아예 없는지) 직접 보여준다.
            새홈_오방코드, 새홈_당근코드 = 테스트_새홈번호별_오방당근코드_조회(테스트_새홈번호_목록)
            print("   [🔍 새홈번호별 상세]")
            for 번호 in 테스트_새홈번호_목록:
                오방코드 = 새홈_오방코드.get(번호, '')
                당근코드 = 새홈_당근코드.get(번호, '')
                if not 오방코드: 오방상태 = "오방코드 없음"
                elif 오방코드 in obangData.get('업데이트매물', []): 오방상태 = f"업데이트 대상(코드:{오방코드})"
                elif 오방코드 in obangData.get('거래완료매물', []): 오방상태 = f"거래완료 대상(코드:{오방코드})"
                else: 오방상태 = f"코드는 있으나({오방코드}) 두 목록 어디에도 없음 — 확인 필요"
                if not 당근코드: 당근상태 = "당근 광고 없음"
                elif 당근코드 in obangData.get('당근_업데이트목록', []): 당근상태 = f"업데이트 대상(코드:{당근코드})"
                elif 당근코드 in obangData.get('당근_거래완료목록', []): 당근상태 = f"거래완료 대상(코드:{당근코드})"
                else: 당근상태 = f"코드는 있으나({당근코드}) 두 목록 어디에도 없음 — 확인 필요"
                print(f"      · {번호} — 오방: {오방상태} | 당근: {당근상태}")

            # [처리결과 가시화] "조회한 매물수"는 입력한 새홈번호 개수(여기서는 2개) 그 자체다 —
            # 그중 하나가 그 플랫폼에 아예 등록돼 있지 않다고 해서 "조회 대상에서 빠진 셈 치고"
            # 조용히 목록에서 빼버리면, 완료 결과의 총건수가 조회 수보다 작아져서 마치 뭔가
            # 누락된 것처럼 보인다(사용자 지적: "조회한 매물수는 2개, 미등록 매물이 1개 있었을
            # 뿐인데 표시가 안 됐다"). obangData에 미등록 건수를 실어 보내 run_platform_workers()의
            # 완료 집계가 "총 N건"을 계산할 때 조회 수와 정확히 맞아떨어지게 한다.
            obangData['오방_미등록_건수'] = sum(1 for 번호 in 테스트_새홈번호_목록 if not 새홈_오방코드.get(번호))
            obangData['당근_미등록_건수'] = sum(1 for 번호 in 테스트_새홈번호_목록 if not 새홈_당근코드.get(번호))

        # 🎯 프리뷰 창에서 [이대로 작업 개시]를 누르면 True가 반환되어 루프를 깨고 탈출합니다.
        if show_update_preview(obangData, before_day, user_settings):
            break
            
        print("   [↩️ 프리뷰 취소 검지] 사용자가 대시보드 진입을 취소하여 메인 환경 설정창으로 복귀(회항)합니다.")
        # break를 만나지 못했으므로 while문의 처음으로 점프하여 get_main_settings()를 다시 호출합니다.

    # 루프를 무사히 깨고 나온 승인된 매물 데이터셋만 가지고 아래 메인 화면을 그립니다.
    dash_win = tk.Tk()
    dash_win.title("⏳ 통합 매물 자동화 진행 대시보드")
    dash_win.geometry("520x420")
    dash_win.attributes("-topmost", True)
    
    sw, sh = dash_win.winfo_screenwidth(), dash_win.winfo_screenheight()
    dash_win.geometry(f"520x420+{int((sw-520)/2)}+{int((sh-420)/2)}")
    dash_win.protocol("WM_DELETE_WINDOW", lambda: sys.exit())

    # 🎯 [안전핀 선언] 플랫폼 체크 해제 시 변수 미생성으로 인한 NameError를 원천 차단하기 위해 초기 껍데기를 바인딩합니다.
    lbl_obang, bar_obang = None, None
    lbl_carrot, bar_carrot = None, None

    if user_settings['obang']:
        frame_obang = tk.LabelFrame(dash_win, text=" 오방부동산 ", font=("Malgun Gothic", 10, "bold"), padx=15, pady=10)
        frame_obang.pack(padx=20, pady=10, fill="x")
        lbl_obang = tk.Label(frame_obang, text="💤 작업 대기 중...", font=("Malgun Gothic", 10), fg="#666666")
        lbl_obang.pack(anchor="w")
        bar_obang = ttk.Progressbar(frame_obang, orient="horizontal", length=440, mode="determinate")
        bar_obang.pack(pady=5)

    if user_settings['carrot']:
        frame_carrot = tk.LabelFrame(dash_win, text=" 당근부동산 ", font=("Malgun Gothic", 10, "bold"), padx=15, pady=10)
        frame_carrot.pack(padx=20, pady=10, fill="x")
        lbl_carrot = tk.Label(frame_carrot, text="💤 작업 대기 중...", font=("Malgun Gothic", 10), fg="#666666")
        lbl_carrot.pack(anchor="w")
        bar_carrot = ttk.Progressbar(frame_carrot, orient="horizontal", length=440, mode="determinate")
        bar_carrot.pack(pady=5)

    # fileName: auto.py (update_start 함수 내부 하반부 구역)

    def update_master_ui(platform, current, total, text, mode='determinate'):
        """
        [스레드 안전 업그레이드] 백그라운드 일꾼들이 보내오는 신호를 
        메인 UI 스레드의 비동기 큐(.after)에 안전하게 적재하여 렉 없이 즉각 반영합니다.
        """
        def gui_update():
            if platform == 'obang' and lbl_obang and bar_obang:
                lbl_obang.config(text=text, fg="#0056b3" if "중" in text else "green")
                bar_obang.config(mode=mode)
                if mode == 'determinate':
                    bar_obang['maximum'] = total
                    bar_obang['value'] = current
                elif current == 1: bar_obang.start(15)
            elif platform == 'carrot' and lbl_carrot and bar_carrot:
                lbl_carrot.config(text=text, fg="#0056b3" if "중" in text else "green")
                bar_carrot.config(mode=mode)
                if mode == 'determinate':
                    bar_carrot['maximum'] = total
                    bar_carrot['value'] = current
                elif current == 1: bar_carrot.start(15)
        
        # 🚀 메인 스레드가 웅크리고 있는 창 루프에 안전하게 변경 지시 전달
        dash_win.after(0, gui_update)

    # 🎯 [대개혁] 대기 모드와 종료 제어를 담당할 상태 변수 및 함수 선언선 정렬
    loop_action = tk.StringVar(value="none")
    def action_wait(): loop_action.set("wait"); dash_win.destroy()
    def action_exit(): loop_action.set("exit"); dash_win.destroy(); sys.exit()

    # =================================================================
    # 🚀 [신설] 백그라운드 독립 고속 선로 전용 실행 팩토리 함수
    # =================================================================
    def run_workers_background():
        global complete_count, restart_ok, update_ok, end_ok, skip_count, error_count

        # 실제 드라이버 기동/워커 실행/카운트 집계는 무인 모드(run_unattended)와 완전히
        # 같은 run_platform_workers를 태운다. 여기서는 그 결과를 GUI 진행바/전역 카운트에
        # 반영하는 "GUI 전용 통지"만 얹는다 — ttk 프로그레스바가 이전에 애니메이션(indeterminate)
        # 중이었을 수 있어, 100% 완료 통지 직전에 반드시 stop()으로 애니메이션을 먼저 끊어준다.
        def gui_progress(platform, current, total, text, mode='determinate'):
            if mode == 'determinate' and current == total:
                bar = bar_obang if platform == 'obang' else bar_carrot
                if bar is not None:
                    dash_win.after(0, lambda: bar.stop())
                    dash_win.after(0, lambda: bar.config(mode='determinate', value=bar['maximum']))
            update_master_ui(platform, current, total, text, mode)

        counts = run_platform_workers(obangData, target_mode, user_settings, gui_progress)
        complete_count += counts['complete']; restart_ok += counts['restart']; update_ok += counts['update']
        end_ok += counts['end']; skip_count += counts['skip']; error_count += counts['error']

        # 🏁 [마감 렌더링]: 일꾼들이 모두 퇴근한 자리에 최종 성공 안내문과 버튼들을 매끄럽게 그립니다.
        def finish_ui():
            lbl_finish = tk.Label(dash_win, text="🎉 모든 지정 플랫폼의 동기화 작업이 완료되었습니다!", font=("Malgun Gothic", 11, "bold"), fg="#28a745")
            lbl_finish.pack(pady=10)

            # [처리결과 가시화] 완료 안내문 한 줄로는 실제로 몇 건이 어떻게 처리됐는지 알 수 없어,
            # 진행 중 스쳐 지나간 플랫폼별 라벨(오방_요약/당근_요약)을 최종 화면에도 그대로
            # 다시 보여준다. 어떤 작업 모드로 실행됐는지, 플랫폼을 아예 선택 안 한 건지(그래서
            # 결과가 없는 건지) 매번 물어보지 않아도 알 수 있게 둘 다 항상 표시한다.
            lbl_mode = tk.Label(dash_win, text=f"⚙️ 작업 모드: {counts.get('작업모드', '?')}", font=("Malgun Gothic", 10, "bold"), fg="#555555")
            lbl_mode.pack(pady=(0, 4))
            요약_줄들 = [
                f"🟠 오방부동산 — {counts.get('오방_요약')}",
                f"🥕 당근부동산 — {counts.get('당근_요약')}",
            ]
            lbl_summary = tk.Label(dash_win, text="\n".join(요약_줄들), font=("Malgun Gothic", 10), fg="#333333", justify="left")
            lbl_summary.pack(pady=(0, 10))

            btn_frame = tk.Frame(dash_win)
            btn_frame.pack(pady=5)

            tk.Button(btn_frame, text="⏳ 10시간 대기 모드 진입", font=("Malgun Gothic", 10, "bold"), bg="#2196F3", fg="white", padx=15, pady=5, command=action_wait).pack(side="left", padx=15)
            tk.Button(btn_frame, text="❌ 프로그램 종료", font=("Malgun Gothic", 10), bg="#9E9E9E", fg="white", padx=15, pady=5, command=action_exit).pack(side="right", padx=15)
        
        dash_win.after(0, finish_ui)
    # =================================================================

    # 🚀 [기차 분리 사출]: 메인 화면을 붙잡지 않도록 백그라운드 전용 일꾼 기차 출발!
    import threading
    worker_thread = threading.Thread(target=run_workers_background)
    worker_thread.daemon = True
    worker_thread.start()

    # 윈도우 메인 화면 그리기 루프 정식 가동 (이제 렉이 완전히 사라집니다)
    dash_win.mainloop()

    if loop_action.get() == "wait":
        process_wait(10)

def load_unattended_settings():
    """
    무인 모드 설정을 운영 DB(obangkr.cafe24.com)의 pr_config 테이블(config_group='auto_update')에서
    읽는다. 2026-08-30부터 진실의 원천이 cafe24 환경설정 화면(web/settings/settings.php의
    "매물 자동업데이트 설정" 카드)으로 바뀌었다 — 이전의 JSON 파일 방식(config/unattended_settings.json,
    나스 자체 web_config Flask 앱)은 카드 하나로 통일하며 폐기했다. DB 접속 정보는 obang_data()가
    쓰는 것과 동일하다(같은 운영 DB).
    """
    conn = pymysql.connect(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', database='obangkr', charset='utf8')
    cursor = conn.cursor()
    cursor.execute("SELECT config_key, config_value FROM pr_config WHERE config_group='auto_update'")
    rows = dict(cursor.fetchall())
    cursor.close(); conn.close()

    required = ('obang', 'carrot', 'before_day', 'run_mode')
    missing = [key for key in required if key not in rows]
    if missing:
        raise ValueError(f"pr_config(auto_update)에 필수 항목이 없습니다: {missing}")

    return {
        'obang': rows['obang'] == 'Y',
        'carrot': rows['carrot'] == 'Y',
        'before_day': int(rows['before_day']),
        'mode': rows['run_mode'],
    }

def run_unattended(log_path):
    """
    Tkinter 팝업(설정입력/미리보기/진행창) 없이, cafe24 환경설정 카드에 저장된 값으로 곧바로
    실행하는 무인 모드. 나스 작업 스케줄러가 예약 시각에 이 함수를 호출하는 것을 전제로 만들었다 —
    사람이 지켜보지 않으므로 messagebox 경고창 대신 모든 상황(성공/실패)을 로그 파일에 남기는 것으로
    대체한다.
    """
    def log(message):
        line = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
        # 작업 스케줄러처럼 콘솔이 연결되지 않은 상태로 실행되면 stdout이 cp949로 잡혀
        # 이모지(❌ 등)를 못 찍고 UnicodeEncodeError로 죽는다(2026-08-30 실제로 재현됨).
        # 로그 파일 기록이 무인 모드의 유일한 확인 수단이므로, 콘솔 출력 실패가 그 기록까지
        # 막지 않도록 화면 출력 실패는 무시하고 넘어간다.
        try:
            print(line)
        except UnicodeEncodeError:
            pass
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(line + "\n")

    def write_run_log(result, message):
        # cafe24 환경설정 카드("최근 실행 결과")가 이 값을 보여준다 — 로그 파일은 나스에만
        # 있어 사람이 SSH로 들어가야 보이는데, 그게 안 되니 "결과를 어디서 확인하냐"는 질문이
        # 실제로 나왔다(2026-08-31). pr_config(설정값 전용)에 넣었다가, 이건 "설정"이 아니라
        # "실행 이력/로그"라는 지적을 받아 pr_log(활동로그, core/lib/lib_common.php::writeLog()가
        # 쓰는 것과 동일한 테이블·컬럼 관례)로 옮겼다 — system 계열 이벤트가 log_target='system'을
        # 쓰는 기존 관례를 그대로 따른다.
        try:
            conn = pymysql.connect(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', database='obangkr', charset='utf8')
            cursor = conn.cursor()
            now = datetime.datetime.now()
            cursor.execute(
                """INSERT INTO pr_log (log_target, log_item, log_value, admin_id, log_wdate, log_wtime)
                   VALUES ('system', 'auto_update', %s, '', %s, %s)""",
                (f"[{result}] {message}", now.date().isoformat(), now.strftime('%H:%M:%S'))
            )
            conn.commit()
            cursor.close(); conn.close()
        except Exception:
            log(f"⚠️ 실행 결과를 DB에 남기지 못했습니다(카드에 최근 결과가 안 보일 수 있음):\n{traceback.format_exc()}")

    log("=== 무인 업데이트 사이클 시작 (설정출처: cafe24 환경설정 pr_config) ===")
    try:
        user_settings = load_unattended_settings()
    except Exception:
        log(f"❌ 설정 조회 실패 — 실행 중단:\n{traceback.format_exc()}")
        write_run_log('error', '설정 조회 실패 — 로그 파일 확인 필요')
        return

    before_day = user_settings['before_day']
    target_mode = user_settings['mode']

    try:
        obangData = obang_data(before_day, user_settings['obang'], user_settings['carrot'])
    except Exception:
        log(f"❌ DB 데이터 수집 실패 — 실행 중단:\n{traceback.format_exc()}")
        write_run_log('error', 'DB 데이터 수집 실패 — 로그 파일 확인 필요')
        return

    def progress_callback(platform, current, total, text, mode='determinate'):
        log(f"[{platform}] {text}")

    try:
        counts = run_platform_workers(obangData, target_mode, user_settings, progress_callback, unattended=True)
        # [처리결과 가시화] 예전엔 오방+당근을 합산한 숫자 하나만 남겨서, 카드에 "성공:30"이
        # 찍혀도 오방 30/당근 0인지 15/15인지 구분할 방법이 없었다 — 플랫폼별 요약(오방_요약/
        # 당근_요약, run_platform_workers가 만들어둔 것)을 항상 같이 남긴다(선택 안 한 플랫폼도
        # "선택 안 함(스킵됨)"으로 명시돼 있어 결과가 비어있는 이유를 따로 물을 필요가 없다).
        # 작업모드(전체/업데이트만/거래완료만)도 같이 남겨 어떤 범위로 실행됐는지 바로 알 수 있게 한다.
        summary = f"[모드: {counts.get('작업모드', '?')}] 🟠오방 — {counts.get('오방_요약')} | 🥕당근 — {counts.get('당근_요약')}"
        log(f"✅ 무인 업데이트 사이클 완료 — {summary}")
        write_run_log('success', summary)
    except Exception:
        # 로그인 세션 만료 등으로 워커가 중간에 실패해도 원인을 로그에 남겨, 나중에 사람이
        # 로그 파일을 확인했을 때 "왜 며칠째 자동화가 안 됐는지" 바로 알 수 있게 한다.
        # str(e)만 남기면 일부 셀레니움 예외는 메시지가 비어 원인 추적이 안 됐다
        # (2026-08-30 실제로 재현) — 예외 종류와 traceback을 전부 남긴다.
        log(f"❌ 실행 중 오류 발생(로그인 세션 만료 등 확인 필요):\n{traceback.format_exc()}")
        write_run_log('error', '실행 중 오류 발생(로그인 세션 만료 등) — 로그 파일 확인 필요')

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--unattended":
        log_path = sys.argv[2] if len(sys.argv) > 2 else "unattended_run.log"
        run_unattended(log_path)
    else:
        update_start()