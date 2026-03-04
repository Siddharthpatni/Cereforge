import React, { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";
import {
    Shield,
    Activity,
    Users,
    AlertTriangle,
    Database,
    BarChart,
    Code,
    Copy,
    Check,
    Edit2,
    Save,
    X,
    RefreshCw,
    Eye,
    EyeOff,
    ChevronUp,
    ChevronDown,
    Ban,
    UserCheck,
    Key,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import apiClient from "@/api/client";
import { cn } from "@/utils/cn";
import { formatDistanceToNow } from "date-fns";
import { useUIStore } from "@/stores/uiStore";

// ─── Overview Tab ───────────────────────────────────────────
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

    const cards = [
        { label: "Total Users", value: stats.total_users, icon: Users, color: "text-primary", bg: "bg-primary/10" },
        { label: "Total Submissions", value: stats.total_submissions, icon: Code, color: "text-success", bg: "bg-success/10" },
        { label: "Active Posts", value: stats.total_active_posts, icon: Activity, color: "text-secondary", bg: "bg-secondary/10" },
        { label: "AI Flagged", value: stats.total_flagged, icon: AlertTriangle, color: "text-danger", bg: "bg-danger/10", border: "border border-danger/20" },
    ];

    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {cards.map(c => (
                <Card key={c.label} className={cn("glass-panel", c.border)}>
                    <CardContent className="p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium text-zinc-400">{c.label}</p>
                                <p className={cn("text-3xl font-bold mt-1", c.color)}>{c.value}</p>
                            </div>
                            <div className={cn("p-3 rounded-full", c.bg, c.color)}>
                                <c.icon className="h-5 w-5" />
                            </div>
                        </div>
                    </CardContent>
                </Card>
            ))}
        </div>
    );
}

// ─── Submissions Tab ─────────────────────────────────────────
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

// ─── Copy Button Helper ──────────────────────────────────────
function CopyButton({ text }) {
    const [copied, setCopied] = useState(false);
    const handleCopy = (e) => {
        e.stopPropagation();
        navigator.clipboard.writeText(text).then(() => {
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        });
    };
    return (
        <button
            onClick={handleCopy}
            className="ml-1 p-0.5 text-zinc-600 hover:text-zinc-300 transition-colors"
            title="Copy"
        >
            {copied ? <Check className="h-3 w-3 text-success" /> : <Copy className="h-3 w-3" />}
        </button>
    );
}

