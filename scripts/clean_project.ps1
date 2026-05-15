# -----------------------------------------------------------------------------
# File: scripts/clean_project.ps1
# Purpose:
# Remove generated cache, coverage, build, log, runtime settings, and
# temporary files from the project workspace.
# Behavior:
# Scans the repository root while skipping protected directories, then removes
# Python caches, test caches, coverage outputs, egg-info metadata, build
# artifacts, log directories, and the runtime settings.toml file.
# Notes:
# The script does not remove .venv, .git, or bundled package defaults. Build
# artifacts, logs, and the root runtime settings.toml are removed by default
# because they are reproducible runtime outputs. Use -IncludeBuildArtifacts:$false,
# -PreserveLogs, or -IncludeRuntimeSettings:$false when those files must be kept.
# -----------------------------------------------------------------------------

[CmdletBinding()]
param(
	[string]$RootPath = (Join-Path $PSScriptRoot ".."),

	[switch]$DryRun,

	[bool]$IncludeBuildArtifacts = $true,

	[switch]$IncludeLogs,

	[switch]$PreserveLogs,

	[bool]$IncludeRuntimeSettings = $true
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


function Get-RootCleanupCandidates {
	param(
		[Parameter(Mandatory = $true)]
		[string]$StartPath,

		[string[]]$CleanupRootFileNames = @()
	)

	foreach ($fileName in $CleanupRootFileNames) {
		$candidatePath = Join-Path $StartPath $fileName

		if (Test-Path -LiteralPath $candidatePath -PathType Leaf) {
			Get-Item -LiteralPath $candidatePath -Force
		}
	}
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
$shouldCleanLogs = -not [bool]$PreserveLogs

if ($IncludeLogs) {
	$shouldCleanLogs = $true
}

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

$cleanupRootFileNames = @()

$cleanupFilePatterns = @(
	"*.pyc",
	"*.pyo",
	".coverage.*"
)

if ($IncludeRuntimeSettings) {
	$cleanupRootFileNames += @(
		"settings.toml"
	)
}

if ($IncludeBuildArtifacts) {
	$cleanupDirectoryNames += @(
		"build",
		"dist"
	)

	$cleanupFilePatterns += @(
		"*.spec"
	)
}

if ($shouldCleanLogs) {
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

if ($shouldCleanLogs) {
	Write-Host "Log cleanup enabled."
}
else {
	Write-Host "Log cleanup disabled."
}

if ($IncludeRuntimeSettings) {
	Write-Host "Runtime settings cleanup enabled."
}
else {
	Write-Host "Runtime settings cleanup disabled."
}

$candidates = @(
	Get-RootCleanupCandidates `
		-StartPath $projectRoot `
		-CleanupRootFileNames $cleanupRootFileNames

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