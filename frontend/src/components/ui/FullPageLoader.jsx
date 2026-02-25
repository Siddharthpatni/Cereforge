import React from "react";

export function FullPageLoader() {
    return (
        <div className="fixed inset-0 flex items-center justify-center z-50" style={{ backgroundColor: "#050508" }}>
            <div className="animate-pulse text-6xl">
                🧠
            </div>
        </div>
    );
}

export default FullPageLoader;
