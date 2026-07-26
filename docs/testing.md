# Testing Guide

## Where you can test

You can test the application in three places:

1. **Local machine**: best for development and debugging.
2. **Supabase local stack**: best for validating migrations, RLS, and database behavior.
3. **GitHub + Vercel preview/production deployment**: best for browser testing from a public URL.

GitHub Pages is not the right target for this application because the app uses Next.js API routes and server-side Supabase service-role operations. Use Vercel, Netlify, or another Node-capable host for the web app, and Supabase for the database/auth/functions.

## Local web testing

```bash
npm install
cp .env.example .env.local
npm run dev
```

Open `http://localhost:3000/new-request` and create a purchase requisition draft.

## Supabase testing

```bash
supabase start
supabase db push
supabase functions serve
```

Create test users in Supabase Auth, create matching `users_profile` rows, add `approval_matrix` rows, then test requester, approver, and admin flows.

## Automated tests

```bash
npm test
```

The current suite includes workflow transition and line calculation tests. Add API and database integration tests before production rollout.

## Build validation

```bash
npm run build
```

The build requires the environment variables from `.env.example`.
