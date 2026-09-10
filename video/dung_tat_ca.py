# -*- coding: utf-8 -*-
"""Dung ca doan phim bang MOT lenh.

    python video/dung_tat_ca.py            dung day du (khoang 30 phut)
    python video/dung_tat_ca.py --tieng     chi lam lai am thanh (khoang 1 phut)

Duong di:

    _mau_video.html                    ban goc: chu, hoat canh, data-giay
      |
      +-- _dung_video.py       nhung anh + phong  -> gioi-thieu-ung-dung.html
      +-- _chup_khung.mjs      chup tung khung    -> _khung/*.jpg
      +-- _tao_tieng.py        doc loi thuyet minh-> _tieng/canh*.mp3
      +-- _tao_nhac.py         dung nhac va tieng diem -> _nen/*.wav
      +-- _tron_tieng.py       tron + ghim nhac + chuan do on -> _nen/tron.wav
      +-- _dung_mp4.py         ghep hinh voi tieng -> gioi-thieu-ung-dung.mp4

Co --tieng thi bo hai buoc hinh anh va bao _dung_mp4.py chep nguyen luong hinh
cua ban mp4 dang co. Dung khi chi doi loi doc, doi nhac hoac doi moc tieng
diem — nhung buoc do khong dung toi mot khung hinh nao.
"""
import os, shutil, subprocess, sys, time

GOC = os.path.dirname(os.path.abspath(__file__))
CHI_TIENG = '--tieng' in sys.argv

BUOC_HINH = [
    ('Nhung anh va phong vao HTML', [sys.executable, '_dung_video.py']),
    ('Chup khung hinh (lau nhat)',  ['node', '_chup_khung.mjs']),
]
BUOC_TIENG = [
    ('Doc loi thuyet minh',        [sys.executable, '_tao_tieng.py']),
    ('Dung nhac va tieng diem',    [sys.executable, '_tao_nhac.py']),
    ('Tron va chuan do on',        [sys.executable, '_tron_tieng.py']),
]
BUOC_GHEP = [
    ('Ghep thanh mp4',             [sys.executable, '_dung_mp4.py']),
]

# Khong co ffmpeg thi moi buoc am thanh deu hong, va hong theo kieu kho doc.
# Bao ngay tu dau, kem cach cai, con hon de nguoi dung doc mot vet loi ffmpeg.
for cong_cu, cach in (('ffmpeg', 'winget install Gyan.FFmpeg'),
                      ('ffprobe', 'winget install Gyan.FFmpeg'),
                      ('node', 'https://nodejs.org')):
    if shutil.which(cong_cu) is None:
        sys.exit('Thieu %s. Cai bang:  %s' % (cong_cu, cach))

buoc = (BUOC_TIENG if CHI_TIENG else BUOC_HINH + BUOC_TIENG) + BUOC_GHEP

# Khi chi lam tieng, phai giau _khung di: _dung_mp4.py nhin vao su ton tai cua
# thu muc do de quyet dinh ma hoa lai hay chep nguyen luong hinh.
khung = os.path.join(GOC, '_khung')
an = os.path.join(GOC, '_khung_giu')
if CHI_TIENG and os.path.isdir(khung):
    os.rename(khung, an)

bat_dau = time.time()
try:
    for i, (ten, lenh) in enumerate(buoc, 1):
        print('\n[%d/%d] %s' % (i, len(buoc), ten))
        r = subprocess.run(lenh, cwd=GOC)
        if r.returncode:
            sys.exit('Dung o buoc: %s' % ten)
finally:
    if CHI_TIENG and os.path.isdir(an):
        os.rename(an, khung)

phut = (time.time() - bat_dau) / 60
print('\nXong sau %.1f phut: %s' % (phut, os.path.join(GOC, 'gioi-thieu-ung-dung.mp4')))
