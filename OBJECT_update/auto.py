import os
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
    root.protocol("WM_DELETE_WINDOW", lambda: sys.exit())

    frame_platform = tk.LabelFrame(root, text=" 🌐 대상 플랫폼 선택 ", font=("Malgun Gothic", 10, "bold"), padx=10, pady=10)
    frame_platform.pack(padx=20, pady=10, fill="x")

    # 🎯 [기억 복원 확장] 테스트용으로 타이핑했던 번호가 프리뷰 취소 회항 시에도 지워지지 않도록 세포를 보존합니다.
    init_obang = prev_settings['obang'] if prev_settings else True
    init_carrot = prev_settings['carrot'] if prev_settings else True
    init_day = prev_settings['before_day'] if prev_settings else 1
    init_mode = prev_settings['mode'] if prev_settings else 'all'
    
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
    frame_test = tk.LabelFrame(root, text=" 🧪 특정 매물번호 단독 테스트 (선택사항) ", font=("Malgun Gothic", 10, "bold"), padx=10, pady=8, fg="#ba264a")
    frame_test.pack(padx=20, pady=5, fill="x")
    
    # 🎯 [명찰 교정] 당근 고유 번호 대신 평소 관리하시던 새홈 매물번호를 입력받도록 텍스트 명찰을 전격 교체합니다.
    tk.Label(frame_test, text="새홈 매물번호 입력:", font=("Malgun Gothic", 10)).pack(side="left", padx=5)
    
    entry_test = tk.Entry(frame_test, width=15, font=("Malgun Gothic", 10, "bold"), justify="center", fg="blue")
    entry_test.pack(side="left", padx=5)
    entry_test.insert(0, init_test_code)

    result_settings = {}

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
        
        # 🎯 [영구 파일 마킹] 확인 클릭 시 새홈 번호 공백을 제거하여 변수에 담고, 로컬 메모장 파일에도 즉시 세이브 보관합니다.
        테스트_입력값 = entry_test.get().strip()
        result_settings['test_code'] = 테스트_입력값
        try:
            with open("test_memo.txt", "w", encoding="utf-8") as 파일조수:
                파일조수.write(테스트_입력값)
        except: pass
        
        root.destroy()

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=15)
    tk.Button(btn_frame, text="확 인", font=("Malgun Gothic", 10, "bold"), bg="#2196F3", fg="white", padx=25, pady=5, command=on_ok).pack(side="left", padx=20)
    tk.Button(btn_frame, text="취 소", font=("Malgun Gothic", 10), bg="#9E9E9E", fg="white", padx=25, pady=5, command=lambda: sys.exit()).pack(side="right", padx=20)

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

    # 🔥 [클리닝 패치] 사용자가 체크박스에서 활성화한 플랫폼의 로우(Row)만 프리뷰 표에 인서트합니다!
    if user_settings['obang']:
        tree.insert("", "end", values=("오방부동산", len(data.get('신규등록매물', [])), len(data.get('금일등록매물', [])), data.get('미등록의뢰수', 0), len(data.get('업데이트매물_관심', [])), len(data.get('업데이트매물_일반', [])), len(data.get('거래완료매물', []))))
        
    if user_settings['carrot']:
        tree.insert("", "end", values=("당근부동산", data.get('당근_신규등록', 0), data.get('당근_금일등록', 0), 0, 0, data.get('당근_일반수정', 0), data.get('당근_거래완료', 0)))

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

