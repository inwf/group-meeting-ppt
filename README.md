# group-meeting-ppt

**简体中文** | [English](README.en.md)

一个 Agent Skills 技能：按固定模板生成中文组会汇报 PPT。给一篇论文 PDF（或论文标题），产出整套 `.pptx` 幻灯片，可选配 8 分钟演讲稿。

技能遵循 [Agent Skills](https://agentskills.io) 开放标准（`SKILL.md` 加脚本与资源目录），任何支持该标准的 agent 都能直接使用，目前已有 40 多个 agent 支持。安装后，agent 会按 `assets/template.pptx` 的版式自动生成封面、五章节分节页、内容页与致谢页，并校验表格排版与图片链接。

## 功能

- **读论文**：从 PDF 提取标题、作者、页数、摘要与 arXiv 编号
- **自动裁图**：按页内坐标从论文中以 600 DPI 裁剪关键插图
- **整套幻灯片**：封面、提纲、研究背景 / 研究思路 / 算法框架 / 实验结果 / 总结五章分节页、内容页、致谢页
- **三种内容版式**：纯文字、图文、表格；表格列宽不齐、重叠、越界会直接报错
- **生成校验**：检查 pptx 是否含外部图片链接（PowerPoint 打开时会因此提示阻止自动下载），并用 LibreOffice 导出 PDF 核对页数
- **演讲稿**：按页讲稿，脚本统计汉字数与预计时长（260 到 270 字/分钟）
- **占位替换**：学校、学院、实验室名称自动绘入页眉与封面横幅，并写入文档属性

## 安装

仓库根目录就是技能目录，克隆到该 agent 的技能目录即可，不需要改动任何文件。常见 agent 的技能目录示例：

- Claude Code：`~/.claude/skills/group-meeting-ppt`
- OpenAI Codex：`~/.codex/skills/group-meeting-ppt`
- Cursor：`~/.cursor/skills/group-meeting-ppt`
- Gemini CLI：`~/.gemini/skills/group-meeting-ppt`
- WorkBuddy / CodeBuddy：`~/.codebuddy/skills/group-meeting-ppt`

```bash
git clone https://github.com/inwf/group-meeting-ppt.git ~/.claude/skills/group-meeting-ppt
```

其他 agent 同理，换成它的技能目录即可；项目级安装放在仓库的 `.agents/skills/`（多数 agent 识别的通用位置）下。仓库内的 `agents/openai.yaml` 提供 Codex 的显示名称、简介与默认提示词。

安装后新开一个会话即可。提到「组会 PPT」「论文分享」时 agent 会按 description 自动调用；显式调用方式各 agent 略有不同，例如 Claude Code 的 `/group-meeting-ppt`、Codex 的 `$group-meeting-ppt`。

## 依赖

Python 包（在技能目录下安装）：

```bash
pip install -r requirements.txt   # lxml、Pillow、numpy
```

系统命令：

| 命令 | 用途 | macOS | Ubuntu / Debian |
| --- | --- | --- | --- |
| `pdfinfo` `pdftotext` `pdftohtml` `pdftoppm` | 读论文、裁图 | `brew install poppler` | `sudo apt install poppler-utils` |
| `libreoffice` 或 `soffice` | 仅校验步骤导出 PDF | `brew install --cask libreoffice` | `sudo apt install libreoffice` |

Windows 上 poppler 没有官方安装包，可用 `scoop install poppler` 或 `conda install -c conda-forge poppler`；LibreOffice 安装后需要把程序目录加入 PATH。

字体：绘制横幅需要一个中文无衬线字体和一个西文衬线粗体字体。macOS 自带 PingFang 或 Hiragino Sans GB 与 Times New Roman；Linux 需 Noto Sans CJK（或文泉驿）与 Liberation / DejaVu；Windows 使用微软雅黑与 Times New Roman。候选路径见 `scripts/banner.py`。

## 使用

在 agent 会话中直接描述任务，例如：

> 用 group-meeting-ppt 做一份组会 PPT：论文在 `~/papers/attention-is-all-you-need.pdf`，汇报人张三，XX大学计算机学院，智能计算实验室，日期 2026 年 10 月，另配一份 8 分钟演讲稿。

信息缺失时：姓名缺失则封面只写「汇报人」；学校、学院、实验室缺失时用 `XX大学`、`XX学院`、`School of XX` 占位；没有 PDF 时 agent 会询问论文标题或 arXiv 编号，据此组织内容。

## 工作流程

1. `scripts/read_paper.py` 读取论文元信息与摘要
2. `scripts/extract_figures.py` 从 PDF 裁出关键插图
3. 按 `references/deck_schema.md` 组织内容 JSON
4. `scripts/build_deck.py` 解包模板、重建全部幻灯片并打包
5. `scripts/render_check.py` 检查外部链接并用 LibreOffice 导出 PDF 核对页数
6. 按 `references/speech_guide.md` 写演讲稿，`scripts/count_speech.py` 统计字数与时长

## 目录结构

```
group-meeting-ppt/
├── SKILL.md                # 技能入口：流程与内容规范
├── agents/openai.yaml      # OpenAI 侧（Codex）的展示元数据
├── assets/template.pptx    # 版式模板（封面、分节页、内容页母版）
├── references/
│   ├── deck_schema.md      # 内容 JSON 字段说明
│   └── speech_guide.md     # 演讲稿写作规范
└── scripts/
    ├── build_deck.py       # 主构建脚本
    ├── pptxkit.py          # 低层 OOXML 组装
    ├── banner.py           # 绘制校徽、页眉与封面横幅
    ├── read_paper.py       # 读取论文元信息
    ├── extract_figures.py  # 从 PDF 裁剪插图
    ├── render_check.py     # 外部链接检查与 PDF 导出
    └── count_speech.py     # 演讲稿字数统计
```

## 内容规范

- 章节固定为研究背景、研究思路、算法框架、实验结果、总结
- 每页要点 4 到 6 条，单条不超过 60 个汉字，符号与下标使用 Unicode（例如 `α`、`N̂`、`R₁`）
- 数值、指标名称、实验设置必须与论文一致，论文没有给出的结论不补写
- `assets/template.pptx` 内的学校与学院是通用占位；不要把带个人信息的模板提交进仓库

## 许可

[MIT](LICENSE)
