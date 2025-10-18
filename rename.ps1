$OutputEncoding = [System.Text.Encoding]::UTF8

$directory = "E:\Torrents\ACDC\"
cd $directory
$mp3_files = Get-ChildItem *.mp3

$band = "ACDC"
$string_to_replace = "^\d{2}\.(.*)"

foreach ($file in $mp3_files) {
    $newName = "$($band) - $($file.Name.Substring(4))"
    
    Rename-Item $file.Name -NewName $newName
    Write-Host "Renamed '$($file.Name)' to '$newName'"
    
}

cd E:\Lander\Muziek