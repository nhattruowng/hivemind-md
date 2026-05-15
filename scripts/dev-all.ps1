param(
    [switch]$SkipInstall,
    [switch]$NoDownload
)

$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$DevDir = Join-Path $Root ".dev"
$LogDir = Join-Path $Root "logs\dev"
$MavenVersion = "3.9.6"
$MavenDir = Join-Path $Root ".tooling\apache-maven-$MavenVersion"
$MavenZip = Join-Path $Root ".tooling\apache-maven-$MavenVersion-bin.zip"
$MavenCmd = Join-Path $MavenDir "bin\mvn.cmd"
$FrontendDir = Join-Path $Root "frontend"
$PythonBackendDir = Join-Path $Root "backend"
$PythonVenvPython = Join-Path $PythonBackendDir ".venv\Scripts\python.exe"

New-Item -ItemType Directory -Force -Path $DevDir, $LogDir, (Join-Path $Root ".tooling") | Out-Null

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Resolve-JavaHome {
    function Test-Java21Home {
        param([string]$JavaHomeCandidate)

        if (!$JavaHomeCandidate -or !(Test-Path (Join-Path $JavaHomeCandidate "bin\java.exe"))) {
            return $false
        }

        $javaExe = Join-Path $JavaHomeCandidate "bin\java.exe"
        $versionOutput = & cmd.exe /c "`"$javaExe`" -version 2>&1"
        $versionText = $versionOutput -join "`n"
        if ($versionText -match 'version "(\d+)') {
            return [int]$Matches[1] -ge 21
        }
        return $false
    }

    $DefaultJava21 = "C:\Program Files\Java\jdk-21"
    if (Test-Java21Home $DefaultJava21) {
        return $DefaultJava21
    }

    if (Test-Java21Home $env:JAVA_HOME) {
        return $env:JAVA_HOME
    }

    $java = Get-Command java.exe -ErrorAction SilentlyContinue
    if ($java) {
        $home = Split-Path (Split-Path $java.Source -Parent) -Parent
        if (Test-Java21Home $home) {
            return $home
        }
    }

    throw "Không tìm thấy JDK 21. Hãy cài JDK 21 hoặc set JAVA_HOME trỏ về JDK 21."
}

function Resolve-Python {
    if (Test-Path $PythonVenvPython) {
        return $PythonVenvPython
    }

    $py = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($py) {
        return $py.Source
    }

    $python = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($python -and $python.Source -notmatch "\\msys64\\") {
        return $python.Source
    }

    if ($python) {
        Write-Warning "Đang dùng Python từ MSYS/không chuẩn Windows: $($python.Source). Nếu pip build lỗi, hãy cài Python chính thức từ python.org."
        return $python.Source
    }

    throw "Không tìm thấy Python. Hãy cài Python 3.11+ hoặc tạo backend\\.venv."
}

function Resolve-Npm {
    $npm = Get-Command npm.cmd -ErrorAction SilentlyContinue
    if ($npm) {
        return $npm.Source
    }
    throw "Không tìm thấy npm.cmd. Hãy cài Node.js 20+."
}

function Resolve-Maven {
    $systemMaven = Get-Command mvn.cmd -ErrorAction SilentlyContinue
    if ($systemMaven) {
        return $systemMaven.Source
    }

    if (Test-Path $MavenCmd) {
        return $MavenCmd
    }

    if ($NoDownload) {
        throw "Không tìm thấy Maven. Bỏ -NoDownload hoặc cài Maven vào PATH."
    }

    Write-Step "Không thấy mvn trong PATH, tải Maven $MavenVersion vào .tooling"
    $url = "https://archive.apache.org/dist/maven/maven-3/$MavenVersion/binaries/apache-maven-$MavenVersion-bin.zip"
    Invoke-WebRequest -Uri $url -OutFile $MavenZip
    Expand-Archive -Path $MavenZip -DestinationPath (Join-Path $Root ".tooling") -Force

    if (!(Test-Path $MavenCmd)) {
        throw "Tải Maven xong nhưng không tìm thấy $MavenCmd"
    }

    return $MavenCmd
}

function Stop-ExistingDevProcess {
    param([string]$Name)

    $pidFile = Join-Path $DevDir "$Name.pid"
    if (!(Test-Path $pidFile)) {
        return
    }

    $oldPid = Get-Content $pidFile -ErrorAction SilentlyContinue
    if ($oldPid) {
        $process = Get-Process -Id $oldPid -ErrorAction SilentlyContinue
        if ($process) {
            Write-Step "Dừng process cũ: $Name ($oldPid)"
            Stop-Process -Id $oldPid -Force
        }
    }
    Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
}

