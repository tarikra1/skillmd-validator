# Changelog

All notable changes to `skillmd-validator` are documented in this file.

## [1.0.0] - 2026-11-25

### Added
- YAML frontmatter validator verifying `name` (kebab-case) and actionable `description` trigger criteria.
- Relative Markdown link resolver verifying `references/`, `scripts/`, and `resources/` targets exist on disk.
- Hardcoded workstation path & secret pattern detector, token estimator, CLI (`skillmd-check`), and GitHub Actions CI matrix.
