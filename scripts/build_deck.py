import argparse
import json
import re
import shutil
import sys
import zipfile
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

from lxml import etree

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))

import banner
from pptxkit import (P, new_spTree, textbox, picture, table, slide_xml,
                     sldnum, fit)

SLIDE_W = 9144000
SLIDE_H = 6858000
LAYOUT_TITLE = '../slideLayouts/slideLayout3.xml'
LAYOUT_CONTENT = '../slideLayouts/slideLayout2.xml'
REL_NS = 'http://schemas.openxmlformats.org/package/2006/relationships'
CT_NS = 'http://schemas.openxmlformats.org/package/2006/content-types'

SKILL_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = SKILL_ROOT / 'assets'
DEFAULT_TEMPLATE_DIR = ASSETS_DIR / 'default'
DEFAULT_TEMPLATE_NAME = 'template.pptx'
REQUIRED_PARTS = [
    'ppt/presentation.xml',
    'ppt/slideLayouts/slideLayout2.xml',
    'ppt/slideLayouts/slideLayout3.xml',
    'ppt/slides/slide2.xml', 'ppt/slides/slide3.xml', 'ppt/slides/slide8.xml',
    'ppt/slides/slide13.xml', 'ppt/slides/slide19.xml', 'ppt/slides/slide27.xml',
    'ppt/media/image1.png', 'ppt/media/image3.jpeg',
    'docProps/app.xml', 'docProps/core.xml', 'docProps/thumbnail.jpeg',
]

SECTIONS = ['研究背景', '研究思路', '算法框架', '实验结果', '总结']
OUTLINE_SOURCE = {'提纲': 2, '研究背景': 3, '研究思路': 8,
                  '算法框架': 13, '实验结果': 19, '总结': 27}

GENERIC = {'presenter': '', 'school': 'XX大学', 'school_en': 'XX UNIVERSITY',
           'college_cn': 'XX学院', 'college_en': 'School of XX',
           'lab_cn': 'XX重点实验室', 'lab_en': 'Key Laboratory of XX'}


def media_size(path):
    from PIL import Image
    with Image.open(path) as im:
        return im.size


def table_specs(spec):
    return spec.get('tables') or []


def check_tables(spec):
    rects = []
    for t in table_specs(spec):
        rows, colw = t['rows'], t['colw']
        x, y, w = t['x'], t['y'], t['w']
        rowh = t.get('rowh', 365760)
        ncol = len(rows[0])
        if len(colw) != ncol:
            raise ValueError(
                f'{spec["subtitle"]}: 列宽数量 {len(colw)} 与单元格数量 {ncol} 不一致')
        if sum(colw) != w:
            raise ValueError(
                f'{spec["subtitle"]}: 列宽之和 {sum(colw)} 与表格宽度 {w} 不一致')
        if any(len(r) != ncol for r in rows):
            raise ValueError(f'{spec["subtitle"]}: 存在列数不齐的行')
        if x < 0 or y < 0 or x + w > SLIDE_W:
            raise ValueError(f'{spec["subtitle"]}: 表格超出幻灯片横向范围')
        h = rowh * len(rows)
        if y + h > SLIDE_H:
            raise ValueError(f'{spec["subtitle"]}: 表格超出幻灯片纵向范围')
        rects.append((x, y, x + w, y + h))
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            a, b = rects[i], rects[j]
            if a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]:
                raise ValueError(f'{spec["subtitle"]}: 表格位置重叠')


def add_pic(tree, sid, media_dir, filename, box):
    iw, ih = media_size(media_dir / filename)
    off, ext = fit(box, iw, ih)
    picture(tree, sid, f'Picture {sid}', off, ext, 'rId2', descr=filename)


def bullet_paras(items, sz=1600):
    paras = []
    for it in items:
        level, text = (0, it) if isinstance(it, str) else it
        if level == 0:
            paras.append({'runs': [{'t': '· ', 'sz': sz, 'b': 1},
                                   {'t': text, 'sz': sz, 'b': 0}],
                          'lnspc': '135000'})
        else:
            paras.append({'runs': [{'t': '– ', 'sz': sz - 200, 'b': 1,
                                    'color': '595959'},
                                   {'t': text, 'sz': sz - 200, 'b': 0}],
                          'lnspc': '135000', 'marL': 457200})
    return paras


