param()

$commitMsg = git log -1 --pretty='%B' 2>$null
if ($LASTEXITCODE -ne 0 -or -not $commitMsg -or $commitMsg.Trim() -eq '') { exit 0 }

$parentCount = (git rev-list --count HEAD 2>$null) -as [int]
if ($parentCount -le 1) {
    $files = (git show --stat --name-only --format='' HEAD 2>$null) -join "`n"
} else {
    $files = (git diff HEAD~1 HEAD --name-only 2>$null) -join "`n"
}

$prompt = @"
You are maintaining Tracktal's Linear documentation. A git commit was just made. Update only the Linear docs affected by these changes.

COMMIT MESSAGE:
$commitMsg

FILES CHANGED:
$files

DOCUMENT MAPPING (update only what is genuinely affected):
- apps/api/migrations/ or schema changes  ->  "Database Schema"
- pipelines/ (scrapers, flows, schedules) ->  "Data Pipeline"
- dbt/ (models, staging, marts)           ->  "dbt Model Layers"
- apps/api/ (non-migration, endpoints)    ->  "API Reference"
- apps/web/ (frontend, components, pages) ->  "Frontend Architecture"
- billing, payments, lemon squeezy        ->  "Payments & Billing"
- setup, tooling, CI, Docker, env         ->  "Development Setup"
- major stack or architecture changes     ->  "Architecture Overview"

STEPS:
1. Use list_documents to find docs attached to team "Tracktal"
2. Identify which doc(s) are affected by the changed files above
3. Use get_document to read the current content of affected doc(s)
4. Use save_document to update only the changed sections — do NOT rewrite unchanged content

RULES:
- Skip trivial commits: typos, formatting fixes, comment-only changes, config tweaks
- Be concise — patch the specific section that changed, not the whole doc
- If nothing substantive changed for a doc, do not update it
"@

claude -p $prompt --dangerously-skip-permissions 2>$null
