# Purchase Requisition & Committee Approval System

Production-ready monorepo for purchase requisitions, committee approval, email approval tokens, printable documents, Supabase RLS, and Next.js 15 UI.

## Commands
- `npm install`
- `npm run dev`
- `npm test`
- `supabase db push`

## Structure
- `apps/web` Next.js 15 React 19 application.
- `packages/types` shared Zod schemas and TypeScript types.
- `packages/workflow` deterministic workflow engine.
- `packages/email` responsive HTML templates.
- `packages/database` Supabase repository layer.
- `supabase/migrations` PostgreSQL schema, functions, RLS.
- `supabase/functions` Edge Functions.

See `docs/architecture.md`, `docs/er-diagram.md`, `docs/workflow.md`, `docs/testing.md`, `docs/deployment.md`, `docs/github-deployment.md`, `docs/final-test-handoff.md`, and `docs/supabase-setup.md`.
