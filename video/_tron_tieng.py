# -*- coding: utf-8 -*-
"""Tron toan bo am thanh cua doan phim thanh MOT tep wav duy nhat.

Tach rieng khoi _dung_mp4.py co chu y: hinh anh mat 25 phut de chup con am
thanh mat vai giay. De chung mot cho thi moi lan chinh tieng lai phai cham
vao duong dung hinh, va som muon se co lan chay nham lam mat ca _khung.

BON DUONG TIENG, tron o cuoi:

  LOI   17 tep doc, moi tep dat dung cho tren truc thoi gian (khong noi duoi
        nhau), roi qua mot day xu ly giong: cat tram, ha tieng gio, nang vung
        phu am, nen dong. Loi luon la lop tren cung.
  NHAC  mot ban duy nhat dai bang ca doan phim, bi CHINH LOI GHIM XUONG moi
        khi co nguoi noi (sidechaincompress) roi tu dang len khi het cau.
  DIEM  cac tieng ngan bam theo dung moc hoat canh trong _mau_video.html.
  CHUAN hai luot do do on: luot mot do that, luot hai bu dung bang do — chac
        chan hon loudnorm mot luot vi loudnorm mot luot phai doan truoc va
        hay bop chet doan to.

Chay: python _tron_tieng.py   (khoang 20 giay)
"""
import io, os, re, json, subprocess, sys

GOC = os.path.dirname(os.path.abspath(__file__))
NEN = os.path.join(GOC, '_nen')
RA = os.path.join(NEN, 'tron.wav')
SR = 48000
LUI = 0.9                      # giay cho hoat canh vao khung truoc khi cat loi
MUC = -14.0                    # LUFS tich hop, muc thong dung cho video tren mang
DINH = -1.0                    # dBTP
# Chan tren tep wav phai thap hon dich MOT KHOANG, vi con mot buoc ma hoa AAC
# nua o _dung_mp4.py va AAC lam vot dinh len. Do that: chan o -1,6 dBFS thi
# ban mp4 ra -0,9 dBTP, tuc vot 0,7 dB. Muc vot thay doi theo noi dung, nen
# de bien 1,2 dB cho chac.
BIEN_AAC = 1.2

giay = [int(x) for x in re.findall(r'data-giay="(\d+)"',
        io.open(os.path.join(GOC, '_mau_video.html'), encoding='utf-8').read())]
DAI = sum(giay)

def dau_canh(n):               # giay tu dau phim toi dau canh thu n (dem tu 1)
    return sum(giay[:n - 1])

def do_dai(tep):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                        '-of', 'csv=p=0', tep], capture_output=True, text=True)
    return float(r.stdout.strip())


# ── Kiem tra loi co lot khung canh khong ─────────────────────────────────
tieng = [os.path.join(GOC, '_tieng', 'canh%02d.mp3' % (i + 1)) for i in range(len(giay))]
tran = [(LUI + do_dai(t), d) for t, d in zip(tieng, giay)]
for i, (het, d) in enumerate(tran):
    print('canh %2d: loi ket thuc %.1fs / canh %ds %s'
          % (i + 1, het, d, 'TRAN!' if het > d - .2 else ''))
if any(h > d - .2 for h, d in tran):
    sys.exit('Co canh bi tran tieng — rut ngan loi trong _loi_thuyet_minh.py')


# ── Cac moc tieng diem ───────────────────────────────────────────────────
# MOI MOC O DAY DEU BAM THEO MOT DO TRE CO THAT TRONG _mau_video.html. Neu
# sua do tre ben do thi phai sua o day, khong thi tieng se roi ra khoi hinh.
# Sai lech cho phep khoang 100-150 ms; ngoai nguong do tai nghe ra ngay la
# hai viec roi nhau chu khong con la mot viec.

CAT_KHOP = {9}                 # canh 10 tiep tuc cung hinh anh — khong duoc danh chuyen

# .canh[data-hien] h1,h2  ->  delay .12s
TRE_TIEU_DE = 0.12
# .canh[data-hien] .diem::after  ->  delay calc(.58s + i*.15s)
TRE_NHAN = 0.58

# The/khoi giao dien bay vao. (canh, so the, tre dau, cach nhau)
THE = [
    ( 2, 5, 0.62, 0.110),      # .mo-dun span   — nam ten mo-dun o canh mo dau
    ( 8, 7, 0.24, 0.075),      # .nut-mach      — bay buoc cua quy trinh
    (16, 8, 0.18, 0.075),      # .kham figure   — bang ghep anh nhin lai
    (17, 5, 0.45, 0.200),      # .ket .quy span — nam the hoi tu ve giua
]

