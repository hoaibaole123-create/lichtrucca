# -*- coding: utf-8 -*-
"""Dung toan bo nen am thanh cho video: mot ban nhac co cau truc va cac tieng
diem danh dau viec dang xay ra tren man hinh.

Nhac o day duoc TU TONG HOP bang numpy chu khong lay tu dau, nen khong vuong
ban quyen. Truoc day no chi la bon hop am ngan chong len nhau, lap di lap lai —
giu cho khung hinh khoi "cam" nhung khong di dau ca. Ban nay co bon doan theo
dung mach cua doan phim:

    MO DAU     0-10%    pad khong, khong nhip. Chua co gi xay ra.
    TRIEN KHAI 10-60%   vao nhip, bass theo phach, arpeggio chay nhe.
    DAY LEN    60-85%   them mot lop synth cao, bass day hon, nhip kin hon.
    KET        85-100%  bo nhip, con lai pad, tan dan.

DO DAI TU DAN RA TU _mau_video.html. Ban truoc dong cung 120 giay trong khi
doan phim da dai 136 giay, nghia la 16 giay cuoi khong he co nhac ma khong ai
biet. Doc data-giay la het lo do vinh vien.

Chay: python _tao_nhac.py
"""
import io, os, re, wave, subprocess
import numpy as np

GOC = os.path.dirname(os.path.abspath(__file__))
RA = os.path.join(GOC, '_nen')
os.makedirs(RA, exist_ok=True)

SR = 48000
# 116 BPM la DO TU DOAN PHIM MAU nguoi dung dua, khong phai chon bua: lay
# duong bao nang luong cua tep mau roi tu tuong quan, dinh cao nhat roi vao
# 116 BPM (hai dinh ke tiep 115 va 114, tuc do do chac). Truoc day la 100.
# Xem _phan_tich_mau.py.
BPM = 116.0
PHACH = 60.0 / BPM              # 0,517 giay
O_NHIP = PHACH * 4              # mot o nhip 2,069 giay

giay = [int(x) for x in re.findall(r'data-giay="(\d+)"',
        io.open(os.path.join(GOC, '_mau_video.html'), encoding='utf-8').read())]
DAI = float(sum(giay))
N = int(DAI * SR)
t = np.arange(N, dtype=np.float64) / SR


def ghi(ten, x):
    """Ghi mang float [-1,1] ra wav 16 bit. x co dang (N,) hoac (N,2)."""
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    d = np.max(np.abs(x))
    if d > 0.999:                              # chi ha khi that su cham tran
        x = x * (0.999 / d)
    p = os.path.join(RA, ten)
    with wave.open(p, 'wb') as f:
        f.setnchannels(x.shape[1]); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes((np.clip(x, -1, 1) * 32767).astype('<i2').tobytes())
    return p


def duong(moc):
    """Duong bao tuyen tinh tu danh sach (ti_le, muc) -> mang dai N.
    Moc ghi theo TI LE do dai video chu khong theo giay, nen doi data-giay la
    bon doan tu co gian theo, khong phai chinh tay."""
    g = np.array([m[0] for m in moc]) * DAI
    v = np.array([m[1] for m in moc])
    return np.interp(t, g, v)


# -- Hoa thanh -----------------------------------------------------------
# Giu nguyen bon hop am cua ban cu (Do - Sol - La thu - Fa): do la giong cua
# doan phim nay roi, doi hoa thanh la doi tinh cach chu khong phai nang cap.
# Moi hop am dai 4 o nhip = 9,6 giay.
HOP_AM = [
    dict(bass=65.41, not_=[130.81, 164.81, 196.00, 261.63]),   # Do truong
    dict(bass=49.00, not_=[ 98.00, 123.47, 146.83, 196.00]),   # Sol truong
    dict(bass=55.00, not_=[110.00, 130.81, 164.81, 220.00]),   # La thu
    dict(bass=43.65, not_=[ 87.31, 110.00, 130.81, 174.61]),   # Fa truong
]
DAI_HOP_AM = O_NHIP * 4

def hop_am_tai(g):
    return HOP_AM[int(g / DAI_HOP_AM) % len(HOP_AM)]


