import argparse
import shutil
import subprocess
import zipfile
from pathlib import Path


def check_package(path):
    problems = []
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        media = [n for n in names if n.startswith('ppt/media/')]
        for n in sorted(names):
            if not n.endswith('.rels'):
                continue
            rels = z.read(n).decode('utf-8')
            for line in rels.split('<Relationship ')[1:]:
                if 'TargetMode="External"' in line:
                    problems.append(f'外部链接关系：{n}')
                if 'r:link' in line:
                    problems.append(f'外部链接引用：{n}')
        for n in sorted(names):
            if not n.startswith('ppt/slides/slide') or not n.endswith('.xml'):
                continue
            xml = z.read(n).decode('utf-8')
            if 'r:link=' in xml:
                problems.append(f'图片使用外部链接：{n}')
    return media, problems


def main():
    ap = argparse.ArgumentParser(description='导出 PDF 并检查外部链接')
    ap.add_argument('--pptx', required=True)
    ap.add_argument('--outdir', required=True)
    args = ap.parse_args()

    pptx = Path(args.pptx).resolve()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    media, problems = check_package(pptx)
    print(f'内嵌媒体文件 {len(media)} 个')
    if problems:
        for p in problems:
            print('问题：', p)
    else:
        print('未发现外部图片链接')

    soffice = shutil.which('libreoffice') or shutil.which('soffice')
    if not soffice:
        raise SystemExit('找不到 libreoffice 或 soffice 命令，请先安装 LibreOffice')
    subprocess.run([soffice, '--headless', '--convert-to', 'pdf',
                    '--outdir', str(outdir), str(pptx)], check=True)
    pdf = outdir / (pptx.stem + '.pdf')
    info = subprocess.run(['pdfinfo', str(pdf)], capture_output=True,
                          text=True, check=True).stdout
    pages = [ln for ln in info.splitlines() if ln.startswith('Pages')]
    print('导出 PDF', pdf, pages[0] if pages else '')
    if problems:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
