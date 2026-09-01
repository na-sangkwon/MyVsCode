#!/bin/bash
# fileName: OBJECT_update/nas_deploy_poll.sh
#
# DSM 작업 스케줄러가 몇 분 간격으로 이 스크립트를 실행한다(예: objectCodeDeployCheck 작업).
# 웹 환경설정 카드의 "최신 코드 반영 요청" 버튼을 누르면 운영 DB(pr_config.nas_deploy)에
# 신호만 남는데, 이 스크립트가 그 신호를 스스로 확인하러 온다 — 나스가 외부 인터넷에서
# 들어오는 연결을 받는 통로는 하나도 열지 않는다는 설계를 지키기 위함(2026-09-01, SSH를
# 인터넷에 새로 여는 대신 선택한 방식).
#
# git/docker 명령 자체는 나스 호스트에 git이 없어서 host에서 직접 pull하지 못하고,
# git이 들어있는 alpine/git 이미지를 그때그때 띄워 대신 시킨다(entrypoint.sh의 "exec" 모드도
# 같은 이유 — 이 이미지 안의 pymysql로 DB 확인/기록만 대신 시킨다).
set -e
REPO=/volume1/DevelopmentTeam/project/repos_python
OBJUPDATE=$REPO/OBJECT_update
DOCKER=/usr/local/bin/docker
LOGFILE=$OBJUPDATE/logs/nas_deploy_poll.log

cd "$OBJUPDATE"

REQUESTED=$($DOCKER compose run --rm automation exec python nas_deploy_check.py check 2>>"$LOGFILE" | tail -1)

if [ "$REQUESTED" != "Y" ]; then
    exit 0
fi

echo "=== $(date '+%Y-%m-%d %H:%M:%S') 반영 시작 ===" >> "$LOGFILE"

if $DOCKER run --rm --entrypoint sh -v "$REPO:/repo" -w /repo alpine/git \
    -c "git fetch --filter=blob:none origin main && git checkout -f main && git clean -fd OBJECT_update util" \
    >> "$LOGFILE" 2>&1; then
    if $DOCKER compose build >> "$LOGFILE" 2>&1; then
        $DOCKER compose run --rm automation exec python nas_deploy_check.py report success "git pull + 이미지 재빌드 완료" >> "$LOGFILE" 2>&1
    else
        $DOCKER compose run --rm automation exec python nas_deploy_check.py report error "docker 이미지 재빌드 실패 - nas_deploy_poll.log 확인 필요" >> "$LOGFILE" 2>&1
    fi
else
    $DOCKER compose run --rm automation exec python nas_deploy_check.py report error "git pull 실패 - nas_deploy_poll.log 확인 필요" >> "$LOGFILE" 2>&1
fi

echo "=== $(date '+%Y-%m-%d %H:%M:%S') 처리 종료 ===" >> "$LOGFILE"