// ─── Inline XP Editor ────────────────────────────────────────
function XPCell({ userId, username, initialXP, onUpdated, addToast }) {
    const [editing, setEditing] = useState(false);
    const [value, setValue] = useState(String(initialXP));
    const [saving, setSaving] = useState(false);

    const save = async () => {
        const xpNum = parseInt(value, 10);
        if (isNaN(xpNum) || xpNum < 0) {
            addToast({ title: "Invalid XP", message: "Must be a non-negative number", type: "error" });
            return;
        }
        setSaving(true);
        try {
            await apiClient.patch(`/admin/users/${userId}/xp`, { xp: xpNum });
            addToast({ title: "XP Updated", message: `${username} → ${xpNum.toLocaleString()} XP`, type: "success" });
            onUpdated(userId, xpNum);
            setEditing(false);
        } catch (err) {
            addToast({ title: "Failed", message: err.response?.data?.detail || "Could not update XP", type: "error" });
        } finally {
            setSaving(false);
        }
    };

    const cancel = () => {
        setValue(String(initialXP));
        setEditing(false);
    };

    if (editing) {
        return (
            <div className="flex items-center gap-1 justify-end" onClick={e => e.stopPropagation()}>
                <input
                    type="number"
                    min="0"
                    className="w-24 bg-zinc-900 border border-primary rounded px-2 py-1 text-sm font-mono text-primary text-right focus:outline-none focus:ring-1 focus:ring-primary"
                    value={value}
                    onChange={e => setValue(e.target.value)}
                    onKeyDown={e => { if (e.key === "Enter") save(); if (e.key === "Escape") cancel(); }}
                    autoFocus
                />
                <button onClick={save} disabled={saving} className="text-success hover:text-success/80 transition-colors p-1" title="Save">
                    {saving ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                </button>
                <button onClick={cancel} className="text-zinc-500 hover:text-danger transition-colors p-1" title="Cancel">
                    <X className="h-4 w-4" />
                </button>
            </div>
        );
    }

    return (
        <div className="flex items-center gap-2 justify-end group/xp cursor-pointer" onClick={() => setEditing(true)} title="Click to edit XP">
            <span className="font-mono text-primary font-bold">{Number(initialXP).toLocaleString()}</span>
            <Edit2 className="h-3.5 w-3.5 text-zinc-600 opacity-0 group-hover/xp:opacity-100 transition-opacity" />
        </div>
    );
}

// ─── Hash Cell ───────────────────────────────────────────────
function HashCell({ hash }) {
    const [visible, setVisible] = useState(false);
    if (!hash) return <span className="text-zinc-600 text-xs">—</span>;
    return (
        <div className="flex items-center gap-1 max-w-[160px]">
            {visible ? (
                <code className="text-[10px] text-primary font-mono break-all leading-tight">{hash}</code>
            ) : (
                <code className="text-[10px] text-zinc-600 font-mono truncate">{"•".repeat(12)} {hash.slice(-6)}</code>
            )}
            <button
                onClick={() => setVisible(!visible)}
                className="shrink-0 text-zinc-600 hover:text-zinc-300 transition-colors p-0.5"
                title={visible ? "Hide" : "Reveal"}
            >
                {visible ? <EyeOff className="h-3 w-3" /> : <Eye className="h-3 w-3" />}
            </button>
            <CopyButton text={hash} />
        </div>
    );
}

// ─── Moderation Actions ───────────────────────────────────────────────
function ModerationActions({ user, onUpdate, addToast }) {
    const [loading, setLoading] = useState(false);
    const [showPwReset, setShowPwReset] = useState(false);
    const [newPw, setNewPw] = useState("");

    if (user.is_admin) {
        return <span className="text-xs text-zinc-600 italic">Protected</span>;
    }

    const toggleBan = async () => {
        setLoading(true);
        try {
            const res = await apiClient.patch(`/admin/users/${user.id}/status`, {
                is_active: !user.is_active,
            });
            addToast({ title: "Success", message: res.data.message, type: "success" });
            onUpdate(user.id, { is_active: !user.is_active });
        } catch {
            addToast({ title: "Error", message: "Action failed", type: "error" });
        } finally {
            setLoading(false);
        }
    };

    const submitPwReset = async () => {
        if (newPw.length < 8) {
            addToast({ title: "Error", message: "Password must be at least 8 characters", type: "error" });
            return;
        }
        setLoading(true);
        try {
            await apiClient.patch(`/admin/users/${user.id}/password`, { new_password: newPw });
            addToast({ title: "Success", message: `Password reset for ${user.username}`, type: "success" });
            setShowPwReset(false);
            setNewPw("");
        } catch {
            addToast({ title: "Error", message: "Password reset failed", type: "error" });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex items-center gap-2">
            <button
                onClick={toggleBan}
                disabled={loading}
                title={user.is_active ? "Ban user" : "Unban user"}
                className={cn(
                    "p-1.5 rounded-lg border transition-colors text-xs",
                    user.is_active
                        ? "border-red-800/40 text-red-500 hover:bg-red-500/10"
                        : "border-green-700/40 text-green-500 hover:bg-green-500/10"
                )}
            >
                {user.is_active ? <Ban className="h-3.5 w-3.5" /> : <UserCheck className="h-3.5 w-3.5" />}
            </button>

            {showPwReset ? (
                <div className="flex items-center gap-1">
                    <input
                        type="password"
                        placeholder="New password"
                        className="text-xs bg-zinc-800 border border-zinc-700 rounded px-2 py-1 text-white w-28 outline-none focus:border-primary"
                        value={newPw}
                        onChange={e => setNewPw(e.target.value)}
                        onKeyDown={e => { if (e.key === 'Enter') submitPwReset(); if (e.key === 'Escape') setShowPwReset(false); }}
                        autoFocus
                    />
                    <button onClick={submitPwReset} disabled={loading} className="text-green-400 hover:text-green-300">
                        <Check className="h-3.5 w-3.5" />
                    </button>
                    <button onClick={() => setShowPwReset(false)} className="text-zinc-500 hover:text-zinc-300">
                        <X className="h-3.5 w-3.5" />
                    </button>
                </div>
            ) : (
                <button
                    onClick={() => setShowPwReset(true)}
                    title="Force reset password"
                    className="p-1.5 rounded-lg border border-zinc-700/40 text-zinc-500 hover:text-yellow-400 hover:border-yellow-600/40 hover:bg-yellow-500/5 transition-colors"
                >
                    <Key className="h-3.5 w-3.5" />
                </button>
            )}
        </div>
    );
}

// ─── Sort Icon (defined outside component to avoid re-creation on render) ──────
function SortIcon({ col, sortKey, sortDir }) {
    if (sortKey !== col) return <ChevronUp className="h-3 w-3 text-zinc-600 inline ml-1" />;
    return sortDir === "asc"
        ? <ChevronUp className="h-3 w-3 text-primary inline ml-1" />
        : <ChevronDown className="h-3 w-3 text-primary inline ml-1" />;
}

// ─── Users Tab ───────────────────────────────────────────────
function UsersTab() {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [sortKey, setSortKey] = useState("created_at");
    const [sortDir, setSortDir] = useState("desc");
    const { addToast } = useUIStore();

    const handleUserUpdate = useCallback((userId, patch) => {
        setUsers(prev => prev.map(u => u.id === userId ? { ...u, ...patch } : u));
    }, []);

    const fetchUsers = useCallback(() => {
        setLoading(true);
        apiClient.get("/admin/users")
            .then(res => setUsers(res.data))
            .catch(() => addToast({ title: "Error", message: "Failed to load users", type: "error" }))
            .finally(() => setLoading(false));
    }, [addToast]);

    useEffect(() => {
        fetchUsers();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);  // Run once on mount; fetchUsers is stable via useCallback

    const handleXPUpdated = (userId, newXP) => {
        setUsers(prev => prev.map(u => u.id === userId ? { ...u, xp: newXP } : u));
    };

    const toggleSort = (key) => {
        if (sortKey === key) {
            setSortDir(d => d === "asc" ? "desc" : "asc");
        } else {
            setSortKey(key);
            setSortDir("desc");
        }
    };

    const sorted = [...users].sort((a, b) => {
        let aVal = a[sortKey];
        let bVal = b[sortKey];
        if (typeof aVal === "string") aVal = aVal.toLowerCase();
        if (typeof bVal === "string") bVal = bVal.toLowerCase();
        if (aVal < bVal) return sortDir === "asc" ? -1 : 1;
        if (aVal > bVal) return sortDir === "asc" ? 1 : -1;
        return 0;
    });

    const thClass = "px-4 py-3 text-left cursor-pointer select-none hover:text-zinc-200 transition-colors";

    if (loading) return <div className="p-8 text-center text-zinc-500 animate-pulse">Loading users...</div>;

    return (
        <div className="space-y-3">
            <div className="flex items-center justify-between">
                <p className="text-sm text-zinc-400">{users.length} users total</p>
                <button onClick={fetchUsers} className="flex items-center gap-1.5 text-xs text-zinc-400 hover:text-white border border-border rounded-lg px-3 py-1.5 hover:border-zinc-600 transition-colors">
                    <RefreshCw className="h-3.5 w-3.5" /> Refresh
                </button>
            </div>

            <Card className="glass-panel overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left text-zinc-300">
                        <thead className="text-xs text-zinc-400 uppercase bg-zinc-900/70 border-b border-border">
                            <tr>
                                <th className={thClass} onClick={() => toggleSort("username")}>
                                    Username <SortIcon col="username" sortKey={sortKey} sortDir={sortDir} />
                                </th>
                                <th className={thClass} onClick={() => toggleSort("email")}>
                                    Email <SortIcon col="email" sortKey={sortKey} sortDir={sortDir} />
                                </th>
                                <th className={thClass + " text-right"} onClick={() => toggleSort("xp")}>
                                    XP <SortIcon col="xp" sortKey={sortKey} sortDir={sortDir} />
                                </th>
                                <th className={thClass} onClick={() => toggleSort("rank")}>
                                    Rank <SortIcon col="rank" sortKey={sortKey} sortDir={sortDir} />
                                </th>
                                <th className="px-3 py-3 text-left text-xs">Hash</th>
                                <th className="px-3 py-3 text-left text-xs">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-border/30">
                            {sorted.map(u => (
                                <tr key={u.id} className={cn("hover:bg-zinc-900/40 transition-colors", !u.is_active && "opacity-60")}>
                                    {/* Username + ID subtitle */}
                                    <td className="px-4 py-3">
                                        <div className="flex flex-col gap-0.5">
                                            <div className="flex items-center gap-1.5">
                                                {u.is_active === false && (
                                                    <span className="text-[9px] font-bold text-red-400 bg-red-500/10 px-1.5 py-0.5 rounded-full">BANNED</span>
                                                )}
                                                <span className="font-medium text-white">{u.username}</span>
                                                {u.is_admin && (
                                                    <Badge className="text-[9px] bg-primary/20 text-primary border-0 px-1.5 py-0 h-4 leading-none">ADMIN</Badge>
                                                )}
                                            </div>
                                            <div className="flex items-center gap-1">
                                                <code className="text-[9px] text-zinc-600 font-mono">{u.id.slice(0, 8)}...</code>
                                                <CopyButton text={u.id} />
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-4 py-3 text-zinc-400 text-xs">{u.email}</td>
                                    <td className="px-4 py-3 text-right">
                                        <XPCell
                                            userId={u.id}
                                            username={u.username}
                                            initialXP={u.xp}
                                            onUpdated={handleXPUpdated}
                                            addToast={addToast}
                                        />
                                    </td>
                                    <td className="px-4 py-3">
                                        <span className="text-xs text-zinc-400">{u.rank}</span>
                                    </td>
                                    <td className="px-3 py-3">
                                        <HashCell hash={u.password_hash} />
                                    </td>
                                    <td className="px-3 py-3">
                                        <ModerationActions user={u} onUpdate={handleUserUpdate} addToast={addToast} />
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </Card>
        </div>
    );
}

// ─── AI Flagged Tab ──────────────────────────────────────────
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

// ─── Main Admin Page ─────────────────────────────────────────
const TABS = [
    { id: "overview", label: "Overview", icon: BarChart },
    { id: "users", label: "Users", icon: Users },
    { id: "submissions", label: "Submissions", icon: Code },
    { id: "flagged", label: "AI Flagged", icon: AlertTriangle },
];

export function Admin() {
    const { user, isInitializing } = useAuthStore();
    const navigate = useNavigate();
    const { addToast } = useUIStore();
    const [activeTab, setActiveTab] = useState("overview");

    useEffect(() => {
        if (!isInitializing && (!user || !user.is_admin)) {
            addToast({ title: "Access Denied", message: "Admin only.", type: "error" });
            navigate("/dashboard");
        }
    }, [user, isInitializing, navigate, addToast]);

    if (isInitializing || !user || !user.is_admin) return null;

    return (
        <div className="flex flex-col md:flex-row gap-6 max-w-full mx-auto pb-12">
            {/* Sidebar Navigation */}
            <div className="w-full md:w-56 shrink-0">
                <div className="sticky top-20 bg-card border border-border rounded-xl p-4 shadow-sm">
                    <div className="flex items-center gap-3 mb-6 px-2">
                        <div className="h-9 w-9 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center text-primary">
                            <Shield className="h-5 w-5" />
                        </div>
                        <div>
                            <h2 className="font-bold text-white leading-tight text-sm">Admin Portal</h2>
                            <p className="text-[10px] text-primary font-mono">Logged in as {user.username}</p>
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

            {/* Content */}
            <div className="flex-1 min-w-0">
                <div className="mb-6">
                    <h1 className="text-2xl font-bold text-white tracking-tight">
                        {TABS.find(t => t.id === activeTab)?.label}
                    </h1>
                    <p className="text-sm text-zinc-500 mt-1">
                        {activeTab === "users" && "Click XP values to edit inline. Hover hash to reveal."}
                        {activeTab === "overview" && "Real-time platform statistics."}
                        {activeTab === "submissions" && "All user submissions, newest first."}
                        {activeTab === "flagged" && "Submissions flagged by the AI detector."}
                    </p>
                </div>

                {activeTab === "overview" && <OverviewTab />}
                {activeTab === "users" && <UsersTab />}
                {activeTab === "submissions" && <SubmissionsTab />}
                {activeTab === "flagged" && <FlaggedTab />}
            </div>
        </div>
    );
}
