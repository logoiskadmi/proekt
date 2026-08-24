#Requires -Version 5.1
<#
.SYNOPSIS
  Собирает ZIP релиза «Списание» и генерирует version.json для OTA.

.EXAMPLE
  .\publish-ota.ps1 -SourceDir "D:\Build\Spisanie\Release" -Version "1.0.1" -VersionCode 101 -Changelog "Исправления печати"
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$SourceDir,

    [Parameter(Mandatory = $true)]
    [string]$Version,

    [Parameter(Mandatory = $true)]
    [int]$VersionCode,

    [string]$Changelog = "Обновление программы Списание",

    [string]$ExeName = "Spisanie.exe",

    [string]$OutDir = "",

    [string]$BaseUrl = "https://lognet.by/ota/Spisanie",

    [switch]$Mandatory
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $SourceDir)) {
    throw "Папка сборки не найдена: $SourceDir"
}

if ([string]::IsNullOrWhiteSpace($OutDir)) {
    $OutDir = Join-Path $PSScriptRoot "..\ota\Spisanie" | Resolve-Path -ErrorAction SilentlyContinue
    if (-not $OutDir) {
        $OutDir = Join-Path (Split-Path $PSScriptRoot -Parent) "ota\Spisanie"
        New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
    }
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$fileName = "Spisanie-$Version.zip"
$zipPath = Join-Path $OutDir $fileName

if (Test-Path -LiteralPath $zipPath) {
    Remove-Item -LiteralPath $zipPath -Force
}

Write-Host "Упаковка $SourceDir -> $zipPath"
Compress-Archive -Path (Join-Path $SourceDir "*") -DestinationPath $zipPath -CompressionLevel Optimal

$hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $zipPath).Hash.ToLowerInvariant()
$size = (Get-Item -LiteralPath $zipPath).Length

$manifest = [ordered]@{
    product         = "Spisanie"
    version         = $Version
    versionCode     = $VersionCode
    minVersionCode  = 100
    publishedAt     = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    mandatory       = [bool]$Mandatory
    changelog       = $Changelog
    package         = [ordered]@{
        url      = "$BaseUrl/$fileName"
        fileName = $fileName
        size     = $size
        sha256   = $hash
    }
    exeName         = $ExeName
    channel         = "stable"
}

$jsonPath = Join-Path $OutDir "version.json"
$manifest | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $jsonPath -Encoding UTF8

Write-Host ""
Write-Host "Готово."
Write-Host "  ZIP:      $zipPath"
Write-Host "  Size:     $size bytes"
Write-Host "  SHA-256:  $hash"
Write-Host "  Manifest: $jsonPath"
Write-Host ""
Write-Host "Загрузите на сервер в папку:"
Write-Host "  www/lognet.by/ota/Spisanie/"
Write-Host "Файлы:"
Write-Host "  - version.json"
Write-Host "  - $fileName"
Write-Host ""
Write-Host "Проверка после загрузки:"
Write-Host "  curl -sI $BaseUrl/version.json"
Write-Host "  (Content-Type должен быть application/json, не text/html)"
