-- Topic areas (fixed seed). Display names come from the app's i18n files
-- (ARB key topicArea_<slug>), so only the slug is stored.
CREATE TABLE public.topic_areas (
    slug text PRIMARY KEY CHECK (slug ~ '^[a-z][a-z_]*$'),
    sort_order integer NOT NULL UNIQUE
);

INSERT INTO public.topic_areas (slug, sort_order) VALUES
    ('politics', 1),
    ('economy', 2),
    ('society', 3),
    ('environment', 4),
    ('technology', 5),
    ('sports', 6),
    ('culture', 7),
    ('education', 8),
    ('health', 9);

-- Debate questions. Drafts come from the news/evergreen pipelines or the
-- operator; only approved questions are offered to rooms (via the backend).
CREATE TABLE public.questions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    language text NOT NULL CHECK (language IN ('en', 'de')),
    format text NOT NULL CHECK (format IN ('scale', 'proposal', 'tradeoff')),
    text text NOT NULL,
    option_a text,
    option_b text,
    -- [{"text": ..., "source_ids": [1, 2]}], validated by the backend models.
    facts jsonb NOT NULL CHECK (jsonb_typeof(facts) = 'array'),
    -- [{"id": 1, "url": ..., "title": ..., "outlet": ..., "published_on": ...}]
    sources jsonb NOT NULL CHECK (jsonb_typeof(sources) = 'array'),
    topic_area text NOT NULL REFERENCES public.topic_areas (slug),
    origin text NOT NULL CHECK (origin IN ('news', 'evergreen')),
    status text NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft', 'approved', 'rejected', 'retired')),
    rejection_reason text,
    prompt_version text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT questions_tradeoff_options CHECK (
        (format = 'tradeoff' AND option_a IS NOT NULL AND option_b IS NOT NULL)
        OR (format <> 'tradeoff' AND option_a IS NULL AND option_b IS NULL)
    ),
    CONSTRAINT questions_rejection_reason CHECK (
        (status = 'rejected') = (rejection_reason IS NOT NULL)
    )
);

CREATE INDEX questions_status_language_idx ON public.questions (status, language, topic_area);

-- Backend-only tables: no direct client access through the Data API.
ALTER TABLE public.topic_areas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.questions ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.topic_areas, public.questions FROM anon, authenticated;
