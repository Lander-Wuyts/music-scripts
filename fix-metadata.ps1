# This script writes the metadata of files to mix the name of the file
# The file should be of .mp3 format and be named in the following format: "Artist name - song name.mp3"
# This script uses the powershell-taglib module (https://github.com/illearth/powershell-taglib)

# To run this script, enter the following PowerShell command first:
# Set-Executionpolicy Unrestricted -Scope Process

# Variables
    # Files
$directory = "My playlist\"
$mp3_files = Get-ChildItem $directory*.mp3
    # UI
$bar_length = 50
    # Parameters
$last_date_modified = "2025-08-23"
$testing = $false

function Get-ToDoList {
    param (
        $Files,
        $LastDateModified
    )

    $todo_list = @()

    foreach ($file in $Files)
    {
        $file_modified_date = $file.LastWriteTime.ToString("yyyy-MM-dd")
        if((get-date $file_modified_date) -gt (get-date $LastDateModified)) {
            $todo_list += $file
        }  
    }
    return $todo_list
}

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



function Set-Data {
    param (
        $FileList
    )

    for ($index = 0; $index -lt $FileList.count; $index++) {

        
        Clear-Host

        # Progress bar
        $bar = Get-Bar -CurrentPosition $index -ListSize $FileList.count

        Write-Host "File [$($index + 1)/$($FileList.count)] [$bar]"

        # Check file
        $File = $FileList[$index]
        Write-Host "Checking $File"
        
        $artist = Get-Artist $File.Name
        $name = Get-Name $File.Name

        $File | set-artist $artist
        $File | set-title $name
    }
}

# Code
if(!$testing) {

    $todo_list = Get-ToDoList -Files $mp3_files -LastDateModified $last_date_modified
    $todo_list | Format-Table -Property Name

    $continue = $Host.UI.PromptForChoice("The $($todo_list.count) files above will be modified","Do you want to continue?", $('&Yes', '&No'), 1)
    if ($continue -eq 0){
        Set-Data -FileList $todo_list

        Clear-Host
        Write-Host "File [$($mp3_files.Length)/$($mp3_files.Length)] [$("*" * $bar_length)]"
        Write-Host "All files checked, $($todo_list.count) files updated"
        Write-Host "Don't forget to update the last_date_modified value to $(Get-Date -Format "yyyy-MM-dd")"
    } else {
        Write-Host "No files modified"
    }

} else {
    Write-Host "Testing..."

    Write-Host "Test done!"
}
