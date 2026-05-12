# -----------------------------------------------------------------------------
# File: scripts/clean_project.ps1
# Purpose:
# Remove generated cache, coverage, build, and temporary files from the project
# workspace.
# Behavior:
# Scans the repository root while skipping protected directories, then removes
# Python caches, test caches, coverage outputs, egg-info metadata, build
# artifacts, and optional log files.
# Notes:
# The script does not remove .venv, .git, or logs by default. Build artifacts are
# removed by default because they are reproducible outputs. Use
# -IncludeBuildArtifacts:$false to preserve build, dist, and spec files.
# -----------------------------------------------------------------------------

[CmdletBinding()]
param(
	[string]$RootPath = (Join-Path $PSScriptRoot ".."),

	[switch]$DryRun,

	[bool]$IncludeBuildArtifacts = $true,

	[switch]$IncludeLogs
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-ProjectRoot {
	param(
		[Parameter(Mandatory = $true)]
		[string]$Path
	)

	$resolvedPath = (Resolve-Path -LiteralPath $Path).Path
	$pyprojectPath = Join-Path $resolvedPath "pyproject.toml"

	if (-not (Test-Path -LiteralPath $pyprojectPath -PathType Leaf)) {
		throw "The path '$resolvedPath' does not look like the project root because pyproject.toml was not found."
	}

	return $resolvedPath
}

function Test-IsCleanupDirectory {
	param(
		[Parameter(Mandatory = $true)]
		[System.IO.DirectoryInfo]$Item,

		[Parameter(Mandatory = $true)]
		[string[]]$CleanupDirectoryNames
	)

	if ($CleanupDirectoryNames -contains $Item.Name) {
		return $true
	}

	if ($Item.Name -like "*.egg-info") {
		return $true
	}

	return $false
}

function Test-IsCleanupFile {
	param(
		[Parameter(Mandatory = $true)]
		[System.IO.FileInfo]$Item,

		[Parameter(Mandatory = $true)]
		[string[]]$CleanupFileNames,

		[Parameter(Mandatory = $true)]
		[string[]]$CleanupFilePatterns
	)

	if ($CleanupFileNames -contains $Item.Name) {
		return $true
	}

	foreach ($pattern in $CleanupFilePatterns) {
		if ($Item.Name -like $pattern) {
			return $true
		}
	}

	return $false
}

function Get-CleanupCandidates {
	param(
		[Parameter(Mandatory = $true)]
		[string]$StartPath,

		[Parameter(Mandatory = $true)]
		[string[]]$IgnoredDirectoryNames,

		[Parameter(Mandatory = $true)]
		[string[]]$CleanupDirectoryNames,

		[Parameter(Mandatory = $true)]
		[string[]]$CleanupFileNames,

		[Parameter(Mandatory = $true)]
		[string[]]$CleanupFilePatterns
	)

	$pendingDirectories = [System.Collections.Generic.Stack[string]]::new()
	$pendingDirectories.Push($StartPath)

	while ($pendingDirectories.Count -gt 0) {
		$currentDirectory = $pendingDirectories.Pop()

		$items = Get-ChildItem `
			-LiteralPath $currentDirectory `
			-Force `
			-ErrorAction SilentlyContinue

		foreach ($item in $items) {
			if ($item.PSIsContainer) {
				if ($IgnoredDirectoryNames -contains $item.Name) {
					continue
				}

				if (
					Test-IsCleanupDirectory `
						-Item $item `
						-CleanupDirectoryNames $CleanupDirectoryNames
				) {
					$item
					continue
				}

				$pendingDirectories.Push($item.FullName)
				continue
			}

			if (
				Test-IsCleanupFile `
					-Item $item `
					-CleanupFileNames $CleanupFileNames `
					-CleanupFilePatterns $CleanupFilePatterns
			) {
				$item
			}
		}
	}
}

function Remove-CleanupItem {
	param(
		[Parameter(Mandatory = $true)]
		[System.IO.FileSystemInfo]$Item,

		[Parameter(Mandatory = $true)]
		[bool]$OnlyPreview
	)

	if ($OnlyPreview) {
		Write-Host "[dry-run] $($Item.FullName)"
		return
	}

	Remove-Item `
		-LiteralPath $Item.FullName `
		-Recurse `
		-Force `
		-ErrorAction Stop

	Write-Host "Removed: $($Item.FullName)"
}

$projectRoot = Resolve-ProjectRoot -Path $RootPath

$ignoredDirectoryNames = @(
	".git",
	".hg",
	".svn",
	".venv",
	"venv",
	"env",
	"node_modules"
)

$cleanupDirectoryNames = @(
	"__pycache__",
	".pytest_cache",
	".ruff_cache",
	".mypy_cache",
	".pyre",
	".pytype",
	".hypothesis",
	".tox",
	".nox",
	"htmlcov"
)

$cleanupFileNames = @(
	".coverage",
	"coverage.xml",
	"junit.xml",
	"pytestdebug.log",
	"Thumbs.db",
	".DS_Store"
)

$cleanupFilePatterns = @(
	"*.pyc",
	"*.pyo",
	".coverage.*"
)

if ($IncludeBuildArtifacts) {
	$cleanupDirectoryNames += @(
		"build",
		"dist"
	)

	$cleanupFilePatterns += @(
		"*.spec"
	)
}

if ($IncludeLogs) {
	$cleanupDirectoryNames += @(
		"logs"
	)
}

Write-Host "Project root: $projectRoot"

if ($DryRun) {
	Write-Host "Dry run enabled. No files will be removed."
}

if ($IncludeBuildArtifacts) {
	Write-Host "Build artifact cleanup enabled."
}
else {
	Write-Host "Build artifact cleanup disabled."
}

if ($IncludeLogs) {
	Write-Host "Log cleanup enabled."
}

$candidates = @(
	Get-CleanupCandidates `
		-StartPath $projectRoot `
		-IgnoredDirectoryNames $ignoredDirectoryNames `
		-CleanupDirectoryNames $cleanupDirectoryNames `
		-CleanupFileNames $cleanupFileNames `
		-CleanupFilePatterns $cleanupFilePatterns
)

if ($candidates.Count -eq 0) {
	Write-Host "Nothing to clean."
	exit 0
}

foreach ($candidate in $candidates) {
	Remove-CleanupItem -Item $candidate -OnlyPreview ([bool]$DryRun)
}

Write-Host "Cleanup completed. Items processed: $($candidates.Count)."