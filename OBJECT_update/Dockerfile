# fileName: OBJECT_update/Dockerfile
#
# 빌드 컨텍스트는 저장소 최상위(리포 루트)여야 한다 — workers/carrot_worker.py가
# sys.path.append(os.path.join(dirname(__file__), '../..'))로 util/ 패키지를 상대경로로
# 찾기 때문에, 컨테이너 안에서도 실제 저장소와 동일하게 OBJECT_update/workers/ 두 단계
# 위에 util/이 있어야 한다. docker-compose.yml에서 context를 ".." 로 지정해 둔 이유가 이것.
#
# 아직 실제로 빌드/실행해보지 않은 초안이다 — 나스에서 처음 build할 때 오류가 나면
# (베이스 이미지의 tkinter 지원 여부, chrome 설치 등) 그 오류 메시지를 보고 함께 고쳐야 한다.
FROM python:3.11

# Xvfb(가상 디스플레이, 화면 없는 서버에서 크롬을 띄우기 위함)
# x11vnc + novnc + websockify(당근 최초 로그인 1회를 위한 VNC 웹뷰어)
# fonts-nanum(오방/당근 화면의 한글이 깨지지 않도록)
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb x11vnc novnc websockify fonts-nanum wget gnupg ca-certificates \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    # 크롬은 --no-install-recommends를 빼고 설치한다 — 렌더링에 필요한 일부 라이브러리가
    # "recommends"로만 걸려 있어서, 빼고 설치하면 렌더러가 SIGTRAP으로 죽는 문제가
    # 실제로 재현됐다(2026-08-30).
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# 콘솔이 연결되지 않은 환경에서 print()의 이모지가 UnicodeEncodeError로 죽는 문제를
# Windows 작업 스케줄러에서 실제로 겪었다(2026-08-30). 리눅스는 보통 문제없지만,
# 최소 베이스 이미지의 로케일이 UTF-8이 아닐 경우를 대비해 방어적으로 강제한다.
ENV PYTHONUTF8=1

WORKDIR /app
COPY util ./util
COPY OBJECT_update/requirements.txt ./OBJECT_update/requirements.txt
RUN pip install --no-cache-dir -r OBJECT_update/requirements.txt

COPY OBJECT_update/auto.py ./OBJECT_update/auto.py
COPY OBJECT_update/workers ./OBJECT_update/workers
COPY OBJECT_update/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /app/OBJECT_update
ENTRYPOINT ["/entrypoint.sh"]