def caption(tree, sid, text, y, x, cx):
    textbox(tree, sid, f'TextBox {sid}', (x, y), (cx, 365760),
            [{'runs': [{'t': text, 'sz': 1100, 'b': 0, 'color': '595959'}],
              'algn': 'ctr'}], anchor='t')


def content_tree(spec, media_dir):
    sec, sub, sz = spec['section'], spec['subtitle'], spec.get('sz', 1500)
    check_tables(spec)
    tree = new_spTree()
    textbox(tree, 2, 'TextBox 1', (6483096, 9144), (1828800, 630936),
            [{'runs': [{'t': sec, 'sz': 3200, 'b': 1, 'color': 'FFFFFF',
                        'latin': 'Times New Roman'}], 'algn': 'ctr'}],
            anchor='ctr', wrap='none')
    textbox(tree, 5056, 'TextBox 5055', (502920, 914400), (7315200, 411480),
            [{'runs': [{'t': sub, 'sz': 2000, 'b': 0, 'color': '014181'}],
              'marL': 342900, 'indent': -342900, 'bullet': ('Wingdings', 'p')}])
    layout = spec['layout']
    if layout == 'full':
        textbox(tree, 5057, 'TextBox 5056', (502920, 1325880),
                (8138160, 5029200), bullet_paras(spec['bullets'], sz=sz))
    elif layout == 'fig':
        textbox(tree, 5057, 'TextBox 5056', (502920, 1325880),
                (8138160, spec.get('txt_h', 1900000)),
                bullet_paras(spec['bullets'], sz=sz))
        add_pic(tree, 5058, media_dir, spec['fig'],
                (502920, spec.get('fig_y', 3300000), 8138160,
                 spec.get('fig_h', 2400000)))
        caption(tree, 5059, spec.get('cap', ''), spec.get('cap_y', 5760000),
                1188720, 6766560)
    elif layout == 'table':
        sid = 5150
        bottom = 0
        for t in table_specs(spec):
            rowh = t.get('rowh', 365760)
            h = rowh * len(t['rows'])
            table(tree, sid, f'Table {sid}', (t['x'], t['y']), (t['w'], h),
                  t['rows'], t['colw'], hdr_h=rowh, row_h=rowh, sz=sz)
            sid += 2
            bottom = max(bottom, t['y'] + h)
        if spec.get('bullets'):
            top = bottom + 137160
            textbox(tree, sid, f'TextBox {sid}', (502920, top),
                    (8138160, SLIDE_H - top - 457200),
                    bullet_paras(spec['bullets'], sz=spec.get('bsz', 1250)))
    else:
        raise ValueError(f'{sub}: 未知版式 {layout}')
    sldnum(tree, 5055)
    return tree


def title_tree(meta):
    tree = new_spTree()
    picture(tree, 2, 'Picture 1', (0, 0), (9144000, 1682496), 'rId2',
            descr='image3.jpeg')
    presenter = meta.get('presenter') or GENERIC['presenter']
    author = f'汇报人：{presenter}' if presenter else '汇报人'
    textbox(tree, 3, 'TextBox 2', (0, 2388235), (9144000, 2721610), [
        {'runs': [{'t': meta['title_en'], 'sz': 2400, 'b': 1, 'color': '000000',
                   'latin': 'Times New Roman'}], 'algn': 'ctr', 'spcBef': 1000},
        {'runs': [{'t': meta['title_cn'], 'sz': 2200, 'b': 1, 'color': '0000CC',
                   'latin': 'Times New Roman'}], 'algn': 'ctr', 'spcBef': 1000},
        {'runs': [{'t': meta['venue'], 'sz': 1800, 'b': 0, 'color': '595959',
                   'latin': 'Times New Roman'}], 'algn': 'ctr', 'spcBef': 1000},
        {'runs': [{'t': author, 'sz': 2400, 'b': 0, 'color': '000000',
                   'latin': 'Times New Roman'}], 'algn': 'ctr', 'spcBef': 1000},
        {'runs': [{'t': meta['date'], 'sz': 2400, 'b': 0, 'color': '000000',
                   'latin': 'Times New Roman'}], 'algn': 'ctr', 'spcBef': 1000},
    ])
    return tree


