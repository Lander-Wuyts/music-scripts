$OutputEncoding = [System.Text.Encoding]::UTF8

$band = $null
$substringLength = $null
$executeFlag = $false

for ($i = 0; $i -lt $args.Length; $i++) {
    if ($args[$i] -eq '-e') {
        $executeFlag = $true
    } elseif ($args[$i] -eq '-n' -and $i + 1 -lt $args.Length) {
        $band = $args[$i + 1]
        $i++  # Skip the next argument since it's the value for -n
    } elseif ($args[$i] -eq '-s' -and $i + 1 -lt $args.Length) {
        $substringLength = $args[$i + 1]
        $i++
    }
}

if (!$band) {
    Write-Host "Set band name with '-n <band name>'"
    exit 1
}

if (!$substringLength) {
    Write-Host "Set substring length with '-s <nr>'"
    exit 1
}

if (!$executeFlag) {
    Write-Host "######################## Test mode ########################"
}


$directory = "E:\Torrents\$($band)\"
$mp3_files = Get-ChildItem $directory*.mp3

foreach ($file in $mp3_files) {
    $newName = "$($band) - $($file.Name.Substring($substringLength))"
    
    if ($executeFlag) {
        Rename-Item -Path $file -NewName $newName
        Write-Host "Renamed '$($file.Name)' to '$newName'"
    } else {
        Write-Host "# To change: '$($file.Name)' ==> '$newName'"
    }    
}

if (!$executeFlag) {
    Write-Host "Use flag '-e' to execute program"
}
