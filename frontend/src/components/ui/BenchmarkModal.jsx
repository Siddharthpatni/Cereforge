import React from 'react';
import { Modal } from './Modal';
import { Button } from './Button';
import { CheckCircle, Clock, Database, Sparkles, ChevronRight } from 'lucide-react';

export function BenchmarkModal({ isOpen, onClose, benchmarks, xpEarned, onContinue }) {
    if (!benchmarks) return null;

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="Solution Analyzed">
            <div className="space-y-6">

                {/* Core Stats Row */}
                <div className="grid grid-cols-3 gap-4">
                    <div className="bg-primary/10 border border-primary/20 rounded-lg p-4 text-center">
                        <Clock className="h-6 w-6 text-primary mx-auto mb-2" />
                        <div className="text-2xl font-bold text-white">{benchmarks.execution_time_ms}ms</div>
                        <div className="text-xs text-zinc-400">Est. Execution Time</div>
                    </div>

                    <div className="bg-secondary/10 border border-secondary/20 rounded-lg p-4 text-center">
                        <Database className="h-6 w-6 text-secondary mx-auto mb-2" />
                        <div className="text-2xl font-bold text-white">{benchmarks.memory_usage_mb}MB</div>
                        <div className="text-xs text-zinc-400">Memory Footprint</div>
                    </div>

                    <div className="bg-success/10 border border-success/20 rounded-lg p-4 text-center">
                        <CheckCircle className="h-6 w-6 text-success mx-auto mb-2" />
                        <div className="text-2xl font-bold text-white">
                            {benchmarks.tests_passed}/{benchmarks.total_tests}
                        </div>
                        <div className="text-xs text-zinc-400">Tests Passed</div>
                    </div>
                </div>

                {/* AI Insights Section */}
                <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 space-y-4">
                    <div className="flex items-center gap-2 text-white font-semibold">
                        <Sparkles className="h-5 w-5 text-accent-llm" />
                        AI Engineering Insights
                    </div>
                    <ul className="space-y-3">
                        {benchmarks.insights?.map((insight, idx) => (
                            <li key={idx} className="flex items-start gap-3 text-sm text-zinc-300">
                                <ChevronRight className="h-4 w-4 text-primary shrink-0 mt-0.5" />
                                <span>{insight}</span>
                            </li>
                        ))}
                    </ul>
                </div>

                {/* Footer Actions */}
                <div className="flex items-center justify-between pt-4 border-t border-zinc-800">
                    <div className="text-success font-medium flex items-center gap-2">
                        <Flame className="h-4 w-4" /> +{xpEarned} XP Earned
                    </div>
                    <Button onClick={onContinue} className="min-w-[120px]">
                        Continue
                    </Button>
                </div>
            </div>
        </Modal>
    );
}

// Ensure Flame is imported for the footer (since it wasn't in the top imports)
import { Flame } from 'lucide-react';
