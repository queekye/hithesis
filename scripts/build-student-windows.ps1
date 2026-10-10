param(
    [string]$Main = "thesis",
    [string]$WorkingDirectory = (Join-Path (Split-Path -Parent $PSScriptRoot) "student"),
    [ValidateRange(0, 3)]
    [int]$ExtraXeLaTeXPasses = 0,
    [Alias("NoLinks")]
    [switch]$NoPageLinks,
    [string]$NoLinksOutput = "",
    [string]$PythonExe = ""
)

# Only existing tools are used. This script never installs or repairs TeX/Python.
$ErrorActionPreference = "Stop"
$repositoryRoot = Split-Path -Parent $PSScriptRoot

function Resolve-Tool {
    param([string]$Name)
    $command = Get-Command $Name -CommandType Application -ErrorAction SilentlyContinue
    if (-not $command) {
        throw "Required tool '$Name' was not found. Install/configure it yourself or supply its path."
    }
    return $command.Source
}

function Invoke-Checked {
    param([string]$Label, [scriptblock]$Command)
    Write-Host "==> $Label"
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$Label failed with exit code $LASTEXITCODE."
    }
}

if (-not (Test-Path -LiteralPath $WorkingDirectory -PathType Container)) {
    throw "Working directory does not exist: $WorkingDirectory"
}
if ($Main.EndsWith(".tex", [System.StringComparison]::OrdinalIgnoreCase)) {
    $Main = $Main.Substring(0, $Main.Length - 4)
}
if ([string]::IsNullOrWhiteSpace($Main) -or $Main -match '[/\\]' -or $Main.StartsWith("-")) {
    throw "-Main must be a filename without a directory (for example: thesis or thesis.tex)."
}
$resolvedWorkingDirectory = (Resolve-Path -LiteralPath $WorkingDirectory).Path
$sourcePath = Join-Path $resolvedWorkingDirectory "$Main.tex"
if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) {
    throw "Main TeX file does not exist: $sourcePath"
}
$runtimeDirectory = $null
$styleDirectory = $null
foreach ($candidate in @($resolvedWorkingDirectory, (Join-Path $resolvedWorkingDirectory "runtime"))) {
    $completeRuntime = $true
    foreach ($name in @("hithesisbook.cls", "hithesisbook.cfg", "hithesis.sty")) {
        if (-not (Test-Path -LiteralPath (Join-Path $candidate $name) -PathType Leaf)) {
            $completeRuntime = $false
        }
    }
    if ($completeRuntime) {
        $runtimeDirectory = $candidate
        $styleDirectory = $candidate
        break
    }
}
if (-not $runtimeDirectory) {
    $upstreamStyleDirectory = Join-Path $repositoryRoot "examples/hitbook/chinese"
    if ((Test-Path -LiteralPath (Join-Path $repositoryRoot "hithesisbook.cls") -PathType Leaf) -and
        (Test-Path -LiteralPath (Join-Path $repositoryRoot "hithesisbook.cfg") -PathType Leaf) -and
        (Test-Path -LiteralPath (Join-Path $upstreamStyleDirectory "hithesis.sty") -PathType Leaf)) {
        $runtimeDirectory = $repositoryRoot
        $styleDirectory = $upstreamStyleDirectory
    } else {
        throw "Student runtime is incomplete (hithesisbook.cls, hithesisbook.cfg, hithesis.sty). Run scripts/prepare-student-windows.cmd in the full repository, or unpack a prepared student release."
    }
}
if ($NoLinksOutput -and -not $NoPageLinks) {
    throw "-NoLinksOutput requires -NoPageLinks."
}

