<#
.SYNOPSIS
  Extract structured numeric changes from cached Homecoming patch HTML pages
  using a hierarchical heading-stack parser, and write a chronologically-
  applied override JSON.

.DESCRIPTION
  Patch notes follow a heading hierarchy (h2/h3/h4/h5) with bullet-point
  change items underneath. The entity (AT/Powerset/Power) is in the heading
  stack; the field+old+new is in each <li>. We track the heading stack while
  walking the HTML linearly and pair each change item with its current
  context.

  Recognized change patterns (case-insensitive):
    "<field> (increased|reduced|decreased|changed|adjusted) from <N> to <M>"
    "<field> from <N> to <M>"
    "<field>:?\s*<N>\s*=>\s*<M>"
    "<field> now <M> (was <N>)"

  Recognized fields are in $FieldMap (string → canonical key).

  Entity path = heading stack (h2 → h3 → h4 → h5), normalized to
  Snake_Case dot-joined.

  Outputs:
    data/diff/patch_history/<patch>.md   per-patch change list
    data/diff/current_overrides.json     latest-wins consolidated map
    data/diff/UNRESOLVED.md              escalation log
#>
[CmdletBinding()]
param(
    [string]$PatchDir = (Join-Path $PSScriptRoot '..\scratch\patches'),
    [string]$ProjectRoot = (Join-Path $PSScriptRoot '..\..\homecoming-build-companion')
)

$ErrorActionPreference = 'Stop'
$PatchDir    = [System.IO.Path]::GetFullPath($PatchDir)
$ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)
$DiffDir     = Join-Path $ProjectRoot 'data\diff'
$HistDir     = Join-Path $DiffDir 'patch_history'
$Unresolved  = Join-Path $DiffDir 'UNRESOLVED.md'

foreach ($d in @($DiffDir, $HistDir)) {
    if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
}

# Chronological order
$Patches = @(
    'Issue_26_Page_1','Issue_26_Page_2','Issue_26_Page_3','Issue_26_Page_4','Issue_26_Page_5',
    'Issue_27_Page_1','Issue_27_Page_2','Issue_27_Page_3','Issue_27_Page_4','Issue_27_Page_5','Issue_27_Page_6','Issue_27_Page_7',
    'Issue_28_Page_1','Issue_28_Page_2','Issue_28_Page_3'
)

$FieldMap = @{
    'recharge time'    = 'recharge_time'
    'recharge'         = 'recharge_time'
    'endurance cost'   = 'endurance_cost'
    'endurance'        = 'endurance_cost'
    'damage scale'     = 'damage_scale'
    'damage'           = 'damage_scale'
    'activation time'  = 'activation_time'
    'cast time'        = 'activation_time'
    'animation time'   = 'activation_time'
    'range'            = 'range'
    'radius'           = 'radius'
    'arc'              = 'arc'
    'accuracy'         = 'accuracy'
    'max targets'      = 'max_targets_hit'
    'maximum targets'  = 'max_targets_hit'
    'target cap'       = 'max_targets_hit'
    'duration'         = 'duration'
    'magnitude'        = 'magnitude'
    'mag'              = 'magnitude'
    'heal'             = 'heal_scale'
    'resistance'       = 'resistance_scale'
    'defense'          = 'defense_scale'
    'hit points'       = 'hp'
    'hp'               = 'hp'
    'movement speed'   = 'movement_speed_modifier'
    'speed'            = 'movement_speed_modifier'
    'tohit'            = 'to_hit_modifier'
    'to-hit'           = 'to_hit_modifier'
    'to hit'           = 'to_hit_modifier'
    'knockback'        = 'knockback'
    'kb'               = 'knockback'
    'interrupt time'   = 'interrupt_time'
}

