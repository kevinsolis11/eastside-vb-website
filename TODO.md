Project idea / Roadmap

- Purpose: Volleyball team management site (players, coaches, stats, videos, AI summaries, access control).
- Core models present: Player, AccessCode, PlayerProfile, PlayerStats, GameVideo, AISummary (see volleyball_site/team/models.py).
- Suggested features: role-based access (coach/player/admin), invite codes & email invites, player profiles, stats tracking, video upload/management, AI-generated match summaries, coach dashboard, CSV import/export, tests + CI, deployment docs.
- Next steps: add UI pages for video upload and AI summaries, wire Celery tasks for AI processing, and create prioritized milestones in this file.
