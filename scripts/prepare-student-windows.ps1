param([switch]$SkipDocstrip)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $repoRoot
try {
    if (-not $SkipDocstrip) {
        foreach ($example in @('hitbook/chinese', 'hitbook/english', 'hitart/reports', 'hitart/reportplus')) {
            New-Item -ItemType Directory -Path (Join-Path $repoRoot "examples/$example/figures") -Force | Out-Null
        }
        if (-not (Get-Command latex -ErrorAction SilentlyContinue)) {
            throw 'latex was not found in PATH. Install/configure a TeX distribution first.'
        }
        & latex '-interaction=nonstopmode' '-halt-on-error' 'hithesis.ins'
        if ($LASTEXITCODE -ne 0) { throw "Official docstrip failed: $LASTEXITCODE" }
    }
    $runtimeFiles = @('hithesisbook.cls', 'hithesisbook.cfg', 'hithesis.bst', 'hithesis.ist')
    foreach ($name in $runtimeFiles) {
        Copy-Item -LiteralPath (Join-Path $repoRoot $name) -Destination (Join-Path $repoRoot "student/$name") -Force
    }
    Copy-Item -LiteralPath (Join-Path $repoRoot 'examples/hitbook/chinese/hithesis.sty') -Destination (Join-Path $repoRoot 'student/hithesis.sty') -Force
    Write-Host 'Ready: compile student/thesis.tex with XeLaTeX, BibTeX, XeLaTeX, XeLaTeX.'
} finally { Pop-Location }
