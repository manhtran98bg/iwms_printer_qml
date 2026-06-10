param(
    [string]$Python = ".\venv\Scripts\python.exe",
    [string]$AppName = "DFPrinter"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PythonPath = Join-Path $ProjectRoot $Python
$EntryPoint = Join-Path $ProjectRoot "src\main.py"
$IconPath = Join-Path $ProjectRoot "src\assets\icon\icon.ico"
$DistPath = Join-Path $ProjectRoot "dist"
$BuildPath = Join-Path $ProjectRoot "build"
$SpecPath = Join-Path $ProjectRoot "$AppName.spec"

if (-not (Test-Path -LiteralPath $PythonPath -PathType Leaf)) {
    throw "Python virtual environment not found: $PythonPath"
}

if (-not (Test-Path -LiteralPath $EntryPoint -PathType Leaf)) {
    throw "Application entry point not found: $EntryPoint"
}

if (-not (Test-Path -LiteralPath $IconPath -PathType Leaf)) {
    throw "Application icon not found: $IconPath"
}

$PreviousErrorActionPreference = $ErrorActionPreference
$ErrorActionPreference = "SilentlyContinue"
& $PythonPath -c "import PyInstaller" *> $null
$PyInstallerAvailable = $LASTEXITCODE -eq 0
$ErrorActionPreference = $PreviousErrorActionPreference

if (-not $PyInstallerAvailable) {
    Write-Host "Installing PyInstaller..."
    & $PythonPath -m pip install PyInstaller
    if ($LASTEXITCODE -ne 0) {
        throw "Could not install PyInstaller."
    }
}

$PyInstallerArgs = @(
    "-m", "PyInstaller",
    "--noconfirm",
    "--clean",
    "--onefile",
    "--windowed",
    "--name", $AppName,
    "--icon", $IconPath,
    "--distpath", $DistPath,
    "--workpath", $BuildPath,
    "--specpath", $ProjectRoot,
    "--paths", $ProjectRoot,
    "--add-data", "$ProjectRoot\src\views;src\views",
    "--add-data", "$ProjectRoot\src\assets;src\assets",
    "--hidden-import", "uvicorn.logging",
    "--hidden-import", "uvicorn.loops.auto",
    "--hidden-import", "uvicorn.protocols.http.auto",
    "--hidden-import", "uvicorn.protocols.websockets.auto",
    "--hidden-import", "uvicorn.lifespan.on",
    $EntryPoint
)

Write-Host "Building $AppName.exe..."
& $PythonPath @PyInstallerArgs
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller build failed with exit code $LASTEXITCODE."
}

$ExePath = Join-Path $DistPath "$AppName.exe"
Write-Host ""
Write-Host "Build completed:"
Write-Host $ExePath
