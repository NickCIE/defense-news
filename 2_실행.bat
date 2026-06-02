@echo off
chcp 65001 >nul
echo ================================
echo  방산 뉴스 대시보드 - 실행 중
echo ================================
echo.
echo 서버 시작 중... 잠시 기다려주세요.
echo 브라우저에서 http://127.0.0.1:8000 으로 접속하세요.
echo 종료하려면 이 창을 닫으세요.
echo.
start "" "http://127.0.0.1:8000"
python "%~dp0main.py"
pause
