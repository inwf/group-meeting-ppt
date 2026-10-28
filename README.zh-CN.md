<div align="center">
  <h1>group-meeting-ppt</h1>
  <p><strong>一份论文 PDF，一套完整的组会幻灯片。</strong></p>
  <p>把一篇论文变成整套中文论文分享与组会汇报幻灯片。<br />固定版式、自动裁图、表格校验，可选配 8 分钟演讲稿。</p>
  <p>
    <a href="#快速开始"><strong>快速开始</strong></a> ·
    <a href="#工作方式">工作方式</a> ·
    <a href="#文档">文档</a> ·
    <a href="README.md">English</a>
  </p>
  <p>
    <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-3b7c57?style=flat-square" alt="MIT 许可证" /></a>
    <a href="https://agentskills.io"><img src="https://img.shields.io/badge/Agent_Skills-standard-4B5563?style=flat-square" alt="Agent Skills 标准" /></a>
    <a href="requirements.txt"><img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.8 及以上" /></a>
    <img src="https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-555555?style=flat-square" alt="支持 macOS、Linux 与 Windows" />
  </p>
</div>

<br />

## 为下一次组会准备

做一份组会 PPT，要通读论文、挑配图、把同一套版式再搭一遍，还要逐张核对表格。这个技能把这一遍流程接管下来：给一篇论文 PDF，产出从封面到致谢页的整套中文幻灯片。

