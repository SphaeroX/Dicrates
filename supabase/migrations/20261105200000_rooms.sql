-- Friend rooms and their members. Backend-only: members never see each other's
-- identities; the API returns counts only.
CREATE TABLE public.rooms (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id uuid NOT NULL REFERENCES public.questions (id),
    language text NOT NULL CHECK (language IN ('en', 'de')),
    round_duration_hours integer NOT NULL CHECK (round_duration_hours IN (1, 6, 12, 24, 48)),
    status text NOT NULL DEFAULT 'FORMING' CHECK (status IN (
        'FORMING', 'R1_OPEN', 'R1_CLOSED', 'R2_OPEN', 'R2_CLOSED', 'R3_OPEN', 'R3_CLOSED',
        'R4_EVALUATING', 'FINISHED', 'ARCHIVED', 'ABORTED'
    )),
    invite_code text NOT NULL CHECK (invite_code ~ '^[ABCDEFGHJKMNPQRTUVWXYZ2346789]{6}$'),
    creator_id uuid NOT NULL REFERENCES auth.users (id) ON DELETE CASCADE,
    created_at timestamptz NOT NULL DEFAULT now(),
    started_at timestamptz
);

-- A code is unique among rooms that are not over yet.
CREATE UNIQUE INDEX rooms_active_invite_code_idx ON public.rooms (invite_code)
    WHERE status NOT IN ('FINISHED', 'ARCHIVED', 'ABORTED');
CREATE INDEX rooms_status_idx ON public.rooms (status);

CREATE TABLE public.room_members (
    room_id uuid NOT NULL REFERENCES public.rooms (id) ON DELETE CASCADE,
    user_id uuid NOT NULL REFERENCES auth.users (id) ON DELETE CASCADE,
    -- Internal anonymous placeholder used in LLM inputs instead of any identity.
    alias uuid NOT NULL DEFAULT gen_random_uuid(),
    joined_at timestamptz NOT NULL DEFAULT now(),
    left_at timestamptz,
    PRIMARY KEY (room_id, user_id)
);

CREATE INDEX room_members_user_idx ON public.room_members (user_id) WHERE left_at IS NULL;

ALTER TABLE public.rooms ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.room_members ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.rooms, public.room_members FROM anon, authenticated;

-- LLM usage records may now point at their room (kept when the room is deleted).
ALTER TABLE public.llm_calls
    ADD CONSTRAINT llm_calls_room_id_fkey FOREIGN KEY (room_id)
    REFERENCES public.rooms (id) ON DELETE SET NULL;
