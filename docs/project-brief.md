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
- One question per match, chosen by the room creator from a library of approved questions. The LLM prepares questions (neutral wording, sourced fact box, neutrality/safety check) from curated news feeds and from a curated list of evergreen/historical debates, preferring controversial topics; nothing is published without operator approval via a backend CLI (`dicrates-admin`)
- Friend rooms have 3–6 members; the creator picks the round duration (default 24 h); a round closes early once everyone has submitted
- Full asynchronous R1–R4 flow with push notifications
- LLM group picture, movement summary, evaluation with compromise proposal
- Anonymity, content filter, report function
- Simple points (no ranking)
- Text input and on-device speech input with editable transcript; read-aloud
- Account (email, Apple, Google; pseudonym), explicit consent, account/content deletion
- App and website in English (base) and German; more languages later
- Closed beta (Play Internal Testing / TestFlight) before the public store release
- Public landing page on GitHub Pages
- Automatically generated app screenshots: per-screen previews (mockups) in the repo and store screenshots (Play Store, App Store) per language

Later phases (not MVP): interests and matching queue, publishing questions without human approval, web admin UI, Glicko/Elo rating and trust score with troll pool, reset rules, admin interface, European rooms, live mode, education/premium offers.

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

## Decided (2026-11-05, roadmap planning)

- Production readiness = MVP (phase 1) publicly in the stores after a closed beta. Plan: `Roadmap/`.
- Rounds: four rounds; the creator chooses the duration per room (default 24 h); early close when all active members have submitted.
- Minimum participation: rooms need 3–6 members; fewer than 3 valid round-1 submissions abort the match without penalty.
- Minimum age: 18+ (self-declared at sign-up).
- Friend rooms are always anonymous in the MVP; the group picture shows no distribution ("4 for, 2 against").
- Questions: news feeds + evergreen/historical debates, LLM-prepared, operator-approved via CLI.
- Languages: English and German for app and website.
- Production hosting for API and worker: decided in roadmap task 17 (EU options compared, user confirms).

## Open decisions

1. Primary target audience beyond the MVP's friend groups.
2. Show the distribution in the group picture later? (A/B test, phase 2)
3. How friend rooms count towards the rating (phase 2).
4. European rooms: separate per language or with translation.
5. News sources for the topic pipeline (which outlets, political range) – roadmap task 07.
6. Optional anonymity in friend rooms (phase 2).
7. Final bundle id / domain – before the first store upload (roadmap task 26).
8. Retention period for plain-text submissions (proposal: 30 days after the match) – roadmap task 22.

---
Maintenance: update this file whenever goals or scope change.
