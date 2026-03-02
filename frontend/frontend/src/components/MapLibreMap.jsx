import React, { useState, useEffect } from 'react';
import Map, { Marker } from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';

// Returns a colour on a green→yellow→orange→red gradient based on 0–1 intensity
function densityColor(t) {
    // Low  (t~0): cool teal   #00b4d8
    // Mid  (t~0.5): warm gold  #f4a261
    // High (t~1): hot red      #e63946
    const stops = [
        [0, [0, 180, 216]],   // teal
        [0.4, [244, 162, 97]],   // orange-gold
        [1, [230, 57, 70]],   // red
    ];
    let lo = stops[0], hi = stops[stops.length - 1];
    for (let i = 0; i < stops.length - 1; i++) {
        if (t >= stops[i][0] && t <= stops[i + 1][0]) {
            lo = stops[i]; hi = stops[i + 1]; break;
        }
    }
    const f = (t - lo[0]) / (hi[0] - lo[0]);
    const r = Math.round(lo[1][0] + f * (hi[1][0] - lo[1][0]));
    const g = Math.round(lo[1][1] + f * (hi[1][1] - lo[1][1]));
    const b = Math.round(lo[1][2] + f * (hi[1][2] - lo[1][2]));
    return `rgb(${r},${g},${b})`;
}

// SVG teardrop pin — size and colour driven by density
const DensityPin = ({ size, color, count, isHovered, onMouseEnter, onMouseLeave }) => (
    <div
        onMouseEnter={onMouseEnter}
        onMouseLeave={onMouseLeave}
        style={{ position: 'relative', cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center' }}
    >
        {/* Tooltip */}
        {isHovered && (
            <div style={{
                position: 'absolute',
                bottom: size + 6,
                left: '50%',
                transform: 'translateX(-50%)',
                backgroundColor: 'rgba(10,10,10,0.85)',
                color: '#fff',
                padding: '4px 10px',
                borderRadius: '8px',
                fontSize: '12px',
                whiteSpace: 'nowrap',
                pointerEvents: 'none',
                zIndex: 99,
                boxShadow: '0 2px 8px rgba(0,0,0,0.5)',
                backdropFilter: 'blur(4px)'
            }}>
                🐾 {count.toLocaleString()} sightings
            </div>
        )}
        {/* Pin SVG */}
        <svg
            width={size}
            height={size * 1.4}
            viewBox="0 0 40 56"
            style={{ filter: `drop-shadow(0 2px 4px rgba(0,0,0,0.4))`, transition: 'transform 0.15s', transform: isHovered ? 'scale(1.2)' : 'scale(1)' }}
        >
            {/* Outer circle */}
            <circle cx="20" cy="20" r="18" fill={color} opacity="0.25" />
            {/* Main teardrop body */}
            <path
                d="M20 2 C9 2 2 10 2 20 C2 32 20 54 20 54 C20 54 38 32 38 20 C38 10 31 2 20 2 Z"
                fill={color}
                stroke="white"
                strokeWidth="2"
            />
            {/* Inner highlight */}
            <circle cx="20" cy="20" r="8" fill="white" opacity="0.45" />
        </svg>
    </div>
);

const MapLibreMap = ({ onGuessSubmit, disabled, trueLocations, currentAnimalId }) => {
    const [markerPos, setMarkerPos] = useState(null);
    const [hoveredIdx, setHoveredIdx] = useState(null);

    useEffect(() => {
        setMarkerPos(null);
        setHoveredIdx(null);
    }, [currentAnimalId]);

    const handleClick = (e) => {
        if (disabled) return;
        setMarkerPos({ lat: e.lngLat.lat, lng: e.lngLat.lng });
    };

    const handleSubmit = () => {
        if (markerPos && !disabled) onGuessSubmit(markerPos.lat, markerPos.lng);
    };

    // Pre-compute density stats so we can normalise pin sizes and colours
    const counts = trueLocations ? trueLocations.map(l => l.count || 0) : [];
    const maxCount = counts.length ? Math.max(...counts) : 1;
    const minCount = counts.length ? Math.min(...counts) : 0;
    const countRange = maxCount - minCount || 1;

    const MIN_PIN = 16;
    const MAX_PIN = 40;

    // Sort locations largest-first so small pins aren't buried under big ones
    const sortedLocations = trueLocations
        ? [...trueLocations].sort((a, b) => (a.count || 0) - (b.count || 0))
        : [];

    return (
        <div style={{ width: '100%', height: '100%', position: 'relative' }}>
            <Map
                initialViewState={{ longitude: 0, latitude: 0, zoom: 1 }}
                mapStyle="https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json"
                onClick={handleClick}
                interactive={!disabled}
                cursor={disabled ? 'default' : 'crosshair'}
            >
                {/* User's guess — distinct white crosshair so it never looks like a density pin */}
                {markerPos && (
                    <Marker longitude={markerPos.lng} latitude={markerPos.lat} anchor="center">
                        <svg width="28" height="28" viewBox="0 0 28 28" style={{ filter: 'drop-shadow(0 1px 3px rgba(0,0,0,0.7))' }}>
                            <circle cx="14" cy="14" r="12" fill="rgba(231,57,70,0.15)" stroke="#e73946" strokeWidth="2" />
                            <line x1="14" y1="4" x2="14" y2="24" stroke="#e73946" strokeWidth="2.5" strokeLinecap="round" />
                            <line x1="4" y1="14" x2="24" y2="14" stroke="#e73946" strokeWidth="2.5" strokeLinecap="round" />
                            <circle cx="14" cy="14" r="3" fill="#e73946" />
                        </svg>
                    </Marker>
                )}

                {/* Density-weighted true location pins (shown after guess) */}
                {disabled && sortedLocations.map((loc, idx) => {
                    const t = ((loc.count || 0) - minCount) / countRange;       // 0–1
                    const size = Math.round(MIN_PIN + t * (MAX_PIN - MIN_PIN));  // 16–40 px
                    const color = densityColor(t);
                    return (
                        <Marker
                            key={idx}
                            longitude={loc.longitude}
                            latitude={loc.latitude}
                            anchor="bottom"
                        >
                            <DensityPin
                                size={size}
                                color={color}
                                count={loc.count || 0}
                                isHovered={hoveredIdx === idx}
                                onMouseEnter={() => setHoveredIdx(idx)}
                                onMouseLeave={() => setHoveredIdx(null)}
                            />
                        </Marker>
                    );
                })}
            </Map>

            {/* Submit Guess button */}
            {!disabled && (
                <div style={{ position: 'absolute', bottom: '20px', left: 0, right: 0, display: 'flex', justifyContent: 'center', zIndex: 10 }}>
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