$xelatex = Resolve-Tool "xelatex"
$bibtex = Resolve-Tool "bibtex"
$pdfPath = Join-Path $resolvedWorkingDirectory "$Main.pdf"
if ($NoPageLinks) {
    $postprocessor = Join-Path $PSScriptRoot "remove_pdf_page_links.py"
    if (-not (Test-Path -LiteralPath $postprocessor -PathType Leaf)) {
        throw "PDF postprocessor was not found: $postprocessor"
    }
    if ($PythonExe) { $python = Resolve-Tool $PythonExe }
    else { $python = Resolve-Tool "python" }
    Invoke-Checked "Check pypdf dependency" {
        & $python -c "from pypdf import PdfReader, PdfWriter; assert hasattr(PdfWriter, 'remove_annotations'), 'pypdf>=6,<7 is required'"
    }
    if (-not $NoLinksOutput) { $NoLinksOutput = "${Main}_no_links.pdf" }
    if (-not [System.IO.Path]::IsPathRooted($NoLinksOutput)) {
        $NoLinksOutput = Join-Path $resolvedWorkingDirectory $NoLinksOutput
    }
    $noLinksPath = [System.IO.Path]::GetFullPath($NoLinksOutput)
    if ([string]::Equals($noLinksPath, [System.IO.Path]::GetFullPath($pdfPath), [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "The no-links output must differ from the original compiled PDF: $pdfPath"
    }
}

$oldTexInputs = $env:TEXINPUTS
$oldBstInputs = $env:BSTINPUTS
Push-Location -LiteralPath $resolvedWorkingDirectory
try {
    # Final empty path component preserves kpathsea's normal system search path.
    $separator = [System.IO.Path]::PathSeparator
    $env:TEXINPUTS = ".${separator}${runtimeDirectory}${separator}${styleDirectory}${separator}${repositoryRoot}${separator}${oldTexInputs}${separator}"
    $env:BSTINPUTS = ".${separator}${runtimeDirectory}${separator}${repositoryRoot}${separator}${oldBstInputs}${separator}"
    Invoke-Checked "XeLaTeX pass 1" { & $xelatex -interaction=nonstopmode -halt-on-error "$Main.tex" }
    Invoke-Checked "BibTeX" { & $bibtex $Main }
    Invoke-Checked "XeLaTeX pass 2" { & $xelatex -interaction=nonstopmode -halt-on-error "$Main.tex" }
    Invoke-Checked "XeLaTeX pass 3" { & $xelatex -interaction=nonstopmode -halt-on-error "$Main.tex" }
    for ($passOffset = 1; $passOffset -le $ExtraXeLaTeXPasses; $passOffset++) {
        $passNumber = 3 + $passOffset
        Invoke-Checked "XeLaTeX pass $passNumber" { & $xelatex -interaction=nonstopmode -halt-on-error "$Main.tex" }
    }

    $errorPatterns = @(
        "^!", "Undefined control sequence",
        "LaTeX Warning: (Reference|Citation).*undefined", "undefined references",
        "There were undefined", "Package natbib Warning", "Rerun to get",
        "BibTeX warning", "I couldn't open", "Emergency stop", "Fatal error"
    )
    $logFiles = @("$Main.log", "$Main.blg") | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf }
    $hits = @()
    if ($logFiles.Count -gt 0) { $hits = @(Select-String -LiteralPath $logFiles -Pattern $errorPatterns) }
    if ($hits.Count -gt 0) {
        $hits | ForEach-Object { Write-Host ("{0}:{1}: {2}" -f $_.Path, $_.LineNumber, $_.Line.Trim()) }
        throw "Build log checks found unresolved references or errors. Inspect the log before submission."
    }
    if (-not (Test-Path -LiteralPath $pdfPath -PathType Leaf)) {
        throw "Expected output PDF was not generated: $pdfPath"
    }
    Write-Host ("OK: {0} ({1} bytes)" -f $pdfPath, (Get-Item -LiteralPath $pdfPath).Length)
    if ($NoPageLinks) {
        Invoke-Checked "Remove PDF page links (preserve bookmarks and original PDF)" {
            & $python $postprocessor $pdfPath $noLinksPath --force
        }
        Write-Host ("OK (no page links): {0}" -f $noLinksPath)
    }
}
finally {
    $env:TEXINPUTS = $oldTexInputs
    $env:BSTINPUTS = $oldBstInputs
    Pop-Location
}
