<#
.SYNOPSIS
    Conductor Universal Installer for Windows PowerShell
.DESCRIPTION
    Spec-Driven Development (SDD) plugin installer for Pi, Claude Code, Copilot, and Gemini/Antigravity.
.PARAMETER Global
    Install globally for user AI agent harnesses (Default).
.PARAMETER Local
    Scaffold Conductor into current project workspace.
.PARAMETER All
    Configure all supported harnesses without prompt.
.PARAMETER Harness
    Configure a specific harness: 'pi', 'claude', 'copilot', 'gemini'.
.PARAMETER Uninstall
    Remove Conductor links and registrations.
#>

[CmdletBinding()]
param(
    [switch]$Global = $true,
    [switch]$Local = $false,
    [switch]$All = $false,
    [string]$Harness = "",
    [switch]$Uninstall = $false
)

$ErrorActionPreference = "Stop"
$RepoUrl = "https://github.com/T-450/conductor-agent-plugin.git"
$DefaultInstallDir = Join-Path $env:USERPROFILE ".conductor"
$BinDir = Join-Path $env:USERPROFILE ".local\bin"

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "          CONDUCTOR UNIVERSAL AGENT INSTALLER           " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# Determine script directory
$ScriptDir = ""
if (Test-Path (Join-Path (Get-Location) "bin\conductor")) {
    $ScriptDir = (Get-Location).Path
} elseif ($PSScriptRoot) {
    $ScriptDir = $PSScriptRoot
}

# Handle Uninstall
if ($Uninstall) {
    Write-Host "Uninstalling Conductor..." -ForegroundColor Yellow
    if ($ScriptDir -and (Test-Path (Join-Path $ScriptDir "bin\conductor"))) {
        node (Join-Path $ScriptDir "bin\conductor") uninstall
    } elseif (Test-Path (Join-Path $DefaultInstallDir "bin\conductor")) {
        node (Join-Path $DefaultInstallDir "bin\conductor") uninstall
    }
    if (Test-Path $DefaultInstallDir) {
        Remove-Item -Recurse -Force $DefaultInstallDir
        Write-Host "Removed managed directory: $DefaultInstallDir"
    }
    Write-Host "Conductor uninstalled successfully." -ForegroundColor Green
    exit 0
}

# Handle Local Scaffolding
if ($Local) {
    Write-Host "Running Local Project Scaffolding..." -ForegroundColor Cyan
    $Src = $ScriptDir
    if (-not $Src -or -not (Test-Path (Join-Path $Src "skills"))) {
        $Src = $DefaultInstallDir
        if (-not (Test-Path $Src)) {
            Write-Host "Fetching Conductor source to $Src..." -ForegroundColor Yellow
            git clone --depth 1 $RepoUrl $Src
        }
    }
    node (Join-Path $Src "bin\conductor") install --local
    exit 0
}

# Global Installation
$SrcDir = ""
if ($ScriptDir -and (Test-Path (Join-Path $ScriptDir "skills"))) {
    $SrcDir = $ScriptDir
    Write-Host "Using local repository at: $SrcDir" -ForegroundColor Cyan
} else {
    $SrcDir = $DefaultInstallDir
    if (Test-Path (Join-Path $SrcDir ".git")) {
        Write-Host "Updating managed installation at $SrcDir..." -ForegroundColor Cyan
        Push-Location $SrcDir
        git pull --ff-only
        Pop-Location
    } else {
        Write-Host "Cloning Conductor into $SrcDir..." -ForegroundColor Cyan
        New-Item -ItemType Directory -Force -Path $SrcDir | Out-Null
        git clone --depth 1 $RepoUrl $SrcDir
    }
}

# Detect active harnesses
$DetectPi = $All
$DetectClaude = $All
$DetectCopilot = $All
$DetectGemini = $All

if (-not $All -and -not $Harness) {
    if (Get-Command "omp" -ErrorAction SilentlyContinue -or (Test-Path (Join-Path $env:USERPROFILE ".omp"))) { $DetectPi = $true }
    if (Get-Command "claude" -ErrorAction SilentlyContinue -or (Test-Path (Join-Path $env:USERPROFILE ".claude"))) { $DetectClaude = $true }
    if (Get-Command "gh" -ErrorAction SilentlyContinue -or (Test-Path (Join-Path $env:USERPROFILE ".config\github-copilot"))) { $DetectCopilot = $true }
    if (Get-Command "agy" -ErrorAction SilentlyContinue -or (Test-Path (Join-Path $env:USERPROFILE ".gemini"))) { $DetectGemini = $true }
}

