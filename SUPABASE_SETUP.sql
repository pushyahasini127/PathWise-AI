-- Run in Supabase SQL Editor. Profiles are private to the signed-in user.
create table if not exists public.student_profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  profile jsonb not null,
  updated_at timestamptz not null default now()
);
alter table public.student_profiles enable row level security;
create policy "Users can read own profile" on public.student_profiles for select to authenticated using ((select auth.uid()) = user_id);
create policy "Users can insert own profile" on public.student_profiles for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "Users can update own profile" on public.student_profiles for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