# Tieng "co trong luong". CHI BA LAN trong ca doan phim: mot con so, mot ket
# qua, mot thong diep. Dung lan thu tu la no thoi con nghia gi.
NHAN = [(9, TRE_TIEU_DE), (16, TRE_NHAN), (17, TRE_TIEU_DE)]

# Cac moc da co tu truoc, giu nguyen:
#   con tro bam   = tre + 2,6s * 63%  (moc "bam xuong" trong keyframe troChay)
#   the thong bao = .3s + thu tu * .16s
DIEM_CU = [
    ( 4, 1.00 + 2.6 * .63, 'cham'),   # bam nut tao tai khoan phan xuong
    (10, 0.70 + 2.6 * .63, 'cham'),   # bam nut "Xem truoc Word"
    (11, 1.30,             'xuat'),   # van ban Word vua dung xong
    (14, 1.25,             'bao'),    # thong bao Zalo
    (14, 1.95,             'bao'),    # thong bao Gmail
]

su_kien = []                   # (giay tu dau phim, ten tep khong duoi)

for i in range(1, len(giay)):                      # chuyen canh
    if i not in CAT_KHOP:
        su_kien.append((float(dau_canh(i + 1)), 'quet'))

for n in range(1, len(giay) + 1):                  # tieu de hien ra
    if n not in [c for c, _ in NHAN]:              # cho nao da co tieng nang thi thoi
        su_kien.append((dau_canh(n) + TRE_TIEU_DE, 'chu'))

for canh, so, tre, cach in THE:
    for k in range(so):
        su_kien.append((dau_canh(canh) + tre + k * cach, 'the'))

for canh, tre in NHAN:
    su_kien.append((dau_canh(canh) + tre, 'nhan'))

for canh, tre, ten in DIEM_CU:
    su_kien.append((dau_canh(canh) + tre, ten))


# ── Dung day loc ─────────────────────────────────────────────────────────
vao, loc, nhan_loi = [], [], []

# 1. LOI — dat tung tep dung cho roi noi lai, nhu ban cu
for i, (t, d) in enumerate(zip(tieng, giay)):
    vao += ['-i', t]
    loc.append('[%d:a]aresample=%d,adelay=%d|%d,apad,atrim=0:%d,asetpts=N/SR/TB[l%d]'
               % (i, SR, int(LUI * 1000), int(LUI * 1000), d, i))
    nhan_loi.append('[l%d]' % i)
loc.append(''.join(nhan_loi) + 'concat=n=%d:v=0:a=1[loi_tho]' % len(giay))

# 2. DAY XU LY GIONG. Tep doc cua edge-tts la mono 24 kHz, sach nhung det:
# khong co gi duoi 100 Hz de cat, nhung vung 200-350 Hz thi day va vung phu
# am thi thieu, nen nghe "gan" ma khong "ro". Thu tu duoi day co chu y:
#   highpass  bo phan tram khong mang tin tuc, don cho cho bass cua nhac
#   equalizer -2,5 dB o 260 Hz   — go bot phan um o long nguc
#   equalizer +3 dB o 2,9 kHz    — vung quyet dinh viec nghe RO tung chu
#   deesser   ha tieng gio chu s/x, vua bi nang len o buoc tren
#   acompressor nen dong 3:1 — cau nho khong bi chim, cau to khong voi len
loc.append('[loi_tho]'
           'highpass=f=85,'
           'equalizer=f=260:t=q:w=1.1:g=-2.5,'
           'equalizer=f=2900:t=q:w=1.3:g=3,'
           'deesser=i=0.4:m=0.5:f=0.25,'
           'acompressor=threshold=0.055:ratio=3:attack=8:release=190:makeup=2.2,'
           'volume=1.15,'
           'aformat=channel_layouts=stereo'
           '[loi_xl]')
# Tach lam hai: mot ban de nghe, mot ban chi de lam CHIA KHOA ghim nhac xuong
loc.append('[loi_xl]asplit=2[loi][khoa]')

