/**
 * Doi chieu nhung cho dang cung giu ten nguoi trong he thong. CHI DOC.
 *
 *   npx tsx api/soat-nhan-su.ts
 *
 * workshops.staff_data KHONG phai danh sach nhan su. No la mot LUOI string[][]:
 * moi dong mot chuc danh, cot 0 la ten chuc danh, cot 1..5 la nguoi truc cua
 * kip 1..5 (xem src/utils/shiftHelpers.ts va nhan "N Chuc danh" trong
 * WorkshopManagerModal). Dem so dong cua no ra "so nhan su" la sai — do la so
 * chuc danh.
 *
 * Ba cho giu ten nguoi, va ten la khoa noi chung lai:
 *   staff_data (cot 1..5)  ai dang truc o kip nao — dung de xep lich
 *   employees              nam vao lam — dung de TINH quy phep nam
 *   signatures             anh chu ky
 *
 * Ten lech mot dau cach hay mot dau tieng Viet la chung roi ra khoi nhau ma
 * khong bao gi.
 */
import "dotenv/config";
import { pool } from "../db";

function che(ten: string): string {
  const s = String(ten || "").trim();
  if (s.length <= 1) return s || "(trong)";
  return s[0] + "*".repeat(Math.min(s.length - 1, 8));
}

// Chuan hoa de so sanh: bo dau cach thua, ve chu thuong. KHONG bo dau tieng
// Viet — hai nguoi ten khac dau la hai nguoi khac.
function chuan(s: string): string {
  return String(s || "").trim().replace(/\s+/g, " ").toLowerCase();
}

async function main() {
  const ws = (await pool.query(
    `SELECT id, name, staff_data FROM workshops ORDER BY created_at ASC`)).rows;

  for (const w of ws) {
    console.log(`\n${"=".repeat(60)}\n${w.name}  (${w.id})`);

    const luoi: string[][] = Array.isArray(w.staff_data) ? w.staff_data : [];
    const chucDanh = luoi.map(h => (Array.isArray(h) ? h[0] : "")).filter(Boolean);
    // Nguoi truc nam o cot 1 tro di
    const nguoiTruc = luoi.flatMap(h => (Array.isArray(h) ? h.slice(1) : []))
                          .map(s => String(s || "").trim()).filter(Boolean);
    const oTrong = luoi.reduce((n, h) =>
      n + (Array.isArray(h) ? h.slice(1).filter(c => !String(c || "").trim()).length : 0), 0);

    const emp = (await pool.query(
      `SELECT name, hire_year, base_days FROM employees WHERE workshop_id=$1 ORDER BY name`,
      [w.id])).rows;
    const sig = (await pool.query(
      `SELECT name FROM signatures WHERE workshop_id=$1`, [w.id])).rows;

    console.log(`  luoi phan ca : ${luoi.length} chuc danh x ${luoi[0]?.length ?? 0} cot`);
    console.log(`  nguoi trong luoi: ${new Set(nguoiTruc.map(chuan)).size} nguoi khac nhau` +
                ` (${nguoiTruc.length} o co ten, ${oTrong} o trong)`);
    console.log(`  employees    : ${emp.length}`);
    console.log(`  signatures   : ${sig.length}`);

    const tapLuoi = new Set(nguoiTruc.map(chuan));
    const tapEmp = new Set(emp.map((e: any) => chuan(e.name)));

    // Nguoi dang truc ma khong co nam vao lam -> khong tinh duoc quy phep nam
    const thieuHoSo = [...tapLuoi].filter(n => !tapEmp.has(n));
    console.log(`\n  Dang truc nhung KHONG co trong employees: ${thieuHoSo.length}`);
    for (const n of thieuHoSo.slice(0, 20)) console.log(`      ${che(n)}`);
    if (thieuHoSo.length > 20) console.log(`      ... con ${thieuHoSo.length - 20}`);

    // Co ho so nhung khong con truc o kip nao — nghi huu, chuyen don vi, hoac du thua
    const khongTruc = emp.filter((e: any) => !tapLuoi.has(chuan(e.name)));
    console.log(`\n  Co trong employees nhung khong o luoi phan ca nao: ${khongTruc.length}`);
    for (const e of khongTruc.slice(0, 20)) {
      console.log(`      ${che(e.name).padEnd(12)} vao nam ${e.hire_year}`);
    }
    if (khongTruc.length > 20) console.log(`      ... con ${khongTruc.length - 20}`);

    const sigLac = sig.filter((s: any) =>
      !tapLuoi.has(chuan(s.name)) && !tapEmp.has(chuan(s.name)));
    console.log(`\n  Co chu ky nhung khong o ca hai cho: ${sigLac.length}`);
    for (const s of sigLac) console.log(`      ${che(s.name)}`);

    // Ten chi khac nhau o dau cach — dau hieu mot nguoi bi ghi hai kieu
    const tatCa = [...new Set([...tapLuoi, ...tapEmp])];
    const gan: string[] = [];
    for (let i = 0; i < tatCa.length; i++)
      for (let j = i + 1; j < tatCa.length; j++)
        if (tatCa[i].replace(/\s/g, "") === tatCa[j].replace(/\s/g, ""))
          gan.push(`${che(tatCa[i])} / ${che(tatCa[j])}`);
    if (gan.length) {
      console.log(`\n  Ten chi khac nhau o dau cach — co the la mot nguoi: ${gan.length}`);
      for (const g of gan) console.log(`      ${g}`);
    }

    // Luoi co ve la du lieu thu nghiem?
    const nguNgan = nguoiTruc.filter(n => n.replace(/\s/g, "").length <= 2);
    if (nguNgan.length >= 2) {
      console.log(`\n  CANH BAO: ${nguNgan.length} o trong luoi chi co 1-2 ky tu` +
                  ` — trong giong du lieu go thu, khong phai ten nguoi.`);
    }
  }

  console.log(`\n${"=".repeat(60)}\napp_config:`);
  for (const r of (await pool.query(`SELECT key, pg_column_size(value) AS co FROM app_config ORDER BY key`)).rows) {
    console.log(`  ${String(r.key).padEnd(24)} ${r.co} byte`);
  }
  console.log(`\nuser_accounts:`);
  for (const r of (await pool.query(
    `SELECT username, role, workshop_id FROM user_accounts ORDER BY role, username`)).rows) {
    console.log(`  ${che(r.username).padEnd(14)} ${String(r.role).padEnd(16)} ${r.workshop_id ?? "(toan he thong)"}`);
  }

  await pool.end();
}

main().catch(e => { console.error(e); process.exit(1); });
