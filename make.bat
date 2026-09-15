@echo off
setlocal EnableExtensions
REM Windows CMD/PowerShell helper (no GNU make required)
REM Usage: make.bat up | down | build | logs | restart | ps | test | clean | help

set COMPOSE=docker compose
set SERVICE=miumiu

if "%~1"=="" goto help
if /I "%~1"=="help" goto help
if /I "%~1"=="build" goto build
if /I "%~1"=="up" goto up
if /I "%~1"=="down" goto down
if /I "%~1"=="restart" goto restart
if /I "%~1"=="logs" goto logs
if /I "%~1"=="ps" goto ps
if /I "%~1"=="shell" goto shell
if /I "%~1"=="test" goto test
if /I "%~1"=="clean" goto clean
if /I "%~1"=="arm-builder" goto armbuilder
if /I "%~1"=="arm-push" goto armpush

echo Unknown target: %~1
goto help

:help
echo MiuMiu 2.0 — make.bat targets:
echo   make.bat build
echo   make.bat up
echo   make.bat down
echo   make.bat restart
echo   make.bat logs
echo   make.bat ps
echo   make.bat shell
echo   make.bat test
echo   make.bat clean
echo   make.bat arm-builder
echo   make.bat arm-push
exit /b 0

:build
%COMPOSE% build
exit /b %ERRORLEVEL%

:up
%COMPOSE% build
%COMPOSE% up -d
echo Bot started. Use: make.bat logs
exit /b %ERRORLEVEL%

:down
%COMPOSE% down
exit /b %ERRORLEVEL%

:restart
%COMPOSE% restart %SERVICE%
exit /b %ERRORLEVEL%

:logs
%COMPOSE% logs -f %SERVICE%
exit /b %ERRORLEVEL%

:ps
%COMPOSE% ps
exit /b %ERRORLEVEL%

:shell
%COMPOSE% exec %SERVICE% /bin/bash
exit /b %ERRORLEVEL%

:test
%COMPOSE% run --rm --no-deps %SERVICE% sh -c "pip install -q pytest pytest-asyncio && pytest -q"
exit /b %ERRORLEVEL%

:clean
%COMPOSE% down
docker rmi miumiu-2.0:latest 2>nul
exit /b 0

:armbuilder
docker buildx create --name miumiuarm --use --bootstrap 2>nul
docker buildx use miumiuarm
docker buildx inspect --bootstrap
exit /b %ERRORLEVEL%

:armpush
call :armbuilder
docker buildx build --platform linux/arm/v7 -t eastwesser/home_arm_miumiu2:latest --push .
exit /b %ERRORLEVEL%