def closing_tree(meta):
    tree = new_spTree()
    picture(tree, 2, 'Picture 1', (0, 0), (9144000, 1682496), 'rId2',
            descr='image3.jpeg')
    textbox(tree, 3, 'TextBox 2', (0, 2743200), (9144000, 608330),
            [{'runs': [{'t': '谢谢！', 'sz': 3600, 'b': 1, 'color': '000000',
                        'latin': 'Times New Roman'}], 'algn': 'ctr'}], anchor='t')
    textbox(tree, 4, 'TextBox 3', (457200, 3840480), (8229600, 731520),
            [{'runs': [{'t': f'{meta["title_en"]}  ({meta["venue_full"]})',
                        'sz': 1400, 'b': 0, 'color': '595959',
                        'latin': 'Times New Roman'}], 'algn': 'ctr'}], anchor='t')
    return tree


def outline_tree(template, section):
    src = template / 'ppt' / 'slides' / f'slide{OUTLINE_SOURCE[section]}.xml'
    root = etree.parse(str(src)).getroot()
    return root.find(f'{{{P}}}cSld').find(f'{{{P}}}spTree')


def plan(deck):
    slides = [dict(kind='title')]
    slides.append(dict(kind='outline', section='提纲'))
    for sec in deck.get('sections', SECTIONS):
        if sec not in OUTLINE_SOURCE:
            raise ValueError(f'未知章节 {sec}，模板只提供 {list(OUTLINE_SOURCE)}')
        slides.append(dict(kind='outline', section=sec))
        for spec in deck['slides']:
            if spec['section'] == sec:
                slides.append(dict(kind='content', spec=spec))
    known = set(deck.get('sections', SECTIONS)) | {'提纲'}
    for spec in deck['slides']:
        if spec['section'] not in known:
            raise ValueError(f'{spec["subtitle"]}: 章节 {spec["section"]} 不在 sections 中')
    slides.append(dict(kind='closing'))
    return slides


def slide_rels(layout, img=None):
    parts = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
             f'<Relationships xmlns="{REL_NS}">',
             f'<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="{layout}"/>']
    if img:
        parts.append(
            '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"'
            f' Target="../media/{img}"/>')
    parts.append('</Relationships>')
    return ''.join(parts).encode()


def fix_content_types(build, n):
    ct = build / '[Content_Types].xml'
    root = etree.parse(str(ct)).getroot()
    for o in list(root):
        if o.get('PartName', '').startswith('/ppt/slides/slide'):
            root.remove(o)
    for i in range(1, n + 1):
        e = etree.SubElement(root, f'{{{CT_NS}}}Override')
        e.set('PartName', f'/ppt/slides/slide{i}.xml')
        e.set('ContentType',
              'application/vnd.openxmlformats-officedocument.presentationml.slide+xml')
    ct.write_bytes(b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n' +
                   etree.tostring(root))


def find_template(explicit=None):
    # 省略 --template 时：assets/ 根目录中的 .pptx 视为用户自定义模板，
    # 没有自定义模板时使用 assets/default/ 中的默认模板
    if explicit:
        return Path(explicit), False
    if not ASSETS_DIR.is_dir():
        raise SystemExit(f'找不到模板目录 {ASSETS_DIR}')
    default = DEFAULT_TEMPLATE_DIR / DEFAULT_TEMPLATE_NAME
    custom = sorted(ASSETS_DIR.glob('*.pptx'))
    if len(custom) > 1:
        names = '、'.join(p.name for p in custom)
        raise SystemExit(
            f'assets/ 中有多个自定义模板：{names}。'
            '请只保留一个，或用 --template 显式指定')
    if custom:
        return custom[0], True
    if not default.exists():
        raise SystemExit(f'找不到默认模板 {default}')
    return default, False


