-- One profile per Supabase Auth user. Pseudonym and language are chosen in onboarding.
CREATE TABLE public.profiles (
    id uuid PRIMARY KEY REFERENCES auth.users (id) ON DELETE CASCADE,
    pseudonym text,
    language text NOT NULL DEFAULT 'en' CHECK (language IN ('en', 'de')),
    created_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Clients may read only their own profile. All writes go through the backend.
REVOKE ALL ON public.profiles FROM anon, authenticated;
GRANT SELECT ON public.profiles TO authenticated;

CREATE POLICY profiles_select_own ON public.profiles
    FOR SELECT TO authenticated
    USING ((SELECT auth.uid()) = id);
