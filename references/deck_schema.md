# 内容 JSON 字段说明

`scripts/build_deck.py` 的 `--deck` 参数读取一个 UTF-8 JSON 文件，结构为：

```json
{
  "meta": { "……": "……" },
  "sections": ["研究背景", "研究思路", "算法框架", "实验结果", "总结"],
  "slides": [ { "section": "……", "subtitle": "……", "layout": "……", "……": "……" } ]
}
```

坐标单位是 EMU（914400 EMU = 1 英寸），幻灯片尺寸 9144000 × 6858000（10 × 7.5 英寸，4:3）；字号单位是百分之一磅，`1500` 表示 15pt。未知字段会被忽略。

## meta

| 字段 | 缺省值 | 用途 |
| --- | --- | --- |
| `title_en` | `论文英文标题` | 封面第一行、致谢页 |
| `title_cn` | `论文中文标题` | 封面第二行 |
| `venue` | `文献调研分享` | 封面第三行（会议、期刊或分享类型） |
| `venue_full` | 空 | 致谢页标题后括号内内容，建议填写 |
| `date` | 当前年月 | 封面日期行 |
| `presenter` | 空 | 封面「汇报人：X」；空时只显示「汇报人」 |
| `school` / `school_en` | `XX大学` / `XX UNIVERSITY` | 页眉横幅、文档属性 |
| `college_cn` / `college_en` | `XX学院` / `School of XX` | 替换模板母版中的页脚 |
| `lab_cn` / `lab_en` | 同 `college_cn` / `college_en` | 页眉横幅与封面横幅 |

学校与实验室名称由 `scripts/banner.py` 绘制进横幅图片，依赖系统字体，候选路径见该脚本。

## sections

可选。缺省为全部五章：研究背景、研究思路、算法框架、实验结果、总结。模板只提供这五章的固定分节页，不能增删章节；`slides[].section` 必须出现在 `sections` 中。

生成顺序：封面 → 提纲页 → 每个章节（分节页 + 该章内容页，章内按 JSON 顺序）→ 致谢页。

## slides 公共字段

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `section` | 是 | 章节名，五选一 |
| `subtitle` | 是 | 内容页标题 |
| `layout` | 是 | `full`、`fig`、`table` 之一 |
| `sz` | 否 | 正文字号，缺省 `1500`(15pt) |
| `bullets` | 否 | 要点数组，元素为字符串（一级）或 `[层级, 文本]`（层级 `1` 为二级） |

要点渲染：一级前缀「·」加粗，二级前缀「–」灰色并缩进，行距 135%。每个章节建议 3 到 6 页，每页要点 4 到 6 条，单条不超过 60 个汉字。

## layout: full

只有要点，占满内容区。字段：`bullets`。

## layout: fig

上方要点，下方图片与图注。

| 字段 | 缺省值 | 说明 |
| --- | --- | --- |
| `fig` | 必填 | 图片文件名，相对 `--media` 目录 |
| `bullets` | 否 | 上方要点 |
| `txt_h` | `1900000` | 要点区高度 |
| `fig_y` | `3300000` | 图片区纵坐标 |
| `fig_h` | `2400000` | 图片区高度 |
| `cap` | 空 | 图注文本 |
| `cap_y` | `5760000` | 图注纵坐标 |

图片按等比缩放并居中放入 (502920, `fig_y`) 起、宽 8138160、高 `fig_h` 的区域，不会裁切或拉伸。图片由 `scripts/extract_figures.py` 生成，命名形如 `fig_p3_1.png`。

## layout: table

表格版式，可选在表格下方加要点。

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `tables` | 是 | 表格数组，每张表见下 |
| `bullets` | 否 | 排在最下方表格之下 |
| `bsz` | 否 | 表格下方要点字号，缺省 `1250`(12.5pt) |

每张表：

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `rows` | 是 | 二维数组，首行为表头（深蓝底白字 13pt），其余行黑字白底 |
| `colw` | 是 | 列宽数组，数量等于列数，各列宽之和必须等于 `w` |
| `x` / `y` | 是 | 左上角坐标 |
| `w` | 是 | 表格宽度 |
| `rowh` | 否 | 行高，缺省 `365760`（0.4 英寸） |

同一页最多两张表；两张表横向并排时，两表宽度加间距之和不超过 8138160 EMU（内容区宽度）。

以下情况会直接报错：列宽数量与单元格数量不一致、列宽之和不等于 `w`、存在列数不齐的行、表格越出幻灯片范围、多张表位置重叠。

## 示例

```json
{
  "meta": {
    "title_en": "Attention Is All You Need",
    "title_cn": "注意力机制即全部所需",
    "venue": "NeurIPS 2017",
    "venue_full": "Advances in Neural Information Processing Systems 30",
    "date": "2026 年 10 月",
    "presenter": "张三",
    "school": "XX大学",
    "school_en": "XX UNIVERSITY",
    "college_cn": "计算机学院",
    "college_en": "School of Computer Science",
    "lab_cn": "智能计算实验室",
    "lab_en": "Laboratory of Intelligent Computing"
  },
  "sections": ["研究背景", "算法框架", "实验结果"],
  "slides": [
    {
      "section": "研究背景",
      "subtitle": "序列建模的现状与问题",
      "layout": "full",
      "bullets": [
        "循环网络按时间步串行计算，训练难以并行",
        [1, "长距离依赖随步数增加而衰减"],
        "卷积网络可并行，但感受野受卷积核大小限制",
        "注意力机制可直接建模任意两位置之间的关系"
      ]
    },
    {
      "section": "算法框架",
      "subtitle": "Transformer 整体架构",
      "layout": "fig",
      "bullets": [
        "编码器与解码器各堆叠 6 层",
        "每层由多头注意力与前馈网络组成",
        "残差连接与层归一化贯穿每个子层"
      ],
      "fig": "fig_p3_1.png",
      "cap": "图 1  模型整体架构（裁剪自论文第 3 页）"
    },
    {
      "section": "实验结果",
      "subtitle": "WMT 2014 英德翻译结果",
      "layout": "table",
      "tables": [
        {
          "rows": [
            ["模型", "BLEU", "训练成本（FLOPs）"],
            ["Transformer (big)", "28.4", "2.3 × 10¹⁹"],
            ["Transformer (base)", "27.3", "3.3 × 10¹⁸"]
          ],
          "colw": [2869080, 1639080, 3630000],
          "x": 502920,
          "y": 1450000,
          "w": 8138160
        }
      ],
      "bullets": ["数值取自论文表 2，均为单模型结果"],
      "bsz": 1250
    }
  ]
}
```
