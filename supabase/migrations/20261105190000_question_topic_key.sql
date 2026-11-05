-- Duplicate protection for generated questions and operator review hints.
ALTER TABLE public.questions ADD COLUMN topic_key text;
ALTER TABLE public.questions ADD COLUMN review_notes jsonb NOT NULL DEFAULT '[]'::jsonb
    CHECK (jsonb_typeof(review_notes) = 'array');
CREATE INDEX questions_topic_key_idx ON public.questions (topic_key);
