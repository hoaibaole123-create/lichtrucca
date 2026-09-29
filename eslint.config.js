// ESLint flat config (ESLint 10). Muc tieu: canh bao, KHONG pha build.
// Gan het rule de muc "warn" — repo dang co ~140 cho `any` va vai deps hook bi
// tat thu cong; bat "error" ngay se ket build. Sua dan roi nang len "error".
import js from '@eslint/js';
import tseslint from 'typescript-eslint';
import reactHooks from 'eslint-plugin-react-hooks';

export default tseslint.config(
  {
    // Khong soi cac thu muc sinh ra hoac ngoai pham vi ma nguon.
    ignores: ['dist/**', 'node_modules/**', 'public/**', 'video/**', 'tools/**', '*.config.js'],
  },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ['**/*.{ts,tsx}'],
    plugins: { 'react-hooks': reactHooks },
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      // Ha xuong "warn" cho tuong xung voi thuc trang; day la no ky thuat da biet.
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_', varsIgnorePattern: '^_' }],
      'react-hooks/exhaustive-deps': 'warn',
      // Rule React-Compiler moi (v7): bat setState trong effect/render. Tin hieu
      // that ve re-render lang phi, nhung repo dang co nhieu cho nhu vay va da
      // kiem chung chay on — de "warn" de thay ma sua dan, khong ket build.
      'react-hooks/set-state-in-effect': 'warn',
      'react-hooks/set-state-in-render': 'warn',
      'no-empty': 'warn',
      // Khoi tao mac dinh (= "" / [] / null) roi gan lai trong try/if la style
      // phong thu co chu dinh o repo nay; bo di co the vo nhanh khong gan.
      'no-useless-assignment': 'warn',
      // Regex co ky tu dieu khien dung co chu dinh khi loc/lam sach chuoi.
      'no-control-regex': 'off',
    },
  }
);