function Get-NormalizedSegment {
    param([string]$Seg)
    $s = $Seg.Trim()
    $s = $s -replace '^\s*[•\-\*\d\.\)]+\s*',''
    $s = $s -replace ':\s*$',''
    $s = $s -replace "[’']", ''
    $s = $s -replace '[^A-Za-z0-9 _-]+', ' '
    $s = ($s -replace '\s+', ' ').Trim()
    if ($s -eq '') { return $null }
    return ($s -replace ' ', '_')
}

function Build-EntityPath {
    param([string[]]$Stack)
    # Skip: structural headings, generic section labels, dates, and overlong
    # narrative segments (the wiki sometimes makes long sentences into headings,
    # e.g. "Shadow Maul (Tanker, Scrapper, Brute, Stalker) is now a much larger
    # faster cone..." — we keep only the first phrase up to the first colon /
    # parenthesis, but if even that is over 40 chars we drop the segment).
    $skipExact = @('powers','patch notes','contents','overview','table of contents',
                   'target cap changes','recharge changes','damage changes','endurance changes',
                   'quality of life','bug fixes','general','features','content',
                   'changes','new powersets','new powers','marquee features',
                   'epic ancillary power pools','epic / ancillary power pools',
                   'epic / ancillary power pool adjustments','various power updates',
                   'miscellaneous','powers gameplay adjustments')

    # Date patterns the wiki uses as h2 headings.
    $dateRx = '^(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d+(st|nd|rd|th)?,?\s+\d{4}$'

    $segs = @()
    foreach ($h in $Stack) {
        if (-not $h) { continue }
        $low = $h.ToLower().Trim().TrimEnd('.', ':')

        # Date heading
        if ($low -match $dateRx) { continue }
        # Patch labels like "Issue 27 Page 3"
        if ($low -match '^issue\s+\d+(\s+page\s+\d+)?$') { continue }
        # Generic skips
        if ($skipExact -contains $low) { continue }
        if ($skipExact | Where-Object { $low.StartsWith($_) }) { continue }

        # Trim narrative tails: take up through the first colon, period, or
        # parenthesis if the heading is long.
        $clean = $h
        if ($clean.Length -gt 40) {
            $clean = ($clean -split '[:.\(]')[0].Trim()
            if ($clean.Length -gt 40) { continue }   # still too long → drop
        }

        $n = Get-NormalizedSegment $clean
        if ($n) { $segs += $n }
    }
    if ($segs.Count -eq 0) { return $null }
    return ($segs -join '.')
}

function Resolve-Field {
    param([string]$Text)
    $low = $Text.ToLower()
    $orderedKeys = $FieldMap.Keys | Sort-Object -Descending Length
    foreach ($k in $orderedKeys) {
        if ($low -match "(^|[^a-z])$([Regex]::Escape($k))([^a-z]|$)") {
            return $FieldMap[$k]
        }
    }
    return $null
}

function ConvertFrom-ChangeLine {
    param(
        [string]$Line,
        [string]$DefaultField = ''   # field implied by surrounding section heading
    )
    # Returns: @(field, from, to, [inline_path]) on success, where inline_path
    # is non-empty if the line itself encoded an entity path before the numbers
    # (e.g. "Tanker > Super Strength > Foot Stomp 10 => 16").
    $field = Resolve-Field $Line
    if (-not $field -and $DefaultField) { $field = $DefaultField }

    if ($Line -match '(?i)from\s+(-?\d+(?:\.\d+)?)\s+to\s+(-?\d+(?:\.\d+)?)') {
        if ($field) { return @($field, [double]$Matches[1], [double]$Matches[2], '') }
    }
    if ($Line -match '^(?<path>.*?\s>\s.+?)\s+(-?\d+(?:\.\d+)?)\s*(?:=>|→|->)\s*(-?\d+(?:\.\d+)?)\s*$') {
        # Inline-path form: "AT > Powerset > Power 10 => 16"
        # PowerShell's $Matches indexes named groups by name only; unnamed
        # captures get sequential numeric indices 1, 2, ... so $Matches[1]/[2]
        # are the two numbers regardless of the named (?<path>) group.
        if ($field) {
            return @($field, [double]$Matches[1], [double]$Matches[2], $Matches['path'].Trim())
        }
    }
    if ($Line -match '(-?\d+(?:\.\d+)?)\s*(?:=>|→|->)\s*(-?\d+(?:\.\d+)?)') {
        if ($field) { return @($field, [double]$Matches[1], [double]$Matches[2], '') }
    }
    if ($Line -match '(?i)now\s+(-?\d+(?:\.\d+)?).*?was\s+(-?\d+(?:\.\d+)?)') {
        if ($field) { return @($field, [double]$Matches[2], [double]$Matches[1], '') }
    }
    return $null
}

