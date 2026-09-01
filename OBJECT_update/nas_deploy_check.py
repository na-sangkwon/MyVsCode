# fileName: OBJECT_update/nas_deploy_check.py
#
# 나스 코드 반영 폴링(nas_deploy_poll.sh)에서 쓰는 보조 스크립트. git pull/docker build
# 자체는 나스 호스트 셸에서 수행하지만(컨테이너 안에는 git/docker가 없음), "반영 요청됐는지
# 확인"과 "결과 기록"은 이 이미지에 이미 있는 pymysql로 운영 DB(obangkr)에 직접 접속해서
# 처리한다 — auto.py가 pr_config/pr_log를 읽고 쓰는 것과 동일한 직접 접속 방식을 그대로
# 따른다(웹 API를 거치지 않음).
import sys
import datetime
import pymysql

DB = dict(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', database='obangkr', charset='utf8')


def check():
    conn = pymysql.connect(**DB)
    cursor = conn.cursor()
    cursor.execute("SELECT config_value FROM pr_config WHERE config_group='nas_deploy' AND config_key='deploy_requested'")
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    print('Y' if (row and row[0] == 'Y') else 'N')


def report(result, message):
    conn = pymysql.connect(**DB)
    cursor = conn.cursor()
    now = datetime.datetime.now()
    cursor.execute(
        """INSERT INTO pr_log (log_target, log_item, log_value, admin_id, log_wdate, log_wtime)
           VALUES ('system', 'nas_deploy', %s, '', %s, %s)""",
        (f"[{result}] {message}", now.date().isoformat(), now.strftime('%H:%M:%S'))
    )
    cursor.execute(
        "UPDATE pr_config SET config_value='N', config_udate=%s, config_utime=%s "
        "WHERE config_group='nas_deploy' AND config_key='deploy_requested'",
        (now.date().isoformat(), now.strftime('%H:%M:%S'))
    )
    conn.commit()
    cursor.close()
    conn.close()
    print('OK')


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else ''
    if mode == 'check':
        check()
    elif mode == 'report':
        report(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else '')
    else:
        print('usage: nas_deploy_check.py check|report <result> <message>', file=sys.stderr)
        sys.exit(1)