def obang_data(before_day, 오방_선택=True, 당근_선택=True):
    """ 기존 DB 로직에 당근 데이터 매핑 연동을 결합한 데이터 수집 함수 """
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
    c_query = f'SELECT object_code_new, ad_code FROM pr_externalad WHERE ad_site = "당근" AND ad_del = "N" AND CURRENT_DATE >= DATE_ADD(ad_start, INTERVAL 14 DAY)'
    # c_query = f'SELECT object_code_new, ad_code FROM pr_externalad WHERE ad_site = "당근" AND ad_del = "N" AND object_code_new = "252477"'
    cursor.execute(c_query)
    
    # 🔥 [DB 실시간 가로채기] 당근 만료 광고 테이블 원본 데이터 출력
    당근_광고_원본목록 = cursor.fetchall()

    for c_row in 당근_광고_원본목록:
        if c_row['object_code_new']: carrot_map[c_row['object_code_new']] = str(c_row['ad_code'])

    query = '''SELECT DISTINCT p.request_code, p.land_code, p.building_code, p.room_code FROM pr_request_give AS p
            LEFT JOIN pr_request_fix AS c ON p.request_code = c.request_code WHERE c.fix_del="N"'''
    cursor.execute(query)
    f_res = cursor.fetchall()
    f_codes_arr = []
    for row in f_res:
        o_query = 'SELECT land_code,building_code,room_code,object_code_obang FROM pr_object WHERE object_status="중개요청" AND object_del="N" AND land_code = %s AND building_code = %s AND room_code = %s'
        cursor.execute(o_query, (row['land_code'], row['building_code'], row['room_code']))
        o_res = cursor.fetchall()
        try:
            if o_res and o_res[0]['object_code_obang'] != '': obang_update.append(str(o_res[0]['object_code_obang'])) 
            f_codes_arr.append(row['request_code'])
        except: pass

    f_codes = "','".join(f_codes_arr) if len(f_codes_arr) > 0 else ''
    f_codes = f"'{f_codes}'"

    query = f'''SELECT p.request_code, p.tr_target, p.object_type1, p.object_type2, p.admin_name, p.request_date, p.request_udate, p.request_wdate,
        c.land_code, c.building_code, c.room_code, c.request_trading, c.request_deposit1, c.request_deposit2, c.request_deposit3,
        c.request_rent1, c.request_rent2, c.request_rent3, c.request_manager, c.request_mmoney, c.request_mlist, c.tr_memo,
        c.request_area1, c.request_area2, c.request_areatype1, c.request_areatype2, c.first_trade 
        FROM pr_request AS p LEFT JOIN pr_request_give AS c ON p.request_code = c.request_code
        WHERE p.request_del="N" AND (p.request_date BETWEEN "{start_date_str}" AND "{today_str}" OR p.request_code IN ({f_codes}))
        AND p.request_main != "전체" AND p.tr_type = "내놓기" AND (p.request_status = "접수" OR p.request_status = "진행")
        AND (c.request_deposit1 != "" OR c.request_rent1 != "")'''
    cursor.execute(query)
    recently_res = cursor.fetchall()

    # 1️⃣ 무조건 다 찍던 구형 코드는 삭제하고, 안내 헤더만 담백하게 남깁니다.
    print(f"\n[🔎 DB 실시간 로딩] 의뢰 데이터 수집 완료 (총 {len(recently_res)}건 중 매칭 시작)")
    print("-" * 80)

    for row in recently_res:
        if not row['land_code']: continue
        o_query = '''SELECT o.object_code_new, o.land_code, o.building_code, o.room_code, o.object_code_obang, o.object_type, o.object_ttype, o.object_rtype, o.object_del, o.object_ori_img,
            l.land_do, l.land_si, l.land_dong, l.land_li, l.land_main, l.land_jibun, l.land_jibung, l.land_address, l.land_totarea, l.land_important, l.land_option, l.land_memo, l.representing_jibun, l.representing_jimok, l.representing_purpose,
            b.building_name, b.building_del, b.building_gate1, b.building_gate2, b.building_parking, b.building_pn, b.building_direction, b.building_bolt, b.building_height, b.building_element, b.building_memo, b.building_important, b.building_option, b.building_purpose, b.building_grndflr, b.building_ugrndflr, b.building_archarea, b.building_totarea, b.building_usedate, b.building_stract, b.building_elvcount,
            r.room_num, r.room_floor, r.room_status, r.room_nmemo, r.room_gate1, r.room_gate2, r.room_memo, r.room_rcount, r.room_bcount, r.r_direction, r.room_direction, r.room_area1, r.room_areatype1, r.room_area2, r.room_areatype2, r.room_important, r.room_option, r.room_purpose
            FROM pr_object AS o
            LEFT JOIN pr_land     AS l ON l.land_code     = o.land_code     AND l.land_del = 'N'
            LEFT JOIN pr_building AS b ON b.building_code = o.building_code AND b.building_del = 'N'
            LEFT JOIN pr_room     AS r ON r.room_code     = o.room_code     AND r.room_del = 'N'
            WHERE o.object_del = 'N' AND o.land_code = %s AND o.building_code = %s AND o.room_code = %s LIMIT 1;'''
        cursor.execute(o_query, (row['land_code'], row.get('building_code',''), row.get('room_code','')))
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
        if tr_target == '층호수' and row.get('room_code','') == '':
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

    # 거래완료매물 수집
    query = f"""SELECT o.object_code_obang, o.object_code_new FROM pr_request AS p
               JOIN pr_request_give AS c ON p.request_code = c.request_code
               JOIN pr_object AS o ON o.object_del = 'N' AND o.land_code = c.land_code AND o.building_code = c.building_code AND o.room_code = c.room_code
               WHERE p.request_del = 'N' AND p.request_main <> '전체' AND p.tr_type = '내놓기' AND p.request_status IN ('성공','실패')
                 AND p.request_date BETWEEN "{start_date_str}" AND "{today_str}" """
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

