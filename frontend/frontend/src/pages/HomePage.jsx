
import React from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

const HomePage = () => {
    const navigate = useNavigate();

    const handleLogout = async () => {
        try {
            await api.post('/auth/logout/');
        } catch (error) {
            console.error("Logout failed:", error);
        } finally {
            localStorage.clear();
            navigate('/');
        }
    };

    return (
        <div style={{ padding: '20px', textAlign: 'center' }}>
            <h1>geoguesser</h1>
            <button onClick={handleLogout} style={{ marginTop: '20px' }}>Logout</button>
        </div>
    );
};

export default HomePage;