function Start-DevProcess {
    param(
        [string]$Name,
        [string]$ScriptPath
    )

    Stop-ExistingDevProcess -Name $Name
    $process = Start-Process -FilePath "powershell.exe" `
        -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $ScriptPath) `
        -WorkingDirectory $Root `
        -WindowStyle Hidden `
        -PassThru

    Set-Content -Path (Join-Path $DevDir "$Name.pid") -Value $process.Id
    Write-Host "$Name PID: $($process.Id)"
}

$JavaHome = Resolve-JavaHome
$Maven = Resolve-Maven
$Python = Resolve-Python
$Npm = Resolve-Npm

Write-Step "Java"
Write-Host "JAVA_HOME=$JavaHome"

Write-Step "Maven"
Write-Host "MAVEN=$Maven"

Write-Step "Python"
Write-Host "PYTHON=$Python"

Write-Step "Node/npm"
Write-Host "NPM=$Npm"

if (!$SkipInstall) {
    Write-Step "Cài/cập nhật Python backend dependencies"
    Push-Location $PythonBackendDir
    if (!(Test-Path $PythonVenvPython)) {
        & $Python -m venv .venv
    }
    & $PythonVenvPython -m pip install --upgrade pip
    & $PythonVenvPython -m pip install -r requirements.txt
    Pop-Location

    Write-Step "Cài/cập nhật frontend dependencies"
    Push-Location $FrontendDir
    & $Npm install
    Pop-Location
}

$HiveMindBackendLog = Join-Path $LogDir "hivemind-backend.log"
$BizFlowBackendLog = Join-Path $LogDir "bizflow-backend.log"
$FrontendLog = Join-Path $LogDir "frontend.log"
$HiveMindBackendScript = Join-Path $DevDir "run-hivemind-backend.ps1"
$BizFlowBackendScript = Join-Path $DevDir "run-bizflow-backend.ps1"
$FrontendScript = Join-Path $DevDir "run-frontend.ps1"

@"
`$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path "$LogDir" | Out-Null
"Starting HiveMind backend at http://127.0.0.1:8000" | Tee-Object -FilePath "$HiveMindBackendLog"
try {
    Set-Location "$PythonBackendDir"
    & "$PythonVenvPython" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 *>&1 | Tee-Object -FilePath "$HiveMindBackendLog" -Append
} catch {
    `$_.Exception.ToString() | Tee-Object -FilePath "$HiveMindBackendLog" -Append
    exit 1
}
"@ | Set-Content -Path $HiveMindBackendScript

@"
`$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path "$LogDir" | Out-Null
"Starting BizFlow backend at http://127.0.0.1:8787" | Tee-Object -FilePath "$BizFlowBackendLog"
try {
    Set-Location "$Root"
    `$env:JAVA_HOME = "$JavaHome"
    `$env:Path = "`$env:JAVA_HOME\bin;`$env:Path"
    & "$Maven" spring-boot:run *>&1 | Tee-Object -FilePath "$BizFlowBackendLog" -Append
} catch {
    `$_.Exception.ToString() | Tee-Object -FilePath "$BizFlowBackendLog" -Append
    exit 1
}
"@ | Set-Content -Path $BizFlowBackendScript

@"
`$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path "$LogDir" | Out-Null
"Starting frontend at http://127.0.0.1:5173" | Tee-Object -FilePath "$FrontendLog"
try {
    Set-Location "$FrontendDir"
    `$env:VITE_API_BASE_URL = "http://127.0.0.1:8000"
    & "$Npm" run dev -- --port 5173 --strictPort *>&1 | Tee-Object -FilePath "$FrontendLog" -Append
} catch {
    `$_.Exception.ToString() | Tee-Object -FilePath "$FrontendLog" -Append
    exit 1
}
"@ | Set-Content -Path $FrontendScript

Write-Step "Start HiveMind backend + BizFlow backend + frontend"
Start-DevProcess -Name "hivemind-backend" -ScriptPath $HiveMindBackendScript
Start-DevProcess -Name "bizflow-backend" -ScriptPath $BizFlowBackendScript
Start-DevProcess -Name "frontend" -ScriptPath $FrontendScript

Write-Host ""
Write-Host "Đã chạy tất cả service." -ForegroundColor Green
Write-Host "HiveMind API:    http://127.0.0.1:8000"
Write-Host "BizFlow API:     http://127.0.0.1:8787"
Write-Host "Frontend:        http://127.0.0.1:5173"
Write-Host "HiveMind log:    $HiveMindBackendLog"
Write-Host "BizFlow log:     $BizFlowBackendLog"
Write-Host "Frontend log:    $FrontendLog"
Write-Host ""
Write-Host "Dừng tất cả:"
Write-Host "powershell -ExecutionPolicy Bypass -File .\scripts\stop-all.ps1"
