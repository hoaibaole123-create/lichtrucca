# -*- coding: utf-8 -*-
"""Doc loi thuyet minh thanh mp3 bang giong neural tieng Viet cua Microsoft
(edge-tts). May nay khong co giong tieng Viet cai san — SAPI chi co David va
Zira tieng Anh — nen phai dung duong nay.

CAO DO -11 Hz: doan phim mau nguoi dung dua co tan so co ban trung vi 129 Hz,
con giong nay o cao do goc doc ra 136-138 Hz. Tham so pitch cua edge-tts KHONG
tuyen tinh — do that ba muc: -8Hz cho 132 Hz, -16Hz cho 123 Hz, -24Hz cho 113
Hz. Noi suy hai muc dau ra -11Hz cho dung 129 Hz.

pitch KHONG lam doi do dai, nen phep kiem tra TRAN trong _tron_tieng.py van
dung nguyen."""
import asyncio, os, sys
import edge_tts
from _loi_thuyet_minh import LOI, GIONG

CAO_DO = '-11Hz'

RA = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_tieng')
os.makedirs(RA, exist_ok=True)

async def doc(i, loi):
    # Thu lai bon lan. edge-tts goi ra may chu cua Microsoft, va dich vu do
    # thinh thoang tra ve rong (NoAudioReceived) voi dung tham so ma lan truoc
    # vua chay duoc. Khong thu lai thi mot lan rot mang giet ca luot dung
    # 30 phut o buoc thu ba.
    t = os.path.join(RA, 'canh%02d.mp3' % (i + 1))
    for lan in range(4):
        try:
            await edge_tts.Communicate(loi, GIONG, rate='+6%', pitch=CAO_DO).save(t)
            return t
        except Exception as e:
            if lan == 3:
                raise
            print('   canh %d hong (%s), thu lai sau %d giay'
                  % (i + 1, type(e).__name__, 2 * (lan + 1)))
            await asyncio.sleep(2 * (lan + 1))

async def main():
    for i, loi in enumerate(LOI):
        t = await doc(i, loi)
        print('%2d  %6.1f KB  %s' % (i + 1, os.path.getsize(t) / 1024, os.path.basename(t)))

asyncio.run(main())
