import { Link } from "react-router-dom";
import { Home, BookOpen, Users, Trophy } from "lucide-react";

export function NotFound() {
    return (
        <div className="min-h-screen flex items-center justify-center p-8" style={{ backgroundColor: "#050508" }}>
            <div className="max-w-lg w-full text-center space-y-8">
                {/* 404 Display */}
                <div>
                    <div className="text-8xl font-black bg-gradient-to-r from-indigo-500 to-purple-500 bg-clip-text text-transparent mb-4">
                        404
                    </div>
                    <h1 className="text-2xl font-bold text-white mb-2">Page not found</h1>
                    <p className="text-zinc-400">
                        The page you&apos;re looking for doesn&apos;t exist or has been moved.
                    </p>
                </div>

                {/* Navigation Options */}
                <div className="grid grid-cols-2 gap-3 max-w-sm mx-auto">
                    <Link
                        to="/"
                        className="flex flex-col items-center gap-2 p-4 bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 hover:border-indigo-500/50 rounded-xl transition-all group"
                    >
                        <Home className="h-6 w-6 text-indigo-400 group-hover:scale-110 transition-transform" />
                        <span className="text-sm font-medium text-white">Dashboard</span>
                    </Link>
                    <Link
                        to="/tasks"
                        className="flex flex-col items-center gap-2 p-4 bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 hover:border-cyan-500/50 rounded-xl transition-all group"
                    >
                        <BookOpen className="h-6 w-6 text-cyan-400 group-hover:scale-110 transition-transform" />
                        <span className="text-sm font-medium text-white">Challenges</span>
                    </Link>
                    <Link
                        to="/community"
                        className="flex flex-col items-center gap-2 p-4 bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 hover:border-emerald-500/50 rounded-xl transition-all group"
                    >
                        <Users className="h-6 w-6 text-emerald-400 group-hover:scale-110 transition-transform" />
                        <span className="text-sm font-medium text-white">Community</span>
                    </Link>
                    <Link
                        to="/leaderboard"
                        className="flex flex-col items-center gap-2 p-4 bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 hover:border-amber-500/50 rounded-xl transition-all group"
                    >
                        <Trophy className="h-6 w-6 text-amber-400 group-hover:scale-110 transition-transform" />
                        <span className="text-sm font-medium text-white">Leaderboard</span>
                    </Link>
                </div>
            </div>
        </div>
    );
}

export default NotFound;
