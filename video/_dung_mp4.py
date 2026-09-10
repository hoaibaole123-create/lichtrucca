# -*- coding: utf-8 -*-
"""Ghep khung hinh voi ban tieng da tron thanh mot tep mp4 phat duoc o moi noi.

Tep nay giay khong con lam am thanh nua — toan bo viec do da chuyen sang
_tron_tieng.py, o day chi con nhan mot tep wav duy nhat. Ly do tach: hinh mat
25 phut de chup, tieng mat vai giay; de chung mot cho thi moi lan chinh tieng
lai phai cham vao duong dung hinh.

Neu chua co _nen/tron.wav thi tu goi _tron_tieng.py truoc, khong bat nguoi
dung phai nho thu tu.
"""
import os, re, io, subprocess, sys

GOC = os.path.dirname(os.path.abspath(__file__))
FFMPEG = 'ffmpeg'
FPS = 25

giay = [int(x) for x in re.findall(r'data-giay="(\d+)"',
        io.open(os.path.join(GOC, '_mau_video.html'), encoding='utf-8').read())]

tieng = os.path.join(GOC, '_nen', 'tron.wav')
if not os.path.exists(tieng):
    print('Chua co ban tieng — chay _tron_tieng.py truoc.')
    subprocess.run([sys.executable, os.path.join(GOC, '_tron_tieng.py')], check=True)

ra = os.path.join(GOC, 'gioi-thieu-ung-dung.mp4')
khung = os.path.join(GOC, '_khung', '%05d.jpg')

# Khi chi sua am thanh — doi loi doc, doi nhac, doi tieng diem — thi hinh khong
# he thay doi. Luc do lay thang luong hinh cua ban mp4 dang co va chep nguyen
# ('-c:v copy'), khong ma hoa lai: xong trong vai giay thay vi phai chup lai
# 3400 khung roi ma hoa lai tu dau.
chi_tieng = not os.path.exists(os.path.dirname(khung)) and os.path.exists(ra)
tam = None
if chi_tieng:
    tam = ra + '.tam.mp4'
    os.replace(ra, tam)
    dau_vao = ['-i', tam]
    hinh = ['-c:v', 'copy']
    hinh_map = ['-map', '0:v']
    loc = []
    print('Chi thay am thanh, giu nguyen luong hinh dang co.')
else:
    dau_vao = ['-framerate', str(FPS), '-i', khung]
    hinh = ['-c:v', 'libx264', '-preset', 'slow', '-crf', '20']
    hinh_map = ['-map', '[v]']
    # Khung chup o 3840x2160 (xem _chup_khung.mjs) nen phai ha ve 1920 truoc khi
    # ma hoa. Lanczos lay trung binh co trong so tren mot cua so rong, cho ra chu
    # net hon han bilinear — day chinh la cho thu duoc lai cua viec sieu lay mau.
    loc = ['-filter_complex', '[0:v]scale=1920:1080:flags=lanczos,format=yuv420p[v]']

lenh = ([FFMPEG, '-y'] + dau_vao + ['-i', tieng] + loc
        + hinh_map + ['-map', '1:a'] + hinh
        + ['-movflags', '+faststart',
           # 192 kb/s stereo 48 kHz. Ban truoc ra 92 kb/s mono 24 kHz vi no
           # thua sam sat theo tep doc cua edge-tts; ca nhac lan tieng diem
           # deu bi ep xuong nua bang thong ma khong ai bao gi.
           '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2',
           '-shortest', ra])
subprocess.run(lenh, check=True)
if tam:
    os.remove(tam)
print('Xong: %s — %.1f MB' % (ra, os.path.getsize(ra) / 1024 / 1024))