function Get-DefaultFieldForHeading {
    param([string]$Heading)
    if (-not $Heading) { return '' }
    $low = $Heading.ToLower()
    if     ($low -match 'target cap')      { return 'max_targets_hit' }
    elseif ($low -match 'recharge.*chang') { return 'recharge_time' }
    elseif ($low -match 'damage.*chang')   { return 'damage_scale' }
    elseif ($low -match 'endurance.*chang'){ return 'endurance_cost' }
    elseif ($low -match 'cast time chang|activation.*chang') { return 'activation_time' }
    elseif ($low -match 'range.*chang')    { return 'range' }
    elseif ($low -match 'radius.*chang')   { return 'radius' }
    elseif ($low -match 'arc chang')       { return 'arc' }
    return ''
}

function ConvertTo-PlainText {
    param([string]$Html)
    $clean = $Html -replace '(?is)<script.*?</script>',''
    $clean = $clean -replace '(?is)<style.*?</style>',''
    $clean = $clean -replace '<[^>]+>',''
    $clean = [System.Net.WebUtility]::HtmlDecode($clean)
    return ($clean -replace '\s+',' ').Trim()
}

# Find the matching close of an HTML tag using depth counting.
# Returns the index just past the </tag>, or -1 if no match.
function Find-MatchingClose {
    param([string]$Html, [int]$StartAfterOpen, [string]$Tag)
    $openTag  = "<$Tag"
    $closeTag = "</$Tag>"
    $depth = 1
    $i = $StartAfterOpen
    while ($depth -gt 0) {
        $nextOpen  = $Html.IndexOf($openTag,  $i, [StringComparison]::OrdinalIgnoreCase)
        $nextClose = $Html.IndexOf($closeTag, $i, [StringComparison]::OrdinalIgnoreCase)
        if ($nextClose -lt 0) { return -1 }
        if ($nextOpen -ge 0 -and $nextOpen -lt $nextClose) {
            # Confirm it's actually <tag> or <tag …> not <tagx>
            $charAfter = $Html[$nextOpen + $openTag.Length]
            if ($charAfter -eq '>' -or $charAfter -eq ' ' -or $charAfter -eq "`t" -or $charAfter -eq "`r" -or $charAfter -eq "`n") {
                $depth++
                $i = $nextOpen + $openTag.Length
            } else {
                $i = $nextOpen + $openTag.Length
            }
        } else {
            $depth--
            $i = $nextClose + $closeTag.Length
        }
    }
    return $i
}

