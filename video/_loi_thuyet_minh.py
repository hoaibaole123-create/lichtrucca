# -*- coding: utf-8 -*-
"""Loi thuyet minh tieng Viet cho video gioi thieu giai phap.
Moi dong ung voi mot phan canh trong _mau_video.html, dung thu tu.

Do dai cau da can theo data-giay cua canh do. Giong vi-VN-NamMinhNeural DOC O
rate +6% (truoc la -4%): loi viet lai dai hon han ban cu, giu -4% thi tong
video len 148 giay; +6% ha xuong 136 giay ma giong van chua nghe voi. O rate
nay giong doc khoang 3,7 am tiet/giay ke ca cho ngat — DO THAT, khong phai uoc
luong; dau phay va dau cham deu them mot khoang lang nen cang nhieu dau cang
cham. Tru ~1,1 giay dau va cuoi de tieng khong dinh vao chuyen canh.

data-giay cua 17 canh hien la [7,8,7,8,8,8,8,8,8,7,8,8,8,9,8,9,9] = 136 giay,
dat bang cach lam tron len tu do dai that cua tung tep tieng. Neu sua loi thi
phai do lai va chinh lai data-giay trong _mau_video.html, roi CHUP LAI TOAN BO
khung — doi data-giay la doi so khung cua moi canh.

_dung_mp4.py se dung han va bao TRAN neu co cau nao vuot, nen cu viet roi do.

BA NGUYEN TAC VIET:

1. KHONG DOC LAI CHU TREN MAN HINH. Day la nguyen tac quan trong nhat va cung
   de vi pham nhat, vi chu tren man hinh va loi noi cung noi ve mot chuc nang.
   Chu tren man hinh noi CAI GI; loi noi cho biet vi sao cai do dang gia.
   Man hinh: "Tru phep tu dong" -> Loi: "khong ai phai cong tay".
   Man hinh: "Tha file Word vao, tu doc" -> Loi: "khoi go lai".
   Neu doc lai chu tren man hinh thi nguoi xem nghe mot lan, doc mot lan, va
   khong nhan them duoc gi ca.

2. MOT MACH LIEN, KHONG PHAI 17 DOAN ROI. Moi cau moc vao cau truoc bang mot
   tu noi hoac mot dai tu chi lui — "quy trinh do", "tu do", "con ai", "du vao
   loi nao", "den ky xep lich", "xep xong", "tu chinh du lieu do", "theo cach
   ay", "song song", "va moi khi", "nho vay". Doc lien 17 dong phai ra mot bai
   noi, khong ra mot muc luc. Neu doi thu tu phan canh thi phai soat lai cac
   tu noi nay, khong thi mach se dut.

3. GIU GIONG DIEM DAM. Khong "dot pha", khong "toi uu toan dien".
   VE CON SO: chu tren man hinh o canh 5 va canh 9 co ghi "30 giay" va "giam
   90% thoi gian". Loi noi CO Y khong nhac lai hai con so nay — noi them mot
   lan la tang gap doi muc do khang dinh cho mot so lieu ma ta khong dan duoc
   nguon. Canh 9 chi noi "trong it phut", vua do de hau thuan chu tren man
   hinh ma khong tu minh dua ra mot con so moi.

MACH 14 Y TRAI TREN 17 CANH:
   1 van de | 2 giai phap | 3-4 quan ly phan xuong | 5 nop don | 6 tinh phep
   7 tiep nhan Word | 8 tap trung | 9-10 lap lich | 11 xuat van ban | 12 doi ca
   13 phep nam | 14 Zalo | 15 cau hinh | 16-17 ket
"""

