@echo off
setlocal EnableExtensions

pushd "%~dp0"

set "CMD=uv run uvicorn main:app --host 127.0.0.1 --port 8000"
set "PAUSE_ON_ERROR=1"
set "PAUSE_ON_SUCCESS=1"

if /i "%~1"=="--dry-run" (
  echo %CMD%
  exit /b 0
)

if /i "%~1"=="--no-pause" (
  set "PAUSE_ON_ERROR=0"
  set "PAUSE_ON_SUCCESS=0"
)

%CMD%
set "EXITCODE=%ERRORLEVEL%"

if not "%EXITCODE%"=="0" (
  echo.
  echo Command failed with exit code %EXITCODE%.
  if "%PAUSE_ON_ERROR%"=="1" pause
  popd
  exit /b %EXITCODE%
)

if "%PAUSE_ON_SUCCESS%"=="1" (
  echo.
  echo Command completed successfully.
  pause
)

popd
