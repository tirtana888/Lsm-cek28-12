$content = Get-Content lang/en/update.php
$newContent = @()
$skip = $false
foreach ($line in $content) {
    if ($line -match "^<<<<<<<") { $skip = $true; continue }
    if ($line -match "^=======") { $skip = $false; continue }
    if ($line -match "^>>>>>>>") { continue }
    if (!$skip) { $newContent += $line }
}
$newContent | Set-Content lang/en/update.php
