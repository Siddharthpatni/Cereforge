import React from 'react';
import { cn } from '@/utils/cn';
import { Loader2 } from 'lucide-react';

const variants = {
    primary: "bg-primary text-white hover:bg-primary-hover shadow-md",
    secondary: "bg-secondary text-white hover:bg-secondary-hover border border-border",
    outline: "bg-transparent border border-border text-foreground hover:bg-secondary-hover",
    ghost: "bg-transparent text-foreground hover:bg-secondary-hover",
    danger: "bg-danger text-white hover:bg-red-600 shadow-md",
};

const sizes = {
    sm: "h-8 px-3 text-xs",
    md: "h-10 px-4 py-2 text-sm",
    lg: "h-12 px-6 text-base",
    icon: "h-10 w-10 justify-center",
};

export const Button = React.forwardRef(({
    className,
    variant = "primary",
    size = "md",
    isLoading = false,
    fullWidth = false,
    children,
    disabled,
    ...props
}, ref) => {
    return (
        <button
            ref={ref}
            disabled={disabled || isLoading}
            className={cn(
                "inline-flex items-center gap-2 rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary disabled:pointer-events-none disabled:opacity-50",
                variants[variant],
                sizes[size],
                fullWidth && "w-full justify-center",
                className
            )}
            {...props}
        >
            {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
            {children}
        </button>
    );
});

Button.displayName = "Button";
