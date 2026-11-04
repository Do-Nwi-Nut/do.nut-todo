```bat
@echo off
chcp 65001 > nul
title PyInstaller EXE 빌드

cd /d "%~dp0"

echo ========================================
echo        PyInstaller EXE 자동 빌드
echo ========================================
echo.

set /p "PY_FILE=변환할 PY 파일명을 입력하세요 (예: main.py): "

if not exist "%PY_FILE%" (
    echo.
    echo [오류] PY 파일을 찾을 수 없습니다: %PY_FILE%
    pause
    exit /b 1
)

echo.
set /p "ICON_FILE=사용할 ICO 파일명을 입력하세요 (없으면 Enter): "

echo.

REM ICO 파일이 존재하면 아이콘 옵션 추가
set "ICON_OPTION="

if not "%ICON_FILE%"=="" (
    if exist "%ICON_FILE%" (
        set "ICON_OPTION=--icon=%ICON_FILE%"
        echo [안내] 아이콘을 적용합니다: %ICON_FILE%
    ) else (
        echo [안내] ICO 파일이 없습니다. 기본 아이콘으로 빌드합니다.
    )
) else (
    echo [안내] 아이콘 설정을 건너뜁니다.
)

echo.
echo ========================================
echo PY 파일 : %PY_FILE%
echo ========================================
echo.

python -m PyInstaller --version > nul 2>&1

if errorlevel 1 (
    echo [오류] PyInstaller가 설치되어 있지 않습니다.
    echo 설치 명령: python -m pip install pyinstaller
    pause
    exit /b 1
)

echo [빌드 시작]
echo.

if not "%ICON_FILE%"=="" if exist "%ICON_FILE%" (
    python -m PyInstaller --onefile --windowed --icon="%ICON_FILE%" --clean --noconfirm "%PY_FILE%"
) else (
    python -m PyInstaller --onefile --windowed --clean --noconfirm "%PY_FILE%"
)

if errorlevel 1 (
    echo.
    echo [오류] 빌드에 실패했습니다.
    pause
    exit /b 1
)

echo.
echo ========================================
echo             빌드 완료!
echo ========================================
echo.

for %%F in ("%PY_FILE%") do set "EXE_NAME=%%~nF"

echo 생성된 파일: %~dp0dist\%EXE_NAME%.exe
echo.
pause
```