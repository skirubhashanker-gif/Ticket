import type { NextConfig } from 'next';
const nextConfig: NextConfig = { transpilePackages: ['@prs/types','@prs/workflow','@prs/email','@prs/database','@prs/ui'] };
export default nextConfig;
