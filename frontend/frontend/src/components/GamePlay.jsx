import React, { useState, useEffect } from 'react';
import AnimalCard from './AnimalCard';
import MapLibreMap from './MapLibreMap';
import useIsMobile from '../hooks/useIsMobile';

const GamePlay = ({
    selectedTime,
    animalStack,
    currentAnimal,
    handleNextAnimal,
    preloadingNext,
    setGameStarted,
    roomCode,
    api
}) => {
    // Timer state
    const parseTime = (timeStr) => parseInt(timeStr.replace('s', ''), 10);
    const [timeLeft, setTimeLeft] = useState(parseTime(selectedTime));

    // Round state
    const [roundScore, setRoundScore] = useState(null);
    const [guessSubmitted, setGuessSubmitted] = useState(false);
    const [trueLocations, setTrueLocations] = useState([]);

    const isMobile = useIsMobile();

    // Auto-progress when round finishes
    useEffect(() => {
        // Reset state for new round
        setTimeLeft(parseTime(selectedTime));
        setRoundScore(null);
        setGuessSubmitted(false);
        setTrueLocations([]);

        // Start new round on backend
        if (roomCode && currentAnimal) {
            api.post('/game/start_round/', {
                room_code: roomCode,
                animal_id: currentAnimal.id
            }).catch(err => {
                console.error("Failed to start round", err);
            });
        }
    }, [currentAnimal, roomCode]);

    // Timer logic
    useEffect(() => {
        if (guessSubmitted || timeLeft <= 0) return;

        const timerId = setInterval(() => setTimeLeft(prev => prev - 1), 1000);
        return () => clearInterval(timerId);
    }, [timeLeft, guessSubmitted]);

    // Handle time out
    useEffect(() => {
        if (timeLeft <= 0 && !guessSubmitted) {
            handleGuessSubmit(200, 200); // Out-of-bounds coordinate signifies a timeout
        }
    }, [timeLeft, guessSubmitted]);

    const handleGuessSubmit = async (lat, lng) => {
        setGuessSubmitted(true);
        try {
            const res = await api.post('/game/guess/', {
                room_code: roomCode,
                latitude: lat,
                longitude: lng
            });
            setRoundScore(res.data.score_awarded);
            if (res.data.true_locations) {
                setTrueLocations(res.data.true_locations);
            }
        } catch (err) {
            console.error("Failed to submit guess", err);
            setRoundScore(0);
        }
    };

    return (
        <div style={{
            zIndex: 2,
            display: 'flex',
            flexDirection: isMobile ? 'column' : 'row',
            width: '100%',
            height: '100%',
            gap: isMobile ? '10px' : '20px',
            padding: isMobile ? '10px 0' : '0' // Slight padding adjustment for mobile overall
        }}>
            {/* LEFT/TOP COLUMN: Animal Card */}
            <div style={{
                width: isMobile ? '100%' : '400px',
                flexShrink: 0,
                height: isMobile ? '40%' : '100%',
                maxHeight: isMobile ? '350px' : 'none',
                minHeight: isMobile ? '200px' : 'auto'
            }}>
                {currentAnimal && <AnimalCard currentAnimal={currentAnimal} />}
            </div>

            {/* RIGHT/BOTTOM COLUMN: Map and Overlays */}
            <div style={{
                flex: 1,
                position: 'relative',
                height: isMobile ? 'auto' : '100%',
                minHeight: isMobile ? '40vh' : 'auto', // ensure it takes up enough screen space
                borderRadius: '20px',
                overflow: 'hidden',
                backgroundColor: '#bdc3c7',
                boxShadow: '0 10px 40px rgba(0,0,0,0.5)'
            }}>
                {currentAnimal && (
                    <MapLibreMap
                        onGuessSubmit={handleGuessSubmit}
                        disabled={guessSubmitted}
                        trueLocations={trueLocations}
                        currentAnimalId={currentAnimal.id}
                    />
                )}

                {/* Top-left: Timer while playing, Score after guess */}
                <div style={{
                    position: 'absolute',
                    top: '20px',
                    left: '20px',
                    backgroundColor: guessSubmitted ? 'rgba(46,204,113,0.85)' : 'rgba(0,0,0,0.7)',
                    padding: '10px 20px',
                    borderRadius: '30px',
                    color: 'white',
                    fontWeight: 'bold',
                    zIndex: 10,
                    transition: 'background-color 0.3s',
                    fontSize: '1rem'
                }}>
                    {guessSubmitted && roundScore !== null
                        ? <>🎯 Score: <span style={{ color: '#fff', fontSize: '1.2rem' }}>{Number(roundScore).toFixed(2)}</span></>
                        : <>Time Left: <span style={{ color: timeLeft <= 5 ? '#e74c3c' : '#f1c40f' }}>{timeLeft}s</span></>
                    }
                </div>

                {/* Top-right: Quit Game */}
                <div style={{ position: 'absolute', top: '20px', right: '20px', zIndex: 10 }}>
                    <button
                        onClick={() => setGameStarted(false)}
                        style={{
                            background: 'rgba(0,0,0,0.7)',
                            border: '1px solid white',
                            color: 'white',
                            padding: '10px 20px',
                            borderRadius: '30px',
                            cursor: 'pointer',
                            fontWeight: 'bold'
                        }}
                    >
                        Quit Game
                    </button>
                </div>

                {guessSubmitted && (
                    <div style={{
                        position: 'absolute',
                        bottom: '20px',
                        left: '0',
                        right: '0',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        zIndex: 10
                    }}>
                        <button
                            onClick={handleNextAnimal}
                            style={{
                                padding: '12px 30px',
                                fontSize: '1.1rem',
                                backgroundColor: '#3498db',
                                color: 'white',
                                border: 'none',
                                borderRadius: '50px',
                                cursor: 'pointer',
                                fontWeight: 'bold',
                                boxShadow: '0 4px 6px rgba(0,0,0,0.3)'
                            }}
                        >
                            Next Animal
                        </button>
                        {preloadingNext && <span style={{ marginTop: '5px', fontSize: '0.9rem', color: 'white', textShadow: '0 1px 3px rgba(0,0,0,0.8)' }}>Preloading next...</span>}
                    </div>
                )}
            </div>
        </div>
    );
};

export default GamePlay;
