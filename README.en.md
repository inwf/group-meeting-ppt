# group-meeting-ppt

**English** | [简体中文](README.md)

An [Agent Skills](https://agentskills.io) skill that builds a full Chinese paper-sharing / group-meeting slide deck (`.pptx`) from a paper PDF, using a fixed template, with an optional 8-minute speech script.

The skill follows the open Agent Skills standard (a `SKILL.md` plus script and asset directories), so it works with any compatible agent (Claude Code, Codex, Cursor, Gemini CLI, WorkBuddy, and 40+ others). Once installed, the agent generates a cover, outline, section dividers for the five chapters, content pages and a closing page based on the layout of `assets/template.pptx`, and validates table layout and image links.

## Features

- **Paper reading**: extract title, authors, page count, abstract and arXiv ID from a PDF
- **Figure cropping**: crop key figures from the paper at 600 DPI using in-page coordinates
- **Full deck**: cover, outline, section dividers for the five chapters (research background, approach, algorithm framework, experiments, conclusion), content pages and a closing page
- **Three content layouts**: text-only, figure and table; misaligned, overlapping or out-of-bounds tables raise an error
- **Validation**: checks the pptx for external image links (which make PowerPoint prompt to block automatic downloads), and exports a PDF via LibreOffice to verify the page count
- **Speech script**: a per-page script, with a helper that counts Chinese characters and estimates duration (260 to 270 characters per minute)
- **Placeholder replacement**: school, college and lab names are drawn into the header and cover banners and written into the document properties

## Install

The repository root is the skill directory. Clone it into the skills directory of your agent; no files need to be modified. Example locations for common agents:

- Claude Code: `~/.claude/skills/group-meeting-ppt`
- OpenAI Codex: `~/.codex/skills/group-meeting-ppt`
- Cursor: `~/.cursor/skills/group-meeting-ppt`
- Gemini CLI: `~/.gemini/skills/group-meeting-ppt`
- WorkBuddy / CodeBuddy: `~/.codebuddy/skills/group-meeting-ppt`

```bash
git clone https://github.com/inwf/group-meeting-ppt.git ~/.claude/skills/group-meeting-ppt
```

For other agents, use their own skills directory; for a project-level install, put it under `.agents/skills/` in the repository (the common location recognized by most agents). `agents/openai.yaml` provides the display name, short description and default prompt for Codex.

Open a new session after installing. The agent invokes the skill automatically when the task mentions a group-meeting deck or paper sharing, and the skill can also be invoked explicitly, for example `/group-meeting-ppt` in Claude Code or `$group-meeting-ppt` in Codex.

## Dependencies

Python packages (install inside the skill directory):

```bash
pip install -r requirements.txt   # lxml, Pillow, numpy
```

System commands:

| Command | Purpose | macOS | Ubuntu / Debian |
| --- | --- | --- | --- |
| `pdfinfo` `pdftotext` `pdftohtml` `pdftoppm` | reading papers, cropping figures | `brew install poppler` | `sudo apt install poppler-utils` |
| `libreoffice` or `soffice` | PDF export in the validation step only | `brew install --cask libreoffice` | `sudo apt install libreoffice` |

On Windows, poppler has no official installer; use `scoop install poppler` or `conda install -c conda-forge poppler`, and add the LibreOffice program directory to PATH.

Fonts: drawing the banners requires one CJK sans-serif font and one Latin serif bold font. macOS ships PingFang or Hiragino Sans GB and Times New Roman; Linux needs Noto Sans CJK (or WenQuanYi) and Liberation / DejaVu; Windows uses Microsoft YaHei and Times New Roman. See `scripts/banner.py` for the candidate paths.

## Usage

Describe the task in an agent session, for example:

> Use group-meeting-ppt to make a group-meeting deck: the paper is at `~/papers/attention-is-all-you-need.pdf`, presenter Zhang San, XX University School of Computer Science, Intelligent Computing Lab, date October 2026, and an 8-minute speech script.

The deck content itself is written in Chinese. When information is missing: without a presenter name the cover shows only 汇报人 (presenter); missing school, college or lab names fall back to `XX大学`, `XX学院` and `School of XX`; without a PDF the agent asks for the paper title or arXiv ID and organizes the content accordingly.

## Workflow

1. `scripts/read_paper.py` reads paper metadata and the abstract
2. `scripts/extract_figures.py` crops key figures from the PDF
3. Organize the content JSON per `references/deck_schema.md`
4. `scripts/build_deck.py` unpacks the template, rebuilds all slides and packages the pptx
5. `scripts/render_check.py` checks external links and exports a PDF via LibreOffice to verify the page count
6. Write the speech script per `references/speech_guide.md`; `scripts/count_speech.py` counts characters and estimates duration

## Repository layout

```
group-meeting-ppt/
├── SKILL.md                # skill entry: workflow and content rules
├── agents/openai.yaml      # UI metadata for Codex
├── assets/template.pptx    # layout template (cover, dividers, content master)
├── references/
│   ├── deck_schema.md      # content JSON field reference
│   └── speech_guide.md     # speech script writing guide
└── scripts/
    ├── build_deck.py       # main build script
    ├── pptxkit.py          # low-level OOXML assembly
    ├── banner.py           # draws the emblem, header and cover banners
    ├── read_paper.py       # reads paper metadata
    ├── extract_figures.py  # crops figures from the PDF
    ├── render_check.py     # external-link check and PDF export
    └── count_speech.py     # speech character count
```

## Content rules

- The five chapters are fixed: research background, approach, algorithm framework, experiments, conclusion
- 4 to 6 bullet points per page, each under 60 Chinese characters; use Unicode for symbols and subscripts (e.g. `α`, `N̂`, `R₁`)
- Numbers, metric names and experimental settings must match the paper; do not add conclusions the paper does not state
- The school and college names inside `assets/template.pptx` are generic placeholders; never commit a template containing personal information

## License

[MIT](LICENSE)
