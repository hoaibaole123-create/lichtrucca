# Video giới thiệu ứng dụng

Toàn bộ phần dựng video nằm trong thư mục này. **Mọi lệnh phải chạy từ đây**
(`_chup_khung.mjs` lấy thư mục hiện hành làm gốc), trừ hai lệnh `npm` bên dưới.

## Dựng bằng một lệnh

```bash
npm run video
```

Dựng đầy đủ, khoảng 30 phút. Chỉ sửa lời đọc, nhạc hoặc mốc tiếng điểm thì
dùng đường tắt — giữ nguyên hình, xong trong khoảng một phút:

```bash
npm run video:tieng
```

## Đường đi

```
_mau_video.html                    bản gốc: chữ, hoạt cảnh, data-giay
  ├── _dung_video.py       nhúng ảnh + phông  → gioi-thieu-ung-dung.html
  ├── _chup_khung.mjs      chụp từng khung    → _khung/*.jpg
  ├── _tao_tieng.py        đọc lời thuyết minh → _tieng/canh*.mp3
  ├── _tao_nhac.py         nhạc + tiếng điểm  → _nen/*.wav
  ├── _tron_tieng.py       trộn, ghìm nhạc, chuẩn độ ồn → _nen/tron.wav
  └── _dung_mp4.py         ghép hình với tiếng → gioi-thieu-ung-dung.mp4
```

## Sửa gì thì chạy lại gì

| Sửa | Cần chạy lại |
|---|---|
| Lời thuyết minh, nhạc, mốc tiếng điểm | `npm run video:tieng` |
| Chữ trên màn hình (`_mau_video.html`) | `node _chup_mot_canh.mjs <số cảnh>` rồi `python _dung_mp4.py` — nếu chỉ một cảnh đổi và `data-giay` giữ nguyên |
| `data-giay` của bất kỳ cảnh nào | `npm run video` — đổi `data-giay` là đổi số khung của mọi cảnh phía sau, `_chup_mot_canh.mjs` sẽ ghi sai chỗ |
| Ảnh chụp trong `_anh_video/` | `npm run video` |

`_tron_tieng.py` tự dừng và báo `TRAN!` nếu có câu thuyết minh dài hơn khung
cảnh chứa nó.

## Hệ thống âm thanh

Bốn đường tiếng, trộn ở cuối trong `_tron_tieng.py`:

| Đường | Nội dung |
|---|---|
| **Lời** | 17 tệp đọc, đặt đúng chỗ trên trục thời gian, qua dây xử lý giọng: cắt trầm 85 Hz, −2,5 dB ở 260 Hz, +3 dB ở 2,9 kHz, hạ tiếng gió, nén động 3:1 |
| **Nhạc** | một bản dài bằng cả đoạn phim, **bị chính lời ghìm xuống 11,8 dB** mỗi khi có người nói rồi tự dâng lên trong 420 ms |
| **Tiếng điểm** | 62 mốc, mỗi mốc bám theo một độ trễ có thật trong `_mau_video.html` |
| **Chuẩn** | hai lượt đo: lượt một đo thật, lượt hai bù đúng bằng đó → −14,1 LUFS, đỉnh −1,4 dBTP |

Nhạc do `_tao_nhac.py` **tự tổng hợp bằng numpy**, không lấy từ đâu nên không
vướng bản quyền. 116 BPM, bốn đoạn theo tỉ lệ độ dài phim: mở đầu chỉ pad →
triển khai vào nhịp → đẩy lên thêm lớp synth cao → kết bỏ nhịp và tan dần.
Muốn thay bằng bản nhạc có giấy phép thì thay `_nen/nhac.wav`, không phải
sửa gì thêm — nhưng nhớ nó phải dài đúng bằng tổng `data-giay`.

Tiếng điểm, tất cả đều tự tổng hợp:

| Tệp | Dùng khi |
|---|---|
| `quet.wav` | chuyển cảnh — tiếng trầm cộng hơi gió quét từ trái sang phải |
| `chu.wav` | tiêu đề hiện ra (trễ 0,12 s sau đầu cảnh) |
| `the.wav` | thẻ giao diện bay vào (cảnh 2, 8, 16, 17) |
| `nhan.wav` | **chỉ ba lần** — một con số, một kết quả, một thông điệp |
| `cham.wav` | con trỏ bấm nút |
| `bao.wav` | có thông báo mới |
| `xuat.wav` | văn bản Word vừa dựng xong |

Mọi mốc tiếng điểm nằm trong `_tron_tieng.py`, mỗi mốc có ghi rõ nó bám vào
độ trễ CSS nào. **Sửa độ trễ bên `_mau_video.html` thì phải sửa cả ở đây**,
không thì tiếng rời ra khỏi hình.

## Các tệp

| Tệp | Việc |
|---|---|
| `_mau_video.html` | **bản gốc để sửa** — 17 cảnh, chữ, hoạt cảnh, `data-giay` |
| `_loi_thuyet_minh.py` | 17 câu thuyết minh + giọng đọc |
| `_tao_tieng.py` | đọc lời thành `_tieng/canh*.mp3` (edge-tts) |
| `_tao_nhac.py` | dựng nhạc và tiếng điểm trong `_nen/` |
| `_tron_tieng.py` | trộn toàn bộ âm thanh → `_nen/tron.wav` |
| `_dung_video.py` | nhúng ảnh base64 → `gioi-thieu-ung-dung.html` |
| `_chup_khung.mjs` | chụp toàn bộ khung ra `_khung/` |
| `_chup_mot_canh.mjs` | chụp lại đúng một cảnh (~2 phút thay vì 25) |
| `_dung_mp4.py` | ghép thành `gioi-thieu-ung-dung.mp4` |
| `dung_tat_ca.py` | chạy cả dây chuyền, đằng sau `npm run video` |
| `_phan_tich_mau.py` | đo một đoạn phim mẫu để đối chiếu — nhịp, cao độ giọng, cân bằng tần số, độ ồn |
| `_tao_du_lieu_demo.mjs` | sinh dữ liệu giả để chụp màn hình, tránh lộ dữ liệu thật |

`_khung/` là ảnh trung gian, dựng lại được — không cần lưu vào git.

## Đối chiếu với đoạn phim mẫu

```bash
python _phan_tich_mau.py "duong/dan/toi/mau.mp4"
```

Đo phong cách, **không sao chép**: nhịp, cao độ giọng nói, cân bằng tần số,
độ ồn. Từ đó chỉnh các tham số của mình cho khớp — giai điệu vẫn là của mình.

Máy dò nhịp trong đó có sai số **±2 BPM** trên nhịp gõ sạch (kiểm định ở 90,
100, 116, 128, 140 BPM). Nó **không** đáng tin trên nhạc dày không có phách rõ:
đưa bản nhạc 116 BPM chỉ gõ ở phách 1 và 3 vào, nó đọc ra 154 BPM. Nếu con số
trả về trông lạ, hãy nghi máy dò trước khi nghi bản nhạc.

## Phụ thuộc

`ffmpeg`, `ffprobe`, `node`, `python` với `numpy` và `edge-tts`.
`dung_tat_ca.py` kiểm tra ba cái đầu ngay từ đầu và báo cách cài nếu thiếu.

Một phụ thuộc ra ngoài thư mục: `_dung_video.py` lấy phông JetBrains Mono từ
`../public/fonts/`, vì phông đó thuộc về ứng dụng web chứ không thuộc về video.
