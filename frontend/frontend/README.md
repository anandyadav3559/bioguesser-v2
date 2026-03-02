# Frontend

The BioGuesser frontend is a React + Vite single-page application. It handles user authentication, the main game loop (animal selection → map guess → results), and user profile display.

---

## Tech Stack

| Tool                                                | Purpose                   |
| --------------------------------------------------- | ------------------------- |
| [React 18](https://react.dev/)                      | UI framework              |
| [Vite](https://vitejs.dev/)                         | Dev server & build tool   |
| [React Router v6](https://reactrouter.com/)         | Client-side routing       |
| [MapLibre GL](https://maplibre.org/)                | Interactive map rendering |
| [H3-js](https://h3geo.org/docs/highlights/indexing) | H3 hexagon cell decoding  |

---

## Project Structure

```
frontend/frontend/
├── src/
│   ├── pages/
│   │   ├── LoginPage.jsx       # Auth entry point (guest / Google login)
│   │   └── HomePage.jsx        # Root game page — composes all components
│   ├── components/
│   │   ├── AnimalCard.jsx      # Flip card UI for selecting an animal
│   │   ├── GameMenu.jsx        # Pre-game animal selection grid
│   │   ├── GamePlay.jsx        # Active game HUD (timer, score, submit)
│   │   ├── MapLibreMap.jsx     # Interactive map with guess + cluster pins
│   │   └── UserProfile.jsx     # Profile stats and game history modal
│   ├── api.js                  # Centralised Axios base URL config
│   ├── App.jsx                 # Router setup + ProtectedRoute wrapper
│   └── main.jsx                # React DOM entry point
├── public/
├── index.html
├── vite.config.js
└── package.json
```

---

## Pages

### `LoginPage` (`/`)

The landing and authentication page. Supports:

- **Google OAuth** — logs in via Google ID token, issues a JWT
- **Guest login** — one-click anonymous session (ephemeral, 4-hour TTL)

On successful auth the token is stored in `localStorage` and the user is redirected to `/home`.

### `HomePage` (`/home`)

The main game page. Manages top-level state and orchestrates the three main views:

- `GameMenu` — animal selection
- `GamePlay` — active round HUD
- `MapLibreMap` — always visible map

Protected by `ProtectedRoute` (redirects to `/` if no token found in `localStorage`).

---

## Components

### `AnimalCard`

A flip-card UI element showing a teaser on the front and biological stats on the back. Used inside `GameMenu`.

### `GameMenu`

Displays a grid of `AnimalCard`s fetched from `GET /api/animal/batch/`. The user picks an animal to start a round.

### `GamePlay`

The active-round overlay. Shows:

- Countdown timer
- Score display (top-left, replaces timer once a guess is submitted)
- Submit button

Communicates with `POST /api/game/guess/` on submission.

### `MapLibreMap`

The central interactive map component built on MapLibre GL JS.

Key behaviours:

- **Guess pin** — distinct marker for the user's click
- **Cluster pins** — sized and coloured by sighting `count` (density-aware)
- Hover tooltip on cluster pins shows exact sighting count
- After a guess is submitted, true sighting locations are rendered as clusters

### `UserProfile`

A modal/panel showing the authenticated user's stats and per-game history. Fetches from `GET /auth/me/`. All scores are displayed rounded to **2 decimal places**.

---

## Authentication

Tokens are stored in `localStorage`:

| Key           | Value                   |
| ------------- | ----------------------- |
| `accessToken` | JWT for permanent users |
| `guestToken`  | JWT for guest sessions  |

`ProtectedRoute` checks for either key before rendering `/home`. The `api.js` Axios instance attaches the token to all outbound requests.

---

## API Communication

All API calls go through the centralised `api.js` Axios instance pointing at the Django backend (default: `http://localhost:8000`). Key endpoints used:

| Endpoint                      | Component     |
| ----------------------------- | ------------- |
| `POST /auth/guest/`           | `LoginPage`   |
| `POST /auth/google/`          | `LoginPage`   |
| `GET /auth/me/`               | `UserProfile` |
| `GET /api/animal/batch/`      | `GameMenu`    |
| `POST /api/game/create/`      | `HomePage`    |
| `POST /api/game/start_round/` | `HomePage`    |
| `POST /api/game/guess/`       | `GamePlay`    |

---

## Development

```bash
cd frontend/frontend
npm install
npm run dev       # Dev server on http://localhost:5173
npm run build     # Production build → dist/
```

> **Environment**: Copy `.env.example` (if present) to `.env` and set `VITE_API_URL` if your backend runs on a non-default port.
