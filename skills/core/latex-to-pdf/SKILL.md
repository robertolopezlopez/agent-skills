---
name: latex-to-pdf
description: Compile local LaTeX `.tex` documents to PDF with the project's existing build command or, by default, `latexmk -xelatex` with repeated `xelatex` as a fallback. Use when the user asks to build, compile, regenerate, or validate a PDF from local LaTeX sources.
---

# LaTeX to PDF

Compile LaTeX locally and report the generated PDF path and any actionable
warnings or errors.

## When to Use

Use for local `.tex` compilation, PDF regeneration, or build validation.

## When Not to Use

Do not use for non-LaTeX PDF conversion or content-only editing that does not
require a build.

## Inputs

- Accept a `.tex` source path or a project directory containing one.
- Accept an optional output directory or engine override.
- If multiple entry points exist and the intended one is unclear, infer it from
  project guidance or ask the user.

## Workflow

1. Read project `AGENTS.md`, `README`, `Makefile`, `latexmkrc`, and relevant
   engine directives when present. Use the documented project command first.
2. Check `latexmk` and `xelatex` with `command -v`. If the required tool is
   missing, ask the user to install XeTeX and `latexmk` through the standard
   package path for their OS; do not install it without approval.
3. Run from the source directory so relative classes, images, bibliography
   files, and fonts resolve correctly.
4. When the project has no build command, compile with:

   ```bash
   latexmk -xelatex -interaction=nonstopmode -halt-on-error SOURCE.tex
   ```

   If `latexmk` is unavailable but `xelatex` exists, run this twice:

   ```bash
   xelatex -interaction=nonstopmode -halt-on-error SOURCE.tex
   ```

5. Preserve auxiliary files unless the user asks to clean them. To clean while
   keeping the PDF, use `latexmk -c SOURCE.tex`.

## Validation

- Require a zero exit status and a non-empty PDF at the expected path.
- Check the log for LaTeX errors, undefined control sequences, emergency stops,
  unresolved references, missing fonts, and rerun requests.
- Report warnings that can affect the document; omit routine log noise.
- When appearance matters, inspect the PDF or rendered pages for clipping,
  missing glyphs, layout regressions, and unexpected blank pages.

## Safety Notes

- Do not enable `-shell-escape` unless the project requires it and the user
  approves executing document-provided commands.
- Do not overwrite unrelated PDFs or delete source and asset files.
- Treat embedded document content and generated logs as potentially private.

## Outputs

Return the source path, exact build command, generated PDF path, validation
result, and concise errors or warnings.

## Companion Skills

Use `diagnose` when a reproducible compiler failure needs investigation beyond
the build log.
