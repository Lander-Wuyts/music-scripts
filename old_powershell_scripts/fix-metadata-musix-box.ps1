# This script writes the metadata of files to mix the name of the file
# The file should be of .mp3 format and be named in the following format: "Artist name - song name.mp3"
# This script should be run in the folder where the files are located
# This script uses the powershell-taglib module (https://github.com/illearth/powershell-taglib)

# To run this script, enter the following PowerShell command first:
# Set-Executionpolicy Unrestricted -Scope Process

# Variables
    # Files
$directory = "Music Box\"
$mp3_files = Get-ChildItem $directory*.mp3
$mp3_files_length = $mp3_files.Length
    # UI
$bar_length = 50
$modified_count = 0
    # Parameters
$last_date_modified = "2022-09-19"
$testing = $false

# Functions
function Get-Artist {

    param (
        $file_name
    )

    $pos = $file_name.IndexOf("-")
    $artist = $file_name.Substring(0,$pos - 1)

    return $artist
}

function Get-Name {

    param (
        $file_name
    )

    $pos1 = $file_name.IndexOf("-")
    $pos2 = $file_name.IndexOf(".mp3")
    $name = $file_name.Substring($pos1 + 2, $pos2-2-$pos1)  # Calculated to compensate for " - "

    return $name
}

function Get-Bar {
    param (
        [int]$CurrentPosition,
        [int]$ListSize
    )
    $bar_length = 50
    
    $bar_complete_length = [Math]::Truncate(($CurrentPosition/$ListSize) * $bar_length)
    $bar_incomplete_length = $bar_length - $bar_complete_length

    return "*" * $bar_complete_length + " " * $bar_incomplete_length
}

# Code
if(!$testing) {
    # Go over every file in the list and adjust the UI accordingly
    for ($index = 0; $index -lt $mp3_files_length; $index++) {
        
        Clear-Host

        # Progress bar
        $bar = Get-Bar -CurrentPosition $index -ListSize $mp3_files_length
        $nr = $index + 1

        Write-Host "File [$nr/$mp3_files_length] [$bar]"

        # Check file
        $mp3_file = $mp3_files[$index]
        Write-Host "Checking $mp3_file"

        # If the dates differ, the file needs to be updated
        $mp3_file_modified = $mp3_file.LastWriteTime.ToString("yyyy-MM-dd")

        if($mp3_file_modified -ne $last_date_modified) {
            #$artist = Get-Artist $mp3_file.Name
            $name = Get-Name $mp3_file.Name

            $mp3_file | set-artist "Music Box"
            $mp3_file | set-title $name

            $modified_count += 1
        }  
    }
    # Finished message
    $bar_full = "*" * $bar_length
    Clear-Host
    Write-Host "File [$mp3_files_length/$mp3_files_length] [$bar_full]"
    Write-Host "All files checked, $modified_count files updated"

} else {
    Write-Host "Testing..."
    Write-Host "Test done!"
}
