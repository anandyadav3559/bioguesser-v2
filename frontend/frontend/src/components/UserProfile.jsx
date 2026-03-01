import React, { useState, useEffect } from 'react';
import api from '../api';

const UserProfile = ({ handleLogout, inlineMode = false }) => {
    const [userData, setUserData] = useState(null);
    const [isOpen, setIsOpen] = useState(false);
    const [isEditing, setIsEditing] = useState(false);
    const [newUsername, setNewUsername] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchUserData();
    }, []);

    const fetchUserData = async () => {
        try {
            const response = await api.get('/auth/me/');
            setUserData(response.data);
            setNewUsername(response.data.username);
        } catch (err) {
            console.error("Failed to fetch user data:", err);
            setError("Could not load profile.");
        }
    };

    const handleUpdateUsername = async (e) => {
        e.preventDefault();
        if (!newUsername.trim() || newUsername === userData.username) {
            setIsEditing(false);
            return;
        }

        setLoading(true);
        try {
            const response = await api.patch('/auth/me/', { username: newUsername });
            setUserData(prev => ({ ...prev, username: response.data.username }));
            setIsEditing(false);
            setError(null);
        } catch (err) {
            console.error("Failed to update username:", err);
            setError("Username update failed. It might be taken.");
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteAccount = async () => {
        if (!window.confirm("Are you sure you want to permanently delete your account and all game history? This cannot be undone.")) {
            return;
        }

        setLoading(true);
        try {
            await api.delete('/auth/me/');
            handleLogout(); // Clears frontend state and redirects
        } catch (err) {
            console.error("Failed to delete account:", err);
            setError("Could not delete account. Please try again later.");
            setLoading(false); // Only unset loading if it failed
        }
    };

    if (error && !userData) {
        return (
            <div style={{ padding: '20px', color: '#e74c3c', textAlign: 'center' }}>
                <p>{error}</p>
                <button onClick={handleLogout} style={{ padding: '10px 20px', backgroundColor: 'rgba(231,76,60,0.2)', color: '#e74c3c', border: '1px solid #e74c3c', borderRadius: '8px', cursor: 'pointer' }}>Log out</button>
            </div>
        );
    }

    if (!userData) {
        return <div style={{ padding: '20px', color: 'white', textAlign: 'center' }}>Loading profile data...</div>;
    }

    const { stats, history = [] } = userData;

    const ProfileContent = () => (
        <div style={{
            backgroundColor: inlineMode ? 'rgba(255, 255, 255, 0.05)' : 'rgba(20, 50, 40, 0.95)',
            padding: '40px',
            borderRadius: '16px',
            boxShadow: inlineMode ? 'none' : '0 8px 32px rgba(0,0,0,0.5)',
            backdropFilter: inlineMode ? 'none' : 'blur(10px)',
            border: '1px solid rgba(255,255,255,0.1)',
            display: 'flex',
            flexDirection: 'column',
            gap: '25px',
            width: inlineMode ? '100%' : '350px',
            boxSizing: 'border-box',
            maxHeight: '100%',
            overflowY: "auto"
        }}>
            {/* Header Section */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                <div style={{
                    width: '70px',
                    height: '70px',
                    borderRadius: '50%',
                    backgroundColor: '#3498db',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    color: '#fff',
                    textTransform: 'uppercase',
                    fontSize: '32px',
                    fontWeight: 'bold',
                    boxShadow: '0 4px 10px rgba(0,0,0,0.3)'
                }}>
                    {userData.username.charAt(0)}
                </div>
                <div>
                    <h3 style={{ color: 'white', margin: 0, fontSize: '1.6rem' }}>{userData.username}</h3>
                    <span style={{ color: '#bdc3c7', fontSize: '1rem' }}>
                        {userData.identity_type === 'guest' ? 'Guest Player' : 'Permanent Explorer'}
                    </span>
                </div>
            </div>

            {error && <p style={{ color: '#e74c3c', fontSize: '1rem', margin: 0 }}>{error}</p>}

            {/* Editing Details */}
            <div style={{ color: 'white', backgroundColor: 'rgba(0,0,0,0.3)', padding: '20px', borderRadius: '12px' }}>
                {userData.email && (
                    <p style={{ margin: '0 0 15px 0', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '10px' }}>
                        <strong style={{ color: '#95a5a6', fontSize: '0.9rem', display: 'block' }}>EMAIL</strong>
                        <span style={{ fontSize: '1.1rem' }}>{userData.email}</span>
                    </p>
                )}

                {isEditing ? (
                    <form onSubmit={handleUpdateUsername} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                        <strong style={{ color: '#95a5a6', fontSize: '0.9rem' }}>EDIT USERNAME</strong>
                        <input
                            type="text"
                            value={newUsername}
                            onChange={(e) => setNewUsername(e.target.value)}
                            style={{
                                padding: '12px',
                                borderRadius: '8px',
                                border: '1px solid #3498db',
                                backgroundColor: 'rgba(255,255,255,0.1)',
                                color: 'white',
                                outline: 'none',
                                fontSize: '1rem'
                            }}
                            disabled={loading}
                            autoFocus
                        />
                        <div style={{ display: 'flex', gap: '10px', marginTop: '5px' }}>
                            <button
                                type="submit"
                                disabled={loading}
                                style={{
                                    flex: 1, padding: '10px', backgroundColor: '#3498db', color: 'white',
                                    border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold'
                                }}
                            >
                                {loading ? '...' : 'Save'}
                            </button>
                            <button
                                type="button"
                                onClick={() => { setIsEditing(false); setNewUsername(userData.username); setError(null); }}
                                disabled={loading}
                                style={{
                                    flex: 1, padding: '10px', backgroundColor: 'rgba(255,255,255,0.1)', color: 'white',
                                    border: 'none', borderRadius: '8px', cursor: 'pointer'
                                }}
                            >
                                Cancel
                            </button>
                        </div>
                    </form>
                ) : (
                    <button
                        onClick={() => setIsEditing(true)}
                        style={{
                            background: 'none', border: '1px solid rgba(255,255,255,0.2)', color: 'white',
                            cursor: 'pointer', fontSize: '1rem', padding: '10px', borderRadius: '8px', width: '100%',
                            transition: 'all 0.2s'
                        }}
                        onMouseOver={(e) => e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.1)'}
                        onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                    >
                        Change Username
                    </button>
                )}
            </div>

            {/* Profile Stats */}
            {stats && (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px' }}>
                    <div style={{ backgroundColor: 'rgba(46, 204, 113, 0.2)', padding: '15px 10px', borderRadius: '12px', textAlign: 'center' }}>
                        <span style={{ color: '#bdc3c7', fontSize: '0.8rem', display: 'block' }}>GAMES</span>
                        <strong style={{ color: '#2ecc71', fontSize: '1.5rem' }}>{stats.games_played}</strong>
                    </div>
                    <div style={{ backgroundColor: 'rgba(52, 152, 219, 0.2)', padding: '15px 10px', borderRadius: '12px', textAlign: 'center' }}>
                        <span style={{ color: '#bdc3c7', fontSize: '0.8rem', display: 'block' }}>TOTAL SCORE</span>
                        <strong style={{ color: '#3498db', fontSize: '1.5rem' }}>{stats.total_score}</strong>
                    </div>
                    <div style={{ backgroundColor: 'rgba(155, 89, 182, 0.2)', padding: '15px 10px', borderRadius: '12px', textAlign: 'center' }}>
                        <span style={{ color: '#bdc3c7', fontSize: '0.8rem', display: 'block' }}>HIGH SCORE</span>
                        <strong style={{ color: '#9b59b6', fontSize: '1.5rem' }}>{stats.high_score}</strong>
                    </div>
                </div>
            )}

            {/* Game History List */}
            <div style={{ marginTop: '10px' }}>
                <h4 style={{ color: 'white', marginBottom: '15px', paddingBottom: '5px', borderBottom: '1px solid rgba(255,255,255,0.2)' }}>
                    Recent Games
                </h4>
                {history.length === 0 ? (
                    <p style={{ color: '#95a5a6', fontSize: '0.9rem', fontStyle: 'italic', textAlign: 'center' }}>
                        No games played yet. Get out there and explore!
                    </p>
                ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', maxHeight: '350px', overflowY: 'auto', paddingRight: '10px' }}>
                        {history.map((game, index) => (
                            <div key={index} style={{
                                backgroundColor: 'rgba(0,0,0,0.4)',
                                borderRadius: '12px',
                                padding: '15px',
                                borderLeft: '4px solid #3498db'
                            }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                                    <span style={{ color: '#bdc3c7', fontSize: '0.8rem' }}>
                                        {new Date(game.played_at).toLocaleDateString()}
                                    </span>
                                    <span style={{ color: '#f1c40f', fontWeight: 'bold' }}>
                                        Score: {game.total_score}
                                    </span>
                                </div>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                    {game.rounds && game.rounds.map((r, rIdx) => (
                                        <div key={rIdx} style={{
                                            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                                            backgroundColor: 'rgba(255,255,255,0.05)', padding: '8px', borderRadius: '6px'
                                        }}>
                                            <span style={{ color: 'white', fontSize: '0.9rem' }}>
                                                R{r.round_number}: {r.animal?.common_name || 'Unknown'}
                                            </span>
                                            <span style={{ color: '#2ecc71', fontSize: '0.9rem', fontWeight: 'bold' }}>
                                                +{r.score_awarded}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Logout and Delete Actions */}
            <div style={{ display: 'flex', gap: '15px', marginTop: 'auto', paddingTop: '20px' }}>
                <button
                    onClick={handleLogout}
                    disabled={loading}
                    style={{
                        flex: 1, padding: '15px', backgroundColor: 'transparent', color: 'white',
                        border: '1px solid rgba(255,255,255,0.3)', borderRadius: '12px', cursor: 'pointer',
                        transition: 'all 0.2s', fontWeight: 'bold'
                    }}
                    onMouseOver={(e) => { e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.1)' }}
                    onMouseOut={(e) => { e.currentTarget.style.backgroundColor = 'transparent' }}
                >
                    Log Out
                </button>
                <button
                    onClick={handleDeleteAccount}
                    disabled={loading}
                    style={{
                        flex: 1, padding: '15px', backgroundColor: 'rgba(231, 76, 60, 0.1)', color: '#e74c3c',
                        border: '1px solid rgba(231, 76, 60, 0.4)', borderRadius: '12px', cursor: 'pointer',
                        transition: 'all 0.2s', fontWeight: 'bold'
                    }}
                    onMouseOver={(e) => { e.currentTarget.style.backgroundColor = '#e74c3c'; e.currentTarget.style.color = 'white'; }}
                    onMouseOut={(e) => { e.currentTarget.style.backgroundColor = 'rgba(231, 76, 60, 0.1)'; e.currentTarget.style.color = '#e74c3c'; }}
                >
                    Delete Account
                </button>
            </div>
        </div>
    );

    if (inlineMode) {
        return <ProfileContent />;
    }

    return (
        <div style={{ position: 'absolute', top: '20px', left: '20px', zIndex: 10, fontFamily: "'Segoe UI', Roboto, Helvetica, Arial, sans-serif" }}>
            <div
                onClick={() => setIsOpen(!isOpen)}
                style={{
                    backgroundColor: 'rgba(20, 50, 40, 0.85)', padding: '8px 16px', borderRadius: '20px',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.3)', backdropFilter: 'blur(8px)', cursor: 'pointer',
                    display: 'flex', alignItems: 'center', gap: '10px', color: 'white', fontWeight: 'bold', border: '1px solid rgba(255,255,255,0.1)',
                }}
            >
                <div style={{ width: '32px', height: '32px', borderRadius: '50%', backgroundColor: '#2ecc71', display: 'flex', justifyContent: 'center', alignItems: 'center', color: '#fff', fontSize: '16px' }}>
                    {userData.username.charAt(0).toUpperCase()}
                </div>
                <span>{userData.username}</span>
            </div>
            {isOpen && (
                <div style={{ position: 'absolute', top: '50px', left: '0' }}>
                    <ProfileContent />
                </div>
            )}
        </div>
    );
};

export default UserProfile;
