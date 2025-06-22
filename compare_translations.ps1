# Compare translation files
Write-Host "Comparing translation files..." -ForegroundColor Green

$heContent = Get-Content "src/i18n/locales/he/translation.json" -Raw | ConvertFrom-Json
$enContent = Get-Content "src/i18n/locales/en/translation.json" -Raw | ConvertFrom-Json

function Get-AllKeys {
    param($obj, $prefix = "")
    
    $keys = @()
    foreach ($prop in $obj.PSObject.Properties) {
        $currentKey = if ($prefix) { "$prefix.$($prop.Name)" } else { $prop.Name }
        $keys += $currentKey
        
        if ($prop.Value -is [PSCustomObject]) {
            $keys += Get-AllKeys $prop.Value $currentKey
        }
    }
    return $keys
}

$heKeys = Get-AllKeys $heContent | Sort-Object
$enKeys = Get-AllKeys $enContent | Sort-Object

Write-Host "Hebrew keys: $($heKeys.Count)" -ForegroundColor Yellow
Write-Host "English keys: $($enKeys.Count)" -ForegroundColor Yellow

$missingInEn = $heKeys | Where-Object { $_ -notin $enKeys }
$missingInHe = $enKeys | Where-Object { $_ -notin $heKeys }

if ($missingInEn) {
    Write-Host "`nMissing in English:" -ForegroundColor Red
    $missingInEn | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
}

if ($missingInHe) {
    Write-Host "`nMissing in Hebrew:" -ForegroundColor Yellow  
    $missingInHe | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
}

if (-not $missingInEn -and -not $missingInHe) {
    Write-Host "`nAll translations match!" -ForegroundColor Green
}

Write-Host "`nComparison complete." -ForegroundColor Green 