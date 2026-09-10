# -*- coding: utf-8 -*-
"""Lap mot ban nhac co san vao lam nen cho doan phim.

    python _nap_nhac.py "duong/dan/toi/ban-nhac.mp3"
    python _nap_nhac.py "ban-nhac.mp3" --tu 12.5      bo qua 12,5 giay dau

Dung khi anh da co mot ban nhac CO QUYEN SU DUNG — mua giay phep, tai tu thu
vien mien phi ban quyen, hoac tu lam. Khong dung de lay nhac tu video cua
nguoi khac: cai do la tai san cua ho, va neu doan phim nay mang ten cong ty
thi rui ro thuoc ve cong ty.

Viec cua tep nay la lo phan may moc:
  - Cat hoac lap cho dai DUNG bang tong data-giay.
  - Vao dau 2,5 giay, tan cuoi 5 giay — de khong bat dot ngot va khong dut dot
    ngot. Neu phai lap vong thi noi bang mot doan chong mo 3 giay cho cho noi
    khong nghe ra.
  - Ha xuong ngang muc ban nhac tu tong hop dang co, de _tron_tieng.py khong
    phai chinh lai gi: chinh no do va bu dung bang do o buoc sau.

Ban tu tong hop khong bi mat: _tao_nhac.py luon ghi no ra nhac_tu_lam.wav.
Tep nay dat them mot dau moc nhac_ngoai.txt de _tao_nhac.py biet ma dung ghi
de len nhac.wav — khong co dau moc do thi ban nhac vua lap se bi xoa ngay o
lan chay dung_tat_ca.py ke tiep, khong bao mot tieng.

Muon quay ve ban tu tong hop: xoa _nen/nhac_ngoai.txt roi chay _tao_nhac.py.
"""
import io, os, re, subprocess, sys

GOC = os.path.dirname(os.path.abspath(__file__))
NEN = os.path.join(GOC, '_nen')
DICH = os.path.join(NEN, 'nhac.wav')
SR = 48000
VAO, RA_ = 2.5, 5.0            # giay vao dau va tan cuoi
CHONG = 3.0                    # giay chong mo khi phai lap vong

# Muc dich: -23 LUFS. Ban tu tong hop dang chay o quanh muc nay, va ca day
# tron o sau da duoc can theo do. Dua ban nhac moi ve cung mot muc thi khong
# phai dong vao gi khac.
MUC_NHAC = -23.0

if len(sys.argv) < 2:
    sys.exit(__doc__)
nguon = sys.argv[1]
if not os.path.exists(nguon):
    sys.exit('Khong thay tep: %s' % nguon)
tu = 0.0
if '--tu' in sys.argv:
    tu = float(sys.argv[sys.argv.index('--tu') + 1])

giay = [int(x) for x in re.findall(r'data-giay="(\d+)"',
        io.open(os.path.join(GOC, '_mau_video.html'), encoding='utf-8').read())]
DAI = float(sum(giay))


def do_dai(t):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                        '-of', 'csv=p=0', t], capture_output=True, text=True)
    return float(r.stdout.strip())


def chay(lenh):
    subprocess.run(lenh, check=True)


co = do_dai(nguon) - tu
print('Ban nhac dai %.1f giay (dung tu %.1f), doan phim can %.0f giay.' % (co, tu, DAI))

tam = os.path.join(NEN, '_nhac_moi.wav')

if co >= DAI:
    print('Du dai — cat lay %.0f giay dau.' % DAI)
    chay(['ffmpeg', '-y', '-v', 'error', '-ss', str(tu), '-t', str(DAI), '-i', nguon,
          '-ar', str(SR), '-ac', '2', tam])
else:
    # Lap vong. Moi vong duoc noi bang mot doan chong mo CHONG giay, nen moi
    # lan lap "an" mat CHONG giay — phai tinh so vong theo do, khong thi thieu.
    buoc = co - CHONG
    so_vong = int((DAI - co) / buoc) + 2
    print('Ngan hon — lap %d vong, noi bang doan chong mo %.0f giay.' % (so_vong, CHONG))
    khuc = os.path.join(NEN, '_khuc.wav')
    chay(['ffmpeg', '-y', '-v', 'error', '-ss', str(tu), '-i', nguon,
          '-ar', str(SR), '-ac', '2', khuc])
    hien = khuc
    for i in range(so_vong - 1):
        ke = os.path.join(NEN, '_noi%d.wav' % i)
        chay(['ffmpeg', '-y', '-v', 'error', '-i', hien, '-i', khuc,
              '-filter_complex',
              '[0:a][1:a]acrossfade=d=%g:c1=tri:c2=tri[ra]' % CHONG,
              '-map', '[ra]', '-ar', str(SR), '-ac', '2', ke])
        if hien != khuc:
            os.remove(hien)
        hien = ke
    chay(['ffmpeg', '-y', '-v', 'error', '-t', str(DAI), '-i', hien,
          '-ar', str(SR), '-ac', '2', tam])
    os.remove(hien); os.remove(khuc)

# Do muc that roi bu dung bang do — cung cach lam nhu _tron_tieng.py.
r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', tam,
                    '-af', 'loudnorm=I=%g:TP=-3:print_format=json' % MUC_NHAC,
                    '-f', 'null', '-'], capture_output=True, text=True)
import json
do = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
bu = MUC_NHAC - float(do['input_i'])
print('Nhac do duoc %.1f LUFS -> bu %+.1f dB cho bang muc nen dang dung.'
      % (float(do['input_i']), bu))

chay(['ffmpeg', '-y', '-v', 'error', '-i', tam, '-af',
      'volume=%.2fdB,afade=t=in:d=%g,afade=t=out:st=%g:d=%g'
      % (bu, VAO, DAI - RA_, RA_),
      '-ar', str(SR), '-ac', '2', DICH])
os.remove(tam)

# Dat dau moc de _tao_nhac.py biet ma KHONG ghi de len ban nhac vua lap.
io.open(os.path.join(NEN, 'nhac_ngoai.txt'), 'w', encoding='utf-8').write(
    '%s\n%s\n' % (os.path.basename(nguon), os.path.abspath(nguon)))

print('Xong: %s (%.0f giay)' % (DICH, do_dai(DICH)))
print('Muon quay ve ban tu tong hop: xoa _nen/nhac_ngoai.txt roi chay _tao_nhac.py')
print('Gio chay:  python _tron_tieng.py  roi  python _dung_mp4.py')
print('Hoac mot lenh:  npm run video:tieng')
