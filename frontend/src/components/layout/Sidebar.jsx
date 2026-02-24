import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, BookOpen, MessageSquare, Trophy, Map, User } from 'lucide-react';
import { cn } from '@/utils/cn';

const navigation = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Tasks', href: '/tasks', icon: BookOpen },
    { name: 'Community', href: '/community', icon: MessageSquare },
    { name: 'Leaderboard', href: '/leaderboard', icon: Trophy },
    { name: 'Paths', href: '/paths', icon: Map },
    { name: 'Profile', href: '/profile', icon: User },
];

export function Sidebar({ className }) {
    const location = useLocation();

    return (
        <div className={cn("hidden md:flex flex-col border-r border-border bg-sidebar", className)}>
            <div className="flex flex-1 flex-col gap-2 p-4">
                {navigation.map((item) => {
                    const isActive = location.pathname === item.href ||
                        (item.href !== '/' && location.pathname.startsWith(item.href));
                    return (
                        <Link
                            key={item.name}
                            to={item.href}
                            className={cn(
                                "group flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                                isActive
                                    ? "bg-secondary text-primary hover:bg-secondary"
                                    : "text-zinc-400 hover:bg-secondary-hover hover:text-white"
                            )}
                        >
                            <item.icon
                                className={cn(
                                    "h-5 w-5 shrink-0 transition-colors",
                                    isActive ? "text-primary" : "text-zinc-500 group-hover:text-white"
                                )}
                                aria-hidden="true"
                            />
                            {item.name}
                        </Link>
                    );
                })}
            </div>

            {/* Small mini-widget could go here at the bottom of sidebar */}
            <div className="p-4 border-t border-border/50 text-xs text-zinc-500">
                <p>NeuralForge v1.0.0</p>
            </div>
        </div>
    );
}
