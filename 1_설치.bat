@echo off
chcp 65001 >nul
echo ================================
echo  방산 뉴스 대시보드 - 설치
echo ================================
echo.
echo Python 패키지를 설치합니다...
pip install -r "%~dp0requirements.txt"
echo.
echo 설치 완료! 이제 [2_실행.bat]을 더블클릭하세요.
echo.
pause
