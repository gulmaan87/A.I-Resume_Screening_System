# Generate secure secrets for production deployment (PowerShell)

Write-Host "Generating secure secrets for production..." -ForegroundColor Green
Write-Host ""

# Generate JWT Secret Key
$jwtSecret = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
$jwtSecret = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($jwtSecret))

# Generate MongoDB Password
$mongoPassword = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
$mongoPassword = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($mongoPassword))

Write-Host "# Add these to your .env file:" -ForegroundColor Yellow
Write-Host ""
Write-Host "JWT_SECRET_KEY=`"$jwtSecret`"" -ForegroundColor Cyan
Write-Host ""
Write-Host "MONGO_ROOT_PASSWORD=`"$mongoPassword`"" -ForegroundColor Cyan
Write-Host ""
Write-Host "Done! Copy the values above to your .env file." -ForegroundColor Green