# Recursively walk a UL block, emitting tokens. Handles arbitrary nesting.
function Add-UlTokens {
    param(
        [string]$Html,
        [int]$Start,            # index just after the opening <ul>
        [int]$End,              # index of the matching </ul>
        [System.Collections.Generic.List[object]]$Tokens
    )
    $i = $Start
    while ($i -lt $End) {
        $liOpen = $Html.IndexOf('<li', $i, [StringComparison]::OrdinalIgnoreCase)
        if ($liOpen -lt 0 -or $liOpen -ge $End) { break }

        # Skip past <li ...>
        $afterLiTag = $Html.IndexOf('>', $liOpen) + 1
        if ($afterLiTag -le 0) { break }

        $liClose = Find-MatchingClose $Html $afterLiTag 'li'
        if ($liClose -lt 0 -or $liClose -gt $End) { break }
        $liInnerEnd = $liClose - '</li>'.Length

        # Look for a nested <ul> that lives directly inside this <li>
        $nestedUl = $Html.IndexOf('<ul', $afterLiTag, [StringComparison]::OrdinalIgnoreCase)
        if ($nestedUl -ge 0 -and $nestedUl -lt $liInnerEnd) {
            # Parent-li with nested ul
            $litext = ConvertTo-PlainText $Html.Substring($afterLiTag, $nestedUl - $afterLiTag)
            $afterUlTag = $Html.IndexOf('>', $nestedUl) + 1
            $ulClose = Find-MatchingClose $Html $afterUlTag 'ul'
            if ($ulClose -lt 0) { $i = $liClose; continue }
            $innerUlEnd = $ulClose - '</ul>'.Length

            if ($litext) {
                $Tokens.Add(@{ type = 'power_open'; text = $litext }) | Out-Null
                Add-UlTokens -Html $Html -Start $afterUlTag -End $innerUlEnd -Tokens $Tokens
                $Tokens.Add(@{ type = 'power_close' }) | Out-Null
            } else {
                # Bare ul without preceding text — recurse without pushing context.
                Add-UlTokens -Html $Html -Start $afterUlTag -End $innerUlEnd -Tokens $Tokens
            }
        } else {
            # Leaf li — change candidate
            $text = ConvertTo-PlainText $Html.Substring($afterLiTag, $liInnerEnd - $afterLiTag)
            if ($text) {
                $Tokens.Add(@{ type = 'change_li'; text = $text }) | Out-Null
            }
        }

        $i = $liClose
    }
}

function ConvertTo-Tokens {
    param([string]$Html)
    $h = $Html -replace '(?is)<script.*?</script>',''
    $h = $h -replace '(?is)<style.*?</style>',''
    # Strip the table-of-contents block — it's an inline <ul> at the top of every
    # wiki page that mirrors the headings and would otherwise generate noise tokens.
    $h = $h -replace '(?is)<div[^>]*id="toc"[^>]*>.*?</div>',''
    $h = $h -replace '(?is)<div[^>]*class="toc"[^>]*>.*?</div>',''

    $tokens = [System.Collections.Generic.List[object]]::new()

    # Walk top-level: find each <hN> or top-level <ul> in document order.
    $idx = 0
    while ($idx -lt $h.Length) {
        # Find next heading or next <ul (whichever comes first)
        $nextHead = -1; $headLevel = 0; $headStart = -1
        foreach ($lvl in 2,3,4,5) {
            $rx = "<h$lvl"
            $pos = $h.IndexOf($rx, $idx, [StringComparison]::OrdinalIgnoreCase)
            if ($pos -ge 0 -and ($nextHead -lt 0 -or $pos -lt $nextHead)) {
                $nextHead = $pos; $headLevel = $lvl
            }
        }
        $nextUl = $h.IndexOf('<ul', $idx, [StringComparison]::OrdinalIgnoreCase)

        if ($nextHead -lt 0 -and $nextUl -lt 0) { break }

        if ($nextHead -ge 0 -and ($nextUl -lt 0 -or $nextHead -lt $nextUl)) {
            # Process heading
            $headStart = $h.IndexOf('>', $nextHead) + 1
            $headClose = Find-MatchingClose $h $headStart "h$headLevel"
            if ($headClose -lt 0) { break }
            $text = ConvertTo-PlainText $h.Substring($headStart, $headClose - $headStart - "</h$headLevel>".Length)
            if ($text) {
                $tokens.Add(@{ type = 'h'; level = $headLevel; text = $text }) | Out-Null
            }
            $idx = $headClose
        } else {
            # Process top-level <ul>
            $afterUlTag = $h.IndexOf('>', $nextUl) + 1
            $ulClose = Find-MatchingClose $h $afterUlTag 'ul'
            if ($ulClose -lt 0) { break }
            $innerEnd = $ulClose - '</ul>'.Length
            Add-UlTokens -Html $h -Start $afterUlTag -End $innerEnd -Tokens $tokens
            $idx = $ulClose
        }
    }
    return $tokens
}

