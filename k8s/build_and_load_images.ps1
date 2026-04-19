<#
PowerShell helper to build all service images and load them into Minikube.
Run from the repository root in PowerShell.
#>

$services = @(
  'auth-service',
  'api-fetch-service',
  'scraper-service',
  'data-cleaner-service',
  'driver-service',
  'constructor-service',
  'race-service',
  'stats-service',
  'frontend-service'
)

foreach ($s in $services) {
  $path = Join-Path -Path "$(Resolve-Path .).Path" -ChildPath $s
  if (-Not (Test-Path $path)) {
    Write-Host "Skipping $s - directory not found: $path" -ForegroundColor Yellow
    continue
  }

  $imageName = "racemetrics/$s:latest"
  Write-Host "Building $imageName from $path"
  docker build -t $imageName $path
  if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker build failed for $s" -ForegroundColor Red
    exit 1
  }

  Write-Host "Loading $imageName into Minikube"
  minikube image load $imageName
  if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to load $imageName into Minikube" -ForegroundColor Red
    exit 1
  }
}

Write-Host "All images built and loaded into Minikube."
