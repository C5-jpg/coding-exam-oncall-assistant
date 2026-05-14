$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$baseOut = Join-Path $root "screenshots\reference"
$url = "https://antigravity.google/"

$viewports = @(
  @{ Name = "1440x900"; Width = 1440; Height = 900 },
  @{ Name = "1366x768"; Width = 1366; Height = 768 },
  @{ Name = "1024x768"; Width = 1024; Height = 768 },
  @{ Name = "768x1024"; Width = 768; Height = 1024 },
  @{ Name = "390x844"; Width = 390; Height = 844 },
  @{ Name = "375x812"; Width = 375; Height = 812 }
)

$states = @(
  @{ Name = "initial"; Timeout = 120 },
  @{ Name = "after-1s"; Timeout = 1000 },
  @{ Name = "after-3s"; Timeout = 3000 }
)

foreach ($viewport in $viewports) {
  $dir = Join-Path $baseOut $viewport.Name
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
  $size = "$($viewport.Width),$($viewport.Height)"

  foreach ($state in $states) {
    $out = Join-Path $dir "$($state.Name).png"
    playwright screenshot --wait-for-timeout $state.Timeout --viewport-size $size $url $out
  }

  $full = Join-Path $dir "full-page-after-3s.png"
  playwright screenshot --full-page --wait-for-timeout 3000 --viewport-size $size $url $full
}
