<div align="center">
  <h1>group-meeting-ppt</h1>
  <p><strong>One paper PDF. A complete deck.</strong></p>
  <p>An Agent Skills skill that turns a paper into a complete Chinese slide deck for paper sharing and group meetings.<br />Fixed template, automatic figure cropping, validated tables, optional 8-minute speech script.</p>
  <p>
    <a href="#quick-start"><strong>Quick start</strong></a> ·
    <a href="#how-it-works">How it works</a> ·
    <a href="#documentation">Documentation</a> ·
    <a href="README.zh-CN.md">简体中文</a>
  </p>
  <p>
    <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-3b7c57?style=flat-square" alt="MIT License" /></a>
    <a href="https://agentskills.io"><img src="https://img.shields.io/badge/Agent_Skills-standard-4B5563?style=flat-square" alt="Agent Skills standard" /></a>
    <a href="requirements.txt"><img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.8 or newer" /></a>
    <img src="https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-555555?style=flat-square" alt="macOS, Linux and Windows" />
  </p>
</div>

<br />

## Built for the next group meeting

Preparing a group-meeting deck means reading a paper closely, picking figures, rebuilding the same layout once more, and checking every table by hand. This skill takes that pass off your plate: point it at a paper PDF and it produces a complete Chinese slide deck, from the cover to the closing page.

