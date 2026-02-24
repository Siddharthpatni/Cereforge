import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { X } from 'lucide-react';
import { useUIStore } from '@/stores/uiStore';

// 7 Phase Animation Sequence
// INITIATING -> SPINNING -> EXPANDING -> FLASH -> REVEAL_BADGE -> TEXT_FADE_IN -> IDLE

export function CinematicRunner() {
    const { isCinematicActive, currentCinematic, endCinematic } = useUIStore();
    const [phase, setPhase] = useState('INITIATING');
    const [particles, setParticles] = useState([]);

    useEffect(() => {
        if (isCinematicActive && currentCinematic) {
            setPhase('INITIATING');

            // Generate random particles
            const newParticles = Array.from({ length: 40 }).map((_, i) => ({
                id: i,
                angle: Math.random() * Math.PI * 2,
                speed: 2 + Math.random() * 5,
                size: Math.random() * 4 + 2,
                delay: Math.random() * 0.5
            }));
            setParticles(newParticles);

            // Sequence Timers
            const t1 = setTimeout(() => setPhase('SPINNING'), 400);
            const t2 = setTimeout(() => setPhase('EXPANDING'), 1400);
            const t3 = setTimeout(() => setPhase('FLASH'), 1800);
            const t4 = setTimeout(() => setPhase('REVEAL_BADGE'), 2000);
            const t5 = setTimeout(() => setPhase('TEXT_FADE_IN'), 2800);
            const t6 = setTimeout(() => setPhase('IDLE'), 3500);

            // Auto close after 8 seconds if user doesn't click
            const autoClose = setTimeout(() => endCinematic(), 8000);

            return () => {
                clearTimeout(t1); clearTimeout(t2); clearTimeout(t3);
                clearTimeout(t4); clearTimeout(t5); clearTimeout(t6);
                clearTimeout(autoClose);
            };
        }
    }, [isCinematicActive, currentCinematic, endCinematic]);

    if (!isCinematicActive || !currentCinematic) return null;

    const { name, description, xp_bonus, icon, track_color } = currentCinematic;
    const color = track_color || 'var(--primary)';

    return createPortal(
        <div className="fixed inset-0 z-[100] flex items-center justify-center overflow-hidden font-sans">
            {/* Backdrop */}
            <div
                className={`absolute inset-0 bg-black/90 transition-opacity duration-1000 ${phase === 'INITIATING' ? 'opacity-0' : 'opacity-100'}`}
                onClick={endCinematic}
            />

            {/* Scanline Effect */}
            <div className="absolute inset-0 pointer-events-none opacity-20" style={{ background: 'linear-gradient(to bottom, transparent 50%, rgba(0,0,0,0.5) 51%)', backgroundSize: '100% 4px' }} />

            <div className="relative z-10 flex flex-col items-center justify-center w-full max-w-2xl px-4">

                {/* Particle Burst Container */}
                {['REVEAL_BADGE', 'TEXT_FADE_IN', 'IDLE'].includes(phase) && (
                    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                        {particles.map(p => {
                            const tx = Math.cos(p.angle) * 300 * Math.random();
                            const ty = Math.sin(p.angle) * 300 * Math.random();
                            return (
                                <div
                                    key={p.id}
                                    className="absolute bg-white rounded-full opacity-0 animate-particle-burst"
                                    style={{
                                        width: p.size, height: p.size,
                                        backgroundColor: color,
                                        boxShadow: `0 0 10px ${color}`,
                                        '--tx': `${tx}px`, '--ty': `${ty}px`,
                                        animationDelay: `${p.delay}s`,
                                        animationDuration: '1.5s',
                                        animationFillMode: 'forwards'
                                    }}
                                />
                            )
                        })}
                    </div>
                )}

                {/* The Badge Graphic */}
                <div className="relative mb-12 flex justify-center">
                    {/* Outer Rotating Ring */}
                    <div
                        className={`absolute inset-[-40px] rounded-full border-2 border-dashed border-[color:var(--color)] transition-all ease-in-out duration-1000`}
                        style={{
                            '--color': color,
                            opacity: phase === 'INITIATING' ? 0 : 0.4,
                            transform: ['INITIATING', 'SPINNING'].includes(phase) ? 'scale(0.5) rotate(0deg)' : 'scale(1) rotate(180deg)'
                        }}
                    />

                    {/* Core Badge Shape */}
                    <div
                        className="w-40 h-40 m-auto flex items-center justify-center relative z-20 transition-all ease-out"
                        style={{
                            transitionDuration: phase === 'FLASH' ? '200ms' : '800ms',
                            opacity: phase === 'INITIATING' ? 0 : 1,
                            transform: phase === 'INITIATING' ? 'scale(0)' :
                                phase === 'SPINNING' ? 'scale(0.8) rotateY(720deg)' :
                                    phase === 'EXPANDING' ? 'scale(1.2)' :
                                        phase === 'FLASH' ? 'scale(1.5)' : 'scale(1)',
                            filter: phase === 'FLASH' ? `brightness(2) drop-shadow(0 0 50px ${color})` : `drop-shadow(0 0 20px ${color})`
                        }}
                    >
                        {/* Hexagon shape using clip path */}
                        <div
                            className="absolute inset-0 bg-zinc-900 border border-[color:var(--color)]"
                            style={{
                                '--color': color,
                                clipPath: 'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)',
                                background: `linear-gradient(135deg, rgba(24,24,27,1) 0%, rgba(24,24,27,0.8) 100%)`
                            }}
                        />
                        {/* Inner Glow */}
                        <div
                            className="absolute inset-2"
                            style={{
                                clipPath: 'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)',
                                background: `radial-gradient(circle at center, ${color}33 0%, transparent 70%)`
                            }}
                        />
                        <span className="text-6xl z-10 mt-1">{icon || '🏆'}</span>
                    </div>

                    {/* Flash Overlay */}
                    {phase === 'FLASH' && (
                        <div className="absolute inset-[-200px] bg-white rounded-full blur-[100px] z-[100] animate-ping opacity-80 pointer-events-none" />
                    )}
                </div>

                {/* Text Details */}
                <div
                    className="text-center space-y-4 transition-all duration-1000 ease-out transform pointer-events-none"
                    style={{
                        opacity: ['TEXT_FADE_IN', 'IDLE'].includes(phase) ? 1 : 0,
                        transform: ['TEXT_FADE_IN', 'IDLE'].includes(phase) ? 'translateY(0)' : 'translateY(20px)'
                    }}
                >
                    <div className="text-sm tracking-[0.3em] uppercase font-bold" style={{ color }}>Badge Unlocked</div>
                    <h2 className="text-4xl md:text-5xl font-bold text-white tracking-tight">{name}</h2>
                    <p className="text-lg text-zinc-400 max-w-lg mx-auto">{description}</p>

                    {xp_bonus > 0 && (
                        <div className="inline-block mt-6 px-6 py-2 rounded-full border bg-zinc-900 shadow-lg" style={{ borderColor: `${color}40`, boxShadow: `0 0 20px ${color}20` }}>
                            <span className="font-mono font-bold text-xl" style={{ color }}>+{xp_bonus} XP</span>
                            <span className="text-zinc-400 text-sm ml-2">Bonus Awarded</span>
                        </div>
                    )}
                </div>

                {/* Dismiss Button */}
                <button
                    onClick={endCinematic}
                    className="absolute top-6 right-6 p-2 rounded-full bg-white/10 text-white hover:bg-white/20 transition-colors z-50 focus:outline-none"
                    style={{
                        opacity: phase === 'IDLE' ? 1 : 0,
                        pointerEvents: phase === 'IDLE' ? 'auto' : 'none',
                        transition: 'opacity 1s ease'
                    }}
                >
                    <X className="h-6 w-6" />
                </button>

                {phase === 'IDLE' && (
                    <div className="absolute bottom-10 text-zinc-500 text-sm animate-pulse pointer-events-none">
                        Click anywhere to continue
                    </div>
                )}

            </div>
        </div>,
        document.body
    );
}
