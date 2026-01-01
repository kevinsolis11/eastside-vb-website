# Python: quick start

Create a virtual environment, install dependencies, and run the simple entrypoint:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

The `requirements.txt` is currently empty — add packages there as needed.

## Project idea / Roadmap

- **Purpose:** Volleyball team management site (players, coaches, stats, videos, AI summaries, access control).
- **Core models present:** Player, AccessCode, PlayerProfile, PlayerStats, GameVideo, AISummary (see `volleyball_site/team/models.py`).
- **Suggested features:** role-based access (coach/player/admin), invite codes & email invites, player profiles, stats tracking, video upload/management, AI-generated match summaries, coach dashboard, CSV import/export, tests + CI, deployment docs.
- **Next steps:** add UI pages for video upload and AI summaries, wire Celery tasks for AI processing, and create a `TODO.md` with prioritized milestones.


## OpenAI AI Summaries

### Setup

1. **Install openai package** (already done if you ran `pip install openai`):
   ```bash
   ./.venv/bin/pip install openai
   ```

2. **Set OpenAI API key** in your environment:
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```
   Or add to `.env` file:
   ```
   OPENAI_API_KEY=sk-...
   ```

3. **Enable in Django settings**:
   - The app reads `OPENAI_API_KEY` from environment and stores in settings.
   - See `volleyball_site/volleyball_site/settings.py` for configuration.

### Usage

**Coaches can generate AI summaries** for players via:
- URL: `/team/player/<player_profile_id>/ai-summary/`
- Form: Enter game context (e.g., "15 kills, 8 digs, 2 aces in state final vs Lincoln")
- Result: Auto-saves to `AISummary` model and displays on player profile

**Debug mode**: Summaries generate synchronously in `DEBUG=True` (good for testing).  
**Production**: Summaries queue as Celery tasks for async processing.

### API

**Synchronous helper** (used in DEBUG or manual calls):
```python
from team.tasks import generate_ai_summary_sync
result = generate_ai_summary_sync(player_profile_id=1, game_context="15 kills, 8 digs...")
# Returns: {'success': True, 'summary': 'Generated text...'} or {'success': False, 'error': '...'}
```

**Celery task** (async in production):
```python
from team.tasks import generate_ai_summary_task
generate_ai_summary_task.delay(player_profile_id=1, game_context="15 kills...")
```

### Testing

Currently uses `gpt-3.5-turbo` model. To test without spending API credits, set `OPENAI_API_KEY` to a dummy value and mock the OpenAI client in tests.

