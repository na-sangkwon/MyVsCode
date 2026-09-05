# fileName: util/property_utils.py
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import pymysql

def 로그저장(log_target, log_item, log_value, admin_id):
    """
    [소장님 설계 원칙 반영 - 범용 시스템 로그 적재 엔진]
    특정 플랫폼이나 비즈니스 로직에 절대 종속되지 않는 순수 유틸리티 함수입니다.
    log_target(client, request, object, system 등) 종류와 관계없이, 던져주는 값 그대로
    pr_log 테이블의 표준 6대 컬럼에 1:1 대입하여 영구 적재합니다.
    """
    # 호출된 시점의 날짜와 시간을 실시간으로 마스킹 수집
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")
    conn = None
    
    try:
        conn = pymysql.connect(
            host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', database='obangkr', charset='utf8'
        )
        cursor = conn.cursor()
        
        # 🎯 소장님 데이터베이스 pr_log 테이블의 표준 구조와 1:1 자석 매칭 쿼리
        insert_query = """
            INSERT INTO pr_log (
                log_target, log_item, log_value, admin_id, log_wdate, log_wtime
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, (
            str(log_target),     # 2. 출처 대상 (예: client, request, object, system 등)
            str(log_item),       # 3. 로그 대상 식별 ID/코드 (예: 매물 고유번호)
            str(log_value),      # 4. 저장할 순수 알맹이 기록 내용 (Text)
            str(admin_id),       # 5. 작업을 수행한 사용자 고유 ID
            current_date,        # 6. log_wdate (자동 생성 날짜)
            current_time         # 7. log_wtime (자동 생성 시간)
        ))
        
        conn.commit()
        print(f"   [💾 범용 로그 적재 완수] [{log_target} ➡️ {log_item}] 히스토리가 pr_log 테이블에 기록되었습니다.")
        return True
        
    except Exception as db_err:
        if conn:
            conn.rollback()
        print(f"   [❌ 범용 로그 적재 실패] 데이터베이스 쿼리 크래시 원인 ➡️ {db_err}")
        return False
        
    finally:
        if conn:
            conn.close()

def 최상단알림창(notice_text, title="알림"):
    """
    [소장님 기획 반영] 크롬 뒤로 숨지 않는 최상단 강제고정형 일반 안내창입니다.
    터미널 콘솔창에 알림 문구를 동시에 출력해 주는 편의 기능이 내장되어 있습니다.
    """
    print(f"\nℹ️  [시스템 알림] {notice_text}\n")
    
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)   # 🚀 최상단 레이어 강제 고정
    messagebox.showinfo(title, notice_text)
    root.destroy()                      # 메모리 청소
    return True

def 최상단에러창(error_text, title="🚨 에러 발생"):
    """
    [소장님 기획 반영] 매크로 구동 중 치명적 예외/오류 발생 시 작동하는 강제 고정 경고창입니다.
    터미널 콘솔창에 빨간 엑스박스 표식과 함께 에러 원인을 동시 리포팅합니다.
    """
    print(f"\n❌ [시스템 에러] {error_text}\n")
    
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        messagebox.showerror(title, error_text)
        root.destroy()
    except:
        # 시스템 GUI 환경 크래시 발생을 대비한 2중 백업 가드레일 기동
        import pyautogui
        pyautogui.alert(text=error_text, title=title)
    return False

def 최상단_예아니오_창(question_text, title="확인"):
    """
    [소장님 천재적 기획 반영] 질문 문구만 매개변수로 던져주면 크롬 뒤로 숨지 않는 
    최상단 예/아니오 창을 띄우고, 사용자의 최종 선택 결과(True / False)를 반환하는 범용 헬퍼 함수
    """
    
    root = tk.Tk()
    root.withdraw()                     # 빈 주창 숨김
    root.attributes("-topmost", True)   # 🚀 화면 최상단 레이어 강제 고정
    
    # 사용자가 [예]를 누르면 True, [아니오]를 누르면 False가 담깁니다.
    result = messagebox.askyesno(title, question_text)
    
    root.destroy()                      # 메모리 청소 및 팝업 폐쇄
    return result

def 공용에러_실시간_더블리포터(error_title, error_message):
    """
    [신설] 에러 발생 시 콘솔창 출력과 최상단 강제 고정 팝업 알림을 동시에 수행하는 엔진
    """
    # 1. 콘솔창 에러 로그 출력
    print(f"\n❌ {error_message}\n")
    
    # 2. 윈도우 최상단 레이어 강제 고정 팝업 알림창 기동
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        messagebox.showerror(error_title, error_message)
        root.destroy()
    except:
        # 혹시 모를 GUI 크래시 발생 시 pyautogui로 2중 백업 방어
        import pyautogui
        pyautogui.alert(text=error_message, title=error_title)


def 건축법상건축물용도로변환(building_purpose, area_private, debug='false'):
    """
    대한민국 건축법 및 중개 실무 기준에 맞추어 대장상 건축물용도를 정제하는 공용 함수
    :param building_purpose: DB에서 가져온 대장상 용도 원본 (문자열)
    :param area_private: 매물의 전용면적 (숫자 또는 문자열)
    :param debug: 디버깅 로그 출력 여부 ('true' 또는 True 입력 시 터미널 관제 모드 가동)
    :return: 정제된 건축물용도 명칭 (매칭 실패 시 None 반환)
    """
    # 🚀 [치료 핵심] 문자열 'true', 'True' 및 순수 Boolean True까지 모두 안전하게 판독하는 스위치
    is_debug = (debug is True or str(debug).lower() == 'true')

    if is_debug:
        print(f"\n   [🔎 건축물용도변환 디버그 시작] 원본 용도문자: '{building_purpose}' | 입력 면적: '{area_private}'")

    if not building_purpose:
        if is_debug:
            print("   [⚠️ 디버그] 원본 건축물 용도 데이터가 비어있어 즉시 None을 반환하고 스킵합니다.")
        return None

    # 1. 전용면적 데이터를 연산 가능한 float 타입으로 안전하게 변환
    try:
        target_area = float(area_private) if area_private else 0.0
    except:
        target_area = 0.0

    if is_debug:
        print(f"   [🔎 디버그 - 1단계] 전용면적 연산용 float 변환 완료 ➡️ {target_area}㎡")

    # 2. 텍스트 정제 및 구분자 분리 (공백 제거 후 특수문자 및 괄호 기준으로 조각냄)
    raw_purpose = str(building_purpose).replace(" ", "")
    parts = re.split(r'[./,|+~()\s]', raw_purpose)
    parts = [p.strip() for p in parts if p.strip()]

    if is_debug:
        print(f"   [🔎 디버그 - 2단계] 공백 제거 및 특수문자 기준 토큰 분리 파싱 결과 ➡️ {parts}")

    mapped_purpose = None

    # 3. 🎯 [건축법 시행령 별표1 기준] 면적에 따라 법적 용도가 갈리는 핵심 키워드 선행 판별
    for part in parts:
        if "사무" in part or "오피스" in part:
            mapped_purpose = "업무시설" if target_area >= 500 else "제2종 근린생활시설"
            if is_debug:
                print(f"   [🎯 면적 분기 매칭 - 3단계] '사무/오피스' 계열 키워드 [{part}] 포획!")
                print(f"      👉 판정 근거: 현재 면적 {target_area}㎡ (500㎡ 미만이므로 [제2종 근린생활시설] 적용)")
            break
        elif "카페" in part or "커피" in part or "휴게" in part:
            mapped_purpose = "제2종 근린생활시설" if target_area >= 300 else "제1종 근린생활시설"
            if is_debug:
                print(f"   [🎯 면적 분기 매칭 - 3단계] '카페/커피/휴게' 계열 키워드 [{part}] 포획!")
                print(f"      👉 판정 근거: 현재 면적 {target_area}㎡ ({'300㎡ 이상이므로 [제2종]' if target_area >= 300 else '300㎡ 미만이므로 [제1종]'} 근린생활시설 적용)")
            break

    # 4. 1:N 마스터 매핑 사전 구동 (기존 네이버/당근 사전의 키워드를 완벽하게 통합)
    if not mapped_purpose:
        if is_debug:
            print("   [🔎 디버그] 3단계 면적 우선순위 조건 통과 ➡️ 4단계 마스터 매핑 사전 전수 스캔 시동")
            
        keyword_mapping = {
            "제1종 근린생활시설": ["소매", "마트", "근린", "의원", "미용", "소형매장", "근린생활시설", "소매점", "제1종근린생활시설"],
            "제2종 근린생활시설": ["식당", "음식", "일반음식", "주점", "학원", "체육", "독서실", "제2종근린생활시설"],
            "판매시설": ["판매", "백화점", "쇼핑", "아울렛"],
            "공장": ["제조", "공장", "작업장", "정비공장", "제조업소"],
            "창고시설": ["창고", "물류", "보관소"],
            "공동주택": ["아파트", "빌라", "다세대", "연립", "다세대주택", "공동주택"],
            "단독주택": ["단독", "다가구", "전원주택", "다가구주택", "단독주택외"],
            "노유자(老幼者: 노인 및 어린이)시설": ["노유자", "노유자시설"],
            "위락시설": ["위락", "여관"],
            "교정(矯正) 및 군사 시설": ["교정", "군사", "교정군사시설"],
            "자동차 관련 시설": ["자동차", "자동차관련시설"],
        }
        
        for part in parts:
            for target_name, keywords in keyword_mapping.items():
                if any(kw in part for kw in keywords):
                    mapped_purpose = target_name
                    if is_debug:
                        print(f"   [✅ 사전 매핑 성공 - 4단계] 단어 [{part}] 내 키워드 매칭 성공 ➡️ 최종 용도: [{mapped_purpose}]")
                    break
            if mapped_purpose:
                break

    if is_debug:
        final_display = f"[{mapped_purpose}]" if mapped_purpose else "None (매칭 실패)"
        print(f"   [🏁 용도변환 디버그 종료] 변환 필터 파이프라인 최종 출력값 ➡️ {final_display}\n")

    return mapped_purpose

def 만원단위숫자금액을한글금액으로(amount_man):

    if amount_man is None or str(amount_man).strip() in ["", "0", "None"]:
        return ""

    try:
        val = int(re.sub(r'\D', '', str(amount_man)))
    except:
        return str(amount_man)

    if val == 0:
        return "0"

    eok = val // 10000
    man = val % 10000

    result = ""

    if eok > 0:
        result += f"{eok}억"

    if man > 0:
        result += f"{man}만"

    return result


def 확인창클릭(driver, 선택='확인', timeout=3, unattended=False):
    """
    브라우저 자바스크립트 기본 confirm 창 및 HTML 기반 크롬 커스텀 레이어 확인창을 교차 탐색하여 제어하는 범용 함수
    :param driver: Selenium WebDriver 객체
    :param 선택: '확인' 또는 '취소' (기본값 '확인')
    :param timeout: 동적 타겟 검속 제한 시간 (초)
    :param unattended: 나스 무인 실행 등 사람이 없는 경우 True — 실패 시 최상단알림창(사람 클릭 대기)
        대신 콘솔 로그로만 남기고 넘어간다. 기존 호출부(다른 프로젝트 포함)는 인자를 안 넘기면
        기존과 동일하게 동작한다.
    :return: 처리 성공 여부 (True / False)
    """
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    import time

    # 1단계 대책: 브라우저 원초적 크롬 시스템 Alert/Confirm 팝업창 체크
    try:
        시스템_알림창 = WebDriverWait(driver, 1.2).until(EC.alert_is_present())
        알림_텍스트 = 시스템_알림창.text.replace('\n', ' ')
        if 선택 == '확인':
            시스템_알림창.accept()
        else:
            시스템_알림창.dismiss()
        print(f"   [⚙️ 공용 유틸] 크롬 시스템 기본 확인창 탐지 성공 ➡️ [{선택}] 제어 완료 (문구: {알림_텍스트[:20]}...)")
        return True
    except:
        pass # 자바스크립트 Alert창이 아니라면 웹 페이지 커스텀 모달창 감시 모드로 바통 터치

    # 2단계 대책: 리액트 돔(DOM) 기반 커스텀 다이얼로그 레이어 모달창 저격
    try:
        # 사장님의 확장성을 고려해 '확인', '예', '동의', '끌어올리기' 등 범용 글자 매칭 구조 설계
        if 선택 == '확인':
            타겟_XPATH = "//div[@role='dialog' or @class='z-modal']//button[text()='확인' or text()='예' or text()='동의' or contains(., '확인')]"
        else:
            타겟_XPATH = "//div[@role='dialog' or @class='z-modal']//button[text()='취소' or text()='아니오' or text()='닫기' or contains(., '취소')]"
            
        버튼_요소 = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, 타겟_XPATH))
        )
        
        # 일반 click()은 간혹 포커스 미스로 씹힐 수 있어 자바스크립트 직통 주입 클릭으로 확실하게 격파합니다.
        driver.execute_script("arguments[0].click();", 버튼_요소)
        print(f"   [⚙️ 공용 유틸] 웹 화면 커스텀 팝업 모달 상자 탐지 성공 ➡️ [{선택}] 버튼 강제 클릭 완수")
        time.sleep(0.5)
        return True
        
    except Exception as 오류:
        print(f"   [❌ 공용 유틸 에러] 최종 확인창 [{선택}] 제어 단추를 화면에서 찾지 못했습니다.")
        print(f"원인: {오류}")
        if not unattended:
            최상단알림창("292")
        return False
    







#당근전용유틸
def 당근매물번호_검색창_입력(driver, 매물번호):
    """
    당근마켓 메인 대시보드 화면에서 검색창에 매물번호를 정밀 입력하고 필터링하는 공용 함수
    """
    try:
        검색창_xpath = "//form//input[contains(@placeholder, '지번')]"
        검색창 = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, 검색창_xpath))
        )
        검색창.click()
        검색창.send_keys(Keys.CONTROL + "a")
        검색창.send_keys(Keys.BACKSPACE)
        time.sleep(0.3)
        
        # 실시간 돔 반영을 위해 엔터 없이 값만 주입
        검색창.send_keys(str(매물번호))
        print(f"   [⚙️ 공용 유틸] 당근 검색창에 번호 [{매물번호}] 입력 및 필터링 완료")
        time.sleep(2.0) # 리스트 갱신 안정화 대기
        return True
    except Exception as 오류:
        print(f"   [❌ 공용 유틸 에러] 당근 검색창 제어 실패 -> 원인: {오류}")
        return False
    
def 검색결과_목록개수_확인(driver):
    """
    현재 당근마켓 화면에 노출된 검색 결과 매물 행(Row)의 총 개수를 반환하는 공용 함수
    """
    try:
        # 당근 대시보드 리스트의 카드 행(Row) 고유 셀렉터 추적
        item_elements = driver.find_elements(By.CSS_SELECTOR, "div.flex.w-full.cursor-pointer.items-center.border-b")
        return len(item_elements)
    except Exception as e:
        print(f"   [❌ 공용 유틸 에러] 목록 개수 확인 중 예외 발생: {e}")
        return 0

def 리액트_입력창_값_강제주입(driver, element, text):
    """
    [소장님 피드백 반영 - 하이브리드 열쇠 매칭 버전]
    리액트 가상돔(State)의 압착을 무력화하고 input/textarea 값을 완벽하게 동기화 주입하는 공용 함수
    """
    try:
        react_script = """
        var el = arguments[0];
        var txt = arguments[1];
        
        // 🚀 [치료 핵심] 타겟 요소의 태그 이름이 TEXTAREA인지 INPUT인지 명확히 판별하여 알맞은 프로토타입 열쇠를 장착합니다.
        var targetPrototype = el.nodeName.toUpperCase() === 'TEXTAREA' 
            ? window.HTMLTextAreaElement.prototype 
            : window.HTMLInputElement.prototype;
            
        var valueSetter = Object.getOwnPropertyDescriptor(targetPrototype, "value").set;
        valueSetter.call(el, txt);
        
        // 리액트 가상 메모리에 입력 신호를 동기화시키는 동적 이벤트 발송
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
        """
        driver.execute_script(react_script, element, str(text))
        return True
    except Exception as e:
        print(f"   [❌ 공용 유틸 에러] 리액트 강제 주입 실패 -> {e}")
        return False


def 당근_매물상태_확인(row_element):
    """
    당근마켓 매물 목록의 단일 행(Row) 객체에서 현재 표시 상태값('숨김', '판매중', '미노출' 등)을 수집
    """
    try:
        status_el = row_element.find_element(By.CSS_SELECTOR, "div[class*='w-[82px]'] span")
        return status_el.text.strip()
    except:
        return ""


def 당근_날짜및_끌어올리기_가능여부_확인(row_element):
    """
    당근마켓 매물 목록의 단일 행(Row) 객체에서 등록 날짜 텍스트와 [끌어올리기] 버튼 활성화 여부를 판별
    """
    try:
        date_col_el = row_element.find_element(By.CSS_SELECTOR, "div[class*='w-[100px]']")
        full_text = date_col_el.text.strip()
        date_text = full_text.split('\n')[0] if '\n' in full_text else full_text
        
        up_buttons = date_col_el.find_elements(By.XPATH, ".//button[text()='끌어올리기']")
        can_up = len(up_buttons) > 0
        return date_text, can_up
    except:
        return "", False    
    
# fileName: util/property_utils.py

def 텍스트창_값검속_및_신규업데이트판정(driver, field_name, db_value, label, xpath_target=None):
    """
    일반 입력창(input) 및 상세설명(textarea)의 현재 화면 값을 스캔 및 동기화 (에러 더블 리포팅 탑재)
    """
    result_log = {"status": "유지(패스)", "before": "", "after": str(db_value).strip()}
    try:
        if xpath_target:
            element = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, xpath_target)))
        else:
            element = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.NAME, field_name)))
            
        current_ui_value = str(element.get_attribute("value")).strip()
        current_ui_value = "" if current_ui_value in ["None", "null"] else current_ui_value
        result_log["before"] = current_ui_value

        if not db_value or str(db_value).strip() in ["", "None", "0"]:
            return result_log

        if current_ui_value == str(db_value).strip():
            return result_log
            
        if current_ui_value == "":
            result_log["status"] = "신규입력"
        else:
            result_log["status"] = "업데이트"

        리액트_입력창_값_강제주입(driver, element, db_value)
        print(f"   [⚙️ 공용 검속 - {label}] 판정: [{result_log['status']}] | '{current_ui_value}' ➡️ '{db_value}'")
        
    except Exception as error_msg:
        result_log["status"] = "실패"
        summary_msg = f"[텍스트 입력창 제어 에러 - {label}]\n\n화면에서 요소를 찾지 못했거나 주입에 실패했습니다.\n\n해당 필드명: {field_name}\n원인: {error_msg}"
        최상단에러창(summary_msg, "🚨 공용 유틸리티 에러 알림")
        
    return result_log


def 체크박스_상태검속_및_신규업데이트판정(driver, xpath_target, target_state, label):
    """
    다중 선택 체크박스의 현재 선택 여부를 스캔 및 제어 (에러 더블 리포팅 탑재)
    """
    result_log = {"status": "유지(패스)", "before": "미체크", "after": "체크" if target_state else "미체크"}
    try:
        checkbox_label = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, xpath_target)))
        is_checked = checkbox_label.get_attribute("data-checked") is not None
        result_log["before"] = "체크" if is_checked else "미체크"

        if is_checked == target_state:
            return result_log

        if not is_checked and target_state:
            result_log["status"] = "신규입력"
            driver.execute_script("arguments[0].click();", checkbox_label)
        elif is_checked and not target_state:
            result_log["status"] = "업데이트"
            driver.execute_script("arguments[0].click();", checkbox_label)

        print(f"   [⚙️ 공용 검속 - {label}] 판정: [{result_log['status']}] | '{result_log['before']}' ➡️ '{result_log['after']}'")
        time.sleep(0.1)
        
    except Exception as error_msg:
        result_log["status"] = "실패"
        summary_msg = f"[체크박스 제어 에러 - {label}]\n\n지정된 체크박스를 UI 화면에서 조작할 수 없습니다.\n\n타겟 XPATH: {xpath_target}\n원인: {error_msg}"
        최상단에러창(summary_msg, "🚨 공용 유틸리티 에러 알림")
        
    return result_log


def 라디오버튼_선택검속_및_신규업데이트판정(driver, base_xpath_container, target_option_text, label):
    """
    단일 선택 라디오 그룹(부과방식, 주차 등) 내 활성화 명찰을 스캔하여 
    목표 명찰과 비교 후 [신규입력/업데이트/유지] 상태를 판정하고 강제 클릭 전환합니다. (태그 무관형 업그레이드)
    """
    result_log = {"status": "유지(패스)", "before": "미선택", "after": target_option_text}
    try:
        # 🚀 [치료 1] span에 의존하지 않고 data-checked 속성을 가진 라벨 단추 자체를 조준하여 현재 UI 선택값 수집
        active_xpath = f"{base_xpath_container}//label[@data-checked or @aria-checked='true' or contains(@class, 'checked') or contains(@class, 'active')]"
        active_elements = driver.find_elements(By.XPATH, active_xpath)
        
        current_ui_text = active_elements[0].text.strip() if active_elements else ""
        result_log["before"] = current_ui_text if current_ui_text else "미선택"

        # 이미 화면 선택값과 DB 목표값이 같다면 불필요한 클릭 연산 없이 프리패스 자석 방어
        if current_ui_text == target_option_text:
            return result_log

        if current_ui_text == "" or current_ui_text == "미선택":
            result_log["status"] = "신규입력"
        else:
            result_log["status"] = "업데이트"

        # 🚀 [치료 2] span 태그 유무와 상관없이 목표 글자를 포함하는 label 또는 요소를 하이브리드로 정밀 타격합니다.
        target_button_xpath = f"{base_xpath_container}//label[contains(., '{target_option_text}')] | {base_xpath_container}//*[text()='{target_option_text}']"
        click_target = driver.find_element(By.XPATH, target_button_xpath)
        
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", click_target)
        time.sleep(0.1)
        driver.execute_script("arguments[0].click();", click_target)
        
        print(f"   [⚙️ 공용 검속 - {label}] 판정: [{result_log['status']}] | '{result_log['before']}' ➡️ '{target_option_text}'")
        time.sleep(0.1)

    except Exception as error_msg:
        result_log["status"] = "실패"
        summary_msg = f"[라디오 버튼 제어 에러 - {label}]\n\n선택하려는 옵션 명찰 단추를 타격하지 못했습니다.\n\n목표 옵션명: {target_option_text}\n원인: {error_msg}"
        최상단에러창(summary_msg, "🚨 공용 유틸리티 에러 알림")
        
    return result_log


def 드롭다운_선택검속_및_신규업데이트판정(driver, trigger_name, target_text, label, current_value_xpath=None):
    """
    선택 드롭다운 메뉴 겉면 단어 스캔 및 목록 매칭 전환 (에러 더블 리포팅 탑재)
    """
    result_log = {"status": "유지(패스)", "before": "", "after": target_text}
    try:
        if not current_value_xpath:
            current_value_xpath = f"//button[@name='{trigger_name}']/following-sibling::div"
            
        value_element = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, current_value_xpath)))
        current_ui_text = value_element.text.strip()
        result_log["before"] = current_ui_text

        if current_ui_text == target_text:
            return result_log

        if current_ui_text in ["", "선택", "선택하세요"]:
            result_log["status"] = "신규입력"
        else:
            result_log["status"] = "업데이트"

        trigger_button = driver.find_element(By.NAME, trigger_name)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", trigger_button)
        driver.execute_script("arguments[0].click();", trigger_button)
        time.sleep(0.3)

        clean_target = target_text.replace(" ", "")
        option_xpath = f"//div[@role='listbox' or @role='dialog' or contains(@class, 'popover')]//button[contains(., '{target_text}')] | //button[translate(text(), ' ', '')='{clean_target}' and not(@name='{trigger_name}')]"
        
        option_button = driver.find_element(By.XPATH, option_xpath)
        driver.execute_script("arguments[0].click();", option_button)
        
        print(f"   [⚙️ 공용 검속 - {label}] 판정: [{result_log['status']}] | '{current_ui_text}' ➡️ '{target_text}'")
        time.sleep(0.2)

    except Exception as error_msg:
        result_log["status"] = "실패"
        summary_msg = f"[드롭다운 드래그 제어 에러 - {label}]\n\n메뉴 목록을 열거나 내부 항목을 매칭하는 데 실패했습니다.\n\n드롭다운 이름: {trigger_name} ➡️ 목표: {target_text}\n원인: {error_msg}"
        최상단에러창(summary_msg, "🚨 공용 유틸리티 에러 알림")
        
    return result_log


def 제목기준_다중체크박스_통합검속엔진(driver, section_title, target_options):
    """
    [소장님 피드백 반영 - 가로 행 전체 스캔 업그레이드 버전]
    대제목 명찰을 찾은 후, 좁은 타이틀 div wrapper를 건너뛰고 
    우측 체크박스들까지 완벽히 포함하는 행(Row) 컨테이너를 타겟팅하여 실시간 스캔 및 조작을 완수합니다.
    """
    result_log = {"status": "유지(패스)", "before": "", "after": ""}
    try:
        # 1. 🎯 [정공법] 대제목 텍스트 요소를 명중 타격
        title_xpath = f"//*[text()='{section_title}' or contains(text(), '{section_title}')]"
        title_element = WebDriverWait(driver, 4).until(
            EC.presence_of_element_located((By.XPATH, title_xpath))
        )
        
        # 화면 중앙으로 스크롤하여 동적 컴포넌트 렌더링 강제 활성화
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", title_element)
        time.sleep(0.4)
        
        # 2. 🚀 [치료 핵심] w-[110px] 미니 상자에 갇히지 않도록 items-start 또는 flex-col을 가진 행 전체 컨테이너 div로 역추적 확장
        container_xpath = "./ancestor::div[contains(@class, 'items-start') or contains(@class, 'flex-col') or contains(@class, 'max-w-')][1]"
        container_element = title_element.find_element(By.XPATH, container_xpath)
        
        print(f"   [⚙️ 공용 엔진 - {section_title}] 행 전체 레이아웃 포커싱 성공 ➡️ 실시간 수집 가동")
        
        # 3. 행 내부 전체 공간에서 활성화된 체크박스/라디오 명찰 요소 전수 수집
        label_elements = container_element.find_elements(
            By.XPATH, 
            ".//span[contains(@class, 'seed-checkbox__label') or contains(@class, 'seed-radio__label') or contains(@class, 'label')]"
        )
        
        discovered_options = []
        before_list = []
        after_list = []
        
        for element in label_elements:
            option_name = element.text.strip()
            if not option_name:
                continue
            if option_name not in discovered_options:
                discovered_options.append(option_name)
            
            checkbox_label = element.find_element(By.XPATH, "./parent::label")
            is_checked = checkbox_label.get_attribute("data-checked") is not None
            if is_checked:
                before_list.append(option_name)
        
        if isinstance(target_options, str):
            clean_targets = [t.strip() for t in target_options.split(',') if t.strip()]
        else:
            clean_targets = [str(t).strip() for t in target_options]

        for option_name in discovered_options:
            should_be_checked = option_name in clean_targets
            if should_be_checked:
                after_list.append(option_name)
            
            try:
                checkbox_label = container_element.find_element(By.XPATH, f".//span[text()='{option_name}']/parent::label")
                is_currently_checked = checkbox_label.get_attribute("data-checked") is not None
                
                if is_currently_checked != should_be_checked:
                    driver.execute_script("arguments[0].click();", checkbox_label)
                    time.sleep(0.05)
            except:
                pass

        before_str = ", ".join(sorted(before_list))
        after_str = ", ".join(sorted(after_list))
        
        result_log["before"] = before_str
        result_log["after"] = after_str
        
        if before_str == after_str:
            result_log["status"] = "유지(패스)"
        elif before_str == "":
            result_log["status"] = "신규입력"
        else:
            result_log["status"] = "업데이트"
            
        print(f"   [⚙️ 공용 엔진 - {section_title}] 스캔 완료 ➡️ [{result_log['status']}] '{before_str}' ➡️ '{after_str}'")
        
    except Exception as error_msg:
        result_log["status"] = "실패"
        summary_msg = f"[만능 다중 체크박스 엔진 에러]\n\n대제목 부모 상자 탐색 및 실시간 스크래핑 무너짐.\n\n요청 대제목: {section_title}\n원인: {error_msg}"
        최상단에러창(summary_msg, "🚨 공용 유틸리티 에러 알림")
        
    return result_log

def 텍스트기준_버튼_클릭(driver, button_text, timeout=5):
    """
    [소장님 천재적 기획 반영] 화면에 보이는 버튼의 글자 이름(명찰)만 넘겨주면
    태그 종류에 상관없이 찾아내어 중앙 스크롤 및 자바스크립트 강제 클릭을 수행하는 만능 엔진
    """
    try:
        # 하이브리드 그물망 XPath (정통 button 태그뿐만 아니라, 버튼 역할을 수행하는 div/span/a 태그까지 일괄 포획)
        button_xpath = f"//button[text()='{button_text}' or contains(., '{button_text}')] | //*[(@role='button' or contains(@class, 'button') or contains(@class, 'btn')) and (text()='{button_text}' or contains(., '{button_text}'))]"
        
        button_element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, button_xpath))
        )
        
        # 화면 가려짐 에러 방지를 위해 뷰포트 중앙 정렬 스크롤
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button_element)
        time.sleep(0.2)
        
        # 물리 클릭 씹힘 현상을 원천 차단하는 JS 강제 타격 클릭
        driver.execute_script("arguments[0].click();", button_element)
        print(f"   [⚙️ 공용 버튼엔진] 명찰 [{button_text}] 단추 타격 성공!")
        return True
    except Exception as error_msg:
        print(f"   [❌ 공용 버튼엔진 에러] [{button_text}] 단추를 화면에서 찾지 못했거나 클릭에 실패했습니다. -> {error_msg}")
        return False
    
def 당근_팝업창_가격_동기화_처리_엔진(driver, popup_element, ad_code, price_specs):
    """
    [소장님 원본 디버깅로그 100% 복원 버전]
    팝업창 내부의 카드들을 DB 가격 명세 스펙에 맞춰 실시간으로 신설/수정/소거하고
    변동 여부 데이터 리포트 및 소장님 원본 디버그 출력을 완벽히 수행합니다.
    """
    db_required_types = [x['종류'] for x in price_specs]
    completed_target_types = set()
    is_price_changed = False
    change_report_list = []

    # 🔄 [1단계]: 기존 카드 재사용 및 실시간 금액 최신화 (덮어쓰기)
    current_popup_cards = popup_element.find_elements(By.XPATH, ".//span[contains(@class, 't5-bold')]/ancestor::div[contains(@class, 'rounded-r3')]")
    print(f"   [🔎 1단계: 기존카드 검속 - {ad_code}] 팝업창 내 기존 생성 카드 {len(current_popup_cards)}개 감지")
    
    for card in current_popup_cards:
        card_text = card.find_element(By.XPATH, ".//span[contains(@class, 't5-bold')]").get_attribute("textContent").strip()
        clean_type = "월세" if "월세" in card_text else "전세" if "전세" in card_text else "매매" if "매매" in card_text else "단기" if "단기" in card_text else ""
        
        if clean_type in db_required_types:
            db_item = next(x for x in price_specs if x['종류'] == clean_type)
            card_value_updated = False
            
            if clean_type in ["월세", "단기"]:
                ui_deposit = card.find_element(By.NAME, "deposit").get_attribute("value")
                ui_rent = card.find_element(By.NAME, "monthlyPay").get_attribute("value")
                if ui_deposit != str(db_item["보증금"]) or ui_rent != str(db_item["월세"]):
                    change_report_list.append(f" 🔄 [{clean_type} 수정] 기존: {ui_deposit}/{ui_rent} ➡️ 완료: {db_item['보증금']}/{db_item['월세']}")
                    리액트_입력창_값_강제주입(driver, card.find_element(By.NAME, "deposit"), str(db_item["보증금"]))
                    리액트_입력창_값_강제주입(driver, card.find_element(By.NAME, "monthlyPay"), str(db_item["월세"]))
                    card_value_updated = True
                    
            elif clean_type == "전세":
                ui_deposit = card.find_element(By.NAME, "deposit").get_attribute("value")
                if ui_deposit != str(db_item["보증금"]):
                    change_report_list.append(f" 🔄 [{clean_type} 수정] 기존: {ui_deposit} ➡️ 완료: {db_item['보증금']}")
                    리액트_입력창_값_강제주입(driver, card.find_element(By.NAME, "deposit"), str(db_item["보증금"]))
                    card_value_updated = True
                    
            elif clean_type == "매매":
                try: price_input = card.find_element(By.NAME, "price")
                except: price_input = card.find_element(By.XPATH, ".//input[@type='number']")
                ui_trade_price = price_input.get_attribute("value")
                if ui_trade_price != str(db_item["매매가"]):
                    change_report_list.append(f" 🔄 [{clean_type} 수정] 기존: {ui_trade_price} ➡️ 완료: {db_item['매매가']}")
                    리액트_입력창_값_강제주입(driver, price_input, str(db_item["매매가"]))
                    card_value_updated = True
            
            if card_value_updated:
                print(f"   [✍️ 금액 업데이트 - {ad_code}] 구형 [{clean_type}] 카드 가격 변동 검지 ➡️ 최신 금액 덮어쓰기 완수")
                is_price_changed = True
            else:
                print(f"   [ 동결 - {ad_code}] 구형 [{clean_type}] 카드 데이터 완전 일치 ➡️ 수정 스킵")
                
            completed_target_types.add(clean_type)

    # ➕ [2단계]: 누락된 거래 종류 스마트 신설 (정밀 추적 트랩 탑재)
    for db_item in price_specs:
        target_type = db_item["종류"]
        if target_type in completed_target_types:
            continue

        check_cards = popup_element.find_elements(By.XPATH, ".//span[contains(@class, 't5-bold')]/ancestor::div[contains(@class, 'rounded-r3')]")
        
        if len(check_cards) == 0:
            print(f"   [➕ 방식 직통신설 - {ad_code}] 청정 공실 상태 확인 ➡️ 대형 직통 [{target_type}] 단추 직접 클릭")
            try:
                direct_btn = popup_element.find_element(By.XPATH, f".//div[contains(@class, 'gap-x2_5')]/button[text()='{target_type}']")
                driver.execute_script("arguments[0].click();", direct_btn)
                time.sleep(0.8)
            except Exception as e:
                print(f"   [❌ 단계 실패] 빈 화면 직통 [{target_type}] 단추를 클릭하지 못했습니다: {e}")
                raise e
        else:
            print(f"   [➕ 방식 레이어신설 - {ad_code}] 팝업창 내 [{target_type}] 누락 확인 ➡️ 다른 거래 방식 메뉴 가동")
            try:
                scroll_container = popup_element.find_element(By.XPATH, ".//div[contains(@class, 'overflow-y-auto')]")
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", scroll_container)
                time.sleep(0.5)
                
                add_btn = popup_element.find_element(By.XPATH, ".//span[contains(text(), '다른 거래 방식 추가')]/ancestor::button")
                dynamic_menu_id = add_btn.get_attribute("aria-controls")
                
                driver.implicitly_wait(0)
                dropdown_menus = driver.find_elements(By.XPATH, "//div[@role='menuitem'] | //div[contains(@class, 'menu')]//button")
                is_menu_visible = any(menu.is_displayed() for menu in dropdown_menus)
                driver.implicitly_wait(5)
                
                if not is_menu_visible:
                    print(f"   [🔎 디버그 - {ad_code}] 추가 메뉴가 물리적으로 열려있지 않으므로 무조건 클릭 탈환!")
                    try: add_btn.click()
                    except: driver.execute_script("arguments[0].click();", add_btn)
                    time.sleep(0.6)
                
                control_layer_id = dynamic_menu_id if dynamic_menu_id else "radix-_r_53_"
                option_xpath = f"//*[@id='{control_layer_id}']//*[contains(text(), '{target_type}')] | //div[@role='menuitem' and contains(., '{target_type}')] | //button[contains(., '{target_type}') and not(ancestor::div[@role='dialog'])]"
                option_target = WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.XPATH, option_xpath)))
                driver.execute_script("arguments[0].click();", option_target)
                time.sleep(0.8)
            except Exception as e:
                print(f"   [❌ 단계 실패] '다른 거래 방식 추가' 버튼 및 스크롤바 제어 실패: {e}")
                raise e
                
        new_target_card = popup_element.find_element(By.XPATH, f".//span[contains(@class, 't5-bold') and contains(text(), '{target_type}')]/ancestor::div[contains(@class, 'rounded-r3')]")
        if target_type in ["월세", "단기"]:
            리액트_입력창_값_강제주입(driver, new_target_card.find_element(By.NAME, "deposit"), str(db_item["보증금"]))
            리액트_입력창_값_강제주입(driver, new_target_card.find_element(By.NAME, "monthlyPay"), str(db_item["월세"]))
        elif target_type == "전세":
            리액트_입력창_값_강제주입(driver, new_target_card.find_element(By.NAME, "deposit"), str(db_item["보증금"]))
        elif target_type == "매매":
            try: price_input = new_target_card.find_element(By.NAME, "price")
            except: price_input = new_target_card.find_element(By.XPATH, ".//input[@type='number']")
            리액트_입력창_값_강제주입(driver, price_input, str(db_item["매매가"]))
            
        print(f"   [✍️ 금액 신설완료 - {ad_code}] 신설 배치된 [{target_type}] 카드에 타겟 금액 기입 완료")
        new_price_str = f"{db_item['보증금']}/{db_item['월세']}" if target_type in ["월세", "단기"] else f"{db_item['보증금']}" if target_type == "전세" else f"{db_item['매매가']}"
        change_report_list.append(f" ➕ [{target_type} 신설] ➡️ 입력금액: {new_price_str}")
        is_price_changed = True

    # 🗑️ [3단계]: DB 요구사항 스펙에 전혀 없는 껍데기 구형 카드 최종 철거
    while True:
        cleanup_cards = popup_element.find_elements(By.XPATH, ".//span[contains(@class, 't5-bold')]/ancestor::div[contains(@class, 'rounded-r3')]")
        is_deleted_this_turn = False
        
        for card in cleanup_cards:
            card_text = card.find_element(By.XPATH, ".//span[contains(@class, 't5-bold')]").get_attribute("textContent").strip()
            clean_type = "월세" if "월세" in card_text else "전세" if "전세" in card_text else "매매" if "매매" in card_text else "단기" if "단기" in card_text else ""
            
            if clean_type not in db_required_types:
                print(f"   [🗑️ 최종 소거 - {ad_code}] DB에 없는 불필요 카드 완전 박멸 ➡️ 유형:[{card_text}] 휴지통 격파")
                try: old_val = card.find_element(By.NAME, "price").get_attribute("value") if clean_type == "매매" else f"{card.find_element(By.NAME, 'deposit').get_attribute('value')}/{card.find_element(By.NAME, 'monthlyPay').get_attribute('value') if clean_type in ['월세','단기'] else ''}".rstrip('/')
                except: old_val = "확인불가"
                change_report_list.append(f" 🗑️ [{clean_type} 삭제] 기존에 적혀있던 금액: {old_val}")
                
                delete_btn = card.find_element(By.XPATH, ".//button[@aria-label='삭제']")
                driver.execute_script("arguments[0].click();", delete_btn)
                time.sleep(0.8)
                is_deleted_this_turn = True
                is_price_changed = True
                break
                
        if not is_deleted_this_turn:
            break

    return is_price_changed, change_report_list


# fileName: util/property_utils.py

def 당근_끌어올리기_마스터_통합엔진(driver, row_element, ad_code, current_status, price_specs, unattended=False, 끌올관측_수집함=None):
    """
    [소장님 지시 반영 - 숨김해제 독립 분리 버전]
    쿨타임 여부와 관계없이 원래 매물이 '숨김' 상태였다면 일반 끌올/수정과 철저히 분리된
    RESCUE_BUMP_SUCCESS 사인을 최종 반환하여 카운터 누수를 원천 봉쇄합니다.
    :param unattended: 나스 무인 실행 등 사람이 없는 경우 True — 내부에서 호출하는 확인창클릭이
        실패해도 사람 클릭을 기다리지 않고 로그만 남기도록 그대로 전달한다.
    :param 끌올관측_수집함: 팝업에서 읽은 관측값을 담아 호출자에게 돌려줄 dict(선택).
        [왜 반환값이 아니라 dict인가 — 2026-09-05]
        이 함수의 반환값(결과 코드 문자열)을 호출자들이 == 비교로 분기하고 있어, 반환 형태를 바꾸면
        호출자 두 곳(carrot_worker.py·daangn.py)이 모두 깨진다. 그래서 기존 반환은 그대로 두고,
        필요한 쪽만 이 dict를 건네받아 가져가는 방식으로 넓혔다. 안 건네면 아무 일도 일어나지 않는다.
        [무엇을 담나] 팝업 제목(당근이 알려주는 남은 쿨타임 원문)과 쿨타임 여부.
        '다음 끌올 가능 시각'을 우리가 상수로 추정하지 않고 당근이 준 값 그대로 쓰기 위한 것이다 —
        쿨타임은 고정값이 아니다(2026-09-05 실측 14일, 과거 5일이던 시기가 있었다는 사용자 확인).
    """
    try:
        # 1. 목록의 1차 끌어올리기 단추 타격
        print(f"   [🔎 디버그 - {ad_code}] 1단계: 목록의 [끌어올리기] 버튼 클릭 시도...")
        click_btn = WebDriverWait(row_element, 5).until(
            EC.visibility_of_element_located((By.XPATH, ".//button[text()='끌어올리기']"))
        )
        click_btn.click()
        
        # 2. 가격 조정 팝업창 출현 정밀 대기
        dialog_popup = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, "//div[@role='dialog' and @data-state='open']"))
        )
        print(f"   [✅ 팝업 확정 - {ad_code}] 실제 작동 팝업창 고유 ID ➡️ '{dialog_popup.get_attribute('id')}'")
        time.sleep(0.5)

        # 3. H2 제목 파싱 및 쿨타임 검지
        try:
            h2_element = dialog_popup.find_element(By.XPATH, ".//h2")
            title_text = h2_element.get_attribute("textContent").strip()
        except:
            title_text = ""
            
        print(f"   [🔎 팝업 제목 분석 - {ad_code}] ➡️ '{title_text}'")
        is_cooldown_active = "뒤에 끌어올릴 수 있어요" in title_text or "뒤에" in title_text

        # 관측값 전달 — 호출자가 이 순간의 쿨타임 원문을 기록해 시계열로 쌓는다(위 파라미터 설명 참고).
        # 지금까지 이 문구는 여기서 판정에만 쓰고 그대로 버려졌다.
        if 끌올관측_수집함 is not None:
            끌올관측_수집함['팝업제목'] = title_text
            끌올관측_수집함['쿨타임여부'] = is_cooldown_active

        if is_cooldown_active:
            print(f"   [⚠️ 쿨타임 제한 검지 - {ad_code}] 쿨타임 락이 걸려있지만, 금액 조율을 위해 스킵하지 않고 계속 전진합니다.")

        if not price_specs:
            print(f"   [⚠️ 경고 - {ad_code}] 유효한 DB 가격 스펙 정보가 누락되어 창을 닫고 취소 처리합니다.")
            try: dialog_popup.find_element(By.XPATH, ".//button[@aria-label='닫기']").click()
            except: pass
            return "FAIL"

        # 4. 하부 가격 조율 팩토리 구동
        is_changed, reports = 당근_팝업창_가격_동기화_처리_엔진(driver, dialog_popup, ad_code, price_specs)

        # 5. 🏁 [이원화 트랙] 쿨타임 여부에 따른 대마감 공정
        if is_cooldown_active:
            final_action_code = "NO_CHANGE_SKIP"
            if is_changed:
                try:
                    print(f"   [🔎 디버그 - {ad_code}] 3단계(쿨타임형): '[가격만 변경하기]' 마감 버튼 터치...")
                    price_only_btn = dialog_popup.find_element(By.XPATH, ".//button[text()='가격만 변경하기']")
                    driver.execute_script("arguments[0].click();", price_only_btn)
                    time.sleep(0.3)
                    # 기존 코드의 智慧='확인'은 함수가 실제로 받는 파라미터명 선택='확인'의 오타로
                    # 보여 여기서 함께 바로잡음(2026-08-30) — 원래는 TypeError로 이 분기가 죽었을 자리.
                    확인창클릭(driver, 선택='확인', timeout=1, unattended=unattended)
                except Exception as button_err:
                    print(f"   [⚠️ 경고 - {ad_code}] '가격만 변경하기' 저장 버튼 작동 실패: {button_err}")
                final_action_code = "PRICE_UPDATE_SUCCESS"
            
            # 잔존 팝업 레이어 닫기(X) 클리어
            try:
                close_x = dialog_popup.find_element(By.XPATH, ".//button[@aria-label='닫기']")
                driver.execute_script("arguments[0].click();", close_x)
                time.sleep(0.5)
            except: pass

            # 🔓 [구출 작전] 쿨타임 제한 매물인데 '숨김' 상태라면 '판매중'으로 반전 구출
            if current_status == "숨김":
                try:
                    print(f"   [🔓 숨김해제 개시 - {ad_code}] 쿨타임 락 상태이나 기존 '숨김' 매물이므로 구출을 위해 더보기(...) 타격")
                    more_btn = row_element.find_element(By.XPATH, ".//button[@aria-haspopup='menu']")
                    try: more_btn.click()
                    except: driver.execute_script("arguments[0].click();", more_btn)
                    time.sleep(0.8)
                    
                    unhide_option = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[@role='menu' and @data-state='open']//*[contains(text(),'숨기기 해제')]"))
                    )
                    driver.execute_script("arguments[0].click();", unhide_option)
                    time.sleep(0.5) # 기습 팝업 전개 대기 버퍼 마진
                    
                    # =================================================================
                    # 🚀 [소장님 기획 반영 - 최소 추가] 사진 필수 제한 기습 팝업 우회 탈출 엔진
                    # =================================================================
                    # 팝업창 내부에 '사진을 추가해 주세요' 문구가 감지되는지 레이더 스캔을 켭니다.
                    photo_popup_xpath = "//span[text()='사진을 추가해 주세요' or contains(text(), '사진을 추가')]"
                    photo_popups = driver.find_elements(By.XPATH, photo_popup_xpath)
                    
                    if photo_popups:
                        print(f"   [🛑 사진 누락 관문 진입 - {ad_code}] 사진 누락 절대 차단 락 감지 ➡️ '게시글 수정' 탈출 팩토리 기동")
                        
                        # 1) 팝업 내부의 '게시글 수정' 버튼을 찾아 자바스크립트로 강제 격파
                        fix_article_btn = driver.find_element(By.XPATH, "//button[text()='게시글 수정']")
                        driver.execute_script("arguments[0].click();", fix_article_btn)
                        
                        # 2) 당근마켓의 공식 수정 양식 폼 페이지가 완전히 로딩될 때까지 홀딩 대기
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "salesType")))
                        time.sleep(1.0)
                        
                        # 3) 소장님 노하우 적용: 양식 최하단 마감 저장 단추인 '매물 수정'을 원격 리클릭하여 승인 제출
                        print(f"   [✍️ 양식 강제마감 - {ad_code}] 수정 화면 진입 성공 ➡️ 하단 [매물 수정] 버튼 강제 터치 마감...")
                        final_submit_btn = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[text()='매물 수정' or contains(text(), '수정 완료') or text()='수정']"))
                        )
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", final_submit_btn)
                        time.sleep(0.3)
                        driver.execute_script("arguments[0].click();", final_submit_btn)
                        
                        # 4) 대시보드 목록 메인 화면으로 바운드되어 안전 복귀할 때까지 최종 대기
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "form input[placeholder*='지번']"))
                        )
                        time.sleep(1.5)
                        print(f"   [✅ 구출 성공 - {ad_code}] 사진 누락 제한 락 완벽 격파 ➡️ 대시보드 리스트 원대복귀 완수 V")
                    
                    else:
                        # ---------------------------------------------------------
                        # 상황 B: 사진이 정상적으로 들어있는 청정 매물일 때 (기존 정통 선로 유지)
                        # ---------------------------------------------------------
                        확인창클릭(driver, 선택='확인', timeout=1, unattended=unattended)
                        print(f"   [✅ 숨김해제 완료 - {ad_code}] 유령 숨김 상태 탈출 ➡️ '판매중' 활성 트랙으로 강제 원대복귀 완수 V")
                        time.sleep(1.0)
                    
                    # 🚀 [오류 해결] 가격수정 여부와 상관없이 '숨김해제'가 수행되었다면 독립 코드를 최우선 반환합니다!
                    return "RESCUE_BUMP_SUCCESS"
                except Exception as ex_err:
                    print(f"   [⚠️ 숨김해제 실패 - {ad_code}] 분리 레이어 메뉴 제어 중 예외 발생: {ex_err}")
            
            return final_action_code

        else:
            # 🟢 쿨타임이 없는 상태: 정통 마스터 끌어올리기 완수 공정
            time.sleep(0.3)
            print(f"   [🔎 디버그 - {ad_code}] 3단계: 1차 가격 팝업창의 [끌어올리기] 실행 단추 터치...")
            final_bump_btn = dialog_popup.find_element(By.XPATH, ".//button[text()='끌어올리기']")
            driver.execute_script("arguments[0].click();", final_bump_btn)
            time.sleep(0.5)

            # 🚀 [소장님 피드백 반영] 시스템 확인창 돌파 모듈
            try:
                WebDriverWait(driver, 1.5).until(EC.alert_is_present())
                print(f"   [🛑 시스템창 포획 - {ad_code}] 크롬 기본 시스템 확인창('숨기기 해제' 등) 감지 ➡️ 즉시 격파 기동")
                확인창클릭(driver, 선택='확인', timeout=1, unattended=unattended)
                time.sleep(0.5)
            except TimeoutException:
                try:
                    opened_dialogs = driver.find_elements(By.XPATH, "//div[@role='dialog' and @data-state='open']")
                    if opened_dialogs:
                        top_dialog = opened_dialogs[-1]
                        try: top_title = top_dialog.find_element(By.XPATH, ".//h2").get_attribute("textContent").strip()
                        except: top_title = ""
                        
                        if "거래중인 매물" in top_title or "허위 매물" in top_title:
                            text_span = top_dialog.find_element(By.XPATH, ".//span[text()='거래중인 매물이에요']")
                            driver.execute_script("arguments[0].click();", text_span)
                            time.sleep(0.4)
                            sub_bump_btn = top_dialog.find_element(By.XPATH, ".//button[text()='끌어올리기']")
                            WebDriverWait(driver, 3).until(lambda d: sub_bump_btn.get_attribute("disabled") is None)
                            driver.execute_script("arguments[0].click();", sub_bump_btn)
                            time.sleep(0.5)
                        elif "집주인" in top_title or "인증" in top_title:
                            pass_btn = top_dialog.find_element(By.XPATH, ".//button[contains(text(), '다음에') or contains(text(), '나중에') or contains(text(), '닫기') or @aria-label='닫기']")
                            driver.execute_script("arguments[0].click();", pass_btn)
                            time.sleep(0.5)
                        else:
                            확인창클릭(driver, 선택='확인', timeout=1, unattended=unattended)
                    else:
                        확인창클릭(driver, 선택='확인', timeout=1, unattended=unattended)
                except:
                    확인창클릭(driver, 선택='확인', timeout=1, unattended=unattended)

            # 🧹 4단계 연쇄 팝업 잔해 최종 청소 세션
            print(f"   [🔎 디버그 - {ad_code}] 4단계: 화면에 남은 모든 팝업창 및 배경 레이어 증발 대기...")
            time.sleep(0.3)
            try:
                final_dialogs = driver.find_elements(By.XPATH, "//div[@role='dialog' and @data-state='open']")
                if final_dialogs:
                    last_dialog = final_dialogs[-1]
                    try: last_title = last_dialog.find_element(By.XPATH, ".//h2").get_attribute("textContent").strip()
                    except: last_title = ""
                    if "집주인" in last_title or "인증" in last_title:
                        last_pass_btn = last_dialog.find_element(By.XPATH, ".//button[contains(text(), '다음에') or contains(text(), '나중에') or contains(text(), '닫기')]")
                        driver.execute_script("arguments[0].click();", last_pass_btn)
                        time.sleep(0.5)
            except: pass

            driver.implicitly_wait(0)
            for _ in range(2):
                try:
                    ghost_close_btn = driver.find_element(By.XPATH, "//div[@role='dialog']//button[@aria-label='닫기'] | //button[@aria-label='닫기']")
                    driver.execute_script("arguments[0].click();", ghost_close_btn)
                    time.sleep(0.4)
                except: break

            try: WebDriverWait(driver, 1).until(EC.invisibility_of_element_located((By.XPATH, "//div[contains(@class, 'bg-bg-overlay')]")))
            except:
                try: driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                except: pass
                time.sleep(0.3)
                
            driver.implicitly_wait(10)
            
            # 🚀 [치료 핵심] 정통 끌올 트랙에서도 원래 매물이 '숨김' 상태였다면 숨김해제 성공 명찰을 달아 내보냅니다!
            if current_status == "숨김":
                return "RESCUE_BUMP_SUCCESS"
            return "BUMP_SUCCESS"

    except Exception as global_error:
        return "FAIL"
    
def 데이터베이스_다중_가격스펙_전수조회(item_code, ad_site=None):
    """
    [소장님 기획 반영 - 다중 가격 스펙 범용 조회 엔진]
    광고사이트명(ad_site) 유무에 따라 매물번호(item_code)를 플랫폼 광고번호(ad_code) 혹은 
    내부 대표 매물번호(object_code_new)로 자동 판별하여 의뢰서의 모든 가격 사양을 분석 후 리턴합니다.
    """
    import pymysql
    import re
    
    유효가격목록 = []
    conn = None
    
    try:
        conn = pymysql.connect(
            host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', database='obangkr', charset='utf8'
        )
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 기본 마스터 조인 베이스 쿼리문 준비
        base_query = """
            SELECT o.object_ttype, c.request_term1,
                   c.request_deposit1, c.request_rent1, 
                   c.request_deposit2, c.request_rent2, 
                   c.request_deposit3, c.request_rent3, 
                   c.request_trading 
            FROM pr_externalad AS e
            JOIN pr_object AS o ON e.object_code_new = o.object_code_new
            JOIN pr_request_give AS c ON o.land_code = c.land_code AND o.building_code = c.building_code AND o.room_code = c.room_code
        """
        
        # 🎯 [소장님 지시 규칙] ad_site 존재 여부에 따른 동적 관문 분기 생성
        if ad_site and str(ad_site).strip():
            # 사이트명이 명시된 경우 (예: '당근') -> 기존의 외부 광고 코드 대조
            query = base_query + " WHERE e.ad_code = %s AND e.ad_site = %s LIMIT 1"
            cursor.execute(query, (str(item_code), str(ad_site)))
            log_label = f"{ad_site} 광고번호:{item_code}"
        else:
            # 사이트명이 없는 경우 -> 대표 내부 새홈 매물번호 직통 타격
            query = base_query + " WHERE e.object_code_new = %s LIMIT 1"
            cursor.execute(query, (str(item_code),))
            log_label = f"새홈 대표번호:{item_code}"
            
        row = cursor.fetchone()
        
        if row:
            term_months = int(re.sub(r'\D', '', str(row['request_term1']))) if row['request_term1'] else 12
            
            # ① 매매 금액 조건 추적 (0원 제외)
            if row.get('request_trading') and str(row['request_trading']).isdigit() and int(row['request_trading']) > 0:
                유효가격목록.append({"종류": "매매", "보증금": 0, "월세": 0, "매매가": int(row['request_trading'])})
            
            # ② 3쌍의 보증금/월세 임대료 다차원 전수 검사 (0원 제외)
            for i in range(1, 4):
                raw_deposit = row.get(f'request_deposit{i}')
                raw_rent = row.get(f'request_rent{i}')
                
                if raw_deposit or raw_rent:
                    deposit_val = int(raw_deposit) if str(raw_deposit).isdigit() else 0
                    rent_val = int(raw_rent) if str(raw_rent).isdigit() else 0
                    
                    if deposit_val > 0 or rent_val > 0:
                        if rent_val > 0 and term_months < 12 and deposit_val < (rent_val * 3):
                            유효가격목록.append({"종류": "단기", "보증금": deposit_val, "월세": rent_val, "매매가": 0})
                        elif rent_val > 0:
                            유효가격목록.append({"종류": "월세", "보증금": deposit_val, "월세": rent_val, "매매가": 0})
                        else:
                            유효가격목록.append({"종류": "전세", "보증금": deposit_val, "월세": 0, "매매가": 0})
                            
        cursor.close()
        print(f"   [🔎 DB 수집 스펙 완수 - {log_label}] 교차 대조용 유효 목표 가격 그룹: {유효가격목록}")
        return 유효가격목록
        
    except Exception as db_err:
        print(f"   [❌ 오류 - {item_code}] 다중 가격 DB 조회 실패: {db_err}")
        return 유효가격목록
    finally:
        if conn:
            conn.close()    

def 당근_끌어올리기_실행():
    print("당근_끌어올리기_실행")