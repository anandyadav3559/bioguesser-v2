import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import background from "../assets/background.png";
import GameMenu from '../components/GameMenu';
import GamePlay from '../components/GamePlay';
import UserProfile from '../components/UserProfile';

const HomePage = () => {
    const navigate = useNavigate();
    const [selectedTime, setSelectedTime] = useState('30s');
    const [gameStarted, setGameStarted] = useState(false);
    const [animalStack, setAnimalStack] = useState([]);
    const [currentAnimal, setCurrentAnimal] = useState(null);
    const [loading, setLoading] = useState(false);
    const [preloadingNext, setPreloadingNext] = useState(false);
    const [nextAnimal, setNextAnimal] = useState(null);

    const nextAnimalImageRef = useRef(new Image());

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

    const [roomCode, setRoomCode] = useState(null);

    // ── Preload animals as soon as the page mounts ──────────────────────────
    useEffect(() => {
        const fetchInitialAnimals = async () => {
            try {
                const response = await api.get('/animal/batch/?limit=10&ordering=random');
                const animals = response.data;
                if (animals && animals.length > 0) {
                    const stack = [...animals];
                    const first = stack.shift();
                    setAnimalStack(stack);
                    setCurrentAnimal(first);
                    // Preload first image
                    if (first.image_url) {
                        const img = new Image(); img.src = first.image_url;
                    }
                    // Preload second image
                    if (stack.length > 0) preloadNextAnimal(stack[0]);
                }
            } catch (err) {
                console.error('Failed to prefetch animals:', err);
            }
        };
        fetchInitialAnimals();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const startSinglePlayer = async () => {
        if (!currentAnimal) {
            alert('Animals are still loading, please wait a moment.');
            return;
        }
        setLoading(true);
        try {
            const roomRes = await api.post('/game/create/', {
                time_per_round: parseInt(selectedTime.replace('s', ''))
            });
            setRoomCode(roomRes.data.room_code);
            setGameStarted(true);
        } catch (error) {
            console.error('Failed to start game:', error);
            alert('Failed to start game. Please check your connection.');
        } finally {
            setLoading(false);
        }
    };

    const preloadNextAnimal = (animal) => {
        if (!animal || !animal.image_url) return;
        setPreloadingNext(true);
        nextAnimalImageRef.current.src = animal.image_url;
        nextAnimalImageRef.current.onload = () => {
            setNextAnimal(animal);
            setPreloadingNext(false);
        };
    };

    const handleNextAnimal = async () => {
        // Refill logic when we are about to run out
        if (animalStack.length <= 3) {
            try {
                // Fetch next batch of 10
                const response = await api.get('/animal/batch/?limit=10&ordering=random');
                const moreAnimals = response.data;
                if (moreAnimals && moreAnimals.length > 0) {
                    setAnimalStack(prev => {
                        // Prevent duplicates by checking IDs ideally, but appending is fine
                        return [...prev, ...moreAnimals];
                    });
                }
            } catch (err) {
                console.error("Failed to fetch more animals", err);
            }
        }

        setAnimalStack(prevStack => {
            const newStack = [...prevStack]; // Use latest state

            if (nextAnimal) {
                newStack.shift();
                setCurrentAnimal(nextAnimal);
                setNextAnimal(null);

                if (newStack.length > 0) {
                    preloadNextAnimal(newStack[0]);
                }
                return newStack;
            } else if (newStack.length > 0) {
                // Fallback if not preloaded yet
                const next = newStack.shift();
                setCurrentAnimal(next);
                if (newStack.length > 0) {
                    preloadNextAnimal(newStack[0]);
                }
                return newStack;
            } else {
                // Should only happen in severe network lag
                setGameStarted(false);
                return newStack;
            }
        });
    };

    return (
        <div style={{
            backgroundImage: `url(${background})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            backgroundAttachment: 'fixed',
            height: '100vh',
            width: '100vw',
            overflow: 'hidden',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '20px',
            boxSizing: 'border-box',
            position: 'relative',
            fontFamily: "'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
        }}>
            <div style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: 'rgba(0, 0, 0, 0.4)',
                zIndex: 1
            }}></div>

            {gameStarted ? (
                <GamePlay
                    selectedTime={selectedTime}
                    animalStack={animalStack}
                    currentAnimal={currentAnimal}
                    handleNextAnimal={handleNextAnimal}
                    preloadingNext={preloadingNext}
                    setGameStarted={setGameStarted}
                    roomCode={roomCode}
                    api={api}
                />
            ) : (
                <GameMenu
                    selectedTime={selectedTime}
                    setSelectedTime={setSelectedTime}
                    startSinglePlayer={startSinglePlayer}
                    loading={loading}
                    handleLogout={handleLogout}
                />
            )}
        </div>
    );
};

export default HomePage;
