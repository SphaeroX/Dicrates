-- Explicit consent to processing political opinions (GDPR Art. 9) plus the
-- self-declared age confirmation (18+). Append-only: every grant is a new row,
-- the newest row per user counts. Backend-only table: no client access.
CREATE TABLE public.consents (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id uuid NOT NULL REFERENCES auth.users (id) ON DELETE CASCADE,
    consent_version text NOT NULL,
    age_confirmed boolean NOT NULL,
    granted_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX consents_user_id_granted_at_idx ON public.consents (user_id, granted_at DESC, id DESC);

ALTER TABLE public.consents ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.consents FROM anon, authenticated;
