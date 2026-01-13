<#
Starts a Docker container that runs `jekyll serve` for local testing
Usage: run this from the repository root (double-clicking testlocally.cmd works).

Requirements:
- Docker Desktop installed and running on Windows
- Ports 4000 available

This script:
- stops/removes any previous container named `snippets_jekyll_local`
- starts a detached `jekyll/jekyll` container mounting the repo into /srv/jekyll
- waits until the site responds and opens the browser at http://127.0.0.1:4000/snippets/
#>

# Prefer to run from the script directory (repo root when run via testlocally.cmd)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

$containerName = 'snippets_jekyll_local'
$sitePath = 'http://127.0.0.1:4000/snippets/'

Write-Host "Stopping and removing any existing container named $containerName (if present)..."
try {
    docker rm -f $containerName | Out-Null
} catch {
    # ignore errors if container doesn't exist
}

Write-Host "Starting Docker container (jekyll/jekyll) serving the repo..."
# Use current working dir path for the mount. Docker Desktop handles Windows paths.
$pwdPath = (Get-Location).Path

$runArgs = @(
    'run','-d',
    '--name', $containerName,
    '-p','4000:4000',
    '-v', "$($pwdPath):/srv/jekyll",
    'jekyll/jekyll',
    'jekyll','serve','--force_polling','--livereload','--baseurl','/snippets'
)

try {
    & docker @runArgs | Out-Null
} catch {
    Write-Error "Failed to start Docker container. Ensure Docker is installed and running. $_"
    exit 1
}

Write-Host "Waiting for the site to become available at $sitePath (timeout 60s)..."
$maxSeconds = 60
$i = 0
while ($i -lt $maxSeconds) {
    Start-Sleep -Seconds 1
    try {
        $resp = Invoke-WebRequest -Uri $sitePath -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
        if ($resp.StatusCode -eq 200) { break }
    } catch {
        # still waiting
    }
    $i++
}

if ($i -lt $maxSeconds) {
    Write-Host "Site is up - opening browser: $sitePath"
    Start-Process $sitePath
    Write-Host "To stop the server: docker rm -f $containerName"
} else {
    Write-Warning ("Timed out waiting for site. Check container logs: docker logs " + $containerName)
}