def run_platform_workers(obangData, target_mode, user_settings, progress_callback, unattended=False):
    """
    크롬 드라이버를 띄우고 오방/당근 워커를 순차 실행해 (성공/재등록/수정/비공개/건너뜀) 누적 카운트를 반환한다.
    사람이 클릭하며 지켜보는 GUI 대시보드(update_start)와, 사람 없이 도는 무인 모드(run_unattended)가
    "실제 업데이트를 수행하는" 이 부분만은 완전히 같은 코드를 타야 한다 — 여기서 갈라지면
    한쪽만 고치고 다른 쪽을 깜빡하는 사고로 이어지기 쉬워서, 진행상황 통지만 progress_callback으로
    분리하고 나머지 로직은 호출부(GUI/무인) 구분 없이 이 함수 하나로 통일했다.
    """
    counts = {'complete': 0, 'restart': 0, 'update': 0, 'end': 0, 'skip': 0}

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
            res = obang_worker.run()
            c_count, r_ok, u_ok, e_ok, s_ok = res if len(res) == 5 else (res[0], res[1], res[2], res[3], 0)
            counts['complete'] += c_count; counts['restart'] += r_ok; counts['update'] += u_ok; counts['end'] += e_ok; counts['skip'] += s_ok
            progress_callback('obang', 100, 100, f"✅ 오방 업데이트 완료 V \n(성공:{u_ok} , 재등록:{r_ok} , 비공개:{e_ok} , 건너뜀:{s_ok}개)", 'determinate')
        else:
            progress_callback('obang', 0, 100, "⏭️ 오방부동산 스킵됨", 'determinate')

        if user_settings['carrot']:
            carrot_worker = CarrotAutomationWorker(
                driver, obangData, target_mode,
                progress_callback=lambda c, t, txt, mode='determinate': progress_callback('carrot', c, t, txt, mode),
                unattended=unattended
            )
            cc, ro, uo, eo, so, ho = carrot_worker.run()
            counts['complete'] += cc; counts['restart'] += ro; counts['update'] += uo; counts['end'] += eo; counts['skip'] += so
            progress_callback(
                'carrot', 100, 100,
                f"✅ 당근 업데이트 완료 V \n(끌올 {ro + ho}건 [일반 {ro} / 숨김해제 {ho}] , 수정:{uo} , 비공개:{eo} , 건너뜀:{so}개)",
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
    global complete_count, restart_ok, update_ok, end_ok, skip_count
    print(f"업데이트 사이클 시작: {datetime.datetime.now()}")

    # 🎯 루프 밖에서 세팅 보관용 빈 메모리 박스를 먼저 비치해 둡니다.
    user_settings = None 
    
    # 🔥 [무한 루프 벨트 탑재] 사용자가 취소했을 때 설정창으로 부드럽게 되돌아가기 위한 가드 회로
    while True:
        # 🎯 위에서 보정 가공한 함수에 현재의 메모리팩을 밀어 넣어 복원을 지시합니다.
        user_settings = get_main_settings(user_settings)
        before_day = user_settings['before_day']
        target_mode = user_settings['mode']

        obangData = obang_data(before_day, user_settings['obang'], user_settings['carrot'])

        # =================================================================
        # 🎯 [지능형 진화] 새홈 번호 기반 단독 테스트 모드 가로채기 및 선로 자동 배정 엔진
        # =================================================================
        if user_settings.get('test_code'):
            새홈_타겟_번호 = user_settings['test_code']
            print(f"   [🧪 새홈 번호 기반 테스트 모드 가동 - {새홈_타겟_번호}] 당근 고유 광고번호(ad_code) 및 DB 매물 상태 실시간 판독을 시작합니다...")
            
            # 🔍 DB 교차 수사대 출동: 입력된 새홈 번호로 당근 광고번호(ad_code)와 새홈 원본 상태(object_status)를 동시에 포획합니다.
            당근_고유_번호 = ""
            DB_상태 = ""
            try:
                import pymysql
                연결고리 = pymysql.connect(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', database='obangkr', charset='utf8')
                명령조수 = 연결고리.cursor()
                역추적쿼리 = """
                    SELECT e.ad_code, o.object_status 
                    FROM pr_externalad AS e
                    JOIN pr_object AS o ON e.object_code_new = o.object_code_new
                    WHERE e.object_code_new = %s AND e.ad_site = '당근' AND e.ad_del = 'N' LIMIT 1
                """
                명령조수.execute(역추적쿼리, (새홈_타겟_번호,))
                결과행 = 명령조수.fetchone()
                if 결과행:
                    당근_고유_번호 = str(결과행[0])
                    DB_상태 = str(결과행[1])
                명령조수.close(); 연결고리.close()
            except Exception as e:
                print(f"   [❌ DB 역추적 실패] 통신 또는 쿼리 오류 발생: {e}")
                
            # 만약 DB에 매핑된 광고 데이터가 전혀 없다면 경고창을 발생시키고 다시 입력하도록 회항 조치합니다.
            if not 당근_고유_번호:
                messagebox.showwarning("역추적 실패", f"입력하신 새홈 매물번호 [{새홈_타겟_번호}]에 매핑된 활성화된 당근 광고 데이터가 DB에 존재하지 않습니다.")
                user_settings['test_code'] = ""
                continue
                
            print(f"   [🎯 역추적 및 상태판독 성공] 새홈번호 [{새홈_타겟_번호}] ➡️ 당근번호 [{당근_고유_번호}] | DB상태: [{DB_상태}]")
            
            # 타 플랫폼 및 노이즈 항목들은 100% 클리닝하여 연산을 통제합니다.
            obangData['당근_신규등록'] = 0
            obangData['당근_금일등록'] = 0
            obangData['금일등록매물'] = []
            obangData['신규등록매물'] = []
            obangData['업데이트매물'] = []
            obangData['업데이트매물_관심'] = []
            obangData['업데이트매물_일반'] = []
            obangData['거래완료매물'] = []

            # 🔄 [핵심 필터] 실시간 DB 원본 상태에 따른 지능형 선로 분기 가동
            if DB_상태 == "중개요청":
                print(f"   [🔄 선로 배정 완료] DB 상태가 '중개요청'이므로 [최신화 업데이트(끌올/수정)] 트랙에 주입합니다.")
                obangData['당근_업데이트목록'] = [당근_고유_번호]
                obangData['당근_일반수정'] = 1
                obangData['당근_거래완료목록'] = []
                obangData['당근_거래완료'] = 0
            else:
                # '거래완료', '보류' 등 이미 종결된 매물인 경우
                print(f"   [🔒 선로 배정 완료] DB 상태가 '{DB_상태}'(종결)이므로 [거래완료 비공개(숨기기)] 트랙에 전격 주입합니다.")
                obangData['당근_업데이트목록'] = []
                obangData['당근_일반수정'] = 0
                obangData['당근_거래완료목록'] = [당근_고유_번호]
                obangData['당근_거래완료'] = 1
        # =================================================================

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
        global complete_count, restart_ok, update_ok, end_ok, skip_count

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
        end_ok += counts['end']; skip_count += counts['skip']

        # 🏁 [마감 렌더링]: 일꾼들이 모두 퇴근한 자리에 최종 성공 안내문과 버튼들을 매끄럽게 그립니다.
        def finish_ui():
            lbl_finish = tk.Label(dash_win, text="🎉 모든 지정 플랫폼의 동기화 작업이 완료되었습니다!", font=("Malgun Gothic", 11, "bold"), fg="#28a745")
            lbl_finish.pack(pady=10)

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
        summary = (
            f"성공:{counts['update']} 재등록:{counts['restart']} "
            f"비공개:{counts['end']} 건너뜀:{counts['skip']}"
        )
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