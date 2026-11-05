# Project Brief

> When to read: when goal, scope or boundaries of the project are unclear. Handover document for roadmap planning.

## Name

**Dicrates** = Discus + Socrates. Guiding idea: "I know that I know nothing."

## Goal and audience

Dicrates turns debating into a game. Up to six anonymous people discuss a current, concretely worded question in four asynchronous rounds. An LLM summarizes the group's positions, proposes a compromise and awards points for understanding other views and finding common ground, not for being right.

Problem: on social media comments are dropped without real discussion. Dicrates rewards listening, defending a position with reasons and being open to compromise.

Primary audience: open decision (politically interested people, groups of friends/family/colleagues, later schools). The MVP targets groups of friends.

## Core principles

1. Understanding over winning. 2. Anonymity. 3. Group picture instead of individual opinions. 4. Accessibility from the start (speech input, read-aloud, screen readers). 5. Neutral and transparent LLM. 6. Data minimization.

## Game flow (per match)

- **Round 1 – blind opinion:** everyone sees the question and a sourced fact box, submits a position (scale or proposal) with reasons, without seeing others. Content filter before further processing.
- **Round 2 – group picture:** LLM summary of all positions (strongest form of each, including minority views, neutral, style-smoothed). Each person revises or keeps their position. "Was your position represented fairly?" feedback.
- **Round 3 – movement:** summary of what changed in the group; feedback on arguments (not people).
- **Round 4 – evaluation:** group summary, compromise proposal with pros/cons, points per dimension (argument quality, perspective-taking, openness, compromise contribution, respect, participation) with reasons; open feedback on the match.

Changing one's position never earns points by itself; well-reasoned persistence is not penalized.

## MVP scope (phase 1)

- Friend rooms with invite code/link (no public matching)
- One question per match (curated, or LLM-generated with manual approval)
- Full asynchronous R1–R4 flow with push notifications
- LLM group picture, movement summary, evaluation with compromise proposal
- Anonymity, content filter, report function
- Simple points (no ranking)
- Text input and on-device speech input with editable transcript; read-aloud
- Account (email, Apple, Google; pseudonym), explicit consent, account/content deletion
- App and website in English first, i18n-ready; more languages later
- Public landing page on GitHub Pages
- Automatically generated app screenshots: per-screen previews (mockups) in the repo and store screenshots (Play Store, App Store) per language

Later phases (not MVP): interests and matching queue, automatic news topic pipeline, Glicko/Elo rating and trust score with troll pool, reset rules, admin interface, European rooms, live mode, education/premium offers.

## Non-goals

- No social network (profiles, followers, free comment threads).
- No mandatory real-time chat.
- No sale of raw user data; at most aggregated, anonymized, consented research data.
- No political advertising or opinion-based ad targeting.

## Constraints

- GDPR Art. 9 (political opinions): explicit consent, deletion concept, EU processing, DPAs with providers, no training on user data. Audio is never stored or transmitted.
- EU hosting (Supabase EU region, Mistral EU).
- Accessibility: WCAG 2.1 AA / EU accessibility requirements.
- AI Act transparency: mark summaries and scores as AI-generated.
- DSA obligations for illegal content: to be clarified with a lawyer.
- License: AGPL-3.0, public repository. Funding preference: grants, education licenses, premium; ads last.

## Open decisions

1. Primary target audience.
2. Exact number and duration of rounds (e.g. 12–24 h each).
3. Show the distribution ("4 for, 2 against") in the group picture? (A/B test)
4. How friend rooms count towards the rating (phase 2).
5. Minimum participation and handling of non-submission (proposal: 4 of 6, abort without penalty).
6. Minimum age (16+ or 18+).
7. European rooms: separate per language or with translation.
8. News sources for the topic pipeline (which outlets, political range).
9. Optional anonymity in friend rooms (proposed: configurable).
10. Final bundle id / domain.

---
Maintenance: update this file whenever goals or scope change.
