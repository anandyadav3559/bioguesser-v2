# Frontend Documentation

The frontend for Bio-Geoguesser V2, built with **React** and **Vite**.

## 💻 Tech Stack

-   **Core**: React 18, Vite
-   **Routing**: React Router DOM v6
-   **HTTP Client**: Axios
-   **Authentication**: @react-oauth/google
-   **Styling**: CSS Modules / Vanilla CSS (Tailored for performance)

## 🚀 Getting Started

### 1. Installation

Navigate to the frontend directory:
```bash
cd frontend/frontend
npm install
```

### 2. Environment Configuration

Create a `.env` file in `frontend/frontend/`:

```ini
# Base URL for the Backend API
VITE_API_BASE_URL=http://localhost:8000/api

# Google OAuth Client ID (Must match the one in Backend)
# Get one from https://console.cloud.google.com/
VITE_GOOGLE_CLIENT_ID=your-google-client-id
```

### 3. Development Server

Run the development server with hot-reload:

```bash
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

### 4. Build for Production

```bash
npm run build
```
The output will be in the `dist/` directory.

## 📂 Project Structure

```text
src/
├── assets/         # Static assets (images, icons)
├── components/     # Reusable UI components (Buttons, Inputs, Modals)
├── pages/          # Page components (routed views)
│   ├── HomePage.jsx   # Main game dashboard
│   ├── LoginPage.jsx  # Auth entry point
├── services/       # API service functions
│   ├── api.js      # Axios instance with interceptors
├── App.jsx         # Main App component & Routing
├── main.jsx        # Entry point
```

## 🔐 Auth Integration

The frontend handles authentication tokens using `localStorage` (for simplicity in v2, consider `httpOnly` cookies for v3):

-   **Login**:
    1.  User authenticates (Guest or Google).
    2.  Backend returns `access` and `refresh` tokens.
    3.  Tokens are stored in `localStorage`.
-   **Requests**:
    -   Axios interceptor (in `api.js`) attaches `Authorization: Bearer <token>` to every request.
-   **Logout**:
    -   Clears `localStorage` and redirects to Login.
