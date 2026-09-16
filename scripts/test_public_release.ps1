$ErrorActionPreference = 'Stop'
$global:PublicReleaseTest = @{
    repo = 'Tachaan/aigenius-copilotsdk-s5ep2'
    calls = [System.Collections.Generic.List[object]]::new()
    visibility = 'private'
    failPages = $false
}
$state = $global:PublicReleaseTest

# Shadow gh so these tests never read or mutate a real repository.
function gh {
    $bodyText = @($input) -join "`n"
    $body = if ($bodyText) { $bodyText | ConvertFrom-Json } else { $null }
    $state = $global:PublicReleaseTest
    $state.calls.Add(@{ args = @($args); body = $body })
    $global:LASTEXITCODE = 0
    $endpoint = $args[1]
    if ($args[0] -eq 'variable') { return }
    if ($endpoint -eq "repos/$($state.repo)" -and $args -notcontains 'PATCH') {
        return (@{
            visibility = $state.visibility
            default_branch = 'main'
            has_pages = $false
        } | ConvertTo-Json)
    }
    if ($endpoint -like '*/rulesets?*') { return '[]' }
    if ($endpoint -like '*/deployment-branch-policies?*') {
        return '{"branch_policies":[]}'
    }
    if ($endpoint -like '*/pages' -and $state.failPages) {
        $global:LASTEXITCODE = 1
        return
    }
    return '{}'
}

$path = Join-Path $PSScriptRoot 'configure_public_release.ps1'
$blocked = $false
try { & $path } catch {
    $blocked = $_.Exception.Message -like 'Repository must already be public*'
}
if (-not $blocked -or $state.calls.Count -ne 1) {
    throw 'Private guard failed'
}

$state.visibility = 'public'
$state.calls.Clear()
& $path
if ($state.calls | Where-Object {
    $_.args[0] -eq 'variable' -or $_.args[1] -like '*/pages'
}) {
    throw 'Pages enabled without opt-in'
}

$state.calls.Clear()
& $path -EnablePages
$variables = @($state.calls | Where-Object { $_.args[0] -eq 'variable' })
if ($variables.Count -ne 2 -or $variables[0].args[-1] -ne 'false' -or
    $variables[1].args[-1] -ne 'true') {
    throw 'Publication gate ordering failed'
}
if ($state.calls | Where-Object {
    $_.body -and $_.body.PSObject.Properties.Name -contains 'visibility'
}) {
    throw 'Unexpected visibility mutation'
}

$state.calls.Clear()
$state.failPages = $true
$failed = $false
try { & $path -EnablePages } catch {
    $failed = $_.Exception.Message -like 'GitHub API failed*'
}
if (-not $failed) { throw 'API failure was swallowed' }
if ($state.calls | Where-Object {
    $_.args[0] -eq 'variable' -and $_.args[-1] -eq 'true'
}) {
    throw 'Gate enabled after failure'
}
Write-Host 'PASS: private refusal, explicit Pages opt-in, and fail-closed deployment.'
Remove-Variable PublicReleaseTest -Scope Global
# The last scenario deliberately simulates gh exiting with code 1.
$global:LASTEXITCODE = 0
