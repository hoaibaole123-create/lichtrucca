/**
 * Soat du lieu trong Supabase. CHI DOC — khong INSERT, khong UPDATE, khong DELETE.
 *
 *   npx tsx api/soat-du-lieu.ts
 *
 * Tim ba loai van de:
 *   1. DU LIEU MO COI  — hang tro toi mot phan xuong khong con ton tai, hoac
 *      khong tro vao dau ca (workshop_id NULL sau khi da chuyen sang pham vi
 *      tung phan xuong).
 *   2. DU LIEU TRUNG   — cung mot nguoi/mot moc xuat hien nhieu lan.
 *   3. DU LIEU THUA    — hang khong con ai dung toi: phien dang nhap het han,
 *      cap phep tro toi don da xoa, nhat ky qua cu.
 *
 * Ten nguoi that duoc CHE khi in ra, chi giu chu dau va so ky tu. Bang nay co
 * ho ten va tham nien cua nhan vien that.
 */
import "dotenv/config";
import { pool } from "../db";

function che(ten: string | null): string {
  if (!ten) return "(trong)";
  const s = String(ten).trim();
  if (s.length <= 1) return s;
  return s[0] + "*".repeat(Math.min(s.length - 1, 8));
}

async function hoi(sql: string, tham: unknown[] = []) {
  const r = await pool.query(sql, tham);
  return r.rows;
}

async function co_bang(ten: string): Promise<boolean> {
  const r = await hoi(
    `SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name=$1`,
    [ten]
  );
  return r.length > 0;
}

const canh_bao: string[] = [];
function bao(muc: "THUA" | "MO COI" | "TRUNG" | "LUU Y", chu: string) {
  canh_bao.push(`[${muc}] ${chu}`);
}

