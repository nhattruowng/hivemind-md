$ErrorActionPreference = "SilentlyContinue"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$DevDir = Join-Path $Root ".dev"

if (!(Test-Path $DevDir)) {
    Write-Host "Không có process dev nào đang được quản lý."
    exit 0
}

Get-ChildItem -Path $DevDir -Filter "*.pid" | ForEach-Object {
    $name = $_.BaseName
    $pidValue = Get-Content $_.FullName
    $process = Get-Process -Id $pidValue
    if ($process) {
        Stop-Process -Id $pidValue -Force
        Write-Host "Đã dừng $name ($pidValue)"
    }
    Remove-Item $_.FullName -Force
}

foreach ($port in 5173, 8000, 8787) {
    netstat -ano | Select-String ":$port\s+" | ForEach-Object {
        $parts = ($_.Line.Trim() -split '\s+')
        if ($parts.Count -ge 5 -and $parts[1] -match ":$port$" -and $parts[3] -eq "LISTENING") {
            $process = Get-Process -Id ([int]$parts[4])
            if ($process -and $process.ProcessName -in @("node", "java", "python", "python3")) {
                Stop-Process -Id $process.Id -Force
                Write-Host "Đã dừng process trên port $port ($($process.ProcessName) $($process.Id))"
            }
        }
    }
}
