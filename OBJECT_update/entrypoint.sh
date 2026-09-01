#!/bin/bash
# fileName: OBJECT_update/entrypoint.sh
#
# 가상 디스플레이(Xvfb)를 먼저 띄운 뒤 두 가지 모드로 분기한다.
# - 기본(인자 없음): 무인 모드로 auto.py를 한 번 실행하고 끝난다. 나스 작업 스케줄러가
#   예약 시각에 이 컨테이너를 실행하는 것을 전제로 한다.
# - "login" 인자: 자동화를 실행하지 않고 크롬만 당근 로그인 화면으로 띄운 채 대기한다.
#   VNC(5900) 또는 noVNC 웹뷰어(7900)로 접속해 사람이 직접 당근 로그인(문자/QR 인증)을
#   완료하면, 그 세션이 daangn_profile 볼륨에 저장되어 이후 무인 실행 때 재사용된다.
set -e

export DISPLAY=:99
Xvfb :99 -screen 0 1600x900x24 &
sleep 1

# pyautogui(obang_worker.py가 의존)가 마우스 위치 확인을 위해 X 디스플레이에 붙을 때
# ~/.Xauthority 파일이 없으면 FileNotFoundError로 죽는다(2026-08-30 실제로 재현).
# Xvfb를 인증 없이 띄웠으니(-auth 옵션 없음) 빈 파일만 있으면 충분하다.
export XAUTHORITY=/root/.Xauthority
touch "$XAUTHORITY"

if [ "$1" = "login" ]; then
    echo "=== VNC 로그인 모드 ==="
    echo "브라우저에서 http://<나스IP>:7900 으로 접속해 당근마켓 로그인을 완료하세요."
    echo "로그인이 끝나면 이 컨테이너를 중지(docker compose down)하면 됩니다."
    x11vnc -display :99 -forever -shared -rfbport 5900 -nopw &
    websockify --web=/usr/share/novnc/ 7900 localhost:5900 &
    google-chrome --no-sandbox --disable-dev-shm-usage --disable-gpu --disable-software-rasterizer --user-data-dir=/app/OBJECT_update/daangn_profile "https://realty.daangn.com/ceo/home"
else
    # 설정값은 이제 파일이 아니라 cafe24 환경설정 카드가 쓰는 pr_config(운영 DB)에서 직접 읽는다
    # (2026-08-30, web_config Flask 앱 폐기와 함께 전환).
    python auto.py --unattended /app/OBJECT_update/logs/unattended_run.log
fi
