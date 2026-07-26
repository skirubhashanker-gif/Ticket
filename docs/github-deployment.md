# GitHub Deployment Guide

## Can this be deployed directly on GitHub Pages?

No. This project is a Next.js application with API routes and server-side Supabase access. GitHub Pages only hosts static files, so it cannot run the API routes required by this app.

## Recommended GitHub-based deployment

Use GitHub as the source repository and deploy the web app to Vercel through GitHub Actions. Supabase hosts PostgreSQL, Auth, and Edge Functions.

## Required GitHub secrets

Add these in GitHub repository settings under **Settings → Secrets and variables → Actions**:

- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `APPROVAL_JWT_SECRET`
- `RESEND_API_KEY`
- `EMAIL_FROM`
- `APP_BASE_URL`
- `VERCEL_TOKEN`

Add this repository variable to enable deployment:

- `ENABLE_VERCEL_DEPLOY=true`

## Required Vercel project values

The Vercel CLI also needs project metadata. The easiest path is:

```bash
npx vercel link
```

Commit the generated `.vercel/project.json` only if your team policy allows it, or configure Vercel Git integration directly in the Vercel dashboard.

## Deployment workflow

This repository includes:

- `.github/workflows/ci.yml` for install, test, and build validation.
- `.github/workflows/vercel-deploy.yml` for production deployment when `ENABLE_VERCEL_DEPLOY` is set to `true`.

## Supabase deployment

Run these commands from a trusted machine or CI job with Supabase credentials:

```bash
supabase db push
supabase functions deploy sendApprovalEmail approvalAction resubmitApproval cancelApproval requestClarification
```

## Manual smoke test after deployment

1. Open the deployed app URL.
2. Sign in with a requester account.
3. Create a PR from `/new-request`.
4. Submit it for approval.
5. Sign in as the configured approver.
6. Open `/approval-inbox`.
7. Approve, reject, or request clarification.
8. Print the PR from the print page.
