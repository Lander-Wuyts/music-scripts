$OutputEncoding = [System.Text.Encoding]::UTF8

$directory = "Queen\"
cd $directory
$mp3_files = Get-ChildItem *.mp3

$band = "Queen"
$string_to_replace = "^\d{2}\.(.*)"

foreach ($file in $mp3_files) {
    # Extract the number and the rest of the file name
    if ($file.Name -match $string_to_replace) {
        $newName = "$($band) -$($matches[1])"
                
        # Rename the file
        Rename-Item $file.Name -NewName $newName
        Write-Host "Renamed '$($file.Name)' to '$newName'"
    }
}

cd ..