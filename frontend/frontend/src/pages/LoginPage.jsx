
import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { GoogleOAuthProvider, GoogleLogin } from "@react-oauth/google";
import api from "../api";
import background from "../assets/background.png";
import logo from "../assets/logo.png";

// Replace with your actual Client ID
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
            <div style={{
                backgroundImage: `url(${background})`,
                backgroundSize: 'cover',
                backgroundPosition: 'center',
                minHeight: '100vh',
                width: '100vw',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexDirection: 'column',
                position: 'relative',
                fontFamily: "'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
                padding: '0px' // Reduced padding to push content up
            }}>
                {/* Overlay for better text readability */}
                <div style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundColor: 'rgba(0, 0, 0, 0.4)', // Slightly darker overlay for contrast
                    zIndex: 1
                }}></div>

                <div style={{
                    zIndex: 2,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: '10px',
                    width: '100%',
                    maxWidth: '800px',
                    padding: '20px',
                    textAlign: 'center'
                }}>

                    {/* Logo Section */}
                    {/* Resized larger and drop shadow for depth */}
                    <img
                        src={logo}
                        alt="Bio-Geoguesser Logo"
                        style={{
                            width: '600px',
                            marginBottom: '0px',
                            filter: 'drop-shadow(0 4px 12px rgba(0,0,0,0.8))'
                        }}
                    />

                    {/* Hero Text Section */}
                    <div style={{ marginBottom: '20px' }}>
                        <h1 style={{
                            color: 'white',
                            margin: '0',
                            fontSize: '3.5rem',
                            textTransform: 'uppercase',
                            fontStyle: 'italic',
                            fontWeight: '900',
                            lineHeight: '1.1',
                            textShadow: '3px 3px 0px rgba(0,0,0,0.5), 0px 4px 15px rgba(0,0,0,0.8)'
                        }}>
                            How well do you know the wild?
                        </h1>

                        <p style={{
                            color: 'rgba(255, 255, 255, 0.95)',
                            fontSize: '1.1rem',
                            fontWeight: '600',
                            textShadow: '0 2px 4px rgba(0,0,0,0.8)',
                            lineHeight: '1.5',
                            maxWidth: '700px',
                            margin: '15px auto 0'
                        }}>
                            Every round shows you an animal — your mission is to guess its habitat.
                            <br />
                            <span style={{
                                color: '#f1c40f', // Vibrant yellow/gold
                                fontWeight: '800',
                                display: 'block',
                                marginTop: '5px',
                                textShadow: '0 2px 4px rgba(0,0,0,0.8)'
                            }}>
                                Play live. Learn fast. Climb the leaderboard.
                            </span>
                        </p>
                    </div>

                    {/* Login Card */}
                    <div style={{
                        backgroundColor: 'rgba(20, 50, 40, 0.85)', // Darker jungle green card
                        padding: '30px 40px',
                        borderRadius: '16px',
                        boxShadow: '0 10px 40px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(255, 255, 255, 0.15)', // Better shadow + subtle border
                        backdropFilter: 'blur(10px)',
                        webkitBackdropFilter: 'blur(10px)',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        gap: '15px',
                        width: '360px'
                    }}>
                        <h3 style={{
                            color: '#f1c40f', // Matching yellow gold
                            margin: '0 0 10px 0',
                            fontSize: '1.4rem',
                            fontStyle: 'italic',
                            fontWeight: '800',
                            letterSpacing: '0.5px'
                        }}>
                            Sign up to play
                        </h3>

                        <GoogleLogin
                            onSuccess={handleGoogleSuccess}
                            onError={() => {
                                console.log('Login Failed');
                                alert("Google Login Failed");
                            }}
                            theme="filled_black"
                            shape="pill"
                            size="large"
                            width="280"
                        />

                        {/* Custom Separator */}
                        <div style={{
                            display: "flex",
                            alignItems: "center",
                            width: "100%",
                            justifyContent: "center",
                            color: "rgba(255,255,255,0.4)",
                            fontSize: "0.85rem",
                            fontWeight: "600",
                            marginTop: "5px",
                            marginBottom: "5px"
                        }}>
                            <div style={{ height: "1px", backgroundColor: "rgba(255,255,255,0.2)", flex: 1 }}></div>
                            <span style={{ padding: "0 10px" }}>OR</span>
                            <div style={{ height: "1px", backgroundColor: "rgba(255,255,255,0.2)", flex: 1 }}></div>
                        </div>

                        <button
                            onClick={handleGuestLogin}
                            style={{
                                width: '100%',
                                padding: "12px 20px",
                                fontSize: "1rem",
                                cursor: "pointer",
                                backgroundColor: '#1e8449', // Stronger green button
                                color: 'white',
                                border: 'none',
                                borderRadius: '50px', // Full pill shape
                                fontWeight: '700',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                gap: '10px',
                                boxShadow: '0 4px 10px rgba(30, 132, 73, 0.3)',
                                transition: 'transform 0.2s, background-color 0.2s',
                                fontFamily: 'inherit'
                            }}
                            onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
                            onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                        >
                            Play as Guest
                        </button>

                        <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.5)', textAlign: 'center', marginTop: '10px', lineHeight: '1.4' }}>
                            By creating an account, you agree to our <br />
                            <a href="#" style={{ color: '#2ecc71', textDecoration: 'none' }}>Terms of Service</a> & <a href="#" style={{ color: '#2ecc71', textDecoration: 'none' }}>Privacy Policy</a>.
                        </div>
                    </div>
                </div>
            </div>
        </GoogleOAuthProvider>
    );
};

export default LoginPage;
