[CmdletBinding()]
param([switch]$EnablePages)

$ErrorActionPreference = 'Stop'
$Repo = 'Tachaan/aigenius-copilotsdk-s5ep2'

function Invoke-RepoApi {
    param(
        [string]$Endpoint,
        [string]$Method = 'GET',
        [object]$Body
    )
    if ($null -eq $Body) {
        $result = gh api "repos/$Repo/$Endpoint" --method $Method
    } else {
        $result = $Body | ConvertTo-Json -Depth 20 -Compress |
            gh api "repos/$Repo/$Endpoint" --method $Method --input -
    }
    if ($LASTEXITCODE -ne 0) {
        throw "GitHub API failed: $Method $Endpoint. Configuration is incomplete."
    }
    if ($result) { return ($result | ConvertFrom-Json) }
}

$repository = gh api "repos/$Repo" | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) { throw 'Cannot read repository settings.' }
if ($repository.visibility -ne 'public') {
    throw 'Repository must already be public. This script never changes visibility.'
}
if ($repository.default_branch -ne 'main') {
    throw 'Expected main as the default branch; review the publishing configuration.'
}

Invoke-RepoApi 'actions/permissions/fork-pr-contributor-approval' 'PUT' @{
    approval_policy = 'all_external_contributors'
} | Out-Null

$security = @{
    security_and_analysis = @{
        secret_scanning = @{ status = 'enabled' }
        secret_scanning_push_protection = @{ status = 'enabled' }
    }
}
$security | ConvertTo-Json -Depth 5 -Compress |
    gh api "repos/$Repo" --method PATCH --input - --silent
if ($LASTEXITCODE -ne 0) { throw 'Could not enable secret scanning / push protection.' }

$ruleName = 'Protect published main'
$rules = @{
    name = $ruleName
    target = 'branch'
    enforcement = 'active'
    bypass_actors = @()
    conditions = @{ ref_name = @{ include = @('refs/heads/main'); exclude = @() } }
    rules = @(@{ type = 'deletion' }, @{ type = 'non_fast_forward' })
}
$existing = @(Invoke-RepoApi 'rulesets?per_page=100') |
    Where-Object { $_.name -eq $ruleName }
if (@($existing).Count -gt 1) { throw "Multiple rulesets named $ruleName." }
if ($existing) {
    Invoke-RepoApi "rulesets/$($existing.id)" 'PUT' $rules | Out-Null
} else {
    Invoke-RepoApi 'rulesets' 'POST' $rules | Out-Null
}

if ($EnablePages) {
    # Fail closed while configuring the environment. This does not unpublish a live site.
    gh variable set ENABLE_PAGES --repo $Repo --body false
    if ($LASTEXITCODE -ne 0) { throw 'Could not close the Pages deployment gate.' }

    Invoke-RepoApi 'environments/github-pages' 'PUT' @{
        deployment_branch_policy = @{
            protected_branches = $false
            custom_branch_policies = $true
        }
    } | Out-Null
    $policies = Invoke-RepoApi 'environments/github-pages/deployment-branch-policies?per_page=100'
    $unexpected = @($policies.branch_policies | Where-Object {
        $_.name -ne 'main' -or $_.type -ne 'branch'
    })
    if ($unexpected.Count -gt 0) {
        throw 'github-pages has non-main deployment policies. Review/remove them before retrying.'
    }
    if (@($policies.branch_policies).Count -eq 0) {
        Invoke-RepoApi 'environments/github-pages/deployment-branch-policies' 'POST' @{
            name = 'main'
            type = 'branch'
        } | Out-Null
    }
    if ($repository.has_pages) {
        Invoke-RepoApi 'pages' 'PUT' @{ build_type = 'workflow' } | Out-Null
    } else {
        Invoke-RepoApi 'pages' 'POST' @{ build_type = 'workflow' } | Out-Null
    }
    gh variable set ENABLE_PAGES --repo $Repo --body true
    if ($LASTEXITCODE -ne 0) { throw 'Could not enable the Pages deployment gate.' }
    Write-Host 'Pages configured. Run Docs site on main, then verify the public URL.'
}
Write-Host 'Public repository guards configured; visibility was not changed.'
