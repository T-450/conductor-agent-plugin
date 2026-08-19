# JavaScript Style Guide Summary

This document summarizes key rules and best practices for JavaScript.

## 1. Language Features
- **Declarations:** Always use `const` or `let`. `var` is strictly forbidden.
- **Equality:** Always use strict equality (`===` and `!==`).
- **Async/Await:** Prefer `async`/`await` over raw promise chains (`.then()`).
- **Modules:** Use standard ES Modules (`import`/`export`).
- **Destructuring:** Use object and array destructuring where it enhances clarity.
- **Rest/Spread:** Use rest parameters (`...args`) instead of the `arguments` object.

## 2. Naming & Structure
- `lowerCamelCase`: Variables, functions, methods, object properties.
- `UpperCamelCase`: Classes, constructor functions.
- `CONSTANT_CASE`: Module-level immutable constants.
- **Semicolons:** Explicitly end statements with semicolons.
