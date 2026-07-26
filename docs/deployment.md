# Deployment Guide
1. Create a Supabase free-tier project.
2. Run `supabase db push` from the repository root.
3. Deploy functions with `supabase functions deploy sendApprovalEmail approvalAction resubmitApproval cancelApproval requestClarification`.
4. Configure Vercel/Next.js environment variables from `.env.example`.
