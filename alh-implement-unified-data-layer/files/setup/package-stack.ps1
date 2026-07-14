param(
  [string]$OutputPath = (Join-Path $PSScriptRoot 'alh-unified-data-layer-stack.zip')
)

$ErrorActionPreference = 'Stop'
$filesRoot = Split-Path -Parent $PSScriptRoot
$terraformRoot = Join-Path $PSScriptRoot 'terraform'
$packageRoot = Join-Path $env:TEMP 'alh-unified-data-layer-stack-package'

if (Test-Path -LiteralPath $packageRoot) {
  Remove-Item -LiteralPath $packageRoot -Recurse -Force
}

New-Item -ItemType Directory -Path $packageRoot | Out-Null
Copy-Item -Path (Join-Path $terraformRoot '*') -Destination $packageRoot -Recurse
Copy-Item -LiteralPath (Join-Path $filesRoot 'source-data') -Destination (Join-Path $packageRoot 'source-data') -Recurse
Copy-Item -LiteralPath (Join-Path $filesRoot 'documents') -Destination (Join-Path $packageRoot 'documents') -Recurse
Copy-Item -LiteralPath (Join-Path $filesRoot 'sql') -Destination (Join-Path $packageRoot 'sql') -Recurse

if (Test-Path -LiteralPath $OutputPath) {
  Remove-Item -LiteralPath $OutputPath -Force
}

Compress-Archive -Path (Join-Path $packageRoot '*') -DestinationPath $OutputPath -CompressionLevel Optimal
Remove-Item -LiteralPath $packageRoot -Recurse -Force

Write-Output "Created $OutputPath"
