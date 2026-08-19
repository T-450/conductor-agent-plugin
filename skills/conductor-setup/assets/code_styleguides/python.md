# Python Style Guide Summary

This document summarizes key rules and best practices based on PEP 8 and modern Python idioms.

## 1. Code Layout & Formatting
- **Indentation:** 4 spaces per indentation level. Do not use tabs.
- **Line Length:** Limit lines to 88-100 characters.
- **Imports:** Group in order: Standard Library, Third-party, Local application. Use explicit imports.

## 2. Type Hints
- Annotate function signatures (`def calculate_tax(amount: float, rate: float = 0.05) -> float:`).
- Use `typing` primitives (`Optional`, `Union`, `Literal`, or `X | Y` in Python 3.10+).

## 3. Naming Conventions
- `snake_case`: Functions, variables, methods, module names.
- `PascalCase`: Class names, custom exception types.
- `UPPER_CASE`: Constants.
- `_single_leading_underscore`: Internal/private methods and attributes.

## 4. Best Practices
- Use context managers (`with open(...) as f:`) for resource safety.
- Prefer list/dict comprehensions over raw loops for transformations, keeping them readable.
- Avoid bare `except:`; catch specific exceptions.
