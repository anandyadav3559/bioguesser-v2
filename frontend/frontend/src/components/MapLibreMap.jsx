import React, { useState, useEffect } from 'react';
import Map, { Marker } from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';

const MapLibreMap = ({ onGuessSubmit, disabled, trueLocations, currentAnimalId }) => {
    const [markerPos, setMarkerPos] = useState(null);

    // Reset marker when the round/animal changes
    useEffect(() => {
        setMarkerPos(null);
    }, [currentAnimalId]);

    const handleClick = (e) => {
        if (disabled) return;
        const lat = e.lngLat.lat;
        const lng = e.lngLat.lng;
        setMarkerPos({ lat, lng });
    };

    const handleSubmit = () => {
        if (markerPos && !disabled) {
            onGuessSubmit(markerPos.lat, markerPos.lng);
        }
    };

    return (
        <div style={{ width: '100%', height: '100%', position: 'relative' }}>
            <Map
                initialViewState={{
                    longitude: 0,
                    latitude: 0,
                    zoom: 1
                }}
                mapStyle="https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json"
                onClick={handleClick}
                interactive={!disabled}
                cursor={disabled ? 'default' : 'crosshair'}
            >
                {/* User's Guess Marker */}
                {markerPos && (
                    <Marker longitude={markerPos.lng} latitude={markerPos.lat} color="red" />
                )}

                {/* Actual True Locations Rendered after Guess Completion */}
                {disabled && trueLocations && trueLocations.map((loc, idx) => (
                    <Marker
                        key={idx}
                        longitude={loc.longitude}
                        latitude={loc.latitude}
                        color="blue"
                    />
                ))}
            </Map>
            {!disabled && (
                <div style={{ position: 'absolute', bottom: '20px', left: '0', right: '0', display: 'flex', justifyContent: 'center', zIndex: 10 }}>
                    <button
                        onClick={handleSubmit}
                        disabled={!markerPos}
                        style={{
                            padding: '12px 30px',
                            fontSize: '1.1rem',
                            backgroundColor: !markerPos ? '#95a5a6' : '#2ecc71',
                            color: 'white',
                            border: 'none',
                            borderRadius: '50px',
                            cursor: !markerPos ? 'not-allowed' : 'pointer',
                            fontWeight: 'bold',
                            boxShadow: '0 4px 6px rgba(0,0,0,0.3)'
                        }}
                    >
                        Submit Guess
                    </button>
                </div>
            )}
        </div>
    );
};

export default MapLibreMap;