def validate_template(path):
    try:
        z = zipfile.ZipFile(path)
    except (FileNotFoundError, zipfile.BadZipFile):
        raise SystemExit(
            f'{path} 不是有效的 pptx 文件。自定义模板需基于默认模板 '
            f'{DEFAULT_TEMPLATE_NAME} 修改后放入 assets/')
    with z:
        names = set(z.namelist())
        missing = [n for n in REQUIRED_PARTS if n not in names]
        if missing:
            raise SystemExit(
                f'{path} 缺少模板所需部件：{", ".join(missing)}。'
                '自定义模板需基于默认模板修改，保留原有版式与媒体文件')
        pres = z.read('ppt/presentation.xml').decode('utf-8')
        m = re.search(r'<p:sldSz\b([^>]*)>', pres)
        cx = re.search(r'cx="(\d+)"', m.group(1)) if m else None
        cy = re.search(r'cy="(\d+)"', m.group(1)) if m else None
        if not cx or not cy or (int(cx.group(1)), int(cy.group(1))) != (SLIDE_W, SLIDE_H):
            raise SystemExit(
                f'{path} 的页面尺寸不是 {SLIDE_W} × {SLIDE_H}（10 × 7.5 英寸，4:3），'
                '无法使用。自定义模板需保持默认模板的页面尺寸')


def personalize(template, meta, n_slides, emblem=None, redraw_banners=True):
    cn = meta.get('college_cn') or GENERIC['college_cn']
    en = meta.get('college_en') or GENERIC['college_en']
    school = meta.get('school') or GENERIC['school']
    if redraw_banners:
        school_en = meta.get('school_en') or GENERIC['school_en']
        lab_cn = meta.get('lab_cn') or cn
        lab_en = meta.get('lab_en') or en
        media = template / 'ppt' / 'media'
        header = media / 'image1.png'
        with Image.open(header) as im:
            header.write_bytes(banner.header_png(school, school_en, lab_cn, lab_en,
                                                 size=im.size, emblem=emblem))
        cover = media / 'image3.jpeg'
        with Image.open(cover) as im:
            cover.write_bytes(banner.cover_jpeg(school, lab_cn, lab_en, size=im.size,
                                                emblem=emblem))
        thumb = template / 'docProps' / 'thumbnail.jpeg'
        with Image.open(thumb) as im:
            thumb.write_bytes(banner.thumb_jpeg(im.width, im.height))
    for f in sorted((template / 'ppt' / 'slideLayouts').glob('*.xml')):
        s = f.read_text(encoding='utf-8')
        s = s.replace('<a:t>XX学院  </a:t>', f'<a:t>{escape(cn)}  </a:t>')
        s = s.replace('<a:t>School of XX</a:t>',
                      f'<a:t>{escape(en)}</a:t>')
        f.write_text(s, encoding='utf-8')
    app = template / 'docProps' / 'app.xml'
    s = app.read_text(encoding='utf-8')
    s = s.replace('<Company>XX大学</Company>', f'<Company>{escape(school)}</Company>')
    s = re.sub(r'<Slides>\d+</Slides>', f'<Slides>{n_slides}</Slides>', s)
    app.write_text(s, encoding='utf-8')
    core = template / 'docProps' / 'core.xml'
    s = core.read_text(encoding='utf-8')
    s = re.sub(r'<dc:title>[^<]*</dc:title>',
               f'<dc:title>{escape(meta["title_en"])}</dc:title>', s)
    s = s.replace('<dc:creator>XX大学</dc:creator>',
                  f'<dc:creator>{escape(school)}</dc:creator>')
    s = s.replace('<cp:lastModifiedBy>XX大学</cp:lastModifiedBy>',
                  f'<cp:lastModifiedBy>{escape(school)}</cp:lastModifiedBy>')
    core.write_text(s, encoding='utf-8')


