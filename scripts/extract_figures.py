import argparse
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

def page_size(pdf):
    info = subprocess.run(['pdfinfo', str(pdf)], capture_output=True,
                          text=True, check=True).stdout
    m = re.search(r'Page size:\s+([\d.]+)\s+x\s+([\d.]+)\s+pts', info)
    if not m:
        raise RuntimeError('无法从 pdfinfo 读取页面尺寸')
    return float(m.group(1)), float(m.group(2))


def parse_pages(pdf, work, first, last):
    stem = work / 'layout'
    subprocess.run(['pdftohtml', '-xml', '-f', str(first), '-l', str(last), str(pdf),
                    str(stem)], check=True, capture_output=True)
    xml = (stem.with_suffix('.xml')).read_text(encoding='utf-8')
    xml = re.sub(r'<!DOCTYPE[^>]*>', '', xml)
    root = ET.fromstring(xml)
    pages = {}
    for page in root.findall('page'):
        num = int(page.get('number'))
        w = float(page.get('width'))
        h = float(page.get('height'))
        items = []
        for img in page.findall('image'):
            items.append(dict(
                top=float(img.get('top')), left=float(img.get('left')),
                width=float(img.get('width')), height=float(img.get('height'))))
        pages[num] = dict(w=w, h=h, items=items)
    return pages


def render_page(pdf, page, dpi, cache):
    target = cache / f'p{page}.png'
    if not target.exists():
        subprocess.run(['pdftoppm', '-r', str(dpi), '-png', '-f', str(page),
                        '-l', str(page), str(pdf), str(cache / f'p{page}')],
                       check=True)
        produced = sorted(cache.glob(f'p{page}-*.png'))
        if not produced:
            raise RuntimeError(f'第 {page} 页渲染失败')
        produced[0].rename(target)
    return Image.open(target)


def main():
    ap = argparse.ArgumentParser(description='从论文 PDF 中裁剪图片')
    ap.add_argument('--pdf', required=True)
    ap.add_argument('--out', required=True, help='输出图片目录')
    ap.add_argument('--pages', required=True, help='页码，逗号分隔，例如 3,6,7')
    ap.add_argument('--dpi', type=int, default=600)
    ap.add_argument('--work', required=True, help='中间目录')
    ap.add_argument('--pad', type=int, default=4, help='裁剪边距，单位 point')
    args = ap.parse_args()

    pdf = Path(args.pdf)
    out = Path(args.out)
    cache = Path(args.work) / 'pages'
    out.mkdir(parents=True, exist_ok=True)
    cache.mkdir(parents=True, exist_ok=True)

    wanted = [int(p) for p in args.pages.split(',') if p.strip()]
    if not wanted:
        raise ValueError('--pages 不能为空')
    pdf_w, pdf_h = page_size(pdf)
    pages = parse_pages(pdf, cache, min(wanted), max(wanted))
    for num in wanted:
        if num not in pages:
            raise ValueError(f'PDF 中没有第 {num} 页')
        info = pages[num]
        sx = pdf_w / info['w']
        sy = pdf_h / info['h']
        image = render_page(pdf, num, args.dpi, cache)
        k = args.dpi / 72.0
        for idx, it in enumerate(info['items'], start=1):
            t = it['top'] * sy - args.pad
            l = it['left'] * sx - args.pad
            b = (it['top'] + it['height']) * sy + args.pad
            r = (it['left'] + it['width']) * sx + args.pad
            box = (max(0, int(l * k)), max(0, int(t * k)),
                   int(r * k), int(b * k))
            name = f'fig_p{num}_{idx}.png'
            image.crop(box).save(out / name)
            print(f'{name} {Image.open(out / name).size} 来源第 {num} 页第 {idx} 张')


if __name__ == '__main__':
    main()
