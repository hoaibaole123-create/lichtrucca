# Ghi nguồn nhạc nền — BẮT BUỘC

Nhạc nền hiện dùng trong `gioi-thieu-ung-dung.mp4`:

> **Future** — MaxKoMusic
> Giấy phép: **Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)**

## Đoạn ghi nguồn phải kèm theo video

Dán nguyên văn vào phần mô tả video, hoặc đưa vào cuối phim:

```
Music: "Future" by MaxKoMusic — https://maxkomusic.com/
Music promoted by https://www.chosic.com/free-music/all/
Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)
https://creativecommons.org/licenses/by-sa/3.0/
```

Bỏ đoạn này là vi phạm giấy phép, kể cả khi không có ai khiếu nại.

## Điều khoản ShareAlike — cần hỏi ý kiến trước khi phát hành rộng

CC BY-SA 3.0 có hai nghĩa vụ, không phải một:

1. **Ghi nguồn** — đoạn trên.
2. **ShareAlike** — tác phẩm phái sinh phải phát hành dưới cùng giấy phép.

Nghĩa vụ thứ hai là chỗ cần cân nhắc. Ghép nhạc khớp với hình thường được coi
là tạo ra tác phẩm phái sinh, và nếu vậy thì toàn bộ video phải mang giấy phép
CC BY-SA — tức bất kỳ ai cũng được tái sử dụng, sửa đổi và phát hành lại video
của Công ty Thủy điện Ialy.

Có ý kiến cho rằng video có nhạc nền chỉ là "tuyển tập" chứ không phải "tác
phẩm phái sinh", và khi đó ShareAlike không lan sang. Điểm này chưa ngã ngũ.
Với một video mang tên đơn vị nhà nước, không nên dựa vào cách hiểu có lợi mà
chưa hỏi ai.

## Nếu muốn tránh hoàn toàn

Ba đường, đều dựng lại trong khoảng một phút:

**Dùng nhạc CC0** — không phải ghi nguồn, không có ShareAlike.
Lọc trên Chosic: <https://www.chosic.com/free-music/all/?sort=&attribution=no>
Hoặc Pixabay Music: <https://pixabay.com/music/>

```bash
python _nap_nhac.py "duong/dan/toi/ban-nhac-CC0.mp3"
npm run video:tieng
```

**Mua giấy phép thương mại** cho chính bản "Future" từ tác giả, nếu đã ưng bản
này. Giấy phép mua thường thay thế hẳn điều khoản CC BY-SA.

**Quay về bản nhạc tự tổng hợp** — không vướng bản quyền của ai, vì nó do
`_tao_nhac.py` sinh ra bằng numpy:

```bash
rm _nen/nhac_ngoai.txt
python _tao_nhac.py
npm run video:tieng
```