# --- Process all patches ---
$AllChanges = @()
$Unresolved_Lines = @()

foreach ($p in $Patches) {
    $htmlPath = Join-Path $PatchDir "$p.html"
    if (-not (Test-Path $htmlPath)) { Write-Warning "Skip (missing): $p"; continue }
    Write-Host "Parsing $p ..." -ForegroundColor Cyan

    $html = Get-Content $htmlPath -Raw
    $tokens = ConvertTo-Tokens $html

    # Heading stack: index 0=h2, 1=h3, 2=h4, 3=h5. Plus a power stack that
    # tracks parent-li nesting (a parent-li can contain another parent-li).
    # Plus a default-field (from section heading like "Target cap changes:").
    $hstack = @('','','','')
    $pstack = New-Object System.Collections.Generic.Stack[string]
    $defaultField = ''
    $patchChanges = @()

    foreach ($t in $tokens) {
        switch ($t.type) {
            'h' {
                $idx = $t.level - 2  # h2->0, h3->1, h4->2, h5->3
                $hstack[$idx] = $t.text
                for ($k = $idx + 1; $k -lt $hstack.Length; $k++) { $hstack[$k] = '' }
                $pstack.Clear()
                # The most-recent heading at any level may carry a section
                # default (e.g. "Target cap changes"). Re-evaluate from the
                # full chain — innermost wins.
                $defaultField = ''
                for ($k = $hstack.Length - 1; $k -ge 0; $k--) {
                    $df = Get-DefaultFieldForHeading $hstack[$k]
                    if ($df) { $defaultField = $df; break }
                }
            }
            'power_open' {
                $df = Get-DefaultFieldForHeading $t.text
                if ($df) { $defaultField = $df }
                $pstack.Push($t.text)
            }
            'power_close' { if ($pstack.Count -gt 0) { $pstack.Pop() | Out-Null } }
            'change_li' {
                $line = $t.text
                $r = ConvertFrom-ChangeLine -Line $line -DefaultField $defaultField
                if ($r) {
                    $field = $r[0]; $from = $r[1]; $to = $r[2]; $inlinePath = $r[3]
                    if ($inlinePath) {
                        # Line carried its own entity path (e.g. I26P4 format).
                        $segs = ($inlinePath -split '\s*>\s*') | Where-Object { $_ }
                        $fullStack = $segs
                    } else {
                        $fullStack = @($hstack | Where-Object { $_ })
                        if ($pstack.Count -gt 0) {
                            $powerSegs = @($pstack.ToArray())
                            [array]::Reverse($powerSegs)
                            $fullStack += $powerSegs
                        }
                    }
                    $entity = Build-EntityPath $fullStack
                    if (-not $entity) {
                        $Unresolved_Lines += "[$p] no-entity-context: $line"
                        continue
                    }
                    $patchChanges += [pscustomobject]@{
                        patch = $p; entity = $entity; field = $field
                        from = $from; to = $to; raw_line = $line
                        heading_stack = (($fullStack) -join ' > ')
                    }
                }
            }
        }
    }

    $AllChanges += $patchChanges

    # Render per-patch markdown via here-string + table-row loop
    $rows = if ($patchChanges.Count -eq 0) {
        '_No structured numeric changes parsed. Review the wiki page directly for prose changes._'
    } else {
        $header = "| Entity | Field | From | To | Heading Stack |`r`n|---|---|---:|---:|---|"
        $body = (
            $patchChanges
            | Sort-Object entity, field
            | ForEach-Object { "| $($_.entity) | $($_.field) | $($_.from) | $($_.to) | $($_.heading_stack) |" }
        ) -join "`r`n"
        "$header`r`n$body"
    }

    $patchMd = @"
# $p — extracted numeric changes

Source: https://homecoming.wiki/wiki/$p
Parsed: $(Get-Date -Format 'yyyy-MM-dd HH:mm')
Changes extracted: $($patchChanges.Count)

$rows
"@

    Set-Content -Path (Join-Path $HistDir "$p.md") -Value $patchMd -Encoding UTF8
    Write-Host "  $($patchChanges.Count) changes"
}

