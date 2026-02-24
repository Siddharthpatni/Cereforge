import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useAuthStore } from '@/stores/authStore';
import { useUIStore } from '@/stores/uiStore';
import apiClient from '@/api/client';
import { Sparkles, Terminal, Code, Cpu } from 'lucide-react';
import { cn } from '@/utils/cn';

const skillLevels = [
    { id: 'absolute_beginner', title: 'Absolute Beginner', desc: 'No coding experience', icon: Sparkles },
    { id: 'some_python', title: 'Some Python', desc: 'Basic scripting', icon: Terminal },
    { id: 'ml_familiar', title: 'ML Familiar', desc: 'Knows basics of ML', icon: Code },
    { id: 'advanced', title: 'Advanced', desc: 'AI Engineer / Researcher', icon: Cpu },
];

export function Auth() {
    const [isLogin, setIsLogin] = useState(true);
    const [loading, setLoading] = useState(false);

    // Forms
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [skillLevel, setSkillLevel] = useState('some_python');

    const { setAuthData } = useAuthStore();
    const { addToast } = useUIStore();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            if (isLogin) {
                const res = await apiClient.post('/auth/login', {
                    email_or_username: username, // API accepts either in this field
                    password,
                });
                setAuthData(res.data);
                addToast({ title: 'Welcome back!', message: `Logged in as ${res.data.user.username}`, type: 'success' });
            } else {
                const res = await apiClient.post('/auth/register', {
                    username,
                    email,
                    password,
                    skill_level: skillLevel,
                    background: "Standard signup",
                });
                setAuthData(res.data);
                addToast({
                    title: 'Account created!',
                    message: res.data.welcome_message || `Welcome to CereForge, ${username}!`,
                    type: 'success',
                    duration: 8000
                });
            }
        } catch (err) {
            const msg = err.response?.data?.detail || 'An error occurred. Please try again.';
            addToast({ title: 'Authentication Failed', message: msg, type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-background bg-grid-pattern relative flex items-center justify-center p-4">
            {/* Decorative ambient light */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-primary/20 rounded-full blur-[120px] pointer-events-none" />

            <Card className="w-full max-w-md relative z-10 glass-panel border-border/50 shadow-2xl">
                <CardHeader className="text-center space-y-2 pb-8">
                    <div className="mx-auto h-12 w-12 rounded-lg bg-primary flex items-center justify-center font-mono font-bold text-2xl text-white shadow-[0_0_20px_rgba(67,56,202,0.6)] mb-4">
                        NF
                    </div>
                    <CardTitle className="text-2xl text-white">
                        {isLogin ? 'Enter the Forge' : 'Begin Your Journey'}
                    </CardTitle>
                    <CardDescription>
                        {isLogin
                            ? 'Log in to continue building AI.'
                            : 'Create an account to start earning your rank.'}
                    </CardDescription>
                </CardHeader>

                <form onSubmit={handleSubmit}>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-zinc-300">
                                {isLogin ? 'Username or Email' : 'Username'}
                            </label>
                            <input
                                type="text"
                                required
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                className="w-full rounded-md bg-zinc-900/50 border border-zinc-800 p-2.5 text-white placeholder-zinc-500 transition-colors focus:border-primary focus:ring-1 focus:ring-primary"
                                placeholder={isLogin ? 'neo@matrix.com' : 'neo_1337'}
                            />
                        </div>

                        {!isLogin && (
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-zinc-300">Email (Optional)</label>
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="w-full rounded-md bg-zinc-900/50 border border-zinc-800 p-2.5 text-white placeholder-zinc-500 transition-colors focus:border-primary focus:ring-1 focus:ring-primary"
                                    placeholder="Optional for password recovery"
                                />
                            </div>
                        )}

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-zinc-300">Password</label>
                            <input
                                type="password"
                                required
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full rounded-md bg-zinc-900/50 border border-zinc-800 p-2.5 text-white placeholder-zinc-500 transition-colors focus:border-primary focus:ring-1 focus:ring-primary"
                                placeholder="••••••••"
                            />
                        </div>

                        {!isLogin && (
                            <div className="space-y-3 pt-2">
                                <label className="text-sm font-medium text-zinc-300">Current AI Skill Level</label>
                                <div className="grid grid-cols-2 gap-3">
                                    {skillLevels.map((level) => (
                                        <button
                                            key={level.id}
                                            type="button"
                                            onClick={() => setSkillLevel(level.id)}
                                            className={cn(
                                                "flex flex-col items-center gap-2 rounded-lg border p-3 text-center text-sm transition-all",
                                                skillLevel === level.id
                                                    ? "border-primary bg-primary/10 text-white"
                                                    : "border-zinc-800 bg-zinc-900/30 text-zinc-400 hover:border-zinc-700 hover:text-zinc-300"
                                            )}
                                        >
                                            <level.icon className={cn("h-5 w-5", skillLevel === level.id ? "text-primary" : "text-zinc-500")} />
                                            <div className="space-y-0.5">
                                                <div className="font-semibold leading-none">{level.title}</div>
                                                <div className="text-[10px] opacity-70">{level.desc}</div>
                                            </div>
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}
                    </CardContent>

                    <CardFooter className="flex-col gap-4">
                        <Button
                            type="submit"
                            fullWidth
                            size="lg"
                            isLoading={loading}
                            className="text-base font-bold shadow-[0_0_15px_rgba(67,56,202,0.3)] hover:shadow-[0_0_20px_rgba(67,56,202,0.5)]"
                        >
                            {isLogin ? 'Authenticate' : 'Forge Account'}
                        </Button>

                        <p className="text-sm text-zinc-400 text-center">
                            {isLogin ? "Don't have an account? " : "Already forged an account? "}
                            <button
                                type="button"
                                onClick={() => setIsLogin(!isLogin)}
                                className="text-primary hover:text-primary-hover hover:underline transition-colors focus:outline-none"
                            >
                                {isLogin ? 'Register now.' : 'Log in.'}
                            </button>
                        </p>
                    </CardFooter>
                </form>
            </Card>
        </div>
    );
}
