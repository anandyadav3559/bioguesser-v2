import React, { useState } from 'react';
import UserProfile from './UserProfile';
import BioExplorer from './BioExplorer';
import useIsMobile from '../hooks/useIsMobile';

const GameMenu = ({
    selectedTime,
    setSelectedTime,
    startSinglePlayer,
    loading,
    handleLogout,
    userData,
    setUserData
}) => {
    const [activeTab, setActiveTab] = useState('singleplayer');
    const isMobile = useIsMobile();

    const styles = {
        container: {
            display: 'flex',
            flexDirection: isMobile ? 'column' : 'row',
            width: '100%',
            maxWidth: '1200px',
            height: isMobile ? '90vh' : '80vh',
            backgroundColor: 'rgba(20, 30, 40, 0.85)',
            borderRadius: '24px',
            overflow: 'hidden',
            boxShadow: '0 10px 40px rgba(0,0,0,0.5)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255,255,255,0.1)'
        },
        sidebar: {
            width: isMobile ? '100%' : '300px',
            backgroundColor: 'rgba(0, 0, 0, 0.4)',
            padding: isMobile ? '20px 15px' : '40px 20px',
            display: 'flex',
            flexDirection: isMobile ? 'row' : 'column',
            gap: '15px',
            overflowX: isMobile ? 'auto' : 'visible',
            whiteSpace: isMobile ? 'nowrap' : 'normal',
            borderBottom: isMobile ? '1px solid rgba(255,255,255,0.1)' : 'none',
            flexShrink: 0
        },
        mainContent: {
            flex: 1,
            padding: isMobile ? '20px' : '40px',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'stretch',
            overflow: 'auto'
        },
        menuButton: (isActive) => ({
            background: isActive ? 'linear-gradient(90deg, #2ecc71, #27ae60)' : 'transparent',
            border: 'none',
            padding: '15px 20px',
            borderRadius: '12px',
            color: 'white',
            fontSize: isMobile ? '1rem' : '1.2rem',
            fontWeight: 'bold',
            textAlign: isMobile ? 'center' : 'left',
            cursor: 'pointer',
            transition: 'all 0.2s',
            opacity: isActive ? 1 : 0.7,
            display: 'flex',
            alignItems: 'center',
            justifyContent: isMobile ? 'center' : 'flex-start',
            gap: '10px',
            whiteSpace: 'nowrap'
        }),
        disabledButton: {
            background: 'transparent',
            border: 'none',
            padding: '15px 20px',
            borderRadius: '12px',
            color: 'white',
            fontSize: isMobile ? '1rem' : '1.2rem',
            fontWeight: 'bold',
            textAlign: isMobile ? 'center' : 'left',
            cursor: 'not-allowed',
            opacity: 0.3,
            display: 'flex',
            alignItems: 'center',
            justifyContent: isMobile ? 'center' : 'flex-start',
            gap: '10px',
            whiteSpace: 'nowrap'
        }
    };

    return (
        <div style={{ zIndex: 2, width: '100%', display: 'flex', justifyContent: 'center' }}>
            <div style={styles.container}>
                {/* Left Sidebar */}
                <div style={styles.sidebar}>
                    <h2 style={{
                        color: 'white',
                        fontSize: '2rem',
                        fontStyle: 'italic',
                        fontWeight: '900',
                        marginBottom: '40px',
                        paddingLeft: '10px',
                        letterSpacing: '2px'
                    }}>
                        BIOGUESSER
                    </h2>

                    <button
                        style={styles.menuButton(activeTab === 'singleplayer')}
                        onClick={() => setActiveTab('singleplayer')}
                    >
                        Singleplayer
                    </button>
                    <button style={styles.disabledButton} disabled>
                        Multiplayer <span style={{ fontSize: '0.8rem', backgroundColor: '#e74c3c', padding: '2px 6px', borderRadius: '4px' }}>Soon</span>
                    </button>
                    <button style={styles.disabledButton} disabled>
                        Custom Room <span style={{ fontSize: '0.8rem', backgroundColor: '#e74c3c', padding: '2px 6px', borderRadius: '4px' }}>Soon</span>
                    </button>
                    <button
                        style={styles.menuButton(activeTab === 'bioexplorer')}
                        onClick={() => setActiveTab('bioexplorer')}
                    >
                        Bio-Explorer
                    </button>
                    <button
                        style={styles.menuButton(activeTab === 'profile')}
                        onClick={() => setActiveTab('profile')}
                    >
                        Profile
                    </button>
                </div>

                {/* Right Content Area */}
                <div style={styles.mainContent}>
                    {activeTab === 'singleplayer' && (
                        <div style={{
                            backgroundColor: 'rgba(255, 255, 255, 0.05)',
                            padding: '40px',
                            borderRadius: '16px',
                            width: '400px',
                            textAlign: 'center',
                            border: '1px solid rgba(255,255,255,0.1)',
                            alignSelf: 'center',
                            margin: 'auto'
                        }}>
                            <h2 style={{ color: '#f1c40f', marginBottom: '30px', fontSize: '1.8rem' }}>Play Singleplayer</h2>

                            <div style={{ textAlign: 'left', marginBottom: '30px' }}>
                                <p style={{ color: 'white', marginBottom: '15px', fontWeight: 'bold' }}>Time Limit Per Round:</p>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                                    {['10s', '30s', '60s'].map(time => (
                                        <label key={time} style={{
                                            color: 'white',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            padding: '12px',
                                            borderRadius: '8px',
                                            cursor: 'pointer',
                                            backgroundColor: selectedTime === time ? 'rgba(46, 204, 113, 0.2)' : 'rgba(0,0,0,0.3)',
                                            border: `1px solid ${selectedTime === time ? '#2ecc71' : 'transparent'}`,
                                            transition: 'all 0.2s'
                                        }}>
                                            <input
                                                type="radio"
                                                name="time"
                                                value={time}
                                                checked={selectedTime === time}
                                                onChange={(e) => setSelectedTime(e.target.value)}
                                                style={{ display: 'none' }}
                                            />
                                            {time}
                                        </label>
                                    ))}
                                </div>
                            </div>

                            <button
                                onClick={startSinglePlayer}
                                disabled={loading}
                                style={{
                                    width: '100%',
                                    padding: '18px',
                                    fontSize: '1.4rem',
                                    fontWeight: 'bold',
                                    backgroundColor: '#2ecc71',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '50px',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s',
                                    boxShadow: '0 4px 15px rgba(46, 204, 113, 0.4)'
                                }}
                                onMouseOver={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
                                onMouseOut={(e) => e.currentTarget.style.transform = 'scale(1)'}
                            >
                                {loading ? 'Loading...' : 'PLAY'}
                            </button>
                        </div>
                    )}

                    {activeTab === 'profile' && (
                        <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column' }}>
                            {/* Repurposed UserProfile specifically engineered to visually sit here */}
                            <UserProfile handleLogout={handleLogout} inlineMode={true} userData={userData} setUserData={setUserData} />
                        </div>
                    )}

                    {activeTab === 'bioexplorer' && (
                        <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column', backgroundColor: 'rgba(0,0,0,0.2)', borderRadius: '16px' }}>
                            <BioExplorer />
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default GameMenu;
