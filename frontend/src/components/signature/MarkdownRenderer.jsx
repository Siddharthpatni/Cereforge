import React from 'react';
import { cn } from '@/utils/cn';

export function MarkdownRenderer({ content, className }) {
    // Simple regex-based markdown parser for the stub/MVP.
    // In a full production app, you would use react-markdown + rehype-prism-plus

    const parseMarkdown = (text) => {
        if (!text) return '';

        // Bold
        let parsed = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        // Code blocks
        parsed = parsed.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        // Inline code
        parsed = parsed.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');
        // Headlines
        parsed = parsed.replace(/### (.*?)\n/g, '<h3>$1</h3>');
        parsed = parsed.replace(/## (.*?)\n/g, '<h2>$1</h2>');
        // Paragraphs roughly
        parsed = parsed.replace(/\n\n/g, '<br/><br/>');

        return parsed;
    };

    return (
        <div
            className={cn("prose prose-invert max-w-none prose-pre:bg-zinc-900 prose-pre:border prose-pre:border-zinc-800", className)}
            dangerouslySetInnerHTML={{ __html: parseMarkdown(content) }}
        />
    );
}
