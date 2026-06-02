@echo off
chcp 65001 >nul
echo ================================
echo  방산 뉴스 수집 및 HTML 생성
echo ================================
echo.
echo 뉴스를 수집하고 HTML 파일을 만들고 있습니다...
python "%~dp0generate.py"
echo.
echo 완료! 브라우저에서 자동으로 열립니다.
echo 생성된 파일: 방산뉴스_대시보드.html
echo.
pause
