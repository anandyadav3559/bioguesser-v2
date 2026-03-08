import React from 'react';
import useIsMobile from '../hooks/useIsMobile';

const formatCharacteristics = (chars) => {
    if (!chars || chars.length === 0) return [];
    const char = chars[0];
    const sentences = [];

    // Helper to safely format strings
    const lower = (str) => typeof str === 'string' ? str.toLowerCase() : str;

    if (char.habitat) sentences.push(`This animal lives in ${lower(char.habitat)}.`);
    if (char.prey) sentences.push(`It preys on ${lower(char.prey)}.`);
    if (char.predators) sentences.push(`Its main predators are ${lower(char.predators)}.`);
    if (char.lifespan) sentences.push(`It has a typical lifespan of ${char.lifespan}.`);
    if (char.weight) sentences.push(`This animal weighs around ${char.weight}.`);
    if (char.length) sentences.push(`It can grow up to a length of ${char.length}.`);
    if (char.top_speed) sentences.push(`It can reach top speeds of ${char.top_speed}.`);
    if (char.color) sentences.push(`Its coloration is typically ${lower(char.color)}.`);
    if (char.skin_type) sentences.push(`It is covered in ${lower(char.skin_type)}.`);
    if (char.gestation_period) sentences.push(`The gestation period is about ${char.gestation_period}.`);
    if (char.average_litter_size) sentences.push(`The average litter size is ${char.average_litter_size}.`);
    if (char.age_of_sexual_maturity) sentences.push(`It reaches sexual maturity at ${char.age_of_sexual_maturity}.`);
    if (char.age_of_weaning) sentences.push(`The age of weaning is around ${char.age_of_weaning}.`);

    return sentences;
};

const AnimalCard = ({ currentAnimal }) => {
    const characteristicsList = formatCharacteristics(currentAnimal.characteristics);
    const isMobile = useIsMobile();

    return (
        <div style={{
            backgroundColor: 'white',
            padding: isMobile ? '10px 15px' : '20px',
            borderRadius: '20px',
            boxShadow: '0 10px 40px rgba(0,0,0,0.5)',
            width: '100%',
            height: '100%',
            overflowY: 'auto',
            boxSizing: 'border-box',
            textAlign: 'center',
            display: 'flex',
            flexDirection: 'column'
        }}>
            <h2 style={{ color: '#2c3e50', margin: '0 0 5px 0', fontSize: isMobile ? '1.2rem' : '1.5rem' }}>{currentAnimal.name}</h2>
            <p style={{ fontStyle: 'italic', color: '#7f8c8d', marginBottom: isMobile ? '10px' : '15px', fontSize: isMobile ? '0.9rem' : '1rem' }}>{currentAnimal.scientific_name}</p>

            {currentAnimal.image_url ? (
                <div style={{
                    width: '100%',
                    height: isMobile ? '140px' : '220px',
                    borderRadius: '12px',
                    overflow: 'hidden',
                    backgroundColor: '#f0f0f0',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                    marginBottom: isMobile ? '10px' : '15px'
                }}>
                    <img
                        src={currentAnimal.image_url}
                        alt={currentAnimal.name}
                        style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                    />
                </div>
            ) : (
                <div style={{
                    width: '100%',
                    height: isMobile ? '140px' : '220px',
                    borderRadius: '12px',
                    backgroundColor: '#ecf0f1',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#95a5a6',
                    fontSize: isMobile ? '1rem' : '1.2rem',
                    flexShrink: 0,
                    marginBottom: isMobile ? '10px' : '15px'
                }}>
                    No Image Available
                </div>
            )}

            {characteristicsList.length > 0 && (
                <div style={{
                    textAlign: 'left',
                    backgroundColor: '#f8f9fa',
                    padding: isMobile ? '10px' : '15px',
                    borderRadius: '12px',
                    marginTop: 'auto',
                    fontSize: isMobile ? '0.85rem' : '0.95rem',
                    color: '#34495e',
                    border: '1px solid #e0e0e0',
                    flexGrow: 1,
                    overflowY: 'auto' // Handle text overflow nicely internally if it's very long
                }}>
                    <h4 style={{ margin: '0 0 8px 0', color: '#2c3e50', fontSize: isMobile ? '0.95rem' : '1rem' }}>Characteristics:</h4>
                    <ul style={{ margin: 0, paddingLeft: '20px', lineHeight: isMobile ? '1.4' : '1.6' }}>
                        {characteristicsList.map((sentence, idx) => (
                            <li key={idx}>{sentence}</li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
};

export default AnimalCard;
