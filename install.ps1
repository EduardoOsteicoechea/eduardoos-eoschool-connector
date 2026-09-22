# Install Eduardo OS eoschool connector as .\.eoschool and wire Cursor skill.
$ErrorActionPreference = "Stop"
$RepoUrl = if ($env:EDUARDOOS_EOSCHOOL_URL) { $env:EDUARDOOS_EOSCHOOL_URL } else { "https://github.com/EduardoOsteicoechea/eduardoos-eoschool-connector.git" }
$Root = (Get-Location).Path
$Target = Join-Path $Root ".eoschool"
$SkillSrc = Join-Path $Target "skill\eoschool"
$SkillDst = Join-Path $Root ".cursor\skills\eoschool"

if ((Test-Path $Target) -and -not (Test-Path (Join-Path $Target ".git"))) {
  Write-Error "Refusing: $Target exists and is not a git clone."
}

if (Test-Path (Join-Path $Target ".git")) {
  try { git -C $Target pull --ff-only } catch { }
} else {
  git clone --depth 1 $RepoUrl $Target
}

New-Item -ItemType Directory -Force -Path (Join-Path $Root ".cursor\skills") | Out-Null
if (Test-Path $SkillDst) { Remove-Item -Recurse -Force $SkillDst }
Copy-Item -Recurse -Force $SkillSrc $SkillDst

$envFile = Join-Path $Target ".env"
$envExample = Join-Path $Target ".env.example"
if (-not (Test-Path $envFile) -and (Test-Path $envExample)) {
  Copy-Item $envExample $envFile
  Write-Host "Created $envFile â€” add your API key (UI only at eduardoos.com)."
}

Write-Host "Installed connector at $Target"
Write-Host "Cursor skill at $SkillDst (name: eoschool)"
Write-Host "Read $SkillSrc\CAVEATS.md before posting materials."

