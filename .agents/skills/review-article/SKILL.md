---
name: create-article
description: Create a new blog article from a markdown source for the Byte My Python Pelican site. Use when the user wants to publish, post, or turn a draft/notes into an article, clean up formatting, fix grammar and spelling, or review a draft for clarity before publishing.
---

# Create Article

Turn a markdown source (draft, notes, or pasted text) into a published-ready article under `content/` for this Pelican blog.

## When to Use

- User gives you markdown (a file path, pasted text, or a draft) and wants an article created.
- User asks to "publish", "post", "clean up", "proofread", or "review" a draft for the blog.
- User wants suggestions to clarify or strengthen a draft before publishing.

## Non-Goals

- Do NOT rewrite the author's voice. Preserve style (see below).
- Do NOT change the technical content or claims without flagging it.
- Do NOT touch `pelicanconf.py`, the theme, or `output/`.

## Workflow

1. **Locate the source.** Read the given file, or treat the pasted text as the source. If no source is given, ask the user for it (one focused question).

2. **Pick the category and directory.** Categories map 1:1 to `content/` subdirectories:

   | Category (metadata) | Directory        |
   |---------------------|------------------|
   | Tools               | `content/tools/` |
   | Language            | `content/language/` |
   | Django              | `content/django/` |
   | MicroPython         | `content/micropython/` |
   | Meta                | `content/meta/` |

   If the source clearly belongs to a new category, ask the user before creating a new directory. Default to the closest existing category.

3. **Choose the filename.** Lowercase, hyphen-separated, descriptive, no date prefix. Examples from the site: `stop-fighting-circular-imports.md`, `git-merge-without-rebase.md`, `queryset-database-binding-gotcha.md`. Do not reuse an existing filename.

4. **Write the metadata block** at the top of the file (Pelican Markdown metadata):

   ```markdown
   Title: <Title Case, no trailing period>
   Date: YYYY-MM-DD
   Modified: YYYY-MM-DD
   Category: <One of the categories above>
   Tags: <comma-separated, lowercase, 2-5 tags>
   ```

   - `Date`: today's date (ISO `YYYY-MM-DD`) unless the user gives a specific date.
   - `Modified`: same as `Date` for a new article.
   - `Tags`: lowercase, hyphenated multi-word tags, derived from the article content.

5. **Clean the layout** without altering meaning:
   - Normalize headings: one `#` H1 is implicit (the Title); body sections use `##`. Don't skip levels.
   - Ensure blank lines around code blocks, blockquotes, and lists.
   - Use fenced code blocks with language tags (```python, ```text, ```bash …).
   - Convert straight quotes to smart quotes in prose only, never inside code.
   - Fix obvious typos and grammar (its/it's, their/there, comma splices, repeated words).
   - Normalize dashes in prose: em dash `—` for asides, `--`/`...` only if that's the author's existing style.
   - Remove leftover artifacts from pasted sources (trailing whitespace, inconsistent bullet markers, hard line wraps mid-sentence).

6. **Preserve the author's style.** This blog's voice is conversational, first-person, lightly opinionated. Keep:
   - First person ("I", "we"), asides, and humor (`:)`, `...`, rhetorical questions).
   - Dialogue in blockquotes (`> `).
   - Sentence-level phrasing and word choice. Only change words to fix errors.
   - Em dashes and ellipses where the author uses them.

   When in doubt, keep the original wording. Style > perfection.

7. **Review and suggest enhancements.** After cleaning, read the article critically and report (do not silently apply) suggestions in these categories:
   - **Clarity:** paragraphs that assume context a reader may not have; jargon introduced without a one-line explanation.
   - **Structure:** missing intro or conclusion; sections that should be split or reordered; a hook that buries the point.
   - **Completeness:** a claim with no example, a code snippet without a language tag or missing context, steps that skip a prerequisite.
   - **Accuracy flags:** anything that looks technically off — raise as a question, never "fix" it.

   Present suggestions as a short bulleted list, each with the location (section/quote) and a concrete, specific recommendation. Prioritize 3-6 high-impact suggestions over an exhaustive copy-edit.

8. **Apply only what the user approves.** Default: write the cleaned article to the chosen path, then list the suggestions for the user to accept/decline. If the user already said "fix it" / "just publish", apply safe layout/grammar fixes only and still surface the clarity/accuracy suggestions before considering the work done.

9. **Verify the build.** After writing, run the site generator to confirm the article compiles:

   ```bash
   make html
   ```

   If it fails, fix the article (not the config) and re-run. Do not claim success without seeing a clean build.

10. **Report.** Tell the user:
    - The path of the new article.
    - The category and tags chosen.
    - A one-line summary of layout/grammar fixes applied.
    - The suggestion list (if any) for them to review.

## Quick Reference

- Articles live in `content/<category>/<slug>.md`.
- Metadata: `Title`, `Date`, `Modified`, `Category`, `Tags` (Pelican Markdown).
- Build: `make html` (uses `uv run pelican`).
- Preview locally: `make serve` then open http://localhost:8000.
- Existing categories: Tools, Language, Django, MicroPython, Meta.

## Common Mistakes

- **Rewriting voice.** "Improving" a sentence the author deliberately wrote casually. Fix errors, not style.
- **Silent technical edits.** Changing a code snippet or a claim because it "looks wrong". Always flag first.
- **Inventing tags.** Tags should come from the content; 2-5 lowercase, hyphenated.
- **Skipping the build check.** A broken metadata block or bad code fence fails Pelican silently or noisily — run `make html`.
- **Date prefixes in filenames.** This site does not prefix filenames with dates; the `Date` field carries that.
- **Forgetting `Modified`.** Pelican uses it for feed updates; set it equal to `Date` on a new article.
