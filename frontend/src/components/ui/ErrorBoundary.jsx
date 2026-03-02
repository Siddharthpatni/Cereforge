import { Component } from "react";
import { AlertTriangle, RefreshCw, Home } from "lucide-react";

/**
 * ErrorBoundary — catches any uncaught React render errors
 * and prevents blank pages by showing a fallback UI.
 *
 * Usage:
 *   <ErrorBoundary>
 *     <YourComponent />
 *   </ErrorBoundary>
 *
 * Or with a custom fallback:
 *   <ErrorBoundary fallback={<MyCustomFallback />}>
 *     ...
 *   </ErrorBoundary>
 */
class ErrorBoundary extends Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null, errorInfo: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        // Log to console in development; swap with Sentry in production
        console.error("[ErrorBoundary] Uncaught error:", error, errorInfo);
        this.setState({ errorInfo });
    }

    handleReset = () => {
        this.setState({ hasError: false, error: null, errorInfo: null });
    };

    render() {
        if (this.state.hasError) {
            // Prefer a custom fallback if provided
            if (this.props.fallback) {
                return this.props.fallback;
            }

            return (
                <div className="min-h-[60vh] flex items-center justify-center p-8">
                    <div className="max-w-md w-full text-center space-y-6">
                        <div className="flex justify-center">
                            <div className="h-20 w-20 rounded-full bg-red-900/20 border border-red-900/50 flex items-center justify-center">
                                <AlertTriangle className="h-10 w-10 text-red-500" />
                            </div>
                        </div>
                        <div>
                            <h2 className="text-2xl font-bold text-white mb-2">
                                Something went wrong
                            </h2>
                            <p className="text-zinc-400 text-sm">
                                An unexpected error occurred. You can try refreshing this section
                                or go back to the dashboard.
                            </p>
                            {import.meta.env.DEV && this.state.error && (
                                <details className="mt-4 text-left">
                                    <summary className="text-xs text-zinc-500 cursor-pointer hover:text-zinc-400">
                                        Error details (dev only)
                                    </summary>
                                    <pre className="mt-2 p-3 bg-zinc-900 border border-zinc-800 rounded text-xs text-red-400 overflow-auto max-h-40">
                                        {this.state.error.toString()}
                                    </pre>
                                </details>
                            )}
                        </div>
                        <div className="flex justify-center gap-3">
                            <button
                                onClick={this.handleReset}
                                className="flex items-center gap-2 px-4 py-2 bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-white rounded-lg text-sm transition-colors"
                            >
                                <RefreshCw className="h-4 w-4" /> Try Again
                            </button>
                            <a
                                href="/"
                                className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm transition-colors"
                            >
                                <Home className="h-4 w-4" /> Dashboard
                            </a>
                        </div>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