LOI = [
 # 1 · VAN DE — ta thuc te, khong che. Man hinh noi "hang gio"; loi noi
 # cho biet hang gio DE LAM GI, va lam moi thang mot lan.
 u"Trước đây, công tác xếp lịch trực thay mỗi tháng tốn hàng giờ đồng hồ với vô số thao tác thủ công.",
 # 2 · GIAI PHAP — "quy trinh do" moc thang vao cau tren
 u"Giờ đây, giải pháp phần mềm mới giúp chuẩn hóa toàn bộ quy trình lên môi trường số, vận hành ngay trên trình duyệt.",
 # 3 · PHAN QUYEN — man hinh noi "bao mat"; loi noi ta cai nguoi dung THAY
 u"Tại đây, hệ thống phân quyền độc lập cho từng phân xưởng, đảm bảo tính bảo mật và đúng chức năng.",
 # 4 · KHAI BAO
 u"Thậm chí, mỗi đơn vị chỉ cần thiết lập ban đầu một lần duy nhất là có thể đưa vào vận hành trơn tru.",
 # 5 · NHAN VIEN NOP DON — khong nhac lai "30 giay" tren man hinh
 u"Nhờ đó, nhân viên có thể chủ động gửi đơn online mọi lúc mọi nơi, loại bỏ hoàn toàn quy trình giấy tờ.",
 # 6 · TU DONG TINH NGAY PHEP
 u"Ngay khi đơn gửi lên, hệ thống sẽ tự động tính và trừ ngày phép chính xác theo ca trực, loại bỏ các sai sót.",
 # 7 · TIEP NHAN WORD — man hinh noi "tu doc", loi noi them "khoi go lai"
 u"Song song đó, nếu đơn đã soạn sẵn bằng Word, phần mềm vẫn hỗ trợ trích xuất dữ liệu tự động mà không cần nhập lại.",
 # 8 · QUAN LY TAP TRUNG — hau thuan cho mach bay nut
 u"Dù tiếp nhận qua kênh nào, toàn bộ dữ liệu vẫn dồn về một nguồn tập trung, giúp tra cứu tức thì.",
 # 9 · LAP LICH — "it phut" du hau thuan, khong dua ra con so moi
 u"Nhờ nguồn dữ liệu này, thống kê phân xưởng dễ dàng nắm bắt danh sách nghỉ phép và hoàn tất lịch trực trong vài phút.",
 # 10 · XEM TRUOC — cau noi sang van ban
 u"Kết quả phân công được trực quan hóa ngay trên màn hình, giúp kiểm duyệt chính xác trước khi ban hành.",
 # 11 · XUAT VAN BAN
 u"Ngay sau khi phê duyệt, hệ thống tự động xuất file Word chuẩn thể thức EVN, tích hợp sẵn thông tin trình ký.",
 # 12 · DOI CA
 u"Không chỉ lịch trực thay, quy trình đổi ca giữa các cá nhân cũng được tự động hóa và xuất văn bản tương tự.",
 # 13 · PHEP NAM — man hinh noi "minh bach"; loi noi ta minh bach nghia la gi
 u"Đi cùng với đó, hệ thống tự động cộng phép năm theo thâm niên, đảm bảo minh bạch tối đa quyền lợi.",
 # 14 · ZALO
 u"Đặc biệt, mọi biến động đơn từ đều được thông báo tức thì qua Zalo và Email, giúp cấp quản lý xử lý 24/7..",
 # 15 · CAU HINH — canh nay chi 6 giay nen chi ke ra cai gi dat duoc; y
 # "nen don vi nao cung dung duoc" doi sang canh 16, cho co du cho
 u"Để đạt được điều đó, mỗi phân xưởng đều có thể linh hoạt cấu hình riêng từ mẫu biểu, người ký đến kênh nhận tin.",
 # 16 · KET — thong diep chinh
 u"Tóm lại, đây là giải pháp thống nhất đáp ứng trọn vẹn nhu cầu mọi đơn vị — kết nối toàn bộ quy trình trên một nền tảng số duy nhất.",
 # 17 · DONG
 u"Phần mềm Quản lý lịch trực thay ca — Cùng Thủy điện Ialy nâng tầm chuyển đổi số. Xin cảm ơn quý vị đã theo dõi.",
]

GIONG = "vi-VN-NamMinhNeural"   # giong nam mien Bac, doc trang trong
