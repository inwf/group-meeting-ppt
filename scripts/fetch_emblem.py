import argparse
import io
import re
import urllib.request
from pathlib import Path

from PIL import Image

LIST_URL = 'https://www.urongda.com/logos'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def parse_schools(text):
    entries, seen = [], set()
    for chunk in text.split('<a href="/logos/')[1:]:
        m_img = re.search(r'src="(https://cdn\.urongda\.com/images/schools/[^"]+)"',
                          chunk)
        m_name = re.search(r'<h3[^>]*>([^<]+)</h3>', chunk)
        if not m_img or not m_name:
            continue
        name = m_name.group(1).strip()
        if name not in seen:
            seen.add(name)
            entries.append((name, m_img.group(1)))
    return entries


def match_school(entries, name):
    for school, url in entries:
        if school == name:
            return school, url, []
    loose = [(s, u) for s, u in entries if name in s]
    if len(loose) == 1:
        return loose[0][0], loose[0][1], []
    return None, None, loose


def main():
    ap = argparse.ArgumentParser(description='从 urongda.com 下载学校校徽')
    ap.add_argument('--school', required=True, help='学校名称，例如 清华大学')
    ap.add_argument('--out', required=True, help='输出图片路径（PNG）')
    args = ap.parse_args()

    name = args.school.strip()
    try:
        html = fetch(LIST_URL).decode('utf-8', errors='ignore')
    except Exception as e:
        raise SystemExit(
            f'无法访问 urongda.com（{e}），'
            '请到 https://www.urongda.com/ 手动下载校徽后提供文件路径')

    entries = parse_schools(html)
    if not entries:
        raise SystemExit(
            '未能从 urongda.com 解析出学校列表，'
            '请到 https://www.urongda.com/ 手动下载校徽后提供文件路径')

    school, url, candidates = match_school(entries, name)
    if school is None:
        if candidates:
            names = '、'.join(s for s, _ in candidates[:10])
            raise SystemExit(
                f'「{name}」匹配到多所学校：{names}。'
                '请用完整校名重试，或到 https://www.urongda.com/ 手动下载')
        raise SystemExit(
            f'未找到「{name}」，'
            '请到 https://www.urongda.com/ 手动下载校徽后提供文件路径')

    try:
        data = fetch(url)
    except Exception as e:
        raise SystemExit(
            f'校徽图片下载失败（{e}），请到 https://www.urongda.com/ 手动下载')

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        with Image.open(io.BytesIO(data)) as im:
            im.convert('RGBA').save(out, format='PNG')
    except Exception as e:
        raise SystemExit(
            f'校徽图片处理失败（{e}），请到 https://www.urongda.com/ 手动下载')
    print(f'已下载 {school} 校徽 -> {out}（来源：{url}）')


if __name__ == '__main__':
    main()