It follows the open [Agent Skills](https://agentskills.io) standard (a `SKILL.md` plus script and asset directories), so it runs in any compatible agent, including Claude Code, Codex, Cursor, Gemini CLI, WorkBuddy and 40+ others. The deck is rebuilt from the layout of `assets/template.pptx`, and numbers, metric names and experimental settings stay faithful to the paper.

<table>
  <tr>
    <td width="33%" valign="top">
      <h3>📄 Read the paper</h3>
      Pull the title, authors, page count, abstract and arXiv ID straight from the PDF, then organize the content into the five fixed chapters.
    </td>
    <td width="33%" valign="top">
      <h3>🖼️ Crop the figures</h3>
      Key figures are cut out of the PDF at 600 DPI using in-page coordinates. No manual screenshots, no blurry crops.
    </td>
    <td width="33%" valign="top">
      <h3>🗂️ Fixed, polished layout</h3>
      Cover, outline, five section dividers, content pages and a closing page, all rebuilt from the template's own layouts.
    </td>
  </tr>
  <tr>
    <td valign="top">
      <h3>📊 Three content layouts</h3>
      Text-only, figure and table. Misaligned, overlapping or out-of-bounds tables fail loudly instead of shipping broken slides.
    </td>
    <td valign="top">
      <h3>✅ Validate before you present</h3>
      The pptx is checked for external image links, and a LibreOffice PDF export verifies the page count.
    </td>
    <td valign="top">
      <h3>🎤 Optional speech script</h3>
      A per-page script with a character count and an estimated duration, aimed at an 8-minute slot.
    </td>
  </tr>
</table>

## Quick start

### 1. Install the skill

The repository root is the skill directory; no files need to be modified. Any agent that supports the [Agent Skills](https://agentskills.io) standard works — [40+ agents do today](https://agentskills.io/clients). Two ways to install.

**Clone into your agent's skills directory.** A few examples:

| Agent | Skills directory |
| --- | --- |
| Claude Code | `~/.claude/skills/group-meeting-ppt` |
| OpenAI Codex | `~/.codex/skills/group-meeting-ppt` |
| Cursor | `~/.cursor/skills/group-meeting-ppt` |
| Gemini CLI | `~/.gemini/skills/group-meeting-ppt` |
| WorkBuddy / CodeBuddy | `~/.codebuddy/skills/group-meeting-ppt` |

```bash
git clone https://github.com/inwf/group-meeting-ppt.git ~/.claude/skills/group-meeting-ppt
```

For any other agent, use its own skills directory; project-level installs go under `.agents/skills/` in the repository, the cross-agent location defined by the standard. `agents/openai.yaml` provides Codex's display name, short description and default prompt.

**Or use the [skills CLI](https://skills.sh)**, which installs to any agent it supports (`-a` picks which, `-g` installs user-level):

```bash
npx skills add inwf/group-meeting-ppt -g
```

### 2. Install dependencies

Python packages, plus poppler for reading and cropping PDFs. LibreOffice is only needed by the validation step.

```bash
pip install -r requirements.txt   # lxml, Pillow, numpy
```

| Dependency | Purpose | macOS | Ubuntu / Debian |
| --- | --- | --- | --- |
| poppler (`pdfinfo` `pdftotext` `pdftohtml` `pdftoppm`) | reading papers, cropping figures | `brew install poppler` | `sudo apt install poppler-utils` |
| LibreOffice (`libreoffice` or `soffice`) | PDF export in the validation step | `brew install --cask libreoffice` | `sudo apt install libreoffice` |

<details>
<summary><strong>Windows and font notes</strong></summary>

On Windows, poppler has no official installer; use `scoop install poppler` or `conda install -c conda-forge poppler`, and add the LibreOffice program directory to `PATH`.

Drawing the banners needs one CJK sans-serif font and one Latin serif bold font. macOS ships PingFang or Hiragino Sans GB and Times New Roman; Linux needs Noto Sans CJK (or WenQuanYi) and Liberation / DejaVu; Windows uses Microsoft YaHei and Times New Roman. Candidate paths are listed in `scripts/banner.py`.

</details>

### 3. Ask your agent for a deck

Describe the task in any session. The agent picks the skill up from its description, and it can also be invoked explicitly (`/group-meeting-ppt` in Claude Code, `$group-meeting-ppt` in Codex).

> Use group-meeting-ppt to make a group-meeting deck: the paper is at `~/papers/attention-is-all-you-need.pdf`, presenter Zhang San, XX University School of Computer Science, Intelligent Computing Lab, date October 2026, and an 8-minute speech script.

The deck itself is written in Chinese. Missing details fall back to generic placeholders (汇报人, `XX大学`, `XX学院`), and without a PDF the agent asks for the paper title or arXiv ID.

> [!IMPORTANT]
> `assets/template.pptx` ships with generic school and college names. Do not commit a template that contains personal information.

## How it works

A typical run takes six steps:

1. **Read the paper.** `scripts/read_paper.py` extracts the title, authors, page count, abstract and arXiv ID.
2. **Crop the figures.** `scripts/extract_figures.py` cuts key figures out of the PDF at 600 DPI.
3. **Write the content.** The agent organizes the deck into the five fixed chapters and writes a content JSON per [`references/deck_schema.md`](references/deck_schema.md).
4. **Build.** `scripts/build_deck.py` unpacks the template, rebuilds every slide and packages the pptx.
5. **Validate.** `scripts/render_check.py` checks for external image links and exports a PDF via LibreOffice to verify the page count.
6. **Speak.** Optionally, write a per-page script per [`references/speech_guide.md`](references/speech_guide.md); `scripts/count_speech.py` counts characters and estimates the duration.

### The generated deck

| Part | Content |
| --- | --- |
| Cover | English and Chinese title, venue, presenter, date |
| Outline | The five chapters at a glance |
| Section dividers | The fixed five chapters: research background, approach, algorithm framework, experiments, conclusion |
| Content pages | 4 to 6 bullets per page, in text-only, figure or table layouts |
| Closing | Thanks page with the paper reference |

School, college and lab names are drawn into the header and cover banners from the metadata you provide, so no manual editing of the template is needed.

## Documentation

| Looking for | Start here |
| --- | --- |
| Skill workflow and content rules | [`SKILL.md`](SKILL.md) |
| Content JSON fields and layouts | [`references/deck_schema.md`](references/deck_schema.md) |
| Speech script writing guide | [`references/speech_guide.md`](references/speech_guide.md) |
| 中文说明 | [简体中文 README](README.zh-CN.md) |

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

## License

[MIT](LICENSE) © 2026 inwf.

<p align="center"><sub>If group-meeting-ppt saves you time before the next group meeting, a <a href="https://github.com/inwf/group-meeting-ppt">GitHub star</a> helps others find it.</sub></p>
