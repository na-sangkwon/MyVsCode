#!/bin/bash
# fileName: OBJECT_update/run_scheduled.sh
#
# 나스 DSM 작업 스케줄러가 예약 시각에 실행할 스크립트. root로 실행하면 docker 소켓
# 권한 문제(2026-08-30 겪었던 sudo 비밀번호 요구) 자체가 없어 sudo 없이 바로 부른다.
cd /volume1/DevelopmentTeam/project/repos_python/OBJECT_update
# [2026-10-03] 인자를 그대로 컨테이너(entrypoint.sh)에 넘긴다 — 인자 없이 부르면 예전과 똑같이 새벽
# 자동업데이트가 돌고, "observe"를 주면 당근 노출 관측만 돈다(스케줄 작업을 둘로 나누되 스크립트는 하나).
/usr/local/bin/docker compose run --rm automation "$@"
