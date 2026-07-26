import type { Config } from 'tailwindcss';
export default { content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}', '../../packages/ui/src/**/*.{ts,tsx}'], theme: { extend: { colors: { brand: { 50:'#eff6ff',600:'#2563eb',700:'#1d4ed8' } } } }, plugins: [] } satisfies Config;
