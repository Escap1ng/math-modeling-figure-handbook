"""提交前图表机器自检：编号 / 引用 / 断引用 / 低分辨率 / 页脚。

用法:
    pip install pymupdf
    python qa_figs.py submission.pdf

输出五项检查:
    缺号/跳号   图题编号是否从 1 连续
    未被引用   只出现在图题、正文从未按号引用的图
    引用无题   正文引用了但不存在图题的编号
    ?? 断引用   LaTeX 交叉引用失败残留
    低dpi      版心 >100pt 但有效分辨率 <200dpi 的位图
    页脚       "Page x of y" 的 y 集合（应与实际正文页数一致）
"""
import re
import sys
from collections import Counter

import fitz

path = sys.argv[1] if len(sys.argv) > 1 else "submission.pdf"
doc = fitz.open(path)

caps, occ = {}, Counter()
for i, p in enumerate(doc):
    for line in p.get_text().splitlines():
        nums = [int(x) for x in re.findall(r"(?:Figure|Fig\.)\s*(\d+)", line)]
        occ.update(nums)
        m = re.match(r"\s*(?:Figure|Fig\.)\s*(\d+)\b", line)
        if m:  # 行首视为图题（每图一条）
            caps.setdefault(int(m.group(1)), i + 1)

nums = set(caps)
print("缺号/跳号:", sorted(set(range(1, max(nums) + 1)) - nums) if nums else [])
print("未被引用:", sorted(n for n in nums if occ[n] <= 1))
print("引用无题:", sorted(set(occ) - nums))
print("?? 断引用:", sum(p.get_text().count("??") for p in doc))
for i, p in enumerate(doc):
    for img in p.get_images(full=True):
        w = doc.extract_image(img[0])["width"]
        for r in p.get_image_rects(img[0]):
            dpi = w / r.width * 72
            if dpi < 200 and r.width > 100:
                print(f"低dpi: p{i + 1} {dpi:.0f}dpi {r.width:.0f}pt")
print("页脚:", sorted({m for p in doc for m in re.findall(r"Page \d+ of (\d+)", p.get_text())}))