# create_github_project.ps1
<#
.SYNOPSIS
    Creates a GitHub project and issues from a checklist markdown file.

.PARAMETER ChecklistPath
    Path to the checklist markdown file. If not provided, uses default path.

.PARAMETER Repo
    GitHub repository in format 'owner/repo'

.PARAMETER ProjectName
    Name for the GitHub project to create

.EXAMPLE
    .\create_github_project.ps1 -ChecklistPath ".\checklist.md" -Repo "user/repo" -ProjectName "My Project"
#>

param(
    [string]$ChecklistPath = "C:\Users\lenovo\.gemini\antigravity\brain\267fafdc-26cb-4600-a4fd-419c766421c8\admin_menu_checklist.md",
    [string]$Repo = "tirtana888/lms-nusadaya",
    [string]$ProjectName = "Admin Menu Verification"
)

# Try to find GitHub CLI in common locations
$ghPaths = @(
    "C:\Program Files\GitHub CLI\gh.exe",
    "C:\Program Files (x86)\GitHub CLI\gh.exe",
    "$env:LOCALAPPDATA\Programs\GitHub CLI\gh.exe"
)

$ghPath = $null
foreach ($path in $ghPaths) {
    if (Test-Path $path) {
        $ghPath = $path
        break
    }
}

# If not found in common locations, try to find in PATH
if (-not $ghPath) {
    $ghPath = (Get-Command gh -ErrorAction SilentlyContinue).Source
}

# 1. Check prerequisites
Write-Host "--- Checking prerequisites ---" -ForegroundColor Cyan
if (-not $ghPath) {
    Write-Error "GitHub CLI ('gh') is not found. Please install it from https://cli.github.com/ and try again."
    exit 1
}

Write-Host "Found GitHub CLI at: $ghPath" -ForegroundColor Green

# Alias gh to the absolute path for subsequent calls
function gh { & $ghPath $args }


# Check if authenticated
$authStatus = gh auth status 2>&1
if ($authStatus -like "*not logged in*") {
    Write-Error "You are not logged in to GitHub CLI. Please run 'gh auth login' first."
    exit 1
}

Write-Host "Success! GitHub CLI found and authenticated." -ForegroundColor Green

# 2. Extract sections and items from the checklist
if (-not (Test-Path $ChecklistPath)) {
    Write-Error "Checklist file not found at $ChecklistPath"
    exit 1
}

try {
    $content = Get-Content $ChecklistPath -ErrorAction Stop
} catch {
    Write-Error "Failed to read checklist file: $_"
    exit 1
}
$sections = @()
$currentSection = $null
$currentItems = @()

foreach ($line in $content) {
    if ($line -match "^## (.*)") {
        if ($currentSection) {
            $sections += [PSCustomObject]@{
                Title = $currentSection
                Items = $currentItems -join "`n"
            }
        }
        $currentSection = $matches[1]
        $currentItems = @()
    }
    elseif ($line -match "^\| (.*) \| (.*) \| \[ \] \|") {
        # Format as GitHub task list item
        $item = "- [ ] $($matches[1].Trim()) - $($matches[2].Trim())"
        $currentItems += $item
    }
}

# Add last section
if ($currentSection) {
    $sections += [PSCustomObject]@{
        Title = $currentSection
        Items = $currentItems -join "`n"
    }
}

# 3. Create the GitHub Project (V2)
# Note: Creating projects requires the 'project' scope in gh auth.
Write-Host "--- Creating GitHub Project: $ProjectName ---" -ForegroundColor Cyan

# Extract owner from repo parameter
$owner = $Repo.Split('/')[0]

try {
    $projectResult = gh project create --owner $owner --title $ProjectName 2>&1 | Out-String
    
    # Try multiple patterns to extract project ID
    if ($projectResult -match "https://github.com/users/$owner/projects/(\d+)") {
        $projectId = $matches[1]
        Write-Host "Project created successfully with ID: $projectId" -ForegroundColor Green
    } elseif ($projectResult -match "id[:\s]+(\d+)") {
        $projectId = $matches[1]
        Write-Host "Project created successfully with ID: $projectId" -ForegroundColor Green
    } else {
        Write-Warning "Could not extract project ID from output. We will proceed with creating Issues only."
        Write-Host "Output was: $projectResult" -ForegroundColor Yellow
    }
} catch {
    Write-Warning "Could not create project board (requires specific permissions). We will proceed with creating Issues only."
    Write-Host "Error: $_" -ForegroundColor Yellow
}

# 4. Create Issues and Add to Project
Write-Host "--- Creating Issues ---" -ForegroundColor Cyan
foreach ($section in $sections) {
    Write-Host "Creating Issue for section: $($section.Title)..."
    $issueBody = "### Checklist for $($section.Title)`n`n$($section.Items)"
    
    try {
        # Create the issue
        $issueUrl = gh issue create --repo $Repo --title "Verification: $($section.Title)" --body $issueBody 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Issue created: $issueUrl" -ForegroundColor Green
            
            # Link to project if project was created
            if ($projectId) {
                try {
                    Write-Host "Adding to project..."
                    gh project item-add $projectId --owner $owner --url $issueUrl 2>&1 | Out-Null
                    if ($LASTEXITCODE -eq 0) {
                        Write-Host "Added to project successfully" -ForegroundColor Green
                    }
                } catch {
                    Write-Warning "Failed to add issue to project: $_"
                }
            }
        } else {
            Write-Warning "Failed to create issue: $issueUrl"
        }
    } catch {
        Write-Warning "Error creating issue for section '$($section.Title)': $_"
    }
}

Write-Host "`n--- Done! ---" -ForegroundColor Green
Write-Host "Please check your repository Issues and Projects tab on GitHub."
