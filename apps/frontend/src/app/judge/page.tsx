"use client";

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronRight, ArrowLeft } from "lucide-react";
import Link from "next/link";

const Scene = dynamic(() => import("@/components/Scene"), { ssr: false });

const scenes = [
  {
    id: 1,
    eyebrow: "The Problem",
    headline: "One procedural error...",
    body: "...can silently derail a student's entire mathematical foundation.",
  },
  {
    id: 2,
    eyebrow: "The Flaw",
    headline: "Scores are insufficient.",
    body: "Grading tells you a student failed. It does not tell you that they consistently added the denominators across twelve different problems.",
  },
  {
    id: 3,
    eyebrow: "The Innovation",
    headline: "Deterministic Inference",
    body: "FaultLine executes candidate procedures against visible student work. No probabilistic guessing. Just exact mathematical deduction.",
  },
  {
    id: 4,
    eyebrow: "The Engine",
    headline: "Information Gain",
    body: "When evidence is weak, FaultLine refuses to guess. Instead, it computes the exact follow-up question required to mathematically resolve the ambiguity.",
  },
  {
    id: 5,
    eyebrow: "The Impact",
    headline: "Test policy before it tests people.",
    body: "Deploy with a held-out proof workflow. FaultLine locks a prediction, issues a cryptographic token, and proves its diagnosis.",
  }
];

export default function JudgeMode() {
  const [currentScene, setCurrentScene] = useState(0);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight" || e.key === " ") {
        setCurrentScene(s => Math.min(s + 1, scenes.length - 1));
      } else if (e.key === "ArrowLeft") {
        setCurrentScene(s => Math.max(s - 1, 0));
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <div className="h-screen w-full bg-background overflow-hidden relative text-foreground">
      {/* Background ambient noise */}
      <div 
        className="fixed inset-0 pointer-events-none opacity-20 -z-20 mix-blend-multiply"
        style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")` }}
      />
      
      <Link href="/" className="absolute top-8 left-8 z-50 text-muted hover:text-foreground transition-colors flex items-center gap-2 text-sm font-medium">
        <ArrowLeft size={16} /> Exit Presentation
      </Link>

      <div className="absolute inset-0 z-0 opacity-80">
        <Scene />
      </div>

      <div className="relative z-10 h-full flex flex-col justify-center max-w-5xl mx-auto px-12 lg:px-24">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentScene}
            initial={{ opacity: 0, x: 20, filter: "blur(4px)" }}
            animate={{ opacity: 1, x: 0, filter: "blur(0px)" }}
            exit={{ opacity: 0, x: -20, filter: "blur(4px)" }}
            transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
            className="max-w-2xl"
          >
            <div className="text-accent font-mono text-sm tracking-widest uppercase mb-6 flex items-center gap-4">
              <span className="w-8 h-px bg-accent/50" />
              {scenes[currentScene].eyebrow}
            </div>
            <h1 className="font-display text-5xl md:text-7xl font-bold leading-tight mb-8 drop-shadow-xl text-foreground">
              {scenes[currentScene].headline}
            </h1>
            <p className="text-xl md:text-2xl text-foreground/80 leading-relaxed font-light">
              {scenes[currentScene].body}
            </p>
          </motion.div>
        </AnimatePresence>
      </div>

      <div className="absolute bottom-12 left-0 right-0 flex justify-between items-center px-12 lg:px-24 z-50">
        <div className="flex gap-2">
          {scenes.map((_, idx) => (
            <div 
              key={idx} 
              className={`h-1 rounded-full transition-all duration-500 ${idx === currentScene ? "w-8 bg-accent" : "w-2 bg-border"}`} 
            />
          ))}
        </div>
        
        {currentScene < scenes.length - 1 ? (
          <button 
            onClick={() => setCurrentScene(s => s + 1)}
            className="flex items-center gap-2 text-foreground hover:text-accent transition-colors font-medium text-lg"
          >
            Next <ChevronRight size={20} />
          </button>
        ) : (
          <Link 
            href="/demo"
            className="flex items-center gap-2 px-6 py-3 bg-accent text-white rounded-lg hover:bg-accent-hover transition-colors font-medium shadow-lg"
          >
            Enter Dashboard <ChevronRight size={20} />
          </Link>
        )}
      </div>
    </div>
  );
}
