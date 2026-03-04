import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
    Card,
    CardHeader,
    CardTitle,
    CardDescription,
    CardContent,
    CardFooter,
} from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { useUIStore } from "@/stores/uiStore";
import apiClient from "@/api/client";
import { KeyRound, Mail, ShieldCheck, ArrowLeft } from "lucide-react";

export function ForgotPassword() {
    const [step, setStep] = useState(1); // 1: Email, 2: OTP/NewPassword, 3: Success
    const [loading, setLoading] = useState(false);
    const [email, setEmail] = useState("");
    const [otp, setOtp] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const [localError, setLocalError] = useState("");

    const { addToast } = useUIStore();
    const navigate = useNavigate();

    const handleRequestOTP = async (e) => {
        e.preventDefault();
        setLoading(true);
        setLocalError("");
        try {
            const res = await apiClient.post("/auth/forgot-password", { email });
            addToast({
                title: "OTP Sent",
                message: res.data.message,
                type: "success",
            });
            setStep(2);
        } catch (err) {
            const msg = err.response?.data?.detail || "Failed to send OTP.";
            setLocalError(msg);
            addToast({ title: "Error", message: msg, type: "error" });
        } finally {
            setLoading(false);
        }
    };

    const handleResetPassword = async (e) => {
        e.preventDefault();
        setLoading(true);
        setLocalError("");
        try {
            const res = await apiClient.post("/auth/reset-password", {
                email,
                otp_code: otp,
                new_password: newPassword,
            });
            addToast({
                title: "Success",
                message: res.data.message,
                type: "success",
            });
            setStep(3);
        } catch (err) {
            const msg = err.response?.data?.detail || "Failed to reset password.";
            setLocalError(msg);
            addToast({ title: "Error", message: msg, type: "error" });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-background bg-grid-pattern relative flex items-center justify-center p-4">
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-primary/20 rounded-full blur-[120px] pointer-events-none" />

            <Card className="w-full max-w-md relative z-10 glass-panel border-border/50 shadow-2xl">
                <CardHeader className="text-center space-y-2 pb-8">
                    <div className="mx-auto h-12 w-12 rounded-lg bg-primary flex items-center justify-center font-mono font-bold text-2xl text-white shadow-[0_0_20px_rgba(67,56,202,0.6)] mb-4">
                        {step === 1 ? <Mail className="h-6 w-6" /> : step === 2 ? <ShieldCheck className="h-6 w-6" /> : <KeyRound className="h-6 w-6" />}
                    </div>
                    <CardTitle className="text-2xl text-white">
                        {step === 1 ? "Forgot Password?" : step === 2 ? "Verify OTP" : "Password Reset!"}
                    </CardTitle>
                    <CardDescription>
                        {step === 1
                            ? "No worries, it happens. Enter your email to receive a 6-digit verification code."
                            : step === 2
                                ? "Enter the code sent to your email and your new password."
                                : "Your password has been successfully updated."}
                    </CardDescription>
                </CardHeader>

                <CardContent className="space-y-4">
                    {localError && (
                        <div className="p-3 text-sm text-red-400 bg-red-900/20 border border-red-900/50 rounded-lg">
                            {localError}
                        </div>
                    )}

                    {step === 1 && (
                        <form onSubmit={handleRequestOTP} className="space-y-4">
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-zinc-300">Email Address</label>
                                <input
                                    type="email"
                                    required
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="w-full rounded-md bg-zinc-900/50 border border-zinc-800 p-2.5 text-white focus:border-primary focus:ring-1 focus:ring-primary"
                                    placeholder="name@example.com"
                                />
                            </div>
                            <Button type="submit" fullWidth isLoading={loading}>
                                Send OTP
                            </Button>
                        </form>
                    )}

                    {step === 2 && (
                        <form onSubmit={handleResetPassword} className="space-y-4">
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-zinc-300">Verification Code (OTP)</label>
                                <input
                                    type="text"
                                    required
                                    maxLength={6}
                                    value={otp}
                                    onChange={(e) => setOtp(e.target.value)}
                                    className="w-full rounded-md bg-zinc-900/50 border border-zinc-800 p-2.5 text-white text-center tracking-[0.5em] font-mono text-xl focus:border-primary focus:ring-1 focus:ring-primary"
                                    placeholder="000000"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-zinc-300">New Password</label>
                                <input
                                    type="password"
                                    required
                                    minLength={8}
                                    value={newPassword}
                                    onChange={(e) => setNewPassword(e.target.value)}
                                    className="w-full rounded-md bg-zinc-900/50 border border-zinc-800 p-2.5 text-white focus:border-primary focus:ring-1 focus:ring-primary"
                                    placeholder="••••••••"
                                />
                            </div>
                            <Button type="submit" fullWidth isLoading={loading}>
                                Reset Password
                            </Button>
                        </form>
                    )}

                    {step === 3 && (
                        <div className="py-4 text-center">
                            <div className="mb-6 inline-flex h-16 w-16 items-center justify-center rounded-full bg-success/10 text-success">
                                <ShieldCheck className="h-8 w-8" />
                            </div>
                            <p className="text-zinc-400 mb-6">
                                You can now log in to your account with your new secure password.
                            </p>
                            <Button fullWidth onClick={() => navigate("/auth")}>
                                Return to Login
                            </Button>
                        </div>
                    )}
                </CardContent>

                <CardFooter className="flex-col">
                    {step < 3 && (
                        <Link
                            to="/auth"
                            className="inline-flex items-center gap-2 text-sm text-zinc-400 hover:text-white transition-colors"
                        >
                            <ArrowLeft className="h-4 w-4" />
                            Back to Login
                        </Link>
                    )}
                </CardFooter>
            </Card>
        </div>
    );
}
