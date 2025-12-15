Write-Output "~~ Starting CocktailBerry-Payment Windows installer... ~~"
Write-Output "> Installing 'uv' via Astral.sh..."
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
# winget install -e --id astral-sh.uv

$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
Write-Output "'uv' installation complete."

Write-Output "> Installing Git via winget..."
winget install --id Git.Git -e --source winget

Write-Output "> Cloning CocktailBerry-Payment repository..."
Set-Location $env:USERPROFILE
git clone https://github.com/AndreWohnsland/CocktailBerry-Payment.git
Set-Location .\CocktailBerry-Payment\

Write-Output "> Installing CocktailBerry-Payment dependencies..."
uv sync --all-extras --frozen

Write-Output "If you want to use docker, install docker desktop from https://docs.docker.com/desktop/setup/install/windows-install/"