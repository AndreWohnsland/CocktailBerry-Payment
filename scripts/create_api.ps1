param (
    [string]$ProjectRoot
)

$WshShell = New-Object -ComObject WScript.Shell

$Startup = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"

$ApiShortcut = $WshShell.CreateShortcut(
    "$Startup\CocktailBerry API.lnk"
)

$ApiShortcut.TargetPath = "uv"
$ApiShortcut.Arguments = "run --extra api -m cocktailberry.api"
$ApiShortcut.WorkingDirectory = $ProjectRoot
$ApiShortcut.Save()