# -- Lop 1 - PAD ---------------------------------------------------------
# Nen tram lien tuc, co mat tu dau den cuoi. Moi not duoc nhan doi va lech
# tan so 0,25 Hz giua hai ben: hai song gan bang nhau troi ra vao nhau rat
# cham, cho tieng "day" va song sanh thay vi mong nhu mot song sin don.
pad_t = np.zeros(N); pad_p = np.zeros(N)
for i in range(int(np.ceil(DAI / DAI_HOP_AM))):
    a = int(i * DAI_HOP_AM * SR); b = min(int((i + 1) * DAI_HOP_AM * SR), N)
    if a >= N: break
    ha = HOP_AM[i % len(HOP_AM)]
    m = np.arange(b - a) / SR
    # Vao ra cham 1,8 giay o hai dau moi hop am de cac hop am tan vao nhau
    bao = np.clip(np.minimum(m / 1.8, (len(m) / SR - m) / 1.8), 0, 1)
    for j, f in enumerate(ha['not_']):
        bien = 0.42 if j == 0 else 0.24
        pad_t[a:b] += np.sin(2 * np.pi * (f - 0.25) * m + j * 1.7) * bien * bao
        pad_p[a:b] += np.sin(2 * np.pi * (f + 0.25) * m + j * 1.7) * bien * bao
pad = np.stack([pad_t, pad_p], 1) * 0.14

# -- Lop 2 - SUB BASS ----------------------------------------------------
# Not goc, danh o phach 1 va 3 cua moi o nhip. Giu o giua (mono) - tieng tram
# ma trai len se lam mix nghe long ra tren loa nho.
bass = np.zeros(N)
so_o = int(np.ceil(DAI / O_NHIP))
for o in range(so_o):
    for phach in (0, 2):
        g = o * O_NHIP + phach * PHACH
        if g >= DAI: continue
        a = int(g * SR); d = int(min(PHACH * 1.7, DAI - g) * SR)
        m = np.arange(d) / SR
        # Tat theo ham mu - mot not bass thuc te tat nhanh, khong keo bang nhau
        bass[a:a + d] += np.sin(2 * np.pi * hop_am_tai(g)['bass'] * m) \
                         * np.exp(-m * 2.6) * 0.55

# -- Lop 3 - ARPEGGIO ----------------------------------------------------
# Not don chay theo mot phan tam, moi not tat nhanh nhu tieng gay. Day la lop
# tao cam giac "cong nghe": deu, sang, nhung khong on. Trai phai luan phien.
arp_t = np.zeros(N); arp_p = np.zeros(N)
buoc = PHACH / 2
MAU = [0, 2, 1, 3, 2, 1, 3, 0]                 # thu tu not trong hop am
k = 0; g = 0.0
while g < DAI:
    f = hop_am_tai(g)['not_'][MAU[k % len(MAU)]] * 2    # len mot quang tam cho sang
    a = int(g * SR); d = int(min(buoc * 2.4, DAI - g) * SR)
    if d > 0:
        m = np.arange(d) / SR
        s = (np.sin(2 * np.pi * f * m) + 0.3 * np.sin(4 * np.pi * f * m)) \
            * np.exp(-m * 7.0) * 0.3
        # Trai phai so le, nhung khong het bien: 0,68 / 0,32 chu khong 1 / 0,
        # de tren loa mono khong co not nao bien mat.
        tr, ph = (0.68, 0.32) if k % 2 == 0 else (0.32, 0.68)
        arp_t[a:a + d] += s * tr; arp_p[a:a + d] += s * ph
    g += buoc; k += 1
arp = np.stack([arp_t, arp_p], 1)

# -- Lop 4 - GO NHE ------------------------------------------------------
# Khong phai trong. Mot tieng tram quet xuong tan so cong mot tieng "sit" rat
# khe o cac phan tam le. Deu bo phan cao.
# PHACH NAO CUNG PHAI CO MOT DAU CHAM. Ban truoc chi go o phach 1 va 3, va
# do do luoi 116 BPM khong bao gio hien ra thanh nhip nghe duoc: cho may do
# nhip vao ban nhac do, no doc ra 154 BPM chu khong phai 116 — no bam vao
# arpeggio va tieng sit chu khong tim thay phach nao. Gio phach 1 va 3 go
# manh, phach 2 va 4 go nhe hon mot nua. Van khong phai trong, nhung da co
# mot nhip de bam vao.
go = np.zeros(N)
rng = np.random.default_rng(7)
for o in range(so_o):
    for phach, manh in ((0, 0.50), (1, 0.22), (2, 0.42), (3, 0.22)):
        g = o * O_NHIP + phach * PHACH
        if g >= DAI: continue
        a = int(g * SR); d = int(min(0.22, DAI - g) * SR)
        m = np.arange(d) / SR
        f = 78 * np.exp(-m * 22) + 44          # quet tu 122 Hz xuong 44 Hz
        go[a:a + d] += np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-m * 15) * manh
    for phach in (0.5, 1.5, 2.5, 3.5):
        g = o * O_NHIP + phach * PHACH
        if g >= DAI: continue
        a = int(g * SR); d = int(min(0.05, DAI - g) * SR)
        m = np.arange(d) / SR
        go[a:a + d] += rng.normal(0, 1, d) * np.exp(-m * 90) * 0.035

