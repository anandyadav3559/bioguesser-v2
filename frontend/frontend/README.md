# Frontend Documentation

The frontend is a **React** application built with **Vite**.

## Tech Stack
-   **Framework**: React 18+
-   **Build Tool**: Vite
-   **Routing**: React Router DOM
-   **HTTP Client**: Axios
-   **Auth**: @react-oauth/google

## Setup

1.  **Environment Variables**:
    Create `.env` in `frontend/frontend/`:
    ```env
    VITE_API_BASE_URL=http://localhost:8000/api
    VITE_GOOGLE_CLIENT_ID=your-google-client-id
    ```

2.  **Dependencies**:
    ```bash
    npm install
    ```

3.  **Run Dev Server**:
    ```bash
    npm run dev
    ```

## Project Structure

-   `src/App.jsx`: Main routing logic (`/`, `/home`).
-   `src/api.js`: configured Axios instance with interceptors for attaching JWT and Guest tokens.
-   `src/pages/`:
    -   `LoginPage.jsx`: Guest Login & Google Sign-In logic.
    -   `HomePage.jsx`: Protected landing page with Logout.

## Authentication Flow

1.  **Login**: User clicks "Guest" or "Google Login".
2.  **Request**: `api.post('/auth/guest/')` or `/auth/google/`.
3.  **Storage**: Frontend receives `access`, `user_id`, `identity_type` and stores them in `localStorage`.
4.  **Interceptors**: `api.js` automatically attaches `Authorization: Bearer <token>` to all subsequent requests.
5.  **Protection**: `ProtectedRoute` in `App.jsx` redirects unauthenticated users to `/`.
6.  **Logout**: Calls backend `/auth/logout/` then clears `localStorage`.
