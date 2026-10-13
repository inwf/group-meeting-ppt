import argparse
import json
import re
import subprocess
from pathlib import Path


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout


def main():
    ap = argparse.ArgumentParser(description='读取论文 PDF 的标题、作者与页数')
    ap.add_argument('--pdf', required=True)
    ap.add_argument('--pages', type=int, default=2, help='提取正文前若干页')
    args = ap.parse_args()

    pdf = Path(args.pdf)
    if not pdf.exists():
        raise FileNotFoundError(f'找不到文件 {pdf}')

    info = run(['pdfinfo', str(pdf)])
    meta = dict(re.findall(r'^(\w[\w\s]*?):\s+(.*)$', info, re.M))
    title = meta.get('Title', '').strip()
    authors = meta.get('Author', '').strip()
    npages = int(meta.get('Pages', '0').strip() or 0)

    text = run(['pdftotext', '-layout', '-f', '1', '-l', str(args.pages),
                str(pdf), '-'])
    head = text.strip().splitlines()
    first_lines = [ln.strip() for ln in head if ln.strip()][:12]

    arxiv = re.search(r'arXiv:\s*(\d{4}\.\d{4,5})(v\d+)?', text)
    abstract = ''
    m = re.search(r'Abstract\s*(.*?)(?:\n\s*\n|1\.\s+Introduction)', text, re.S)
    if m:
        abstract = re.sub(r'\s+', ' ', m.group(1)).strip()

    print(json.dumps(dict(
        title=title,
        authors=authors,
        pages=npages,
        arxiv=arxiv.group(0) if arxiv else '',
        first_lines=first_lines,
        abstract=abstract[:1200],
    ), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
