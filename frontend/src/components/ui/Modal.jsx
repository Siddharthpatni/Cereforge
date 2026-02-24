import React, { useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { X } from 'lucide-react';
import { Button } from './Button';
import { cn } from '@/utils/cn';

export function Modal({ isOpen, onClose, title, children, className, container }) {
    const overlayRef = useRef(null);

    useEffect(() => {
        const handleEscape = (e) => {
            if (e.key === 'Escape') onClose();
        };

        if (isOpen) {
            document.addEventListener('keydown', handleEscape);
            document.body.style.overflow = 'hidden';
        }

        return () => {
            document.removeEventListener('keydown', handleEscape);
            document.body.style.overflow = 'unset';
        };
    }, [isOpen, onClose]);

    const handleOverlayClick = (e) => {
        if (e.target === overlayRef.current) onClose();
    };

    if (!isOpen) return null;

    const modalContent = (
        <div
            ref={overlayRef}
            onMouseDown={handleOverlayClick}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 sm:p-6"
        >
            <div
                className={cn(
                    "relative w-full max-w-lg rounded-xl border border-border bg-card shadow-2xl animate-in fade-in zoom-in-95 duration-200",
                    className
                )}
            >
                <div className="flex items-center justify-between border-b border-border p-4 sm:p-6">
                    <h2 className="text-xl font-semibold text-foreground">{title}</h2>
                    <Button variant="ghost" size="icon" onClick={onClose} className="-mr-2 text-zinc-400 hover:text-white">
                        <X className="h-5 w-5" />
                    </Button>
                </div>

                <div className="p-4 sm:p-6">
                    {children}
                </div>
            </div>
        </div>
    );

    return createPortal(
        modalContent,
        container || document.body
    );
}
