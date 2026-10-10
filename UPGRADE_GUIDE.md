# PathWise 2.1 — Student-first release

- No demo student names or sample-profile dropdown in the application.
- New students enter their own name, interests, skills, prerequisites and career goal.
- Dashboard is hidden until a name and at least one interest are provided.
- With Supabase configured, sign-in is required and profiles can be saved to the private database.
- Without Supabase, profiles are **not persisted across devices**; use the JSON backup/restore buttons.

## Run locally

```powershell
uv run --python 3.13 --with streamlit --with pandas --with supabase streamlit run app.py
```

## Enable private cloud accounts

1. Create a Supabase project and run `SUPABASE_SETUP.sql` in its SQL Editor.
2. Set `SUPABASE_URL` and `SUPABASE_ANON_KEY` in `.streamlit/secrets.toml` locally or Streamlit Community Cloud secrets. Never commit secrets.
3. Configure authentication/email verification in Supabase, then test sign-up, sign-in, save, sign-out and reload in separate accounts.
4. Only deploy after testing. Existing live Step 6 app should remain untouched until ready.

This prototype uses an illustrative course catalogue, not verified institutional requirements.
