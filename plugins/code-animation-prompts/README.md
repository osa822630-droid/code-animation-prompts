# Code Animation Prompts — Claude Web plugin

اختَر من **341 نمط أنيميشن بالكود** و**193 صورة مرجعية**، وحوّل فكرتك إلى أنيميشن قابل للتعديل باستخدام HTML وCanvas وSVG وCSS.

## Add from Claude Web

Add the **repository**, not this subfolder, through **Customize → Plugins → Add → Add marketplace → Add from a repository**:

```text
https://github.com/osa822630-droid/code-animation-prompts
```

Then add **Code Animation Prompts** from the marketplace and start a new chat. No Claude Code installation, terminal command, API key, MCP server, or paid external service is needed by this plugin. Feature availability is controlled by Claude for your account.

Try:

```text
/code-animation-prompts:animate B3، مدخل أنيميشن 12 ثانية عن تحويل الفكرة إلى واقع، مقاس 16:9، جزيئات ذهبية على خلفية داكنة.
```

Or ask naturally in Arabic, English, or Chinese. You can also invoke the bundled skill as `/code-animation-prompts:code-animation-prompts`; the shorter `animate` command is provided for convenience.

<details>
<summary>Optional Claude Code compatibility — not needed for Claude Web</summary>

The same marketplace also works in Claude Code:

```text
/plugin install code-animation-prompts --marketplace osa822630-droid/code-animation-prompts
```

</details>

## What is included

- All 341 style prompts, including the 148 text-only references.
- All 193 reference stills and the offline style picker.
- The searchable JSON catalog and standard-library Python lookup script.
- Example HTML, prompts, screenshots, attribution, and third-party licenses.
- A deterministic HTML starter and the optional local video-rendering script.

The three large original MP4 example videos are **not duplicated into this web package**. They remain in the [full source library](https://github.com/osa822630-droid/code-animation-prompts/tree/main/skills/code-animation-prompts/assets/library/示例). References to those videos inside the original example notes describe the full collection, not this lightweight distribution.

## Runtime expectations

For access to bundled files and code execution, enable Claude's **Code execution and file creation** / **Create and edit files** capability if your interface offers it. The skill must not assume a terminal, a local installation path, Playwright, Chromium, or FFmpeg. If it cannot execute or deliver files, it should provide a useful text brief and clearly state what remains unrendered.

See the [Claude Web guide](https://github.com/osa822630-droid/code-animation-prompts/blob/main/docs/CLAUDE_WEB.md) for setup and troubleshooting.

## Source and maintenance

The canonical skill lives at `skills/code-animation-prompts/` in the repository root. This plugin's `skills/` directory and `LICENSE.md` are generated from it, excluding MP4 files and Python caches. Maintainers should edit the canonical skill and run:

```bash
python scripts/build_web_plugin.py
python scripts/build_web_plugin.py --check
python scripts/validate_repo.py
```

Original curation: **俯仰观照**. Skill packaging and tools: **XiaoyeCodes**. Claude Web marketplace packaging is maintained in the **osa822630-droid** fork. See [LICENSE.md](LICENSE.md) and the bundled [attribution](skills/code-animation-prompts/references/attribution.md); the mixed-source collection is not relicensed as MIT.
