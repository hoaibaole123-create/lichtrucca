// Phan xuong MAU voi ten nhan vien HU CAU de quay video. Chay voi "xoa" de don sach.
const B = 'http://localhost:3000', MA = 'ZZDEMO', TEN_PX = 'Phân xưởng Vận hành Ialy';
let jar = '';
const api = async (u, o = {}) => {
  const r = await fetch(B + u, { ...o, headers: { ...(o.headers || {}), Cookie: jar } });
  const sc = r.headers.getSetCookie ? r.headers.getSetCookie() : [];
  if (sc.length) jar = sc.map(c => c.split(';')[0]).join('; ');
  const t = await r.text(); try { return JSON.parse(t); } catch { return t; }
};
const CHUC_DANH = ['Trưởng ca','Trực TTĐK','Trực chính điện','Trực phụ điện','Trực chính máy',
  'Trực phụ máy','TC TBA 500 kV','Trực OPY','Trực CNN','Trưởng kíp','Trực chính GM',
  'Trực phụ điện MR','Trực phụ máy MR'];
const HO=['Nguyễn','Trần','Lê','Phạm','Hoàng','Vũ','Đặng','Bùi','Đỗ','Hồ','Ngô','Dương','Lý'];
const DEM=['Văn','Quốc','Minh','Đức','Gia','Hữu','Thanh','Xuân','Tuấn','Hải','Anh','Bá','Công'];
const TEN=['An','Bảo','Cường','Dũng','Đạt','Giang','Hùng','Khang','Lâm','Nam','Phong','Quân',
 'Sơn','Thành','Tùng','Vinh','Khoa','Lộc','Minh','Nhân','Phúc','Quang','Tài','Thắng','Trung',
 'Tuân','Việt','Bình','Chiến','Dân','Đông','Hòa','Kiên','Long','Nghĩa','Phú','Sang','Thái',
 'Tiến','Trí','Tú','Vũ','Xuân','Yên','Hoàng','Kha','Luân','Mạnh','Ngân','Oanh','Phi','Quý',
 'Sinh','Toàn','Trọng','Tường','Ước','Vượng','Bách','Cảnh','Duy','Đại','Hà','Khôi','Lợi'];
const daDung = new Set();
const sinhTen = i => { for (let k=0;k<600;k++){
  const t=`${HO[(i*7+k*3)%HO.length]} ${DEM[(i*5+k)%DEM.length]} ${TEN[(i*11+k*7)%TEN.length]}`;
  if(!daDung.has(t)){daDung.add(t);return t;} } throw new Error('het ten'); };
const staffData = CHUC_DANH.map((cd,i)=>[cd,...Array.from({length:5},(_,k)=>sinhTen(i*5+k))]);

(async () => {
  await api('/api/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({username:'admin',password:'admin123'})});
  const xoa = process.argv[2]==='xoa';
  const cu = (await api('/api/workshops')).find(w=>w.code===MA);

  if (xoa) {
    if (cu) {
      for (const a of (await api('/api/accounts')).filter(x=>x.username==='demo'))
        await api('/api/accounts/'+a.id,{method:'DELETE'});
      await api('/api/workshops/'+cu.id,{method:'DELETE'});
      console.log('Da xoa phan xuong mau va tai khoan demo.');
    } else console.log('Khong con gi de xoa.');
    console.log('Con sot:', (await api('/api/workshops')).filter(w=>w.code===MA).length);
    return;
  }

  const ws = await api('/api/workshops',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({ id:cu?.id, name:TEN_PX, code:MA, description:'Du lieu mau quay video',
      staffData, features:{},
      config:{ companyName:'CÔNG TY THỦY ĐIỆN IALY', headerWorkshopName:'PHÂN XƯỞNG VẬN HÀNH IALY',
        recipientWorkshopName:'Phân xưởng Vận hành Ialy', shortWorkshopName:'Phân xưởng Vận hành Ialy',
        documentCodeSuffix:'/VHIALY', locationName:'Gia Lai', soVanBan:'', ngayKy:'',
        nguoiKy:'Nguyễn Văn An', chucVuNguoiKy:'Quản đốc', zaloWebhookUrl:'', notifyEmail:'' }})});
  const wsId = ws.workshop.id;
  console.log('Phan xuong mau:', wsId);

  await api('/api/accounts',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({username:'demo',password:'Demo12345',fullName:'Tài khoản trình chiếu',
      role:'workshop_admin',workshopId:wsId})});

  const rows = staffData.flatMap(r=>r.slice(1)).map((name,i)=>({
    name, hireYear:2026-(3+(i*7)%26), baseDays:16, used:[0,2,5,0,3,8][i%6] }));
  console.log((await api('/api/leave/employees/import',{method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({workshopId:wsId,year:'2026',rows})})).message);

  const don = [
    {name:staffData[0][1],chucDanh:'Trưởng ca',kip:'1',startDate:'2026-09-07',endDate:'2026-09-11',
     reason:'Giải quyết việc riêng gia đình',location:'Gia Lai'},
    {name:staffData[4][3],chucDanh:'Trực chính máy',kip:'3',startDate:'2026-09-14',endDate:'2026-09-16',
     reason:'Về quê có việc gia đình',location:'Bình Định'},
    {name:staffData[2][2],chucDanh:'Trực chính điện',kip:'2',startDate:'2026-09-21',endDate:'2026-09-23',
     reason:'Nghỉ phép năm',location:'Đà Nẵng'},
  ];
  for (const d of don)
    await api('/api/sheets/leave-requests',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({...d,birthYear:'1990',phone:'0900 000 000',workshopId:wsId})});
  console.log('Da tao', don.length, 'don nghi phep.');
  console.log('\nDang nhap: demo / Demo12345');
})();
