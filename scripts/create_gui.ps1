param (
    [string]$ProjectRoot
)

$WshShell = New-Object -ComObject WScript.Shell

$TargetExe = "uv"
$GuiArgs   = "run --extra gui -m cocktailberry.gui"
$WorkDir   = $ProjectRoot
$Icon      = "$ProjectRoot\scripts\assets\berry.ico"

# ---- Start Menu (Programs) ----
$ProgramsDir = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs"
$ProgramsShortcut = Join-Path $ProgramsDir "CocktailBerry.lnk"

$Shortcut = $WshShell.CreateShortcut($ProgramsShortcut)
$Shortcut.TargetPath = $TargetExe
$Shortcut.Arguments = $GuiArgs
$Shortcut.WorkingDirectory = $WorkDir
$Shortcut.IconLocation = $Icon
$Shortcut.Save()

# ---- Desktop ----
$DesktopDir = [Environment]::GetFolderPath("Desktop")
$DesktopShortcut = Join-Path $DesktopDir "CocktailBerry.lnk"

$Shortcut = $WshShell.CreateShortcut($DesktopShortcut)
$Shortcut.TargetPath = $TargetExe
$Shortcut.Arguments = $GuiArgs
$Shortcut.WorkingDirectory = $WorkDir
$Shortcut.IconLocation = $Icon
$Shortcut.Save()