if ($Harness) {
    $DetectPi = ($Harness -eq "pi" -or $Harness -eq "omp")
    $DetectClaude = ($Harness -eq "claude")
    $DetectCopilot = ($Harness -eq "copilot" -or $Harness -eq "gh")
    $DetectGemini = ($Harness -eq "gemini" -or $Harness -eq "agy")
}

Write-Host "`nConfiguring AI Agent Harnesses:" -ForegroundColor Cyan

# 1. Pi / Oh-My-Pi
if ($DetectPi) {
    Write-Host "  -> Configuring Pi / Oh-My-Pi..." -ForegroundColor Green
    $OmpPluginsDir = Join-Path $env:USERPROFILE ".omp\plugins"
    $OmpSkillsDir = Join-Path $env:USERPROFILE ".omp\agent\skills"
    New-Item -ItemType Directory -Force -Path $OmpPluginsDir | Out-Null
    New-Item -ItemType Directory -Force -Path $OmpSkillsDir | Out-Null

    $InstalledJsonPath = Join-Path $OmpPluginsDir "installed_plugins.json"
    $PluginsObj = @{}
    if (Test-Path $InstalledJsonPath) {
        try {
            $PluginsObj = Get-Content $InstalledJsonPath -Raw | ConvertFrom-Json -AsHashtable
        } catch {}
    }
    $PluginsObj["conductor@conductor-marketplace"] = @(
        @{
            scope = "user"
            installPath = $SrcDir
            version = "1.2.0"
        }
    )
    $PluginsObj | ConvertTo-Json -Depth 5 | Set-Content $InstalledJsonPath -Encoding UTF8

    Get-ChildItem (Join-Path $SrcDir "skills") -Directory | ForEach-Object {
        $DestSkill = Join-Path $OmpSkillsDir $_.Name
        if (Test-Path $DestSkill) { Remove-Item -Recurse -Force $DestSkill }
        New-Item -ItemType Junction -Path $DestSkill -Target $_.FullName -ErrorAction SilentlyContinue | Out-Null
    }
}

# 2. Claude Code
if ($DetectClaude) {
    Write-Host "  -> Configuring Claude Code..." -ForegroundColor Green
    $ClaudePlugins = Join-Path $env:USERPROFILE ".claude\plugins"
    New-Item -ItemType Directory -Force -Path $ClaudePlugins | Out-Null
    $ClaudeDest = Join-Path $ClaudePlugins "conductor"
    if (Test-Path $ClaudeDest) { Remove-Item -Recurse -Force $ClaudeDest }
    New-Item -ItemType Junction -Path $ClaudeDest -Target $SrcDir -ErrorAction SilentlyContinue | Out-Null
}

# 3. Gemini / Antigravity
if ($DetectGemini) {
    Write-Host "  -> Configuring Gemini CLI & Antigravity..." -ForegroundColor Green
    $GeminiPlugins = Join-Path $env:USERPROFILE ".gemini\config\plugins"
    New-Item -ItemType Directory -Force -Path $GeminiPlugins | Out-Null
    $GeminiDest = Join-Path $GeminiPlugins "conductor"
    if (Test-Path $GeminiDest) { Remove-Item -Recurse -Force $GeminiDest }
    New-Item -ItemType Junction -Path $GeminiDest -Target $SrcDir -ErrorAction SilentlyContinue | Out-Null
}

# 4. GitHub Copilot CLI
if ($DetectCopilot) {
    Write-Host "  -> Configuring GitHub Copilot CLI..." -ForegroundColor Green
    $CopilotDir = Join-Path $env:USERPROFILE ".config\github-copilot"
    New-Item -ItemType Directory -Force -Path $CopilotDir | Out-Null
    Copy-Item (Join-Path $SrcDir ".github\copilot-instructions.md") (Join-Path $CopilotDir "conductor-instructions.md") -Force
}

# Configure Windows CLI command runner (conductor.cmd)
Write-Host "`nSetting up Terminal CLI Bridge:" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path $BinDir | Out-Null
$CmdWrapper = "@echo off`nnode `"$SrcDir\bin\conductor`" %*"
Set-Content -Path (Join-Path $BinDir "conductor.cmd") -Value $CmdWrapper -Encoding ASCII
Write-Host "  -> Created $(Join-Path $BinDir 'conductor.cmd')"

# Ensure $BinDir in PATH
$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($UserPath -notlike "*$BinDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$UserPath;$BinDir", "User")
    Write-Host "  -> Added $BinDir to User PATH." -ForegroundColor Yellow
}

# Run Doctor
Write-Host "`nRunning Conductor Doctor Verification..." -ForegroundColor Cyan
node (Join-Path $SrcDir "bin\conductor") doctor

Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "Start using Conductor in your terminal or agent sessions:"
Write-Host "  - Terminal: conductor status or conductor doctor"
Write-Host "  - In Agent:  /conductor-setup or /conductor-new-track`n"
