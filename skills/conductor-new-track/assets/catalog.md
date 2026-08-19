# Agent Skills Catalog & Ecosystem Reference

This catalog defines the curriculum of high-quality, verified skills available for recommendation within the Conductor framework, sourced directly from official repositories and recognized community leaders.

---

## 1. Official 1P Skills (Anthropic, Firebase, Google Cloud)

### Official Anthropic Agent Skills (`anthropic-agent-skills`)
- **claude-api**: Official Anthropic SDK & Claude API reference (model IDs, streaming, tool use, prompt caching, token budgets).
  - *URL*: `https://raw.githubusercontent.com/anthropics/anthropic-agent-skills/main/skills/claude-api/SKILL.md`
  - *Party*: 1p (Anthropic)
  - *Detection Signals*: Keywords: `anthropic`, `claude`, `@anthropic-ai/sdk`, `Claude 3.5 Sonnet`, `Opus`, `Haiku`
- **document-skills**: Official document extraction and processing (PDF, DOCX, XLSX).
  - *URL*: `https://raw.githubusercontent.com/anthropics/anthropic-agent-skills/main/skills/document-skills/SKILL.md`
  - *Party*: 1p (Anthropic)
  - *Detection Signals*: File extensions: `.pdf`, `.docx`, `.xlsx`; Dependencies: `pdfplumber`, `docx`, `openpyxl`

### Official Firebase Skills (`firebase/agent-skills`)
- **firebase-basics**: Official Firebase environment setup, local emulators, and project initialization.
  - *URL*: `https://raw.githubusercontent.com/firebase/agent-skills/main/skills/firebase-basics/SKILL.md`
  - *Party*: 1p (Google / Firebase)
  - *Detection Signals*: Dependencies: `firebase`, `firebase-admin`, `firebase-tools`
- **firebase-firestore-basics**: Provisioning, security rules, composite indexing, and Firestore SDK data modeling.
  - *URL*: `https://raw.githubusercontent.com/firebase/agent-skills/main/skills/firebase-firestore-basics/SKILL.md`
  - *Party*: 1p (Google / Firebase)
  - *Detection Signals*: Dependencies: `@google-cloud/firestore`, `firebase/firestore`
- **firebase-auth-basics**: Authentication flows, custom claims, session verification, and Identity Platform integration.
  - *URL*: `https://raw.githubusercontent.com/firebase/agent-skills/main/skills/firebase-auth-basics/SKILL.md`
  - *Party*: 1p (Google / Firebase)
  - *Detection Signals*: Dependencies: `firebase-auth`, `@angular/fire/auth`, `next-auth`
- **firebase-ai-logic-basics**: Firebase AI Logic & Gemini API multimodal inference and structured outputs.
  - *URL*: `https://raw.githubusercontent.com/firebase/agent-skills/main/skills/firebase-ai-logic-basics/SKILL.md`
  - *Party*: 1p (Google / Firebase)
  - *Detection Signals*: Dependencies: `@google/genai`, `@google/generative-ai`

### Official Google Cloud DevOps (`gemini-cli-extensions/devops`)
- **cloud-deploy-pipelines**: Delivery pipelines, releases, targets, and progressive rollouts via Google Cloud Deploy.
  - *URL*: `https://raw.githubusercontent.com/gemini-cli-extensions/devops/main/skills/cloud-deploy-pipelines/SKILL.md`
  - *Party*: 1p (Google)
  - *Detection Signals*: Manifests: `skaffold.yaml`, `clouddeploy.yaml`
- **gcp-cicd-deploy**: Multi-target deployment automation (Cloud Run, GCS Static Sites, GKE).
  - *URL*: `https://raw.githubusercontent.com/gemini-cli-extensions/devops/main/skills/gcp-cicd-deploy/SKILL.md`
  - *Party*: 1p (Google)
  - *Detection Signals*: Dependencies: `gcloud`, `google-cloud-run`
- **gcp-cicd-terraform**: Infrastructure as Code with Terraform and standard GCS backend state locks.
  - *URL*: `https://raw.githubusercontent.com/gemini-cli-extensions/devops/main/skills/gcp-cicd-terraform/SKILL.md`
  - *Party*: 1p (Google)
  - *Detection Signals*: Manifests: `main.tf`, `backend.tf`

---

## 2. Community Leader Curated Skills

### Addy Osmani Engineering Skills (`addy-agent-skills`)
- **spec-driven-development**: Structured specification-first architecture decomposition and plan tracking.
  - *Party*: 3p (Verified Community Leader)
  - *Detection Signals*: SDD workflow active, architecture scaffolding requests
- **test-driven-development**: Strict Red-Green-Refactor enforcement with unit test generation.
  - *Party*: 3p (Verified Community Leader)
  - *Detection Signals*: Test suites: `jest`, `vitest`, `pytest`, `cargo test`
- **performance-optimization**: Profiling, bundle size analysis, Core Web Vitals, and runtime optimization.
  - *Party*: 3p (Verified Community Leader)
  - *Detection Signals*: Frontend/Node.js performance tuning, high-load services

### Samber Golang Suite (`samber/cc-skills-golang`)
- **golang-code-style & golang-concurrency**: Idiomatic Go, goroutines, channels, sync primitives, and error cascades.
  - *Party*: 3p (Verified Community Leader)
  - *Detection Signals*: Manifests: `go.mod`, `go.sum`

### Microsoft Official Documentation & SDKs (`claude-plugins-official`)
- **microsoft-docs**: Grounded architecture lookups and code samples from Microsoft Learn (.NET, Azure, Microsoft 365).
  - *Party*: 1p (Microsoft Official)
  - *Detection Signals*: Dependencies: `@azure/*`, `Microsoft.Azure.*`, `.csproj`
