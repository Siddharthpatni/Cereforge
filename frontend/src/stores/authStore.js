import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useAuthStore = create(
    persist(
        (set, get) => ({
            // State
            accessToken: null,
            refreshToken: null,
            user: null,
            rank: null,
            isAuthenticated: false,

            // Actions
            setTokens: (accessToken, refreshToken) => {
                set({ accessToken, refreshToken, isAuthenticated: !!accessToken });
            },

            setUser: (user, rank = null) => {
                set((state) => ({
                    user: { ...state.user, ...user },
                    rank: rank ? rank : state.rank
                }));
            },

            updateXP: (addedXP) => {
                set((state) => {
                    if (!state.user) return state;
                    return {
                        user: { ...state.user, xp: state.user.xp + addedXP }
                    };
                });
            },

            setAuthData: (data) => {
                set({
                    accessToken: data.access_token,
                    refreshToken: data.refresh_token,
                    user: data.user,
                    rank: data.rank,
                    isAuthenticated: true,
                });
            },

            logout: () => {
                set({
                    accessToken: null,
                    refreshToken: null,
                    user: null,
                    rank: null,
                    isAuthenticated: false,
                });
            },
        }),
        {
            name: 'cereforge-auth-storage', // key in local storage
            partialize: (state) => ({
                accessToken: state.accessToken,
                refreshToken: state.refreshToken, // Optionally store user details, but fetching /me on load is safer
            }),
        }
    )
);
