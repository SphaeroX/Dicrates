-- Rounds of a room (1-3 accept submissions; round 4 is the evaluation) and who
-- has submitted in which round. Participation holds no text: the submissions
-- themselves come with Task 11.
ALTER TABLE public.rooms ADD COLUMN finished_at timestamptz;

CREATE TABLE public.rounds (
    room_id uuid NOT NULL REFERENCES public.rooms (id) ON DELETE CASCADE,
    number integer NOT NULL CHECK (number BETWEEN 1 AND 3),
    opened_at timestamptz NOT NULL,
    deadline_at timestamptz NOT NULL,
    closed_at timestamptz,
    PRIMARY KEY (room_id, number)
);

CREATE TABLE public.round_participation (
    room_id uuid NOT NULL,
    round_number integer NOT NULL,
    user_id uuid NOT NULL REFERENCES auth.users (id) ON DELETE CASCADE,
    submitted_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (room_id, round_number, user_id),
    FOREIGN KEY (room_id, round_number) REFERENCES public.rounds (room_id, number)
        ON DELETE CASCADE
);

ALTER TABLE public.rounds ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.round_participation ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.rounds, public.round_participation FROM anon, authenticated;