# 3. NHAC bi ghim xuong khi co nguoi noi.
# sidechaincompress khong nghe nhac — no nghe [khoa] roi van nho nhac lai.
# release 420 ms de nhac dang len TU TU sau moi cau, khong giat len ngay giua
# hai chu; threshold thap vi giong noi sau khi nen da kha deu.
# RATIO 4 LA DO DUOC CHU KHONG PHAI CHON BUA: do muc nhac o giay 2,5 (dang co
# tieng noi) truoc va sau khi ghim, ratio 4 cho ra dung 11,8 dB — nam trong
# khoang 8-12 dB. Ratio 9 cho 14 dB, nhac tut qua sau thanh ra moi cau noi lai
# hut mot mang nen, nghe ra ngay cho no dang len lai.
i_nhac = len(giay)
vao += ['-i', os.path.join(NEN, 'nhac.wav')]
loc.append('[%d:a]aresample=%d,aformat=channel_layouts=stereo[nhac]' % (i_nhac, SR))
loc.append('[nhac][khoa]sidechaincompress='
           'threshold=0.03:ratio=4:attack=12:release=420:makeup=1:detection=rms[nhac_ghim]')

# 4. TIENG DIEM. Moi tep chi mo MOT lan roi nhan ban bang asplit — re hon
# nhieu so voi mo cung mot tep hai muoi lan.
chi_so = i_nhac
nhan_diem = []
for ten in sorted(set(x for _, x in su_kien)):
    moc = sorted(m for m, x in su_kien if x == ten)
    chi_so += 1
    vao += ['-i', os.path.join(NEN, ten + '.wav')]
    loc.append('[%d:a]aresample=%d,aformat=channel_layouts=stereo,asplit=%d%s'
               % (chi_so, SR, len(moc), ''.join('[%s%d]' % (ten, k) for k in range(len(moc)))))
    for k, m in enumerate(moc):
        loc.append('[%s%d]adelay=%d|%d[%sd%d]'
                   % (ten, k, int(m * 1000), int(m * 1000), ten, k))
        nhan_diem.append('[%sd%d]' % (ten, k))
loc.append(''.join(nhan_diem) + 'amix=inputs=%d:normalize=0[diem]' % len(nhan_diem))

# 5. TRON. normalize=0 vi ta da tu dinh muc tung duong; de amix tu chia deu
# thi no ha het ba duong xuong mot phan ba va pha bo can chinh o tren.
loc.append('[loi][nhac_ghim][diem]amix=inputs=3:normalize=0:dropout_transition=0,'
           'atrim=0:%d,asetpts=N/SR/TB[ra]' % DAI)


def dung(dich, them):
    lenh = (['ffmpeg', '-y', '-v', 'error'] + vao
            + ['-filter_complex', ';'.join(loc), '-map', '[ra]']
            + them + ['-ar', str(SR), '-ac', '2', dich])
    subprocess.run(lenh, check=True)


# ── Luot 1: dung ban tho roi do that su no to bao nhieu ──────────────────
tho = os.path.join(NEN, '_tron_tho.wav')
dung(tho, [])

r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', tho,
                    '-af', 'loudnorm=I=%g:TP=%g:print_format=json' % (MUC, DINH),
                    '-f', 'null', '-'], capture_output=True, text=True)
do = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
dang = float(do['input_i']); dinh_dang = float(do['input_tp'])
bu = MUC - dang
print('\nDo duoc: %.1f LUFS, dinh %.1f dBTP -> bu %+.1f dB' % (dang, dinh_dang, bu))

# ── Luot 2: bu dung bang do vua tinh, roi chan dinh ──────────────────────
# Bu bang MOT he so co dinh chu khong dung loudnorm mot luot: loudnorm mot
# luot phai doan truoc do to sap toi nen no keo len keo xuong lien tuc, nghe
# ra ngay o cac doan chi co nhac. alimiter chi cham vao vai dinh cao nhat.
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', tho, '-af',
                'volume=%.2fdB,alimiter=limit=%.4f:attack=5:release=60:level=disabled'
                % (bu, 10 ** ((DINH - BIEN_AAC) / 20.0)),
                '-ar', str(SR), '-ac', '2', RA], check=True)
os.remove(tho)

# ── Do lai ban cuoi ──────────────────────────────────────────────────────
r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', RA,
                    '-af', 'loudnorm=I=%g:TP=%g:print_format=json' % (MUC, DINH),
                    '-f', 'null', '-'], capture_output=True, text=True)
do = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
print('Ban cuoi: %.1f LUFS, dinh %.1f dBTP, LRA %.1f'
      % (float(do['input_i']), float(do['input_tp']), float(do['input_lra'])))
print('%d tieng diem tren %d giay.' % (len(su_kien), DAI))
print('Xong: %s' % RA)
