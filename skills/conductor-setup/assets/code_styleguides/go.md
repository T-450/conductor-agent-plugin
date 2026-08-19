# Go Style Guide Summary

This document summarizes key rules from Effective Go and standard Go conventions.

## 1. Formatting & Organization
- Always format code with `gofmt` or `goimports`.
- Package names must be short, lowercase, single-word names (`auth`, `config`, `store`). Avoid `utils` or `helpers`.

## 2. Error Handling
- Return errors as the last return value.
- Check errors immediately after the call (`if err != nil { return fmt.Errorf("reading config: %w", err) }`).
- Never ignore errors with `_` unless explicitly justified with a comment.
- Wrap errors with context using `%w`.

## 3. Naming Conventions
- `camelCase` / `PascalCase`: MixedCaps for exported and unexported identifiers.
- Short variable names for small scopes (`i`, `r`, `ctx`), descriptive names for package-level symbols.
- Interfaces: Name with `-er` suffix where single method (`Reader`, `Writer`, `Closer`).