# -- Lop 5 - LOP SANG (chi o doan day len) -------------------------------
# Mot bat tam tren cac not cua chinh hop am dang chay, vao rat cham. No khong
# them not moi nao - chi lam hoa thanh dang co mo ra phia tren, du de nghe ra
# "cao trao" ma khong doi bai.
sang_t = np.zeros(N); sang_p = np.zeros(N)
for i in range(int(np.ceil(DAI / DAI_HOP_AM))):
    a = int(i * DAI_HOP_AM * SR); b = min(int((i + 1) * DAI_HOP_AM * SR), N)
    if a >= N: break
    ha = HOP_AM[i % len(HOP_AM)]
    m = np.arange(b - a) / SR
    bao = np.clip(np.minimum(m / 2.2, (len(m) / SR - m) / 2.2), 0, 1)
    for j, f in enumerate(ha['not_'][1:]):
        sang_t[a:b] += np.sin(2 * np.pi * (f * 4 - 0.4) * m + j) * 0.1 * bao
        sang_p[a:b] += np.sin(2 * np.pi * (f * 4 + 0.4) * m + j) * 0.1 * bao
sang = np.stack([sang_t, sang_p], 1)

# -- Duong bao cua tung lop theo bon doan --------------------------------
e_pad  = duong([(0, .55), (.10, .85), (.60, .95), (.85, 1.0), (.94, .85), (1, .45)])
e_bass = duong([(0, 0), (.09, 0), (.13, .55), (.58, .65), (.62, .90), (.85, .90),
                (.90, .35), (1, 0)])
e_arp  = duong([(0, 0), (.09, 0), (.14, .50), (.58, .60), (.62, .85), (.86, .80),
                (.93, .25), (1, 0)])
e_go   = duong([(0, 0), (.10, 0), (.15, .45), (.58, .50), (.62, .85), (.85, .85),
                (.89, .20), (.93, 0), (1, 0)])
e_sang = duong([(0, 0), (.58, 0), (.64, .70), (.85, .80), (.92, .30), (1, 0)])

nhac = (pad * e_pad[:, None] + arp * e_arp[:, None] + sang * e_sang[:, None]
        + (bass * e_bass + go * e_go)[:, None])

# Vao dau va tan cuoi. Cuoi dai 5 giay: yeu cau la "khong ket thuc dot ngot".
nhac *= (np.clip(t / 2.5, 0, 1) * np.clip((DAI - t) / 5.0, 0, 1))[:, None]
tam = ghi('_nhac_tho.wav', nhac)

# Loc lan cuoi bang ffmpeg: cat phan rat tram cho khoi um, ha phan cao cho
# tieng mem, them tieng vang cho co khong gian, roi ha han xuong lam nen.
# Ban tu tong hop LUON ghi ra nhac_tu_lam.wav — do la san pham cua tep nay.
# Chi khi KHONG co nhac ngoai thi no moi duoc dat vao vi tri nhac.wav ma
# _tron_tieng.py doc.
TU_LAM = os.path.join(RA, 'nhac_tu_lam.wav')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', tam, '-af',
                'highpass=f=32,lowpass=f=7200,'
                'aecho=0.85:0.9:380|610:0.20|0.13,'
                'acompressor=threshold=0.12:ratio=2.5:attack=25:release=320,'
                'volume=0.62',
                '-ar', str(SR), '-ac', '2', TU_LAM], check=True)
os.remove(tam)

# DAU MOC nhac_ngoai.txt do _nap_nhac.py dat xuong khi nguoi dung lap mot ban
# nhac co giay phep vao. Khong co no thi tep nay tung ghi thang de len
# nhac.wav — va vi dung_tat_ca.py --tieng co goi tep nay, ban nhac vua lap
# bi xoa ngay o lan dung ke tiep, khong bao mot tieng. Do la loi that, da xay
# ra mot lan.
MOC = os.path.join(RA, 'nhac_ngoai.txt')
if os.path.exists(MOC):
    print('Co nhac ngoai (%s) — giu nguyen nhac.wav, ban tu lam de o nhac_tu_lam.wav.'
          % io.open(MOC, encoding='utf-8').read().strip().splitlines()[0])
else:
    import shutil
    shutil.copyfile(TU_LAM, os.path.join(RA, 'nhac.wav'))


# -- Tieng diem ----------------------------------------------------------
# Deu ngan va deu khe. Chung la dau cham cau cho hinh anh, khong phai hieu
# ung: neu nguoi xem nghe thay ro rang tung tieng thi da la to.

def truc(d):
    return np.arange(int(d * SR)) / SR

def loc(ten, x, af):
    tam = ghi('_t_' + ten, x)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', tam, '-af', af,
                    '-ar', str(SR), '-ac', '2', os.path.join(RA, ten)], check=True)
    os.remove(tam)

