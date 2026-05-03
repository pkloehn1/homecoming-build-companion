<#
.SYNOPSIS
  Convert a .docx to markdown. No pandoc required — walks the OOXML
  document.xml directly, preserving headings, paragraphs, lists, tables,
  and image placeholders.

.DESCRIPTION
  A .docx is a zip with word/document.xml inside. We extract that, parse it
  with [xml], and emit markdown:
    Heading1..Heading6 styles  → # .. ######
    bullet/numbered lists      → -/1.
    paragraphs                 → blank-line separated text
    tables                     → GFM tables
    embedded images            → ![image](path) with file copied

  Run-level bold/italic is converted to **/_..._. Hyperlinks rendered as
  [text](url) when the relationship is resolvable.

.PARAMETER Source
  Path to a .docx file.

.PARAMETER OutDir
  Folder to write the markdown + extracted images into. The .md filename
  is the docx basename. Images go into <OutDir>/<basename>.assets/.

.EXAMPLE
  & extract-docx.ps1 -Source "$env:USERPROFILE\Downloads\RechargeGuide.docx" `
                     -OutDir "$env:USERPROFILE\repos\homecoming-build-companion\inbox"
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$Source,
    [Parameter(Mandatory)] [string]$OutDir
)

$ErrorActionPreference = 'Stop'
$Source = [System.IO.Path]::GetFullPath($Source)
$OutDir = [System.IO.Path]::GetFullPath($OutDir)
if (-not (Test-Path $Source)) { throw "Not found: $Source" }
if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Path $OutDir -Force | Out-Null }

$base = [System.IO.Path]::GetFileNameWithoutExtension($Source)
$assets = Join-Path $OutDir "$base.assets"
$mdPath = Join-Path $OutDir "$base.md"

# --- Unzip into temp ---
$tmp = Join-Path $env:TEMP ("docx-" + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $tmp -Force | Out-Null
try {
    Expand-Archive -Path $Source -DestinationPath $tmp -Force
    $docXml  = Join-Path $tmp 'word\document.xml'
    $relsXml = Join-Path $tmp 'word\_rels\document.xml.rels'
    $mediaDir = Join-Path $tmp 'word\media'
    if (-not (Test-Path $docXml)) { throw "No word/document.xml in $Source — is it really a .docx?" }

    [xml]$doc = Get-Content $docXml -Raw -Encoding UTF8

    # Build relationship map: rId → Target (for hyperlinks + images)
    $relMap = @{}
    if (Test-Path $relsXml) {
        [xml]$rels = Get-Content $relsXml -Raw -Encoding UTF8
        foreach ($r in $rels.Relationships.Relationship) {
            $relMap[$r.Id] = @{ Type = $r.Type; Target = $r.Target; Mode = $r.TargetMode }
        }
    }

    # Copy media files referenced by image relationships
    if (Test-Path $mediaDir) {
        if (-not (Test-Path $assets)) { New-Item -ItemType Directory -Path $assets -Force | Out-Null }
        Copy-Item -Path (Join-Path $mediaDir '*') -Destination $assets -Force
    }

    # XML namespace manager
    $nsMgr = New-Object System.Xml.XmlNamespaceManager $doc.NameTable
    $nsMgr.AddNamespace('w', 'http://schemas.openxmlformats.org/wordprocessingml/2006/main')
    $nsMgr.AddNamespace('a', 'http://schemas.openxmlformats.org/drawingml/2006/main')
    $nsMgr.AddNamespace('pic', 'http://schemas.openxmlformats.org/drawingml/2006/picture')
    $nsMgr.AddNamespace('r', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships')

    # --- Helpers ---
    function Get-RunText {
        param([System.Xml.XmlElement]$Run)
        $sb = [System.Text.StringBuilder]::new()
        $bold   = ($Run.SelectSingleNode('w:rPr/w:b',  $nsMgr)) -ne $null
        $italic = ($Run.SelectSingleNode('w:rPr/w:i',  $nsMgr)) -ne $null
        $tab    = ($Run.SelectSingleNode('w:tab',      $nsMgr)) -ne $null
        $br     = ($Run.SelectSingleNode('w:br',       $nsMgr)) -ne $null
        foreach ($t in $Run.SelectNodes('w:t', $nsMgr)) {
            $null = $sb.Append($t.InnerText)
        }
        $text = $sb.ToString()
        if ($tab) { $text = "`t" + $text }
        if ($br)  { $text = $text + "  `r`n" }
        # Image inside a run
        $blip = $Run.SelectSingleNode('.//a:blip', $nsMgr)
        if ($blip) {
            $rid = $blip.GetAttribute('embed', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships')
            if ($relMap.ContainsKey($rid)) {
                $tgt = $relMap[$rid].Target -replace '^media/',''
                $text = "$text![image]($base.assets/$tgt)"
            }
        }
        if ($text -and $bold)   { $text = "**$text**" }
        if ($text -and $italic) { $text = "*$text*" }
        return $text
    }

    function Get-ParagraphMarkdown {
        param([System.Xml.XmlElement]$Para)
        $styleNode = $Para.SelectSingleNode('w:pPr/w:pStyle', $nsMgr)
        $style     = if ($styleNode) { $styleNode.GetAttribute('val', $nsMgr.LookupNamespace('w')) } else { '' }
        $isList    = ($Para.SelectSingleNode('w:pPr/w:numPr', $nsMgr)) -ne $null

        # Iterate runs and hyperlinks in order
        $partsBuilder = [System.Text.StringBuilder]::new()
        foreach ($child in $Para.ChildNodes) {
            if ($child.LocalName -eq 'r') {
                $null = $partsBuilder.Append((Get-RunText $child))
            }
            elseif ($child.LocalName -eq 'hyperlink') {
                $rid = $child.GetAttribute('id', $nsMgr.LookupNamespace('r'))
                $linkText = ''
                foreach ($r in $child.SelectNodes('w:r', $nsMgr)) {
                    $linkText += Get-RunText $r
                }
                if ($relMap.ContainsKey($rid)) {
                    $url = $relMap[$rid].Target
                    $null = $partsBuilder.Append("[$linkText]($url)")
                } else {
                    $null = $partsBuilder.Append($linkText)
                }
            }
        }
        $text = $partsBuilder.ToString().Trim()
        if (-not $text) { return '' }

        # Map heading styles
        switch -Regex ($style) {
            '^(?:Heading1|Title)$' { return "# $text" }
            '^Heading2$'           { return "## $text" }
            '^Heading3$'           { return "### $text" }
            '^Heading4$'           { return "#### $text" }
            '^Heading5$'           { return "##### $text" }
            '^Heading6$'           { return "###### $text" }
        }
        if ($isList) { return "- $text" }
        return $text
    }

    function Get-TableMarkdown {
        param([System.Xml.XmlElement]$Tbl)
        $rows = @()
        foreach ($tr in $Tbl.SelectNodes('w:tr', $nsMgr)) {
            $cells = @()
            foreach ($tc in $tr.SelectNodes('w:tc', $nsMgr)) {
                $cellText = (
                    $tc.SelectNodes('w:p', $nsMgr) | ForEach-Object {
                        Get-ParagraphMarkdown -Para $_
                    }
                ) -join ' '
                # Pipe in cell content would break GFM table; escape it.
                $cellText = ($cellText -replace '\|','\|').Trim()
                if (-not $cellText) { $cellText = ' ' }
                $cells += $cellText
            }
            if ($cells.Count -gt 0) { $rows += ,@($cells) }
        }
        if ($rows.Count -eq 0) { return '' }
        $colCount = ($rows | Measure-Object -Maximum -Property Count).Maximum
        $sb = [System.Text.StringBuilder]::new()
        $null = $sb.AppendLine('| ' + ($rows[0] -join ' | ') + ' |')
        $null = $sb.AppendLine('|' + (('---|') * $colCount))
        for ($i = 1; $i -lt $rows.Count; $i++) {
            # Pad row if this row has fewer cells than the header
            $padded = $rows[$i]
            while ($padded.Count -lt $colCount) { $padded += ' ' }
            $null = $sb.AppendLine('| ' + ($padded -join ' | ') + ' |')
        }
        return $sb.ToString().TrimEnd()
    }

    # --- Walk body ---
    $body = $doc.SelectSingleNode('//w:body', $nsMgr)
    if (-not $body) { throw 'No <w:body> in document.xml' }
    $output = [System.Text.StringBuilder]::new()
    foreach ($el in $body.ChildNodes) {
        switch ($el.LocalName) {
            'p' {
                $line = Get-ParagraphMarkdown -Para $el
                if ($line) {
                    $null = $output.AppendLine($line)
                    $null = $output.AppendLine()
                }
            }
            'tbl' {
                $tableMd = Get-TableMarkdown -Tbl $el
                if ($tableMd) {
                    $null = $output.AppendLine($tableMd)
                    $null = $output.AppendLine()
                }
            }
            'sectPr' { } # section properties — skip
        }
    }

    Set-Content -Path $mdPath -Value $output.ToString().Trim() -Encoding UTF8
    Write-Host "Wrote $mdPath  ($([math]::Round((Get-Item $mdPath).Length/1KB,1)) KB)" -ForegroundColor Green
    if (Test-Path $assets) {
        $imgCount = (Get-ChildItem $assets -File -ErrorAction SilentlyContinue).Count
        if ($imgCount -gt 0) { Write-Host "  $imgCount asset(s) → $assets" -ForegroundColor DarkGray }
    }
}
finally {
    if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue }
}
