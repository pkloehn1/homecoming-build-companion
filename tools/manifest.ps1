<#
.SYNOPSIS
  Regenerate homecoming-build-companion/manifest.json — the snapshot index.

.DESCRIPTION
  Walks homecoming-build-companion/ and records, per file: relative path, size, SHA256,
  and the lane that produced it. Lanes:
    mids-manual       — harvested from the running MidsReborn app
    mids-repo-shipped — copied from MidsReborn/Databases/Homecoming/*.json
    mids-derived      — hand-transcribed from MidsReborn C# source
    canonical-binc    — produced by Lane B (Pigg Wrangler + Bin Crawler)
    hand-authored     — markdown docs we wrote
    community-capture — manual forum/wiki captures
    strategy          — hand-curated build-strategy data
    samples           — sample builds + sidecars

  The manifest lets you (and Claude) tell at a glance whether the project
  folder is stale relative to current data sources.
#>
[CmdletBinding()]
param(
    [string]$ProjectRoot = (Join-Path $PSScriptRoot '..\..\homecoming-build-companion')
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)

if (-not (Test-Path $ProjectRoot)) { throw "Not found: $ProjectRoot" }

function Get-Lane {
    param([string]$Rel)
    switch -Wildcard ($Rel) {
        'data\mids\repo-shipped\*'   { 'mids-repo-shipped' }
        'data\mids\derived\*'        { 'mids-derived' }
        'data\mids\*'                { 'mids-manual' }
        'data\canonical\*'           { 'canonical-binc' }
        'data\diff\*'                { 'diff-spotcheck' }
        'docs\*'                     { 'hand-authored' }
        'community\*'                { 'community-capture' }
        'strategy\*'                 { 'strategy' }
        'build-format\samples\*'     { 'samples' }
        'build-format\*'             { 'hand-authored' }
        'README.md'                  { 'hand-authored' }
        '.vscode\*'                  { 'editor-config' }
        default                      { 'unknown' }
    }
}

function Get-AppVersion {
    $appSettings = "$env:APPDATA\LoadedCamel\MidsReborn\appSettings.json"
    if (Test-Path $appSettings) {
        try {
            $obj = Get-Content $appSettings -Raw | ConvertFrom-Json
            return $obj.version ?? '<unknown>'
        } catch { return '<unparseable>' }
    }
    return '<not installed>'
}

function Get-RepoSha {
    $repo = "$env:USERPROFILE\repos\MidsReborn"
    if (-not (Test-Path "$repo\.git")) { return '<no .git>' }
    try {
        Push-Location $repo
        $sha = (& git rev-parse --short HEAD 2>$null)
        Pop-Location
        return $sha
    } catch { return '<unknown>' }
}

Write-Host "Scanning $ProjectRoot ..." -ForegroundColor Cyan

$files = Get-ChildItem -Path $ProjectRoot -Recurse -File | Where-Object {
    $_.Name -ne 'manifest.json'  # don't include the manifest in itself
}

$entries = foreach ($f in $files) {
    $rel = $f.FullName.Substring($ProjectRoot.Length + 1)
    [pscustomobject]@{
        path   = $rel.Replace('\','/')
        size   = $f.Length
        sha256 = (Get-FileHash $f.FullName -Algorithm SHA256).Hash
        lane   = Get-Lane $rel
    }
}

$manifest = [ordered]@{
    schema_version  = 1
    generated_at    = (Get-Date -Format 'o')
    project_root    = $ProjectRoot
    mids_app_version = Get-AppVersion
    mids_repo_sha   = Get-RepoSha
    file_count      = $entries.Count
    total_bytes     = ($entries | Measure-Object -Sum size).Sum
    by_lane         = ($entries | Group-Object lane | ForEach-Object {
        [pscustomobject]@{ lane = $_.Name; count = $_.Count }
    })
    files           = $entries
}

$out = Join-Path $ProjectRoot 'manifest.json'
$manifest | ConvertTo-Json -Depth 8 | Set-Content -Path $out -Encoding UTF8

Write-Host "Wrote $out" -ForegroundColor Green
Write-Host "  $($entries.Count) files, $([math]::Round(($entries|Measure-Object -Sum size).Sum/1MB,1)) MB"
$entries | Group-Object lane | Sort-Object Count -Descending |
    Format-Table @{N='Lane';E={$_.Name}}, @{N='Files';E={$_.Count}} -AutoSize
