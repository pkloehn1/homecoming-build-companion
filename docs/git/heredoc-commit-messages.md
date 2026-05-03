# Multi-line commit messages with heredoc (Conventional Commits aligned)

```yaml
Document-Slug: git-heredoc-commit-messages
Agent-Slugs: augment, repository-standards, commit-messages
Related-Slugs: conventional-commits, commit-template, git-workflow
Cross-References: docs/infrastructure/workflow-standards.md, .github/COMMIT_TEMPLATE
```

This guide shows how to write clear, multi-line commit messages using heredoc/Here-Strings while following our Conventional Commits standard.

## When to use

- Complex changes that need context (why, alternatives considered, trade-offs)
- Control-doc changes (AUGMENT.md, docs/\*\*) where rationale must be preserved
- CI/CD or security policy updates

## Conventional commit structure

- Header: `<type>(scope)!: short summary` (max ~72 chars)
- Blank line
- Body: motivation, what changed, how validated
- Footer: Breaking changes and issue refs (BREAKING CHANGE:, Fixes #123)

## Bash/Git Bash (Linux/Windows) – using a temporary file

```bash
cat > COMMIT_MSG <<'MSG'
ci(validator-parity): add Windows success cleanup step

- Remove tmp/validator-parity after successful runs to avoid residue
- Keep failure artifacts via upload-artifact for debugging

Refs: docs/ci/github-actions-style-guide.md
MSG

git add .
git commit -F COMMIT_MSG
rm -f COMMIT_MSG
```

## Bash – process substitution (when supported)

```bash
git commit -F <(cat <<'MSG'
docs(git): add heredoc commit message guide

- When to use
- Syntax for Bash and PowerShell
- Conventional Commit alignment and examples
MSG
)
```

## PowerShell (Windows) – Here-String to a temp file

```powershell
$temp = Join-Path $env:TEMP 'commit-msg.txt'
@'
docs(testing): document cleanup flags for validators

- Add optional -Cleanup/--cleanup flags
- Note validators create no temp artifacts by themselves
'@ | Set-Content -NoNewline -Path $temp -Encoding UTF8

git add .
git commit -F $temp
Remove-Item $temp
```

## Tips

- Prefer short, imperative headers: "add", "fix", "remove"
- Wrap body at ~72 chars per line
- Use bullets for readability; focus on why over what
- Keep related changes in separate commits
