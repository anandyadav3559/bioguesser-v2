
import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { GoogleOAuthProvider, GoogleLogin } from "@react-oauth/google";
import api from "../api";

// Replace with your actual Client ID (make sure to set this in .env or hardcode for dev if needed)
// For now I'm using a placeholder, USER MUST UPDATE ENV
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || "YOUR_GOOGLE_CLIENT_ID";

const LoginPage = () => {
    const navigate = useNavigate();

    useEffect(() => {
        // Redirect if already logged in
        if (localStorage.getItem("accessToken") || localStorage.getItem("guestToken")) {
            navigate("/home");
        }
    }, [navigate]);

    const handleGuestLogin = async () => {
        try {
            const response = await api.post("/auth/guest/");
            localStorage.setItem("guestToken", response.data.access);
            localStorage.setItem("userId", response.data.user_id);
            localStorage.setItem("identityType", "guest");
            navigate("/home");
        } catch (error) {
            console.error("Guest login failed:", error);
            alert("Guest login failed!");
        }
    };

    const handleGoogleSuccess = async (credentialResponse) => {
        try {
            const { credential } = credentialResponse;
            const response = await api.post("/auth/google/", {
                token: credential,
            });

            localStorage.setItem("accessToken", response.data.access);
            localStorage.setItem("userId", response.data.user_id);
            localStorage.setItem("identityType", "permanent");
            localStorage.setItem("userEmail", response.data.email);

            navigate("/home");
        } catch (error) {
            console.error("Google login failed:", error);
            alert("Google login failed!");
        }
    };

    return (
        <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100vh", gap: "20px" }}>
                <h1>Login to Geoguesser</h1>

                <button onClick={handleGuestLogin} style={{ padding: "10px 20px", fontSize: "16px", cursor: "pointer" }}>
                    Play as Guest
                </button>

                <div style={{ display: "flex", alignItems: "center", width: "100%", justifyContent: "center" }}>
                    <div style={{ borderBottom: "1px solid #ccc", width: "40%", margin: "0 10px" }}></div>
                    <span>OR</span>
                    <div style={{ borderBottom: "1px solid #ccc", width: "40%", margin: "0 10px" }}></div>
                </div>

                <GoogleLogin
                    onSuccess={handleGoogleSuccess}
                    onError={() => {
                        console.log('Login Failed');
                        alert("Google Login Failed");
                    }}
                />
            </div>
        </GoogleOAuthProvider>
    );
};

export default LoginPage;
