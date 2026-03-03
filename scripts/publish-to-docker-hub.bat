@echo off
REM Alkemist Docker Hub Publish Script (Windows)
REM Usage: publish-to-docker-hub.bat <docker-username> <version>
REM Example: publish-to-docker-hub.bat myusername 0.1.0

if "%1"=="" (
    echo Error: Docker Hub username required
    echo Usage: %0 ^<docker-username^> [version]
    echo Example: %0 myusername 0.1.0
    exit /b 1
)

setlocal enabledelayedexpansion
set DOCKER_USER=%1
set VERSION=%2
if "%VERSION%"=="" set VERSION=latest

echo.
echo ======================================
echo   Alkemist Docker Hub Publisher
echo ======================================
echo Username: %DOCKER_USER%
echo Version:  %VERSION%
echo ======================================
echo.

REM Check if Docker is running
docker ps >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not running. Please start Docker.
    exit /b 1
)

REM Build backend
echo Building backend image...
docker build -t alkemist-server:%VERSION% ./alkemist-server
docker tag alkemist-server:%VERSION% %DOCKER_USER%/alkemist-server:%VERSION%

if NOT "%VERSION%"=="latest" (
    docker tag alkemist-server:%VERSION% %DOCKER_USER%/alkemist-server:latest
)

REM Build frontend
echo.
echo Building frontend image...
docker build -t alkemist-client:%VERSION% ./alkemist-client
docker tag alkemist-client:%VERSION% %DOCKER_USER%/alkemist-client:%VERSION%

if NOT "%VERSION%"=="latest" (
    docker tag alkemist-client:%VERSION% %DOCKER_USER%/alkemist-client:latest
)

REM Push backend
echo.
echo Pushing backend to Docker Hub...
docker push %DOCKER_USER%/alkemist-server:%VERSION%
if NOT "%VERSION%"=="latest" (
    docker push %DOCKER_USER%/alkemist-server:latest
)

REM Push frontend
echo.
echo Pushing frontend to Docker Hub...
docker push %DOCKER_USER%/alkemist-client:%VERSION%
if NOT "%VERSION%"=="latest" (
    docker push %DOCKER_USER%/alkemist-client:latest
)

REM Clean up
echo.
echo Cleaning up local images...
docker rmi alkemist-server:%VERSION% alkemist-client:%VERSION% 2>nul
docker rmi %DOCKER_USER%/alkemist-server:%VERSION% %DOCKER_USER%/alkemist-client:%VERSION% 2>nul

echo.
echo ======================================
echo   Successfully published to Docker Hub!
echo ======================================
echo Backend:  https://hub.docker.com/r/%DOCKER_USER%/alkemist-server
echo Frontend: https://hub.docker.com/r/%DOCKER_USER%/alkemist-client
echo ======================================
echo.
echo Next: Update docker-compose.yml to use your images:
echo   image: %DOCKER_USER%/alkemist-server:%VERSION%
echo   image: %DOCKER_USER%/alkemist-client:%VERSION%
echo.
pause