# --- Consolidate (latest-wins) ---
Write-Host "`nConsolidating overrides (latest-wins)..." -ForegroundColor Cyan

# Step 1: build per-(entity, field) history lists.
$historyByKey = @{}
foreach ($c in $AllChanges) {
    $key = "$($c.entity)::$($c.field)"
    if (-not $historyByKey.ContainsKey($key)) { $historyByKey[$key] = @() }
    $historyByKey[$key] += [pscustomobject]@{
        patch = $c.patch
        from  = $c.from
        to    = $c.to
    }
}

# Step 2: build entity-grouped overrides. Latest entry in history wins.
$grouped = @{}
foreach ($key in $historyByKey.Keys) {
    $entity, $field = $key -split '::', 2
    $hist = @($historyByKey[$key])
    $latest = $hist[-1]
    if (-not $grouped.ContainsKey($entity)) { $grouped[$entity] = @{} }
    $grouped[$entity][$field] = [pscustomobject]@{
        value          = $latest.to
        source_patch   = $latest.patch
        previous_value = $latest.from
        change_count   = $hist.Count
        history        = $hist
    }
}

$out = [ordered]@{
    schema_version = 1
    generated_at   = (Get-Date -Format 'o')
    note           = 'Latest-wins consolidation of structured numeric changes from Homecoming I26P1 through I28P3 patch notes. Parser: tools/parse-patches.ps1. When a (entity, field) pair is in this map, the canonical zip value is stale; prefer this override.'
    source_chronology = $Patches
    total_distinct_overrides = $historyByKey.Count
    total_extracted_records  = $AllChanges.Count
    fields_overridden_summary = ($AllChanges | Group-Object field | ForEach-Object { @{ field = $_.Name; count = $_.Count } })
    overrides = $grouped
}

$jsonOut = Join-Path $DiffDir 'current_overrides.json'
$out | ConvertTo-Json -Depth 16 | Set-Content $jsonOut -Encoding UTF8
Write-Host "Wrote $jsonOut" -ForegroundColor Green
Write-Host "  $($AllChanges.Count) raw changes; $($historyByKey.Count) distinct (entity, field) pairs after dedup"

$AllChanges | Group-Object field | Sort-Object Count -Descending |
    Format-Table @{N='Field';E={$_.Name}}, @{N='Count';E={$_.Count}} -AutoSize

# Unresolved log
if ($Unresolved_Lines.Count -gt 0) {
    $body = ($Unresolved_Lines | Select-Object -First 200) -join "`r`n"
    if ($Unresolved_Lines.Count -gt 200) {
        $body = "$body`r`n... ($($Unresolved_Lines.Count - 200) more, truncated)"
    }
    $unresolvedMd = @"
# Unresolved patch lines — needs manual review

Lines that matched a numeric-change pattern but couldn't be classified by entity path. Walk these manually and either: add to current_overrides.json by hand, or extend tools/parse-patches.ps1 to handle the pattern.

Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm')
Total: $($Unresolved_Lines.Count)

``````
$body
``````
"@
    Set-Content -Path $Unresolved -Value $unresolvedMd -Encoding UTF8
    Write-Host "Unresolved: $($Unresolved_Lines.Count) lines → $Unresolved" -ForegroundColor Yellow
} elseif (Test-Path $Unresolved) {
    Remove-Item $Unresolved -Force
}
