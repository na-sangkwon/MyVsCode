@echo off
REM Launcher for Windows Task Scheduler. Kept ASCII-only on purpose:
REM Korean comments in a .bat file get misread under cmd.exe's codepage
REM and can be parsed as stray commands instead of a comment (reproduced 2026-08-30).
cd /d "%~dp0"

REM Call python.exe by its full path instead of the "py" launcher: the "py -3.11"
REM launcher failed to find this per-user Python install when run non-interactively
REM by Task Scheduler (schtasks result code 255, reproduced 2026-08-30).
REM
REM Task Scheduler runs with no console attached, so Python falls back to the
REM system ANSI codepage (cp949 on Korean Windows) for stdout instead of UTF-8,
REM and crashes the whole process the moment any of the many emoji-laden print()
REM calls in obang_data()/obang_worker.py/carrot_worker.py runs (reproduced 2026-08-30,
REM UnicodeEncodeError on U+1F50E). PYTHONUTF8=1 forces Python's UTF-8 mode from
REM startup so every print() in the program is safe, without editing each one.
set PYTHONUTF8=1
"C:\Users\nsk98\AppData\Local\Programs\Python\Python311\python.exe" auto.py --unattended unattended_settings.example.json test_run.log >> run_unattended_batch.log 2>&1
echo [%date% %time%] exit code: %errorlevel% >> run_unattended_batch.log
