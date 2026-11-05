-- Usage log of LLM calls for cost and reliability monitoring.
-- Deliberately contains NO text: no prompt, no user input, no model output.
CREATE TABLE public.llm_calls (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    created_at timestamptz NOT NULL DEFAULT now(),
    task text NOT NULL,
    prompt_version text NOT NULL,
    model text NOT NULL,
    input_tokens integer NOT NULL CHECK (input_tokens >= 0),
    output_tokens integer NOT NULL CHECK (output_tokens >= 0),
    duration_ms integer NOT NULL CHECK (duration_ms >= 0),
    success boolean NOT NULL,
    error_kind text,
    attempts integer NOT NULL CHECK (attempts >= 1),
    -- Foreign key to rooms is added once the rooms table exists (Task 09).
    room_id uuid
);

CREATE INDEX llm_calls_created_at_idx ON public.llm_calls (created_at);

ALTER TABLE public.llm_calls ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.llm_calls FROM anon, authenticated;
