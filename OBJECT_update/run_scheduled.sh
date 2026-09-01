#!/bin/bash
# fileName: OBJECT_update/run_scheduled.sh
#
# 나스 DSM 작업 스케줄러가 예약 시각에 실행할 스크립트. root로 실행하면 docker 소켓
# 권한 문제(2026-08-30 겪었던 sudo 비밀번호 요구) 자체가 없어 sudo 없이 바로 부른다.
cd /volume1/DevelopmentTeam/project/repos_python/OBJECT_update
/usr/local/bin/docker compose run --rm automation
