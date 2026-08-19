# C# Style Guide Summary

## 1. Coding Conventions
- Use `PascalCase` for classes, methods, properties, events, and namespaces.
- Use `camelCase` for method arguments, local variables, and `_camelCase` for private fields.
- Prefer file-scoped namespaces in C# 10+.
- Use pattern matching, records, and nullable reference types (`#nullable enable`).
- Use `var` when the type is obvious from the right-hand side.
- Always use `async`/`await` with `CancellationToken` support on I/O operations.
