@echo off
setlocal

REM Check Docker is available
docker --version >nul 2>&1
if errorlevel 1 (
  echo Docker not found. Please install Docker Desktop and ensure 'docker' is in PATH.
  pause
  exit /b 1
)

REM Image names
set OFFICIAL_IMAGE=jekyll/jekyll:pages
set LOCAL_IMAGE=jekyll-local-pages:latest
set IMAGE_NAME=

REM Prefer a locally built image (includes build tools). If missing, build it first;
REM if build fails, fall back to pulling the official image as a last resort.
docker image inspect %LOCAL_IMAGE% >nul 2>&1
if %ERRORLEVEL%==0 (
  echo Found local image %LOCAL_IMAGE%; using it.
  set IMAGE_NAME=%LOCAL_IMAGE%
) else (
  echo Local image %LOCAL_IMAGE% not found — building local image from Dockerfile (this may take a few minutes)
  docker build --pull -t %LOCAL_IMAGE% -f Dockerfile .
  if %ERRORLEVEL%==0 (
    echo Built %LOCAL_IMAGE% successfully; using it.
    set IMAGE_NAME=%LOCAL_IMAGE%
  ) else (
    echo Local build failed; attempting to pull official image %OFFICIAL_IMAGE%
    docker pull %OFFICIAL_IMAGE%
    if %ERRORLEVEL%==0 (
      echo Pulled %OFFICIAL_IMAGE%; using official image.
      set IMAGE_NAME=%OFFICIAL_IMAGE%
    ) else (
      echo Both local build and pull failed. Aborting.
      pause
      exit /b 1
    )
  )
)

REM Start the container in a new window (attached so you can stop it there)
echo Starting container (attached) in a new window
echo Note: first run may install gems and may take several minutes.
start "Jekyll Docker" cmd /k docker run --rm -it -p 4000:4000 -v "%CD%:/srv/jekyll" %IMAGE_NAME% jekyll serve --watch --incremental --host 0.0.0.0

REM Poll http://localhost:4000/snippets/ until the site responds (max 5 minutes), then open browser
set MAX_ATTEMPTS=300
set ATTEMPT=0

:poll_loop
powershell -Command "try{ Invoke-WebRequest -UseBasicParsing -Uri 'http://localhost:4000/snippets/' -TimeoutSec 2 > $null; exit 0 } catch { exit 1 }" >nul 2>&1
if %ERRORLEVEL%==0 (
  goto :ready
)

set /a ATTEMPT+=1
if %ATTEMPT% GEQ %MAX_ATTEMPTS% (
  echo Timeout waiting for http://localhost:4000/snippets/
  echo Opening browser anyway
  goto :ready
)

timeout /t 1 >nul
goto :poll_loop

:ready
start "" "http://localhost:4000/snippets/"

echo Launched browser. Stop the server in the "Jekyll Docker" window when finished.

endlocal
exit /b 0