技能遵循 [Agent Skills](https://agentskills.io) 开放标准（`SKILL.md` 加脚本与资源目录），可用于任何兼容的 agent，包括 Claude Code、Codex、Cursor、Gemini CLI、WorkBuddy 等 40 多个。幻灯片按 `assets/` 中模板的版式重建：默认使用 `assets/default/` 里自带的模板，也可以把改好的模板直接放进 `assets/` 替换。

<table>
  <tr>
    <td width="33%" valign="top">
      <h3>📄 读论文</h3>
      从 PDF 直接提取标题、作者、页数、摘要与 arXiv 编号，再把内容整理进固定的五个章节。
    </td>
    <td width="33%" valign="top">
      <h3>🖼️ 自动裁图</h3>
      按页内坐标从 PDF 中以 600 DPI 裁出关键插图，不需要手动截图，也没有糊图。
    </td>
    <td width="33%" valign="top">
      <h3>🗂️ 固定版式</h3>
      封面、提纲、五个分节页、内容页与致谢页，全部按模板自带的版式重建。
    </td>
  </tr>
  <tr>
    <td valign="top">
      <h3>📊 三种内容版式</h3>
      纯文字、图文与表格。列宽不齐、重叠、越界的表格会直接报错，不会带着坏幻灯片出场。
    </td>
    <td valign="top">
      <h3>✅ 生成后校验</h3>
      检查 pptx 是否含外部图片链接，并用 LibreOffice 导出 PDF 核对页数。
    </td>
    <td valign="top">
      <h3>🎤 可选演讲稿</h3>
      逐页讲稿，附汉字数与预计时长，按 8 分钟目标控制。
    </td>
  </tr>
</table>

## 快速开始

### 1. 安装技能

仓库根目录就是技能目录，不需要改动任何文件。任何支持 [Agent Skills](https://agentskills.io) 标准的 agent 都能用，[目前已有 40 多个](https://agentskills.io/clients)。两种安装方式。

**克隆到 agent 的技能目录。** 几个示例：

| Agent | 技能目录 |
| --- | --- |
| Claude Code | `~/.claude/skills/group-meeting-ppt` |
| OpenAI Codex | `~/.codex/skills/group-meeting-ppt` |
| Cursor | `~/.cursor/skills/group-meeting-ppt` |
| Gemini CLI | `~/.gemini/skills/group-meeting-ppt` |
| WorkBuddy / CodeBuddy | `~/.codebuddy/skills/group-meeting-ppt` |

```bash
git clone https://github.com/inwf/group-meeting-ppt.git ~/.claude/skills/group-meeting-ppt
```

其他 agent 换成它自己的技能目录即可；项目级安装放在仓库的 `.agents/skills/`（标准约定的跨 agent 位置）下。仓库内的 `agents/openai.yaml` 提供 Codex 的显示名称、简介与默认提示词。

**或用 [skills CLI](https://skills.sh) 安装**，支持它适配的全部 agent（`-a` 指定 agent，`-g` 安装到用户级）：

```bash
npx skills add inwf/group-meeting-ppt -g
```

### 2. 安装依赖

Python 包，加上读取与裁剪 PDF 所需的 poppler。LibreOffice 只有校验步骤会用到。

```bash
pip install -r requirements.txt   # lxml、Pillow、numpy
```

| 依赖 | 用途 | macOS | Ubuntu / Debian |
| --- | --- | --- | --- |
| poppler（`pdfinfo` `pdftotext` `pdftohtml` `pdftoppm`） | 读论文、裁图 | `brew install poppler` | `sudo apt install poppler-utils` |
| LibreOffice（`libreoffice` 或 `soffice`） | 校验步骤导出 PDF | `brew install --cask libreoffice` | `sudo apt install libreoffice` |

<details>
<summary><strong>Windows 与字体说明</strong></summary>

Windows 上 poppler 没有官方安装包，可用 `scoop install poppler` 或 `conda install -c conda-forge poppler`；LibreOffice 安装后需要把程序目录加入 `PATH`。

绘制横幅需要一个中文无衬线字体和一个西文衬线粗体字体。macOS 自带 PingFang 或 Hiragino Sans GB 与 Times New Roman；Linux 需 Noto Sans CJK（或文泉驿）与 Liberation / DejaVu；Windows 使用微软雅黑与 Times New Roman。候选路径见 `scripts/banner.py`。

</details>

### 3. 让 agent 生成一份 PPT

在会话里直接描述任务即可。agent 会按 description 自动调用这个技能，也可以显式调用（Claude Code 用 `/group-meeting-ppt`，Codex 用 `$group-meeting-ppt`）。

> 用 group-meeting-ppt 做一份组会 PPT：论文在 `~/papers/attention-is-all-you-need.pdf`，汇报人张三，XX大学计算机学院，智能计算实验室，日期 2026 年 10 月，另配一份 8 分钟演讲稿。

开场 agent 会询问姓名、学校、学院（专业）与实验室，回答「用默认」即使用通用占位（汇报人、`XX大学`、`XX学院`）；提供了学校时，会从 [urongda.com](https://www.urongda.com/) 获取该校校徽并绘制进页眉与封面。幻灯片内容本身是中文；没有 PDF 时 agent 会询问论文标题或 arXiv 编号。

> [!IMPORTANT]
> `assets/default/template.pptx` 内的学校与学院是通用占位。自定义模板已被 Git 忽略（`.gitignore` 忽略 `assets/*.pptx`）。

### 4. 可选：使用自己的模板

把校徽、学校名称、配色都已改好的 pptx 放进 `assets/` 根目录（默认模板在 `assets/default/` 里，不需要动），脚本会自动优先使用它：

```bash
cp ~/Downloads/我的组会模板.pptx ~/.claude/skills/group-meeting-ppt/assets/
```

自定义模板的约定：

- 必须基于默认模板修改：页面尺寸保持 4:3（10 × 7.5 英寸），保留全部版式、母版与所需媒体文件；否则脚本会报错并列出缺少的部件
- 页眉与封面沿用模板原样，不再按个人信息重绘，也就不需要获取校徽
- `assets/` 里只能放一个自定义模板；有多个时脚本会报错，删除多余文件或用 `--template` 显式指定
- 仍要按新信息重绘页眉与封面时，加 `--redraw-banners`；配合 `--emblem` 可替换模板里的校徽

## 工作方式

一次典型生成分六步：

1. **读论文。** `scripts/read_paper.py` 提取标题、作者、页数、摘要与 arXiv 编号。
2. **裁配图。** `scripts/extract_figures.py` 以 600 DPI 从 PDF 中裁出关键插图。
3. **写内容。** agent 按固定五章整理内容，并按 [`references/deck_schema.md`](references/deck_schema.md) 写内容 JSON。
4. **生成。** `scripts/build_deck.py` 解包模板、重建全部幻灯片并打包成 pptx。
5. **校验。** `scripts/render_check.py` 检查外部图片链接，并用 LibreOffice 导出 PDF 核对页数。
6. **讲稿。** 可选，按 [`references/speech_guide.md`](references/speech_guide.md) 写逐页讲稿，`scripts/count_speech.py` 统计汉字数与时长。

### 生成的幻灯片

| 部分 | 内容 |
| --- | --- |
| 封面 | 中英文标题、会议或期刊、汇报人、日期 |
| 提纲 | 五个章节一览 |
| 分节页 | 固定五章：研究背景、研究思路、算法框架、实验结果、总结 |
| 内容页 | 每页 4 到 6 条要点，纯文字、图文或表格版式 |
| 致谢页 | 谢谢页与论文出处 |

学校、学院与实验室名称会从你提供的信息绘制进页眉与封面横幅；提供学校名称时，从 [urongda.com](https://www.urongda.com/) 获取的真实校徽会替换通用校徽，不需要手动改模板。

## 文档

| 内容 | 入口 |
| --- | --- |
| 技能流程与内容规范 | [`SKILL.md`](SKILL.md) |
| 内容 JSON 字段与版式 | [`references/deck_schema.md`](references/deck_schema.md) |
| 演讲稿写作规范 | [`references/speech_guide.md`](references/speech_guide.md) |
| 英文介绍 | [English README](README.md) |

## 仓库结构

```
group-meeting-ppt/
├── SKILL.md                # 技能入口：流程与内容规范
├── agents/openai.yaml      # OpenAI 侧（Codex）的展示元数据
├── assets/
│   └── default/
│       └── template.pptx   # 默认版式模板（封面、分节页、内容页母版）
├── references/
│   ├── deck_schema.md      # 内容 JSON 字段说明
│   └── speech_guide.md     # 演讲稿写作规范
└── scripts/
    ├── build_deck.py       # 主构建脚本
    ├── pptxkit.py          # 低层 OOXML 组装
    ├── banner.py           # 绘制校徽、页眉与封面横幅
    ├── read_paper.py       # 读取论文元信息
    ├── extract_figures.py  # 从 PDF 裁剪插图
    ├── fetch_emblem.py     # 从 urongda.com 下载学校校徽
    ├── render_check.py     # 外部链接检查与 PDF 导出
    └── count_speech.py     # 演讲稿字数统计
```

## 内容规范

- 章节固定为研究背景、研究思路、算法框架、实验结果、总结
- 每页要点 4 到 6 条，单条不超过 60 个汉字，符号与下标使用 Unicode（例如 `α`、`N̂`、`R₁`）
- 数值、指标名称、实验设置必须与论文一致，论文没有给出的结论不补写

## 许可证

[MIT](LICENSE) © 2026 inwf。

<p align="center"><sub>如果 group-meeting-ppt 让你在组会前省下时间，欢迎在 <a href="https://github.com/inwf/group-meeting-ppt">GitHub</a> 上点亮 Star，让更多人发现它。</sub></p>
