import React, { useState, useEffect, useRef } from 'react';
import api from '../api';

const BioExplorer = () => {
    const [animals, setAnimals] = useState([]);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [loading, setLoading] = useState(true);
    const [preloadedData, setPreloadedData] = useState(null);

    const fetchPage = async (pageNumber) => {
        try {
            const res = await api.get(`/bioExplorer/animals/?page=${pageNumber}`);
            return res.data;
        } catch (error) {
            console.error('Failed to fetch animals:', error);
            return null;
        }
    };

    // Initial load
    useEffect(() => {
        const loadInitialData = async () => {
            setLoading(true);
            const data = await fetchPage(1);
            if (data) {
                setAnimals(data.results);
                setTotalPages(Math.ceil(data.count / 10));
                
                // Preload page 2 if exists
                if (data.next) {
                    const nextData = await fetchPage(2);
                    setPreloadedData(nextData);
                }
            }
            setLoading(false);
        };
        loadInitialData();
    }, []);

    const handleNext = async () => {
        if (page >= totalPages) return;
        
        const nextPage = page + 1;
        
        // If we have preloaded data for the next page, use it immediately
        if (preloadedData) {
            setAnimals(preloadedData.results);
            setPage(nextPage);
            setPreloadedData(null); // Clear it
            
            // Now preload the page after that
            if (preloadedData.next) {
                const nextNextData = await fetchPage(nextPage + 1);
                setPreloadedData(nextNextData);
            }
        } else {
            // Fallback if not preloaded
            setLoading(true);
            const data = await fetchPage(nextPage);
            if (data) {
                setAnimals(data.results);
                setPage(nextPage);
                if (data.next) {
                    const nextNextData = await fetchPage(nextPage + 1);
                    setPreloadedData(nextNextData);
                }
            }
            setLoading(false);
        }
    };

    const handleBack = async () => {
        if (page <= 1) return;
        const prevPage = page - 1;
        
        setLoading(true);
        const data = await fetchPage(prevPage);
        if (data) {
            setAnimals(data.results);
            setPage(prevPage);
            
            // Clear preloaded data and set it to what we are leaving 
            // OR just let it fetch page+1 in background again
            const nextData = await fetchPage(page); // We know this exists because we were just there
            setPreloadedData(nextData);
        }
        setLoading(false);
    };

    const styles = {
        container: {
            width: '100%',
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            color: 'white',
            padding: '20px',
            boxSizing: 'border-box',
            overflowY: 'auto',
        },
        header: {
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '20px',
        },
        title: {
            fontSize: '2rem',
            fontWeight: 'bold',
            color: '#2ecc71',
            margin: 0,
        },
        grid: {
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
            gap: '20px',
            flex: 1,
            overflowY: 'auto',
            paddingBottom: '20px',
        },
        card: {
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
            borderRadius: '16px',
            padding: '15px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            transition: 'transform 0.2s, box-shadow 0.2s',
            cursor: 'pointer',
            textAlign: 'center',
        },
        image: {
            width: '100%',
            height: '150px',
            objectFit: 'cover',
            borderRadius: '12px',
            marginBottom: '15px',
            backgroundColor: 'rgba(0,0,0,0.2)',
        },
        animalName: {
            fontSize: '1.2rem',
            fontWeight: 'bold',
            margin: '0 0 5px 0',
        },
        scientificName: {
            fontSize: '0.9rem',
            fontStyle: 'italic',
            color: '#aaa',
            margin: 0,
        },
        pagination: {
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            gap: '20px',
            marginTop: '20px',
            paddingTop: '20px',
            borderTop: '1px solid rgba(255, 255, 255, 0.1)',
        },
        button: (disabled) => ({
            padding: '10px 20px',
            borderRadius: '8px',
            border: 'none',
            backgroundColor: disabled ? 'rgba(255, 255, 255, 0.1)' : '#3498db',
            color: disabled ? 'rgba(255, 255, 255, 0.3)' : 'white',
            cursor: disabled ? 'not-allowed' : 'pointer',
            fontWeight: 'bold',
            transition: 'all 0.2s',
        }),
        pageInfo: {
            fontSize: '1.1rem',
            fontWeight: 'bold',
            color: '#ddd',
        }
    };

    if (loading && animals.length === 0) {
        return <div style={{...styles.container, justifyContent: 'center', alignItems: 'center'}}><h2>Loading Animals...</h2></div>;
    }

    return (
        <div style={styles.container}>
            <div style={styles.header}>
                <h2 style={styles.title}>Bio-Explorer</h2>
            </div>
            
            <div style={styles.grid}>
                {animals.map(animal => (
                    <div 
                        key={animal.id} 
                        style={styles.card}
                        onMouseOver={(e) => {
                            e.currentTarget.style.transform = 'translateY(-5px)';
                            e.currentTarget.style.boxShadow = '0 10px 20px rgba(0,0,0,0.3)';
                        }}
                        onMouseOut={(e) => {
                            e.currentTarget.style.transform = 'translateY(0)';
                            e.currentTarget.style.boxShadow = 'none';
                        }}
                    >
                        {animal.image_url ? (
                            <img src={animal.image_url} alt={animal.name} style={styles.image} loading="lazy" />
                        ) : (
                            <div style={{...styles.image, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>No Image</div>
                        )}
                        <h3 style={styles.animalName}>{animal.name}</h3>
                        <p style={styles.scientificName}>{animal.scientific_name}</p>
                    </div>
                ))}
            </div>

            <div style={styles.pagination}>
                <button 
                    style={styles.button(page === 1)} 
                    onClick={handleBack}
                    disabled={page === 1}
                >
                    Back
                </button>
                <span style={styles.pageInfo}>Page {page} of {totalPages || 1}</span>
                <button 
                    style={styles.button(page >= totalPages)} 
                    onClick={handleNext}
                    disabled={page >= totalPages}
                >
                    Next
                </button>
            </div>
        </div>
    );
};

export default BioExplorer;
