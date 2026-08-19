# Contributing to Conductor

We welcome contributions to the Conductor agent plugin.

## How to Contribute

1. Fork the repository and create a new feature branch.
2. Make your changes adhering to existing skill schemas and style guides.
3. Test your changes locally by running:
   ```bash
   python evals/run_evals.py
   ```
4. Submit a Pull Request with a clear description of the change.

## Code Standards

- Follow Conventional Commits format (`feat:`, `fix:`, `docs:`, `chore:`).
- Keep all python scripts compatible with Python 3.10+ standard library.
- Ensure all skills have valid YAML frontmatter and clear operational instructions.