def main():
    ap = argparse.ArgumentParser(description='按模板生成组会汇报 PPT')
    ap.add_argument('--deck', required=True, help='内容 JSON 文件')
    ap.add_argument('--out', required=True, help='输出 pptx 路径')
    ap.add_argument('--media', required=True, help='图片目录')
    ap.add_argument('--work', required=True, help='中间目录')
    ap.add_argument('--template',
                    help='模板 pptx 路径；省略时自动选用 assets/ 中的自定义模板，没有则用 assets/default/ 的默认模板')
    ap.add_argument('--emblem', help='校徽图片路径（可选），绘制进页眉与封面')
    ap.add_argument('--redraw-banners', action='store_true',
                    help='使用自定义模板时，仍按 meta 重绘页眉与封面横幅')
    args = ap.parse_args()

    template_path, custom = find_template(args.template)
    validate_template(template_path)
    print(f'模板：{template_path}' + ('（自定义）' if custom else '（默认）'))
    deck = json.loads(Path(args.deck).read_text(encoding='utf-8'))
    meta = dict(deck.get('meta', {}))
    meta.setdefault('title_en', '论文英文标题')
    meta.setdefault('title_cn', '论文中文标题')
    meta.setdefault('venue', '文献调研分享')
    meta.setdefault('venue_full', '')
    meta.setdefault('date', f'{date.today().year} 年 {date.today().month} 月')

    work = Path(args.work)
    media = Path(args.media)
    template = work / 'template'
    build = work / 'build'
    out = Path(args.out)

    if work.exists():
        shutil.rmtree(work)
    template.mkdir(parents=True)
    with zipfile.ZipFile(template_path) as z:
        z.extractall(template)

    emblem = None
    if args.emblem:
        ep = Path(args.emblem)
        if not ep.exists():
            raise SystemExit(f'找不到校徽文件 {ep}')
        with Image.open(ep) as im:
            emblem = im.convert('RGBA')

    slides = plan(deck)
    redraw = (not custom) or args.redraw_banners or args.emblem is not None
    personalize(template, meta, len(slides), emblem,
                redraw_banners=redraw)
    if custom and not redraw:
        print('自定义模板：页眉与封面沿用模板内容，未重绘')

    if build.exists():
        shutil.rmtree(build)
    shutil.copytree(template, build)

    slides_dir = build / 'ppt' / 'slides'
    for f in slides_dir.glob('*.xml'):
        f.unlink()
    rels_dir = slides_dir / '_rels'
    for f in rels_dir.glob('*.rels'):
        f.unlink()

    figs = []
    for s in slides:
        if s['kind'] == 'content' and s['spec']['layout'] == 'fig':
            figs.append(s['spec']['fig'])
    for name in sorted(set(figs)):
        shutil.copy(media / name, build / 'ppt' / 'media' / name)

    entries = []
    for i, s in enumerate(slides, start=1):
        if s['kind'] in ('title', 'closing'):
            tree = title_tree(meta) if s['kind'] == 'title' else closing_tree(meta)
            rels = slide_rels(LAYOUT_TITLE, 'image3.jpeg')
        elif s['kind'] == 'outline':
            tree = outline_tree(template, s['section'])
            rels = slide_rels(LAYOUT_CONTENT)
        else:
            tree = content_tree(s['spec'], media)
            img = s['spec']['fig'] if s['spec']['layout'] == 'fig' else None
            rels = slide_rels(LAYOUT_CONTENT, img)
        (slides_dir / f'slide{i}.xml').write_bytes(slide_xml(tree))
        (rels_dir / f'slide{i}.xml.rels').write_bytes(rels)
        entries.append((256 + i - 1, f'rId{100 + i}', f'slides/slide{i}.xml'))

    n = len(slides)
    pres = etree.parse(str(build / 'ppt' / 'presentation.xml'))
    root = pres.getroot()
    lst = root.find(f'{{{P}}}sldIdLst')
    for c in list(lst):
        lst.remove(c)
    for sid, rid, target in entries:
        e = etree.SubElement(lst, f'{{{P}}}sldId')
        e.set('id', str(sid))
        e.set('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id', rid)

    prels = etree.parse(str(build / 'ppt' / '_rels' / 'presentation.xml.rels'))
    proot = prels.getroot()
    for rel in list(proot):
        if rel.get('Type', '').endswith('/slide'):
            proot.remove(rel)
    for sid, rid, target in entries:
        e = etree.SubElement(proot, f'{{{REL_NS}}}Relationship')
        e.set('Id', rid)
        e.set('Type', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide')
        e.set('Target', target)

    (build / 'ppt' / 'presentation.xml').write_bytes(
        b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n' +
        etree.tostring(root))
    (build / 'ppt' / '_rels' / 'presentation.xml.rels').write_bytes(
        b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n' +
        etree.tostring(proot))

    fix_content_types(build, n)

    if out.exists():
        out.unlink()
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        ct = build / '[Content_Types].xml'
        z.write(ct, '[Content_Types].xml')
        for p in sorted(build.rglob('*')):
            if p.is_file() and p.name != '[Content_Types].xml':
                z.write(p, str(p.relative_to(build)).replace('\\', '/'))
    print(f'生成 {n} 页 -> {out}')


if __name__ == '__main__':
    main()
