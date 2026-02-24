import React from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Navbar } from './Navbar';
import { ToastContainer } from '../ui/ToastContainer';
import { useAuthStore } from '@/stores/authStore';
import { CinematicRunner } from '../signature/CinematicRunner';

export function Layout() {
    const { isAuthenticated } = useAuthStore();

    if (!isAuthenticated) {
        return <Navigate to="/auth" replace />;
    }

    return (
        <div className="min-h-screen bg-background flex text-foreground pt-16">
            <Navbar />

            <Sidebar className="hidden md:flex w-64 flex-col fixed inset-y-0 pt-16 z-30" />

            <main className="flex-1 max-w-7xl mx-auto w-full md:pl-64 flex flex-col min-h-[calc(100vh-4rem)]">
                <div className="w-full flex-1 p-4 md:p-8">
                    <Outlet />
                </div>

                {/* Simple Footer */}
                <footer className="w-full border-t border-border py-6 text-center text-sm text-zinc-500">
                    <p>© {new Date().getFullYear()} CereForge. All rights reserved.</p>
                </footer>
            </main>

            <ToastContainer />
            <CinematicRunner />
        </div>
    );
}
