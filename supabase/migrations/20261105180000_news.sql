-- Language versions of one question share a group id.
ALTER TABLE public.questions ADD COLUMN group_id uuid;
CREATE INDEX questions_group_id_idx ON public.questions (group_id);

-- Feed entries from the curated news sources (backend/config/news_sources.toml).
-- Only feed metadata and the feed's own short text, kept for a few days.
CREATE TABLE public.news_items (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    url text NOT NULL UNIQUE,
    title text NOT NULL,
    summary text NOT NULL,
    outlet text NOT NULL,
    language text NOT NULL CHECK (language IN ('en', 'de')),
    leaning text NOT NULL,
    published_at timestamptz NOT NULL,
    fetched_at timestamptz NOT NULL DEFAULT now(),
    expires_at timestamptz NOT NULL
);

CREATE INDEX news_items_published_at_idx ON public.news_items (published_at DESC);
CREATE INDEX news_items_expires_at_idx ON public.news_items (expires_at);

ALTER TABLE public.news_items ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.news_items FROM anon, authenticated;
