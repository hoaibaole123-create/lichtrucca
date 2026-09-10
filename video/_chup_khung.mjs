// Chup tung khung hinh cua ban trinh chieu ra anh, de ffmpeg ghep thanh mp4.
//
// Khong quay man hinh thoi gian thuc, ma DIEU KHIEN dong ho cua tung hoat canh:
// tat tu dong chay, khoa moi animation o trang thai paused, roi voi moi khung
// dat currentTime = so mili giay tinh tu luc canh bat dau. Nho vay khung hinh
// deu tap tap, khong phu thuoc may nhanh hay cham, va khong bao gio roi khung.
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const GOC = path.resolve('.');
const RA = path.join(GOC, '_khung');
const FPS = 25, RONG = 1920, CAO = 1080;

fs.rmSync(RA, { recursive: true, force: true });
fs.mkdirSync(RA);

const trinhDuyet = await chromium.launch({ channel: 'chrome' });
// SIEU LAY MAU. Trang van duoc bay o 1920x1080 CSS - moi kich thuoc, moi
// clamp() giu nguyen - nhung ve ra o gap doi so diem anh, roi ffmpeg ha lai
// xuong 1920 bang lanczos. Anh chup man hinh goc rong 2560px dang bi thu ve
// ~1000px de trinh bay, nen o gap doi van con du chi tiet that de lay; chu
// thi duoc khu rang cua bang cach lay trung binh bon diem anh thay vi mot.
// Doi lai: moi khung nang gap ~3 lan va chup lau hon khoang ba lan.
const trang = await trinhDuyet.newPage({ viewport: { width: RONG, height: CAO },
  deviceScaleFactor: 2 });
await trang.goto(pathToFileURL(path.join(GOC, 'gioi-thieu-ung-dung.html')).href);
await trang.waitForTimeout(2500);          // cho anh base64 va phong giai ma xong

const giay = await trang.evaluate(() => {
  // Dung bo dem cua ban trinh chieu, an thanh dieu khien (video xuat ra khong can),
  // va khoa moi hoat canh lai de ta tu tay tua tung khung.
  const nut = document.getElementById('chay');
  if (nut && nut.getAttribute('aria-pressed') !== 'false') nut.click();
  // An ca thanh dieu khien (.chan: vach thoi gian, dong ho, nut chay) lan nut
  // "Xem lai tu dau". Tep mp4 co thanh dieu khien cua trinh phat roi, de lai
  // se thanh hai thanh chong nhau, va dong ho trong trang thi dung yen mot cho.
  ['goi', 'chay'].forEach(id => { const e = document.getElementById(id); if (e) e.style.display = 'none'; });
  document.querySelectorAll('.chan').forEach(e => { e.style.display = 'none'; });
  const st = document.createElement('style');
  st.textContent = '*,*::before,*::after{animation-play-state:paused !important}';
  document.head.appendChild(st);
  return [].map.call(document.querySelectorAll('.canh'), c => +c.dataset.giay);
});
console.log('Canh:', giay.join(' '), '| tong', giay.reduce((a, b) => a + b, 0), 'giay');

let n = 0;
for (let i = 0; i < giay.length; i++) {
  await trang.evaluate(k => {
    const ds = document.querySelectorAll('.canh');
    // Canh vua chieu xong duoc danh dau data-ra de no lui ra trong khi canh moi
    // tien vao. Khong danh dau thi chuyen canh mat mot nua chieu sau.
    const cu = k > 0 ? ds[k - 1] : null;
    ds.forEach(c => { c.removeAttribute('data-hien'); c.removeAttribute('data-ra'); });
    if (cu) { void cu.offsetWidth; cu.setAttribute('data-ra', ''); }
    const c = ds[k];
    void c.offsetWidth;
    c.setAttribute('data-hien', '');
    // Bat lai vet quet chuyen canh. Vi dang chay tay tung khung nen ban trinh
    // chieu khong tu goi no; khong bat thi moi lan cat canh chi con mo dan
    // suong, mat han nhip chuyen.
    // ...tru canh CAT KHOP: no tiep tuc cung mot hinh anh voi canh truoc, chi
    // doi cach nhin. Quet mot vet sang ngang qua do la pha mat cu cat khop.
    const q = document.getElementById('quet');
    if (q && k > 0 && !c.classList.contains('noi-tiep')) {
      q.removeAttribute('data-chay'); void q.offsetWidth;
      q.setAttribute('data-chay', '');
    }
  }, i);
  const soKhung = giay[i] * FPS;
  for (let f = 0; f < soKhung; f++) {
    await trang.evaluate(ms => {
      document.getAnimations().forEach(a => { try { a.currentTime = ms; } catch (e) {} });
    }, (f / FPS) * 1000);
    n++;
    await trang.screenshot({ path: path.join(RA, String(n).padStart(5, '0') + '.jpg'),
      type: 'jpeg', quality: 92 });
  }
  console.log('canh', i + 1, '->', soKhung, 'khung (tong', n + ')');
}
await trinhDuyet.close();
console.log('Xong', n, 'khung tai', RA);
