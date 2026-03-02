# `userprofile` App

The `userprofile` app maintains persistent game statistics for registered users. It is a thin companion to the `authentication` app — `UserProfile` records are created automatically via Django signals whenever a `User` is created.

---

## Model

### `UserProfile`

| Field          | Type                  | Description                           |
| -------------- | --------------------- | ------------------------------------- |
| `user`         | `OneToOneField(User)` | Linked user (related name: `profile`) |
| `games_played` | `IntegerField`        | Total number of games completed       |
| `total_score`  | `FloatField`          | Cumulative score across all games     |
| `high_score`   | `FloatField`          | Best single-game score                |
| `created_at`   | `DateTimeField`       | Auto-set on creation                  |
| `updated_at`   | `DateTimeField`       | Auto-updated on every save            |

**DB table**: `user_profiles`

---

## Signals

Two `post_save` signals are registered on the `User` model:

| Signal                | Trigger            | Behaviour                                              |
| --------------------- | ------------------ | ------------------------------------------------------ |
| `create_user_profile` | New `User` created | Automatically creates a linked `UserProfile`           |
| `save_user_profile`   | Any `User` saved   | Cascades save to the linked `UserProfile` if it exists |

This means you **never need to manually create a `UserProfile`** — it is always in sync with the `User`.

---

## How Stats Are Updated

`UserProfile` is not updated by this app's own views. Stats are written by `GameService.end_game()` in the `game` app at the conclusion of every game:

```python
profile.games_played = F('games_played') + 1
profile.total_score  = F('total_score')  + player.score
if player.score > profile.high_score:
    profile.high_score = player.score
profile.save()
```

The `F()` expressions ensure atomic DB-level increments without race conditions.

---

## Exposed Data

`UserProfile` data is surfaced to the client through the `GET /auth/me/` endpoint (owned by the `authentication` app). The response includes:

```json
{
  "user_id": "uuid",
  "username": "anand",
  "is_guest": false,
  "stats": {
    "games_played": 12,
    "total_score": 847.5,
    "high_score": 98.0
  },
  "game_history": [ ... ]
}
```

---

## Dependencies

- **`authentication`** — `User` model is the base for `UserProfile.user`
- **`game`** — `GameService.end_game()` writes to this model
