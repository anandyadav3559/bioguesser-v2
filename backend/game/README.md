# `game` App

The `game` app manages the room-round-guess lifecycle for both single-player and multiplayer game sessions. Core scoring logic lives in `GameService`.

---

## Models

### `Room`

The top-level container for a game session.

| Field            | Type               | Description                            |
| ---------------- | ------------------ | -------------------------------------- |
| `id`             | `UUIDField`        | Primary key                            |
| `room_code`      | `CharField(10)`    | Short unique join code (indexed)       |
| `host`           | `ForeignKey(User)` | Room creator (`SET_NULL` on delete)    |
| `status`         | `CharField`        | `waiting` → `playing` → `finished`     |
| `max_players`    | `IntegerField`     | Default `4` (single-player uses `1`)   |
| `max_rounds`     | `IntegerField`     | Default `5` (single-player uses `100`) |
| `time_per_round` | `IntegerField`     | Seconds per round, default `30`        |
| `created_at`     | `DateTimeField`    | Auto-set                               |

### `MultiplayerGame`

Optional metadata attached to rooms that are multiplayer.

| Field                  | Type                  | Description                                     |
| ---------------------- | --------------------- | ----------------------------------------------- |
| `room`                 | `OneToOneField(Room)` | Related room (related name: `multiplayer_data`) |
| `has_permanent_player` | `BooleanField`        | Whether a non-guest player is present           |

### `Player`

A user's participation record within a room.

| Field       | Type               | Description                  |
| ----------- | ------------------ | ---------------------------- |
| `user`      | `ForeignKey(User)` | The participant              |
| `room`      | `ForeignKey(Room)` | Which room                   |
| `score`     | `FloatField`       | Cumulative round score       |
| `is_active` | `BooleanField`     | Whether still in the session |
| `joined_at` | `DateTimeField`    | Timestamp                    |

**Constraint**: `unique_together = ('user', 'room')` — one player record per user per room.

### `Round`

A single question within a room, tied to one `Animal`.

| Field                     | Type                 | Description                     |
| ------------------------- | -------------------- | ------------------------------- |
| `room`                    | `ForeignKey(Room)`   | Parent room                     |
| `round_number`            | `IntegerField`       | 1-indexed position              |
| `animal`                  | `ForeignKey(Animal)` | The animal to guess location of |
| `status`                  | `CharField`          | `active` or `finished`          |
| `start_time` / `end_time` | `DateTimeField`      | Round timing                    |

**Constraint**: `unique_together = ('room', 'round_number')`

### `Guess`

One player's location guess for a round.

| Field                    | Type                 | Description                   |
| ------------------------ | -------------------- | ----------------------------- |
| `player`                 | `ForeignKey(Player)` | Who guessed                   |
| `round`                  | `ForeignKey(Round)`  | Which round                   |
| `latitude` / `longitude` | `FloatField`         | Guessed coordinates           |
| `score_awarded`          | `FloatField`         | Computed score for this guess |

**Constraint**: `unique_together = ('player', 'round')` — one guess per player per round.

> **Timeout sentinel**: A guess with `(200.0, 200.0)` is treated as a timed-out / no-answer guess and scores `0`.

---

## GameService

`GameService` (`services.py`) is a stateless class of `@staticmethod` methods wrapping all DB mutations in `@transaction.atomic`.

### Scoring Algorithm (`evaluate_round`)

Scoring combines two strategies and takes the best result:

1. **H3 Probability Score**
   - Convert the guess's `(lat, lng)` to an H3 cell at resolution 2
   - Look up the sighting count in that cell
   - Compute `p_guess = cell_count / total_sightings`
   - Apply sqrt dampening: `score_prob = √(p_guess / p_max)`

2. **Distance Fallback Score**
   - Find the closest real sighting location (Haversine formula)
   - Apply exponential decay: `score_dist = e^(-distance / 1000km)`

3. **Final score**:
   ```
   final_score = clamp(max(score_prob, score_dist) × 100, min=0.5, max=100.0)
   ```

   - A real guess always earns at least `0.5` points
   - `(200, 200)` timeout sentinel earns exactly `0`

### Key Methods

| Method                                   | Description                                                        |
| ---------------------------------------- | ------------------------------------------------------------------ |
| `create_room(host, ...)`                 | Creates a `Room` + adds host as first `Player`                     |
| `add_player(room, user)`                 | Adds a player (validates room is `waiting` and not full)           |
| `start_round(room)`                      | Picks a random unplayed `Animal`, creates `Round`                  |
| `submit_answer(player, round, lat, lng)` | Creates a `Guess` record                                           |
| `evaluate_round(round)`                  | Scores all guesses, marks round `finished`, updates `Player.score` |
| `end_game(room)`                         | Marks room `finished`, updates `UserProfile` stats                 |

---

## API Endpoints

All endpoints require `IsAuthenticated`.

### `POST /api/game/create/`

Creates a new single-player room.

**Body:**

```json
{ "time_per_round": 30 }
```

**Response:**

```json
{ "room_code": "ABC123", "status": "waiting" }
```

---

### `POST /api/game/start_round/`

Manually starts a round for a given room (single-player flow where the frontend picks the animal).

**Body:**

```json
{ "room_code": "ABC123", "animal_id": "uuid" }
```

**Response:**

```json
{ "round_number": 1, "status": "active" }
```

---

### `POST /api/game/guess/`

Submits a guess and immediately evaluates the round (single-player).

**Body:**

```json
{ "room_code": "ABC123", "latitude": -1.3, "longitude": 36.8 }
```

**Response:**

```json
{
  "score_awarded": 72.45,
  "total_score": 214.23,
  "true_locations": [{ "latitude": -1.3, "longitude": 36.8, "count": 42 }]
}
```

> `true_locations` is capped at 50 entries to avoid oversized payloads.

---

## Signals

`pre_delete` on `User` → `cleanup_user_rooms`:

- If the user's room has **no other permanent players**, the room is deleted.
- If multiplayer and other permanent players remain, the room is preserved (host may become `null`).

---

## Dependencies

- **`authentication`** — `User` model
- **`animal`** — `Animal` / `AnimalLocation` for round selection and scoring
- **`userprofile`** — `UserProfile` updated via `end_game()`
