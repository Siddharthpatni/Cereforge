import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";
import {
    Shield,
    Activity,
    Users,
    AlertTriangle,
    Database,
    BarChart,
    Code
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import apiClient from "@/api/client";
import { cn } from "@/utils/cn";
import { formatDistanceToNow } from "date-fns";
import { useUIStore } from "@/stores/uiStore";

// --- Tab Components ---

function OverviewTab() {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        apiClient.get("/admin/stats")
            .then(res => setStats(res.data))
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <div className="p-8 text-center text-zinc-500 animate-pulse">Loading stats...</div>;
    if (!stats) return null;

    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card className="glass-panel">
                <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-zinc-400">Total Users</p>
                            <p className="text-3xl font-bold text-white mt-1">{stats.total_users}</p>
                        </div>
                        <div className="p-3 bg-primary/10 rounded-full text-primary">
                            <Users className="h-5 w-5" />
                        </div>
                    </div>
                </CardContent>
            </Card>
            <Card className="glass-panel">
                <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-zinc-400">Total Submissions</p>
                            <p className="text-3xl font-bold text-white mt-1">{stats.total_submissions}</p>
                        </div>
                        <div className="p-3 bg-success/10 rounded-full text-success">
                            <Code className="h-5 w-5" />
                        </div>
                    </div>
                </CardContent>
            </Card>
            <Card className="glass-panel">
                <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-zinc-400">Active Posts</p>
                            <p className="text-3xl font-bold text-white mt-1">{stats.total_active_posts}</p>
                        </div>
                        <div className="p-3 bg-secondary/10 rounded-full text-secondary">
                            <Activity className="h-5 w-5" />
                        </div>
                    </div>
                </CardContent>
            </Card>
            <Card className="glass-panel border border-danger/20">
                <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-zinc-400">AI Flagged</p>
                            <p className="text-3xl font-bold text-danger mt-1">{stats.total_flagged}</p>
                        </div>
                        <div className="p-3 bg-danger/10 rounded-full text-danger">
                            <AlertTriangle className="h-5 w-5" />
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}

function SubmissionsTab() {
    const [subs, setSubs] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        apiClient.get("/admin/submissions")
            .then(res => setSubs(res.data))
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <div className="p-8 text-center text-zinc-500 animate-pulse">Loading submissions...</div>;

    return (
        <Card className="glass-panel">
            <CardHeader>
                <CardTitle>Recent Submissions</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="divide-y divide-border/50">
                    {subs.map(sub => (
                        <div key={sub.id} className="py-4 flex items-center justify-between">
                            <div>
                                <p className="font-semibold text-white">{sub.task_title}</p>
                                <p className="text-sm text-zinc-400">by u/{sub.username} • {formatDistanceToNow(new Date(sub.submitted_at))} ago</p>
                            </div>
                            <div>
                                {sub.is_ai_flagged ? (
                                    <Badge variant="outline" className="text-danger border-danger/30 bg-danger/5">
                                        Flagged ({sub.ai_flag_score})
                                    </Badge>
                                ) : (
                                    <Badge variant="outline" className="text-success border-success/30 bg-success/5">
                                        Clean
                                    </Badge>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
}

function UsersTab() {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        apiClient.get("/admin/users")
            .then(res => setUsers(res.data))
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <div className="p-8 text-center text-zinc-500 animate-pulse">Loading users...</div>;

    return (
        <Card className="glass-panel overflow-hidden">
            <div className="overflow-x-auto">
                <table className="w-full text-sm text-left text-zinc-300">
                    <thead className="text-xs text-zinc-400 uppercase bg-zinc-900/50 border-b border-border">
                        <tr>
                            <th className="px-6 py-4">Username</th>
                            <th className="px-6 py-4">Email</th>
                            <th className="px-6 py-4">Rank</th>
                            <th className="px-6 py-4 text-right">XP</th>
                            <th className="px-6 py-4">Joined</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-border/50">
                        {users.map(u => (
                            <tr key={u.id} className="hover:bg-zinc-900/30">
                                <td className="px-6 py-4 font-medium text-white flex items-center gap-2">
                                    {u.username}
                                    {u.is_admin && <Badge className="text-[10px] bg-primary/20 text-primary border-0 px-1.5 py-0 h-4">ADMIN</Badge>}
                                </td>
                                <td className="px-6 py-4">{u.email}</td>
                                <td className="px-6 py-4">{u.rank}</td>
                                <td className="px-6 py-4 text-right font-mono text-primary">{u.xp.toLocaleString()}</td>
                                <td className="px-6 py-4">{new Date(u.created_at).toLocaleDateString()}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </Card>
    );
}

function FlaggedTab() {
    const [subs, setSubs] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        apiClient.get("/admin/ai-flagged")
            .then(res => setSubs(res.data))
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <div className="p-8 text-center text-zinc-500 animate-pulse">Loading flagged submissions...</div>;

    if (subs.length === 0) {
        return (
            <div className="p-12 text-center border-2 border-dashed border-zinc-800 rounded-xl bg-zinc-900/20">
                <Shield className="h-12 w-12 mx-auto mb-4 text-success opacity-50" />
                <h3 className="text-xl font-bold text-white mb-2">System Secure</h3>
                <p className="text-zinc-400">No suspicious activity detected.</p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {subs.map(sub => (
                <Card key={sub.id} className="border-danger/30 bg-danger/5">
                    <CardHeader className="pb-3 border-b border-danger/10">
                        <div className="flex items-start justify-between">
                            <div>
                                <CardTitle className="text-danger flex items-center gap-2 text-lg">
                                    <AlertTriangle className="h-5 w-5" /> AI Generation Suspected
                                </CardTitle>
                                <p className="text-sm text-zinc-400 mt-1">
                                    Task: <span className="text-white">{sub.task_title}</span> • User: <span className="text-white">u/{sub.username}</span>
                                </p>
                            </div>
                            <Badge variant="outline" className="border-danger/50 text-danger bg-danger/10 text-sm py-1">
                                Score: {sub.ai_flag_score}
                            </Badge>
                        </div>
                    </CardHeader>
                    <CardContent className="pt-4">
                        <div className="mb-4">
                            <span className="text-xs font-bold text-zinc-500 uppercase tracking-wider">Detection Reasons</span>
                            <p className="text-sm text-zinc-300 mt-1">{sub.ai_flag_reason}</p>
                        </div>
                        <div>
                            <span className="text-xs font-bold text-zinc-500 uppercase tracking-wider">Submission Excerpt</span>
                            <div className="mt-1 p-3 rounded bg-black/40 border border-zinc-800 text-sm font-mono text-zinc-400 max-h-48 overflow-y-auto w-full">
                                {sub.solution_text}
                            </div>
                        </div>
                    </CardContent>
                </Card>
            ))}
        </div>
    );
}

// --- Main Page ---

const TABS = [
    { id: "overview", label: "Overview", icon: BarChart },
    { id: "submissions", label: "Submissions", icon: Code },
    { id: "users", label: "Users", icon: Users },
    { id: "flagged", label: "AI Flagged", icon: AlertTriangle },
];

export function Admin() {
    const { user, isInitializing } = useAuthStore();
    const navigate = useNavigate();
    const { addToast } = useUIStore();
    const [activeTab, setActiveTab] = useState("overview");

    useEffect(() => {
        if (!isInitializing && (!user || !user.is_admin)) {
            addToast({
                title: "Access Denied",
                message: "You must be an admin to view this area.",
                type: "error"
            });
            navigate("/dashboard");
        }
    }, [user, isInitializing, navigate, addToast]);

    if (isInitializing || !user || !user.is_admin) return null;

    return (
        <div className="flex flex-col md:flex-row gap-6 max-w-6xl mx-auto pb-12">
            {/* Sidebar Navigation */}
            <div className="w-full md:w-64 shrink-0">
                <div className="sticky top-20 bg-card border border-border rounded-xl p-4 shadow-sm">
                    <div className="flex items-center gap-3 mb-6 px-2">
                        <div className="h-10 w-10 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center text-primary">
                            <Shield className="h-6 w-6" />
                        </div>
                        <div>
                            <h2 className="font-bold text-white leading-tight">Admin Portal</h2>
                            <p className="text-xs text-primary font-mono">System Control</p>
                        </div>
                    </div>

                    <nav className="space-y-1">
                        {TABS.map(tab => {
                            const isActive = activeTab === tab.id;
                            return (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id)}
                                    className={cn(
                                        "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors cursor-pointer",
                                        isActive
                                            ? "bg-primary text-white shadow-[0_0_15px_rgba(67,56,202,0.3)]"
                                            : "text-zinc-400 hover:text-white hover:bg-zinc-800/50"
                                    )}
                                >
                                    <tab.icon className="h-4 w-4" />
                                    {tab.label}
                                </button>
                            );
                        })}
                    </nav>
                </div>
            </div>

            {/* Main Content Area */}
            <div className="flex-1 min-w-0">
                <div className="mb-6">
                    <h1 className="text-3xl font-bold text-white tracking-tight">
                        {TABS.find(t => t.id === activeTab)?.label}
                    </h1>
                </div>

                {activeTab === "overview" && <OverviewTab />}
                {activeTab === "submissions" && <SubmissionsTab />}
                {activeTab === "users" && <UsersTab />}
                {activeTab === "flagged" && <FlaggedTab />}
            </div>
        </div>
    );
}
