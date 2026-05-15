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