# quet.wav - chuyen canh. Mot tieng TRAM tron dan len roi tat, cong mot hoi
# gio nhe quet ngang khung hinh. Hoi gio di tu trai sang phai de cu cat canh
# co huong, dung nhu may dang luot qua chu khong phai mot tieng dung yen.
m = truc(1.2)
tram = (np.sin(2*np.pi*98*m) * 0.6 + np.sin(2*np.pi*147*m) * 0.28)
tram *= np.clip(m/0.28, 0, 1) * np.exp(-np.clip(m-0.28, 0, None) * 3.4)
rng = np.random.default_rng(11)
gio = np.convolve(rng.normal(0, 1, len(m)), np.ones(60)/60, 'same')
gio *= np.sin(np.pi * np.clip(m/0.85, 0, 1))**2 * 0.16
quet = np.stack([tram + gio * np.clip(1 - m/0.85, 0, 1),
                 tram + gio * np.clip(m/0.85, 0, 1)], 1)
loc('quet.wav', quet, 'lowpass=f=1800,highpass=f=55,volume=0.34')

# chu.wav - mot dong chu vua hien. Rat khe, rat ngan, khong co than am: chi
# la mot cai "cham" bao rang co gi do vua xuat hien.
m = truc(0.07)
loc('chu.wav', (np.sin(2*np.pi*2100*m)*0.5 + np.sin(2*np.pi*3150*m)*0.25)
    * np.exp(-m*60), 'highpass=f=900,lowpass=f=5200,volume=0.085')

# the.wav - mot the giao dien vua bay vao. Not di xuong nhanh, nghe nhu vat
# vua dat xuong cho.
m = truc(0.16)
f = 900 * np.exp(-m * 9) + 380
loc('the.wav', np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-m*22) * 0.5,
    'lowpass=f=3000,volume=0.10')

# nhan.wav - mot con so hoac mot y quan trong vua hien. Mot cu tram ngan o
# duoi cong mot anh sang rat mong o tren. Day la tieng "co trong luong" duy
# nhat trong ca doan phim, va no chi duoc dung ba lan.
m = truc(1.0)
f = 120 * np.exp(-m * 14) + 52
sau = np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-m*4.5) * 0.75
lap = (np.sin(2*np.pi*1568*m) + np.sin(2*np.pi*2093*m)*0.6) * np.exp(-m*5.5) \
      * np.clip(m/0.05, 0, 1) * 0.09
# 0,20 chu khong phai 0,30: o muc 0,30 do duoc tieng nay chay trung binh
# -11 dB trong khi giong noi -15 dB, tuc no TO HON nguoi dang noi. Mot tieng
# nhan manh khong duoc phep to hon thu ma no nhan manh.
loc('nhan.wav', np.stack([sau + lap*0.8, sau + lap*1.2], 1),
    'lowpass=f=6000,volume=0.20')

# cham.wav - con tro bam nut. Go ngan, da cat het phan cao cho khoi "tach"
# nhu chuot may tinh re tien.
m = truc(0.12)
loc('cham.wav', np.sin(2*np.pi*1150*m)*0.5*np.exp(-m*30)
    + np.sin(2*np.pi*330*m)*0.7*np.exp(-m*22), 'lowpass=f=2600,volume=0.24')

# bao.wav - co thong bao moi. Hai not di len quang nam: mot tin bao, khong
# phai mot canh bao.
m = truc(0.9); tre = int(0.14 * SR)
b2 = np.zeros(len(m)); mm = m[:len(m)-tre]
b2[tre:] = np.sin(2*np.pi*880.0*mm) * 0.5 * np.exp(-mm*3.0)
loc('bao.wav', np.sin(2*np.pi*587.33*m)*0.6*np.exp(-m*3.2) + b2,
    'lowpass=f=3200,volume=0.19')

# xuat.wav - van ban vua dung xong. Tieng dong lai, di XUONG chu khong len,
# de nghe ra "da hoan tat".
m = truc(0.75); tre = int(0.09 * SR)
x2 = np.zeros(len(m)); mm = m[:len(m)-tre]
x2[tre:] = np.sin(2*np.pi*130.81*mm) * 0.7 * np.exp(-mm*3.4)
loc('xuat.wav', np.sin(2*np.pi*196*m)*0.45*np.exp(-m*5.5) + x2,
    'lowpass=f=1400,volume=0.26')

for f in sorted(os.listdir(RA)):
    if f.endswith('.wav'):
        print('%-12s %9.1f KB' % (f, os.path.getsize(os.path.join(RA, f)) / 1024))
print('Nhac dai %.0f giay, %g BPM — khop voi tong data-giay.' % (DAI, BPM))
