# -*- coding: utf-8 -*-
"""Nhung anh chup + phong mono vao mot file HTML tu chay duoc.
Times New Roman co san tren may nguoi xem nen khong can nhung."""
import base64, io, os, re

GOC = os.path.dirname(os.path.abspath(__file__))
# Moi thu cua video nam trong thu muc nay. Chi mot thu phai voi ra ngoai: bo
# phong JetBrains Mono, vi no thuoc ve ung dung web chu khong thuoc ve video.
DUAN = os.path.dirname(GOC)

def b64(p):
    with open(p, 'rb') as f:
        return base64.b64encode(f.read()).decode('ascii')

# Chi nhung JetBrains Mono — dung cho ma ca va dong ho, doc nhu so lieu may
fonts = ("@font-face{font-family:'JBM';font-style:normal;font-weight:500;font-display:swap;"
         "src:url(data:font/woff2;base64,%s) format('woff2')}"
         % b64(os.path.join(DUAN, 'public', 'fonts', 'jetbrains-mono-500-latin.woff2')))

with io.open(os.path.join(GOC, '_mau_video.html'), encoding='utf-8') as f:
    html = f.read()

html = html.replace('{{FONTS}}', fonts)
# Ten cho trong duoc doc thang tu HTML: bo canh la khong con phai sua tay o day.
# {{ANH_BANGPHEPNAM}} <-> _anh_video/bang-phep-nam.png (bo dau gach ngang de doi chieu).
tep = {f[:-4].replace('-', ''): f for f in os.listdir(os.path.join(GOC, '_anh_video'))}
for kh in sorted(set(re.findall(r'\{\{ANH_([A-Z]+)\}\}', html))):
    duong = os.path.join(GOC, '_anh_video', tep[kh.lower()])
    html = html.replace('{{ANH_%s}}' % kh, 'data:image/png;base64,' + b64(duong))

ra = os.path.join(GOC, 'gioi-thieu-ung-dung.html')
with io.open(ra, 'w', encoding='utf-8', newline='\n') as f:
    f.write(html)

con = set(re.findall(r'\{\{[A-Z_]+\}\}', html))
print('Da dung: %.1f MB' % (os.path.getsize(ra) / 1024 / 1024))
print('Cho trong chua thay: %s' % (con if con else 'khong con'))

# Kiem tra tong thoi luong dung 120 giay
giay = [int(x) for x in re.findall(r'data-giay="(\d+)"', html)]
print('So canh: %d | Tong: %d giay (%d:%02d)' % (len(giay), sum(giay), sum(giay)//60, sum(giay)%60))
