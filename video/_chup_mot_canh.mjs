// Chup lai khung hinh cua DUNG MOT canh, ghi de vao _khung co san.
//   node _chup_mot_canh.mjs 16
// Dung khi chi mot canh doi noi dung: chup lai ca 3000 khung mat 25 phut, con
// chup mot canh mat khoang hai phut. Logic ben trong phai giong het
// _chup_khung.mjs - cung deviceScaleFactor, cung cach danh dau data-ra cho
// canh lien truoc, cung cach tua currentTime - neu khong khung moi se lech
// mau hoac lech chuyen dong so voi phan con lai cua doan phim.
import { chromium } from 'playwright';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const GOC = path.resolve('.');
const RA = path.join(GOC, '_khung');
const FPS = 25, RONG = 1920, CAO = 1080;
const SO_CANH = Number(process.argv[2]);           // dem tu 1
if (!SO_CANH) { console.error('Thieu so canh'); process.exit(1); }

const trinhDuyet = await chromium.launch({ channel: 'chrome' });
const trang = await trinhDuyet.newPage({ viewport: { width: RONG, height: CAO },
  deviceScaleFactor: 2 });
await trang.goto(pathToFileURL(path.join(GOC, 'gioi-thieu-ung-dung.html')).href);
await trang.waitForTimeout(2500);

const giay = await trang.evaluate(() => {
  const nut = document.getElementById('chay');
  if (nut && nut.getAttribute('aria-pressed') !== 'false') nut.click();
  ['goi', 'chay'].forEach(id => { const e = document.getElementById(id); if (e) e.style.display = 'none'; });
  document.querySelectorAll('.chan').forEach(e => { e.style.display = 'none'; });
  const st = document.createElement('style');
  st.textContent = '*,*::before,*::after{animation-play-state:paused !important}';
  document.head.appendChild(st);
  return [].map.call(document.querySelectorAll('.canh'), c => +c.dataset.giay);
});

const k = SO_CANH - 1;
// Khung dau tien cua canh nay = tong so khung cua moi canh dung truoc no
const batDau = giay.slice(0, k).reduce((a, b) => a + b, 0) * FPS;
const soKhung = giay[k] * FPS;
console.log('canh', SO_CANH, '-> khung', batDau + 1, '..', batDau + soKhung);

await trang.evaluate(k => {
  const ds = document.querySelectorAll('.canh');
  const cu = k > 0 ? ds[k - 1] : null;
  ds.forEach(c => { c.removeAttribute('data-hien'); c.removeAttribute('data-ra'); });
  if (cu) { void cu.offsetWidth; cu.setAttribute('data-ra', ''); }
  const c = ds[k];
  void c.offsetWidth;
  c.setAttribute('data-hien', '');
  const q = document.getElementById('quet');
  if (q && k > 0 && !c.classList.contains('noi-tiep')) {
    q.removeAttribute('data-chay'); void q.offsetWidth;
    q.setAttribute('data-chay', '');
  }
}, k);

for (let f = 0; f < soKhung; f++) {
  await trang.evaluate(ms => {
    document.getAnimations().forEach(a => { try { a.currentTime = ms; } catch (e) {} });
  }, (f / FPS) * 1000);
  const n = batDau + f + 1;
  await trang.screenshot({ path: path.join(RA, String(n).padStart(5, '0') + '.jpg'),
    type: 'jpeg', quality: 92 });
}
await trinhDuyet.close();
console.log('Xong', soKhung, 'khung');
