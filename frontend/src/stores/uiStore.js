import { create } from 'zustand';

// Simple toast notification store
export const useUIStore = create((set) => ({
    // Toasts
    toasts: [],
    addToast: (toast) => {
        const id = Math.random().toString(36).substring(2, 9);
        set((state) => ({
            toasts: [...state.toasts, { id, duration: 5000, ...toast }]
        }));

        // Auto remove
        setTimeout(() => {
            set((state) => ({
                toasts: state.toasts.filter((t) => t.id !== id)
            }));
        }, toast.duration || 5000);
    },

    removeToast: (id) => {
        set((state) => ({
            toasts: state.toasts.filter((t) => t.id !== id)
        }));
    },

    // Badge Cinematic sequence queue
    cinematicQueue: [],
    isCinematicPlaying: false,

    queueCinematic: (cinematicData) => {
        set((state) => ({
            cinematicQueue: [...state.cinematicQueue, cinematicData]
        }));
    },

    setCinematicPlaying: (isPlaying) => {
        set({ isCinematicPlaying: isPlaying });
    },

    popCinematic: () => {
        set((state) => {
            const newQueue = [...state.cinematicQueue];
            newQueue.shift();
            return { cinematicQueue: newQueue };
        });
    }
}));
