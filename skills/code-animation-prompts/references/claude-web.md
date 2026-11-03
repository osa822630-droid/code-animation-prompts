# Claude Web execution guide

This skill can be installed through a GitHub marketplace in Claude's web interface. The plugin is already installed when this file is available: do not clone the repository again, run `install_skill.py`, or ask the user to install Claude Code.

## Resolve files from the installed skill

Use the directory containing this loaded `SKILL.md` as the skill root. Its actual location is supplied by the host and may differ from `~/.claude/skills/`. Resolve `references/catalog.json`, selected prompts, and assets relative to that root. Never hard-code a marketplace cache path or assume the current working directory is the skill root.

1. Read `references/catalog.json` to find a style ID and its `file` and optional `image` paths.
2. Read only the selected Markdown prompt and, when useful, its still. Do not load the entire library into context.
3. If Python and file tools are available, `scripts/styles.py search`, `show`, and `list` work from any working directory when invoked by absolute path.
4. Save generated work in the user's working/output directory, not in the installed plugin. Keep the bundled library unchanged.

The web distribution contains every style prompt and still, plus HTML examples and screenshots. It omits the three large MP4 example videos. Do not try to open those missing videos or claim they are bundled. The full repository retains them for local use.

## Respect the actual tools available

- With file creation and code execution: create editable HTML/CSS/JavaScript and preview frames when supported. Return actual downloadable files.
- Without Python but with file access: use the JSON catalog and Markdown files directly; the lookup script is optional.
- Without access to bundled files or execution: explain the limitation. Offer a concise animation brief based only on information actually available, and ask the user to enable the relevant capability or provide the selected prompt. Do not invent a style prompt or pretend the library was read.
- MP4 export requires a compatible browser-rendering environment and FFmpeg. Their presence must be checked, not assumed. If unavailable, deliver the HTML and exact local export instructions and label the video as not rendered.

Do not install dependencies, start persistent servers, or contact external services merely to choose a style. Follow the user's language and requested deliverables.

## Example request

```text
استخدم code-animation-prompts واختَر نمط B3 لعمل مدخل أنيميشن 12 ثانية عن تحويل الفكرة إلى واقع، بمقاس 16:9 وجزيئات ذهبية على خلفية داكنة. سلّم HTML قابل للتعديل، ووضّح هل تم تصدير فيديو فعليًا أم لا.
```
