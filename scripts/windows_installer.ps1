Write-Output "~~ Starting CocktailBerry-Payment Windows installer... ~~"
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
  Write-Output "> Installing 'uv' via Astral.sh..."
  try {
    powershell -ExecutionPolicy Bypass -Command "irm 'https://astral.sh/uv/install.ps1' | iex"
    $machinePath = [System.Environment]::GetEnvironmentVariable('Path','Machine')
    $userPath = [System.Environment]::GetEnvironmentVariable('Path','User')
    $env:Path = "$machinePath;$userPath"
    Write-Output "'uv' installation complete."
  } catch {
    Write-Warning "Failed to install 'uv': $_"
  }
} else {
  Write-Output "'uv' is already installed."
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  Write-Output "> Installing Git via winget..."
  if (Get-Command winget -ErrorAction SilentlyContinue) {
    try {
      winget install --id Git.Git -e --source winget
      Write-Output "Git installation complete."
    } catch {
      Write-Warning "winget failed to install Git: $_"
    }
  } else {
    Write-Warning "winget not available. Please install Git manually from https://git-scm.com/downloads"
  }
} else {
  Write-Output "Git is already installed."
}

Write-Output "> Cloning CocktailBerry-Payment repository..."
Set-Location $env:USERPROFILE
git clone https://github.com/AndreWohnsland/CocktailBerry-Payment.git
Set-Location .\CocktailBerry-Payment\

Write-Output "> Installing CocktailBerry-Payment dependencies..."
uv sync --all-extras --frozen

Write-Output "If you want to use docker, install docker desktop from https://docs.docker.com/desktop/setup/install/windows-install/"