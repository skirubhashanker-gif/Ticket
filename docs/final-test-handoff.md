# Final GitHub + Supabase Test Handoff

This document explains exactly where to test the Purchase Requisition & Committee Approval System after GitHub and Supabase access are configured.

## Current deploy target

- **Source control and CI/CD:** GitHub repository.
- **Web application hosting:** Vercel or another Node-capable Next.js host connected to GitHub.
- **Backend:** Supabase PostgreSQL, Supabase Auth, and Supabase Edge Functions.

Do not use GitHub Pages for the live app because GitHub Pages cannot run Next.js API routes.

## Access validation

Run this from the repository root before deployment:

```bash
./scripts/check-deployment-access.sh
```

The script checks for required CLIs and environment variables needed to deploy/test the app.

## Supabase setup commands

```bash
supabase link --project-ref <your-project-ref>
supabase db push
supabase functions deploy sendApprovalEmail approvalAction resubmitApproval cancelApproval requestClarification
```

After this, open the Supabase dashboard and verify:

1. Tables exist: `purchase_headers`, `purchase_line_items`, `approval_logs`, `users_profile`, `approval_matrix`, `email_queue`, and `approval_tokens`.
2. RLS is enabled on the application tables.
3. Auth email login is enabled.
4. Test users exist for requester, approver, and admin roles.
5. `approval_matrix` has at least one approver row for the requester department.

## GitHub Actions setup

Add the following repository secrets:

- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `APPROVAL_JWT_SECRET`
- `RESEND_API_KEY`
- `EMAIL_FROM`
- `APP_BASE_URL`
- `VERCEL_TOKEN`

Add the repository variable:

- `ENABLE_VERCEL_DEPLOY=true`

Then push to `main` or run the `Deploy Web to Vercel` workflow manually from the GitHub Actions tab.

## Browser smoke-test path

Use the deployed app URL from Vercel or your configured Next.js host.

1. Open `/new-request`.
2. Create a PR with one or more line items.
3. Submit the PR for approval.
4. Verify the PR status becomes `PENDING_APPROVAL_L1`.
5. Sign in as the level-one approver from `approval_matrix`.
6. Open `/approval-inbox`.
7. Approve, reject, or request clarification.
8. Verify an `approval_logs` row is written.
9. If clarification is requested, sign in as requester, edit the same PR, and resubmit.
10. Open the print page and verify the printable document layout.

## Automated verification commands

```bash
npm install
npm test
npm run build
```

If dependency installation fails, fix registry/network access first because the app cannot be validated without installing Node dependencies.
