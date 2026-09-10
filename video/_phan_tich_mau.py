# -*- coding: utf-8 -*-
"""Do dac mot doan phim mau de doi chieu voi ban cua ta.

    python _phan_tich_mau.py "duong/dan/toi/mau.mp4"

MUC DICH LA DO DAC PHONG CACH, KHONG PHAI SAO CHEP. Cai ta lay ra o day la
cac con so mo ta: nhip bao nhieu, giong noi tram bao nhieu, can bang tan so
nghieng ve dau, nhac bi ghim xuong bao nhieu khi co nguoi noi. Tu do dung lai
mot ban nhac CUA MINH cho khop cac con so ay. Giai dieu cua nguoi khac thi
van la cua nguoi khac.
"""
import os, subprocess, sys, wave
import numpy as np

GOC = os.path.dirname(os.path.abspath(__file__))
mau = sys.argv[1] if len(sys.argv) > 1 else None
if not mau or not os.path.exists(mau):
    sys.exit('Dua duong dan toi tep mau')

tam = os.path.join(GOC, '_nen', '_ref.wav')
if not os.path.exists(tam):
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', mau,
                    '-ar', '48000', '-ac', '2', tam], check=True)

with wave.open(tam, 'rb') as f:
    SR = f.getframerate()
    x = np.frombuffer(f.readframes(f.getnframes()), '<i2').astype(np.float64) / 32768
    x = x.reshape(-1, f.getnchannels())
mono = x.mean(1)
DAI = len(mono) / SR
print('Dai %.1f giay, %d Hz' % (DAI, SR))

# ── Rong stereo ──────────────────────────────────────────────────────────
# So sanh nang luong phan LECH giua hai ben voi phan CHUNG. Gan 0 la gan nhu
# mono; cang lon thi anh nhac cang mo rong sang hai ben.
giua = (x[:, 0] + x[:, 1]) / 2
ben = (x[:, 0] - x[:, 1]) / 2
print('Rong stereo: %.1f dB (lech so voi giua)'
      % (20 * np.log10(max(ben.std(), 1e-9) / max(giua.std(), 1e-9))))

# ── Can bang tan so ──────────────────────────────────────────────────────
# Chia pho thanh sau dai roi tinh ti le nang luong. Day la "van tay" de doi
# chieu: ban cua ta co qua nhieu tram khong, co thieu phan sang khong.
n = 1 << 15
cua = np.hanning(n)
pho = np.zeros(n // 2 + 1)
so = 0
for i in range(0, len(mono) - n, n // 2):
    pho += np.abs(np.fft.rfft(mono[i:i+n] * cua)) ** 2
    so += 1
pho /= max(so, 1)
hz = np.fft.rfftfreq(n, 1 / SR)
DAI_TAN = [(20, 80, 'that tram   20-80'), (80, 250, 'tram       80-250'),
           (250, 800, 'trung thap 250-800'), (800, 2500, 'trung   800-2,5k'),
           (2500, 6000, 'ro chu   2,5k-6k'), (6000, 16000, 'sang      6k-16k')]
tong = pho.sum()
print('\nCan bang tan so:')
for a, b, ten in DAI_TAN:
    m = (hz >= a) & (hz < b)
    print('  %-18s %5.1f %%' % (ten, 100 * pho[m].sum() / tong))

# ── Nhip ─────────────────────────────────────────────────────────────────
# Lay duong bao nang luong roi tu tuong quan: neu ban nhac co nhip deu, duong
# bao se giong chinh no khi truot di dung mot phach.
buoc = 512
bao = np.array([np.abs(mono[i:i+buoc]).mean() for i in range(0, len(mono) - buoc, buoc)])
bao = np.diff(bao).clip(0, None)               # chi giu cho nang luong TANG
bao -= bao.mean()
tt = np.correlate(bao, bao, 'full')[len(bao) - 1:]
fps_bao = SR / buoc
diem = []
for bpm in np.arange(70, 160, 0.5):
    tre = int(round(60.0 / bpm * fps_bao))
    if 0 < tre < len(tt):
        diem.append((tt[tre] + 0.6 * tt[min(2 * tre, len(tt) - 1)], bpm))
diem.sort(reverse=True)
print('\nNhip co the: ' + ', '.join('%.0f BPM' % b for _, b in diem[:3]))

# ── Cao do giong noi ─────────────────────────────────────────────────────
# Uoc luong tan so co ban o cac doan CO NANG LUONG TRUNG — do la cho nguoi
# dang noi. Dung tu tuong quan tren tin hieu da loc con 70-400 Hz.
tho = np.fft.rfft(mono)
loc = np.zeros_like(tho)
h = np.fft.rfftfreq(len(mono), 1 / SR)
loc[(h > 70) & (h < 400)] = tho[(h > 70) & (h < 400)]
giong = np.fft.irfft(loc, len(mono))
f0 = []
n2 = 2048
for i in range(0, len(giong) - n2, n2):
    khuc = giong[i:i+n2]
    if np.abs(khuc).mean() < 0.004: continue
    c = np.correlate(khuc, khuc, 'full')[n2-1:]
    lo, hi = int(SR / 400), int(SR / 70)
    if hi >= len(c): continue
    k = lo + int(np.argmax(c[lo:hi]))
    if c[k] > 0.35 * c[0]:
        f0.append(SR / k)
if f0:
    f0 = np.array(f0)
    print('\nCao do giong noi: trung vi %.0f Hz (khoang %.0f-%.0f Hz), %d khuc'
          % (np.median(f0), np.percentile(f0, 10), np.percentile(f0, 90), len(f0)))

# ── Ti le co tieng noi ───────────────────────────────────────────────────
muc = np.array([20*np.log10(max(np.abs(mono[i:i+4800]).mean(), 1e-9))
                for i in range(0, len(mono) - 4800, 4800)])
nguong = np.percentile(muc, 55)
print('Co am thanh dang ke tren %.0f %% thoi luong' % (100 * (muc > nguong).mean()))
print('Muc cao nhat %.1f dB, thap nhat %.1f dB, chenh %.1f dB'
      % (muc.max(), muc.min(), muc.max() - muc.min()))
