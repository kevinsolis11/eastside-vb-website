# Eastside VB Website - API Documentation

## Overview
This API provides comprehensive endpoints for managing volleyball team operations including player profiles, game videos, AI-powered video analysis, and team announcements.

---

## Authentication

All endpoints (except login) require authentication via token.

### Login
**Endpoint:** `POST /api/login/`

**Request:**
```json
{
  "username": "coach_name",
  "password": "your_password"
}
```

**Response:**
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbea6f7",
  "user": {
    "id": 1,
    "username": "coach_name",
    "email": "coach@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "profile": {
    "id": 1,
    "position": "Setter",
    "height": "6'2\"",
    "stats": {
      "kills": 150,
      "blocks": 45,
      "aces": 20,
      "digs": 200,
      "updated_at": "2025-12-25T10:30:00Z"
    }
  }
}
```

### Logout
**Endpoint:** `POST /api/logout/`

**Headers:** 
- `Authorization: Token YOUR_TOKEN`

**Response:**
```json
{
  "message": "Logged out successfully"
}
```

---

## Player Endpoints

### Get Player Profile
**Endpoint:** `GET /api/player/profile/`

**Headers:** 
- `Authorization: Token YOUR_TOKEN`

**Response:**
```json
{
  "id": 1,
  "user": {
    "id": 2,
    "username": "player1",
    "email": "player@example.com",
    "first_name": "Jane",
    "last_name": "Smith"
  },
  "player": {
    "id": 1,
    "first_name": "Jane",
    "last_name": "Smith",
    "number": 12,
    "position": "Outside Hitter"
  },
  "position": "Outside Hitter",
  "height": "6'0\"",
  "stats": {
    "id": 1,
    "kills": 180,
    "blocks": 35,
    "aces": 15,
    "digs": 220,
    "updated_at": "2025-12-25T10:30:00Z"
  }
}
```

### Get Player Stats
**Endpoint:** `GET /api/player/stats/`

**Headers:** 
- `Authorization: Token YOUR_TOKEN`

**Response:**
```json
{
  "id": 1,
  "kills": 180,
  "blocks": 35,
  "aces": 15,
  "digs": 220,
  "updated_at": "2025-12-25T10:30:00Z"
}
```

### Get AI Summary
**Endpoint:** `GET /api/player/summary/`

**Headers:** 
- `Authorization: Token YOUR_TOKEN`

**Response:**
```json
{
  "id": 1,
  "summary": "Excellent performance in the state tournament. Strong hitting with 15 kills and solid defensive play with 8 digs. Keep working on block technique.",
  "generated_at": "2025-12-25T09:15:00Z"
}
```

---

## Video Endpoints

### List Game Videos
**Endpoint:** `GET /api/videos/`

**Headers:** 
- `Authorization: Token YOUR_TOKEN`

**Query Parameters:**
- `game_type`: Filter by 'full', 'highlight', or 'practice'
- `opponent`: Filter by opponent name
- `ordering`: Order by '-game_date' or '-uploaded_at'

**Response:**
```json
[
  {
    "id": 1,
    "title": "State Championship vs Lincoln High",
    "description": "Full game recording from the state tournament final",
    "game_type": "full",
    "game_date": "2025-12-20",
    "opponent": "Lincoln High",
    "thumbnail": "https://example.com/media/video_thumbnails/2025/12/thumb.jpg",
    "duration_seconds": 3600,
    "view_count": 45,
    "uploaded_by_name": "Coach Smith",
    "uploaded_at": "2025-12-20T18:30:00Z"
  }
]
```

### Get Video Details
**Endpoint:** `GET /api/videos/{video_id}/`

**Headers:** 
- `Authorization: Token YOUR_TOKEN`

**Response:** Same as list item above

---

## Video Analysis Endpoints (ChatGPT 5 - NEW)

### Request Video Analysis
**Endpoint:** `POST /api/videos/{video_id}/analyze/`

**Headers:** 
- `Authorization: Token YOUR_TOKEN`
- `Content-Type: application/json`

**Description:** Coaches can request AI analysis of a game video. Uses configured GPT model (default: gpt-5.1-codex-max).

**Response:**
```json
{
  "message": "Video analysis queued for 'State Championship vs Lincoln High'. Check back soon!",
  "status": "pending",
  "analysis_id": 1
}
```

**Status Values:**
- `pending` - Analysis queued, waiting to process
- `processing` - Currently analyzing the video
- `completed` - Analysis finished
- `failed` - Analysis encountered an error

### Get Video Analysis Results
**Endpoint:** `GET /api/videos/{video_id}/analysis/`

**Headers:** 
- `Authorization: Token YOUR_TOKEN`

**Response (When Complete):**
```json
{
  "status": "completed",
  "analysis": "Full detailed analysis of the game...",
  "highlights": "Key moments and impressive plays...",
  "player_performance": "Individual player insights...",
  "tactical_notes": "Strategic recommendations...",
  "analysis_model": "gpt-5.1-codex-max",
  "created_at": "2025-12-25T10:00:00Z",
  "completed_at": "2025-12-25T10:15:00Z",
  "error": null
}
```

**Response (When Pending):**
```json
{
  "status": "pending",
  "analysis": null,
  "highlights": null,
  "player_performance": null,
  "tactical_notes": null,
  "analysis_model": "gpt-5.1-codex-max",
  "created_at": "2025-12-25T10:00:00Z",
  "completed_at": null,
  "error": null
}
```

---

## Announcement Endpoints

### Get All Announcements
**Endpoint:** `GET /api/announcements/`

**Headers:** 
- `Authorization: Token YOUR_TOKEN`

**Response:**
```json
[
  {
    "id": 1,
    "title": "Practice Schedule Change",
    "message": "Tuesday practice moved to Wednesday this week",
    "is_urgent": true,
    "coach_name": "Coach Smith",
    "created_at": "2025-12-25T09:00:00Z",
    "updated_at": "2025-12-25T09:00:00Z"
  }
]
```

---

## Configuration

### GPT Model Selection
The API uses the model specified in `OPENAI_GPT_MODEL` setting:

**Current:** `gpt-5.1-codex-max`

**Other Options:**
- `gpt-3.5-turbo`
- `gpt-4`
- `gpt-4-turbo`

**To Change:** Set `OPENAI_GPT_MODEL` environment variable

### GPT-5.1-Codex-Max Feature
**Status:** Enabled if `ENABLE_GPT_5_1_CODEX_MAX=True`

**Features:**
- Advanced video analysis
- Player performance insights
- Tactical recommendations
- Highlight identification

---

## Error Responses

All error responses follow this format:

```json
{
  "error": "Error message describing what went wrong",
  "detail": "Additional context if available"
}
```

**Common Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized (no token or invalid token)
- `403` - Forbidden (permission denied)
- `404` - Not Found
- `500` - Server Error

---

## Usage Examples

### Example 1: Login and Get Player Profile
```bash
# Login
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "player1", "password": "password123"}'

# Response includes token: 9944b09199c62bcf9418ad846dd0e4bbea6f7

# Get profile with token
curl -X GET http://localhost:8000/api/player/profile/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbea6f7"
```

### Example 2: Request Video Analysis
```bash
# Request analysis for video ID 1
curl -X POST http://localhost:8000/api/videos/1/analyze/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json"

# Check analysis status
curl -X GET http://localhost:8000/api/videos/1/analysis/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### Example 3: Get Video List and Announcements
```bash
# Get all videos
curl -X GET http://localhost:8000/api/videos/ \
  -H "Authorization: Token YOUR_TOKEN"

# Get announcements
curl -X GET http://localhost:8000/api/announcements/ \
  -H "Authorization: Token YOUR_TOKEN"
```

---

## Rate Limiting
Currently not implemented. Available in future releases.

## Pagination
Currently not implemented. Available in future releases.

## Changelog
- **v1.0** (2025-12-25): Initial release with video analyzer, GPT model configuration
