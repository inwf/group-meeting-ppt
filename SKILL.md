---
name: group-meeting-ppt
description: 依据 assets/template.pptx 的版式生成中文学术论文分享或组会汇报 PPT，并可选配 8 分钟演讲稿。适用于用户要求做文献调研汇报、组会 PPT、论文分享幻灯片，且手头有一篇论文 PDF 或只给论文标题的场景。
metadata:
  short-description: 用固定模板生成论文分享与组会 PPT
---

# 组会 PPT 生成

用 `assets/` 中的模板的封面、分节页、内容页版式生成整套汇报幻灯片，产出物是 `.pptx` 文件。内容来自用户提供的论文 PDF；没有 PDF 时按用户给出的论文标题和摘要组织内容。

## 输入信息

开场先询问用户的个人信息：姓名、学校、学院（专业）、实验室，并说明可以回答「用默认信息」跳过。用户消息里已给出的不要重复问；论文 PDF 路径、论文标题、汇报场景也从消息或询问中获得。缺省处理：

- 姓名缺失：封面只写「汇报人」，不写占位符以外的姓名。
- 学校缺失：使用 `XX大学`。
- 学院缺失：中文用 `XX学院`，英文用 `School of XX`。
- 实验室缺失：沿用学院名称。
- 论文 PDF 缺失：向用户询问论文标题或 arXiv 编号，据此组织内容。
- 汇报日期缺失：使用当前年月。

通用名称只用于填空，不要写进正文段落。不要在产出物中写入任何用户未提供过的个人信息。

## 模板

模板从 `assets/` 目录选取，`build_deck.py` 在省略 `--template` 时自动判断：

1. `assets/` 中除 `template.pptx` 外只有一个 `.pptx` 时，视为用户自定义模板，直接使用。用户把带好学校名称、校徽、配色的 pptx 放进 `assets/` 即可，此时页眉与封面沿用模板内容，不再按 `meta` 重绘，也不需要下载校徽。仍有多个自定义模板时脚本会报错，这时让用户只保留一个，或用 `--template` 显式指定。
2. 没有自定义模板时使用 `assets/template.pptx`（默认模板），并按 `meta` 重绘页眉与封面。
3. 使用自定义模板但用户要求按个人信息重绘页眉与封面时，加 `--redraw-banners`；同时提供了 `--emblem` 时也会自动重绘。

自定义模板必须基于默认模板修改：页面尺寸保持 4:3（9144000 × 6858000 EMU），保留全部版式、母版与所需媒体文件。不符合时脚本会报错并说明缺少什么。

## 校徽

只在**使用默认模板**时获取校徽，生成时用 `--emblem` 画进页眉与封面：

1. 先尝试下载：在 urongda.com（校徽大全）找到该校校徽，执行 `python3 scripts/fetch_emblem.py --school <学校名> --out <中间目录>/emblem.png`。
2. 下载失败（找不到该校、站点不可用等）时，请用户提供校徽图片路径，或提示用户到 https://www.urongda.com/ 自行下载后给出文件路径。
3. 用户用默认信息，或明确不要校徽时跳过，`build_deck.py` 会绘制通用校徽。

使用自定义模板时，校徽应已画在模板里，不需要这一步；用户要求替换模板里的校徽时，可用 `--emblem <文件> --redraw-banners` 重绘。

校徽图片 PNG（可带透明通道）或 JPG 均可，正方形或圆形图案效果最好。

## 流程

下面命令中的 `scripts/`、`assets/`、`references/` 路径都相对本技能目录，执行时先切换到技能目录，或把路径换成绝对路径。

1. 读取论文。有 PDF 时执行 `python3 scripts/read_paper.py --pdf <pdf>` 取得标题、作者、页数、摘要与首页行，用于填写封面和正文。再通读全文，按 `references/deck_schema.md` 的五个章节整理内容。
2. 挑选配图。用 `python3 scripts/extract_figures.py --pdf <pdf> --pages 3,6,7 --out <图片目录> --work <中间目录>` 从论文中裁出关键插图，脚本会按页内坐标裁剪并输出文件名。只保留能说明机制或结果的图，其余页面用文字要点。
3. 写内容 JSON。按 `references/deck_schema.md` 的字段组织 `meta` 与 `slides`，每个章节 3 到 6 页。数值、指标名称、实验设置必须与论文一致。
4. 生成 PPT。省略 `--template`，脚本会自动选用 `assets/` 中的自定义模板或默认模板；需要校徽时按「校徽」一节获取并加 `--emblem <校徽文件>`。执行：

   ```
   python3 scripts/build_deck.py --deck <内容.json> --out <输出.pptx> \
     --media <图片目录> --work <中间目录>
   ```

   脚本会解包模板、替换学院名称与文档属性、重建全部幻灯片、写回内容类型表并打包。表格列宽不齐、表格重叠、表格越界都会直接报错。
5. 校验。执行 `python3 scripts/render_check.py --pptx <输出.pptx> --outdir <导出目录>`，它会检查包内是否存在外部图片链接（PowerPoint 会因此提示阻止自动下载图片），并用 LibreOffice 导出 PDF 核对页数。
6. 需要演讲稿时，按 `references/speech_guide.md` 写逐页讲稿。

## 内容要求

- 章节顺序为研究背景、研究思路、算法框架、实验结果、总结，模板的分节页只提供这五个章节。
- 每页要点控制在 4 到 6 条，单条不超过 60 个汉字，符号与下标使用 Unicode（例如 `α`、`N̂`、`R₁`）。
- 表格用于实验设置和结果对比，同一页最多两张表，两表横向并排时左表宽度加右表宽度再加间距不超过 8138160 EMU。
- 论文没有给出的结论不要补写，数据以论文原文为准。

## 素材与脚本

- `assets/template.pptx`：默认版式来源，包含封面、五套分节页、内容页母版与配色。素材内的学院与学校已是通用名称，页脚与文档属性中的占位由 `build_deck.py` 按 `meta` 替换，不要把带个人信息的默认模板直接放进来。
- `assets/` 中的其他 `.pptx`：用户自定义模板，优先于默认模板使用，页眉与封面保持模板原样。
- `scripts/pptxkit.py`：低层 OOXML 组装函数，供 `build_deck.py` 调用。
- `scripts/banner.py`：绘制通用校徽、页眉横幅与封面横幅，文字取自 `meta`。
- `scripts/build_deck.py`：主构建脚本。
- `scripts/read_paper.py`：读取论文元信息与摘要。
- `scripts/extract_figures.py`：从 PDF 裁剪插图。
- `scripts/fetch_emblem.py`：从 urongda.com 下载学校校徽。
- `scripts/render_check.py`：外部链接检查与 PDF 导出。
- `scripts/count_speech.py`：统计演讲稿汉字数与预计时长。
- `references/deck_schema.md`：内容 JSON 字段说明与版式示例。
- `references/speech_guide.md`：演讲稿写作规范与时长控制。

脚本依赖 `lxml`、`Pillow` 与 `numpy`，并使用系统命令 `pdfinfo`、`pdftotext`、`pdftohtml`、`pdftoppm`、`libreoffice`（或 `soffice`）；横幅绘制需要 `scripts/banner.py` 中列出的中英文字体。缺失时用 `uv` 安装 Python 依赖。
