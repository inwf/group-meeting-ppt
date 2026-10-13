import argparse
import re
from pathlib import Path

SPEED_LOW = 260
SPEED_HIGH = 270


def body_text(text):
    text = re.sub(r'^#.*$', '', text, flags=re.M)
    text = re.sub(r'^---$', '', text, flags=re.M)
    text = re.sub(r'^(论文|时长|说明)：.*$', '', text, flags=re.M)
    return text


def main():
    ap = argparse.ArgumentParser(description='统计演讲稿汉字数与预计时长')
    ap.add_argument('path')
    ap.add_argument('--target', type=float, default=8.0, help='目标时长，单位分钟')
    args = ap.parse_args()

    text = Path(args.path).read_text(encoding='utf-8')
    count = len(re.findall(r'[\u4e00-\u9fff]', body_text(text)))
    low = count / SPEED_HIGH
    high = count / SPEED_LOW
    print(f'汉字数 {count}')
    print(f'预计时长 {low:.2f} 到 {high:.2f} 分钟')
    target_low = int(args.target * SPEED_LOW)
    target_high = int(args.target * SPEED_HIGH)
    if count < target_low:
        print(f'低于 {args.target} 分钟下限，建议补充到 {target_low} 到 {target_high} 字')
    elif count > target_high:
        print(f'超过 {args.target} 分钟上限，建议压缩到 {target_low} 到 {target_high} 字')
    else:
        print(f'在 {args.target} 分钟目标区间内')


if __name__ == '__main__':
    main()