async function main() {
  if (!process.env.DATABASE_URL) {
    console.error("Chua dat DATABASE_URL trong .env");
    process.exit(1);
  }

  // ── 1. Diem danh tung bang ─────────────────────────────────────────────
  const bang = [
    "workshops", "user_accounts", "user_sessions", "employees",
    "leave_requests", "leave_allocations", "leave_balances",
    "location_distances", "app_config", "signatures", "audit_log",
  ];
  console.log("=== SO HANG TUNG BANG ===");
  const dem: Record<string, number> = {};
  for (const b of bang) {
    if (!(await co_bang(b))) { console.log(`  ${b.padEnd(20)} (chua co bang)`); continue; }
    const n = Number((await hoi(`SELECT count(*)::int AS n FROM ${b}`))[0].n);
    dem[b] = n;
    console.log(`  ${b.padEnd(20)} ${String(n).padStart(6)}`);
  }

  // ── 2. Phan xuong ──────────────────────────────────────────────────────
  console.log("\n=== PHAN XUONG ===");
  const px = await hoi(`
    SELECT id, name, code, created_at,
           jsonb_array_length(COALESCE(staff_data, '[]'::jsonb)) AS so_nhan_su
    FROM workshops ORDER BY created_at ASC
  `);
  for (const w of px) {
    const nv = Number((await hoi(`SELECT count(*)::int AS n FROM employees WHERE workshop_id=$1`, [w.id]))[0].n);
    const don = Number((await hoi(`SELECT count(*)::int AS n FROM leave_requests WHERE workshop_id=$1`, [w.id]))[0].n);
    const tk = Number((await hoi(`SELECT count(*)::int AS n FROM user_accounts WHERE workshop_id=$1`, [w.id]))[0].n);
    console.log(`  ${w.id}  "${w.name}" (${w.code})`);
    console.log(`      nhan su trong staff_data: ${w.so_nhan_su} | bang employees: ${nv} | don: ${don} | tai khoan: ${tk}`);
    if (w.so_nhan_su > 0 && nv === 0) {
      bao("LUU Y", `Phan xuong "${w.name}": co ${w.so_nhan_su} nguoi trong staff_data nhung bang employees rong. ` +
        `Quy phep nam tinh tu employees.hire_year, nen nhung nguoi nay chua co so ngay phep.`);
    }
  }

  // ── 3. Hang mo coi ─────────────────────────────────────────────────────
  console.log("\n=== HANG MO COI ===");
  const co_px = px.length > 0;
  for (const b of ["employees", "leave_requests", "leave_balances", "signatures"]) {
    if (!(await co_bang(b))) continue;
    const cot = await hoi(
      `SELECT 1 FROM information_schema.columns WHERE table_name=$1 AND column_name='workshop_id'`, [b]);
    if (!cot.length) { console.log(`  ${b.padEnd(18)} chua co cot workshop_id`); continue; }

    const rong = Number((await hoi(`SELECT count(*)::int AS n FROM ${b} WHERE workshop_id IS NULL`))[0].n);
    const lac = Number((await hoi(
      `SELECT count(*)::int AS n FROM ${b} t
       WHERE t.workshop_id IS NOT NULL
         AND NOT EXISTS (SELECT 1 FROM workshops w WHERE w.id = t.workshop_id)`))[0].n);
    console.log(`  ${b.padEnd(18)} workshop_id NULL: ${rong}   tro toi phan xuong khong ton tai: ${lac}`);
    if (rong > 0 && co_px) {
      bao("MO COI", `${b}: ${rong} hang khong thuoc phan xuong nao. ` +
        `Cac truy van deu loc theo workshop_id nen nhung hang nay khong ai doc toi, nhung van nam do.`);
    }
    if (lac > 0) {
      bao("MO COI", `${b}: ${lac} hang tro toi mot phan xuong da bi xoa.`);
    }
  }

  // leave_allocations tro toi don da xoa
  if (await co_bang("leave_allocations")) {
    const la = Number((await hoi(
      `SELECT count(*)::int AS n FROM leave_allocations a
       WHERE NOT EXISTS (SELECT 1 FROM leave_requests r WHERE r.id = a.leave_id)`))[0].n);
    console.log(`  leave_allocations  tro toi don khong ton tai: ${la}`);
    if (la > 0) bao("MO COI", `leave_allocations: ${la} hang tro toi don da xoa (dang le ON DELETE CASCADE phai don).`);
  }

  // ── 4. Trung lap ───────────────────────────────────────────────────────
  console.log("\n=== TRUNG LAP ===");
  if (await co_bang("employees")) {
    const t = await hoi(`
      SELECT workshop_id, name, count(*)::int AS n FROM employees
      GROUP BY workshop_id, name HAVING count(*) > 1 ORDER BY n DESC LIMIT 20`);
    console.log(`  employees trung (cung phan xuong + ten): ${t.length}`);
    for (const r of t) console.log(`      ${che(r.name)} x${r.n}`);
    if (t.length) bao("TRUNG", `employees: ${t.length} ten bi lap trong cung mot phan xuong.`);
  }
  if (await co_bang("leave_balances")) {
    const t = await hoi(`
      SELECT workshop_id, name, year, count(*)::int AS n FROM leave_balances
      GROUP BY workshop_id, name, year HAVING count(*) > 1 ORDER BY n DESC LIMIT 20`);
    console.log(`  leave_balances trung (phan xuong + ten + nam): ${t.length}`);
    if (t.length) bao("TRUNG", `leave_balances: ${t.length} bo (ten, nam) bi lap.`);
  }
  // Don trung: cung nguoi, cung ngay bat dau va ket thuc
  if (await co_bang("leave_requests")) {
    const t = await hoi(`
      SELECT name, start_date, end_date, count(*)::int AS n
      FROM leave_requests
      WHERE start_date IS NOT NULL AND end_date IS NOT NULL
      GROUP BY name, start_date, end_date HAVING count(*) > 1
      ORDER BY n DESC LIMIT 20`);
    console.log(`  leave_requests trung (ten + ngay di + ngay ve): ${t.length}`);
    for (const r of t) console.log(`      ${che(r.name)}  ${r.start_date} -> ${r.end_date}  x${r.n}`);
    if (t.length) bao("TRUNG", `leave_requests: ${t.length} truong hop cung nguoi cung khoang ngay bi nhap nhieu lan. ` +
      `Neu la nhap trung that thi so ngay phep da bi tru hai lan.`);
  }

  // ── 5. Du lieu thua ────────────────────────────────────────────────────
  console.log("\n=== DU LIEU THUA ===");
  if (await co_bang("user_sessions")) {
    const het = Number((await hoi(`SELECT count(*)::int AS n FROM user_sessions WHERE expires_at < now()`))[0].n);
    console.log(`  user_sessions het han: ${het}`);
    if (het > 0) bao("THUA", `user_sessions: ${het} phien da het han, xoa duoc ngay.`);
  }
  if (await co_bang("audit_log")) {
    const cu = Number((await hoi(`SELECT count(*)::int AS n FROM audit_log WHERE at < now() - interval '180 days'`))[0].n);
    const tong = dem["audit_log"] ?? 0;
    console.log(`  audit_log cu hon 180 ngay: ${cu} / ${tong}`);
    if (cu > 0) bao("THUA", `audit_log: ${cu} dong cu hon 180 ngay.`);
  }
  if (await co_bang("leave_balances")) {
    // Hang chi co ten ma khong co so lieu nao — khong mang thong tin gi
    const rong = Number((await hoi(
      `SELECT count(*)::int AS n FROM leave_balances
       WHERE COALESCE(entitled,'')='' AND COALESCE(used,'')='' AND COALESCE(remaining,'')=''
         AND COALESCE(used_adjust,'')=''`))[0].n);
    console.log(`  leave_balances khong co so lieu nao: ${rong}`);
    if (rong > 0) bao("THUA", `leave_balances: ${rong} hang trong rong.`);
  }
  if (await co_bang("signatures")) {
    const kb = await hoi(`SELECT name, length(data) AS n FROM signatures ORDER BY length(data) DESC LIMIT 5`);
    for (const r of kb) console.log(`  chu ky ${che(r.name).padEnd(12)} ${(Number(r.n)/1024).toFixed(0)} KB`);
  }

  // ── 6. Nguoi co don nhung khong co trong employees ──────────────────────
  console.log("\n=== KHONG KHOP GIUA CAC BANG ===");
  if ((await co_bang("leave_requests")) && (await co_bang("employees"))) {
    const t = await hoi(`
      SELECT DISTINCT r.name, r.workshop_id FROM leave_requests r
      WHERE NOT EXISTS (
        SELECT 1 FROM employees e
        WHERE e.name = r.name AND e.workshop_id IS NOT DISTINCT FROM r.workshop_id)
      LIMIT 30`);
    console.log(`  co don nhung khong co trong employees: ${t.length}`);
    for (const r of t.slice(0, 10)) console.log(`      ${che(r.name)}`);
    if (t.length) bao("LUU Y", `${t.length} nguoi da nop don nhung khong co trong bang employees, ` +
      `nen he thong khong tinh duoc quy phep nam cho ho.`);
  }

  // ── Ket luan ───────────────────────────────────────────────────────────
  console.log("\n=== KET LUAN ===");
  if (!canh_bao.length) console.log("  Khong thay van de nao.");
  else for (const c of canh_bao) console.log("  " + c);

  await pool.end();
}

main().catch(e => { console.error(e); process.exit(1); });
