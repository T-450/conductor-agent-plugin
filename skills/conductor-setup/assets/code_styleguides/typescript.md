# TypeScript Style Guide Summary

This document summarizes key rules and best practices for TypeScript.

## 1. Language Features
- **Variable Declarations:** Always use `const` or `let`. `var` is forbidden. Use `const` by default.
- **Modules:** Use ES6 modules (`import`/`export`). Do not use `namespace`.
- **Exports:** Use named exports. Avoid default exports where possible.
- **Classes:**
  - Mark properties never reassigned outside constructor with `readonly`.
  - Restrict visibility with `private` or `protected`.
- **Functions:** Prefer function declarations for top-level named functions. Use arrow functions for callbacks.
- **Equality Checks:** Always use strict equality (`===` and `!==`).
- **Type Assertions:** Avoid `as SomeType` or `!` assertions unless strictly necessary with justification.

## 2. Types & Safety
- **`any` Type:** Avoid `any`. Prefer `unknown` or specific union/object types.
- **Type Inference:** Rely on inference for simple primitives; declare explicit return types on public APIs.
- **Nullability:** Prefer optional properties (`?`) over explicit `| undefined`.
- **Arrays:** Use `T[]` for simple element types; `Array<T>` for complex types.

## 3. Naming Conventions
- `UpperCamelCase`: Classes, interfaces, type aliases, enums.
- `lowerCamelCase`: Variables, functions, methods, properties.
- `CONSTANT_CASE`: Global constants and enum members.
