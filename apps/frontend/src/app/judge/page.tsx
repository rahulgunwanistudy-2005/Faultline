"use client";

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

const Scene = dynamic(() => import("@/components/Scene"), { ssr: false });

const scenes = [
  {
    id: 1,
    eyebrow: "The Problem",
    headline: "One procedural error...",
    body: "...can silently derail a student's entire mathematical foundation. Brute-forcing the diagnosis creates a massive, slow computational tree.",
  },
  {
    id: 2,
    eyebrow: "The Innovation",
    headline: "Neuro-Symbolic AI",
    body: "We don't train our own models. We leverage existing LLMs as a heuristic to predict likely bugs and instantly shrink the search space. But the LLM doesn't guess the answer—it guides our deterministic arithmetic engine to definitively prove it. Zero hallucinations.",
  },
  {
    id: 3,
    eyebrow: "The Engine",
    headline: "Bayesian Active Learning",
    body: "When a student makes a mistake, FaultLine calculates a probability distribution of bugs. It then mathematically selects the exact next question that maximizes Expected Information Gain.",
  },
  {
    id: 4,
    eyebrow: "The Visualization",
    headline: "Unsupervised Clustering",
    body: "We map student errors into high-dimensional space, visually plotting 'Fault Lines' across classrooms. Teachers instantly see exactly where collective understanding is splitting.",
  },
  {
    id: 5,
    eyebrow: "The Impact",
    headline: "See the procedure behind the mistake.",
    bullets: [
      "Neuro-symbolic diagnosis: Bayesian inference for search, deterministic verification for truth",
      "Confidence-aware, not confidently wrong",
      "Held-out prediction proof",
      "Information-gain question selection",
      "Immediate teacher action"
    ]
  }
];

const SLIDE_DURATION = 8000; // 8 seconds per slide
const TOTAL_DURATION = SLIDE_DURATION * scenes.length; // 40 seconds total

// VISUAL SIMULATIONS FOR THE JUDGES

function NeuroSymbolicVisual() {
  const nodes = Array.from({ length: 48 });
  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="w-full max-w-md aspect-square relative"
    >
      <div className="absolute inset-0 grid grid-cols-6 gap-4 p-8">
        {nodes.map((_, i) => {
          const isPath = [3, 9, 15, 21, 27, 33].includes(i);
          return (
            <motion.div
              key={i}
              initial={{ opacity: 0, backgroundColor: "#444" }}
              animate={{ 
                opacity: isPath ? [0, 1, 1] : [0, 0.5, 0.05],
                backgroundColor: isPath ? ["#444", "#E07A5F", "#E07A5F"] : "#444",
                scale: isPath ? [1, 1.2, 1.1] : 1
              }}
              transition={{ 
                duration: 2, 
                times: [0, 0.4, 1],
                repeat: Infinity, 
                repeatDelay: 1,
                delay: i * 0.02
              }}
              className="rounded-full shadow-lg"
            />
          );
        })}
      </div>
      <div className="absolute bottom-0 text-center w-full text-xs font-mono text-muted uppercase tracking-widest">
        LLM Search Space Pruning
      </div>
    </motion.div>
  );
}

function BayesianVisual() {
  const [step, setStep] = useState(0);
  useEffect(() => {
    const timer = setInterval(() => {
      setStep(s => (s + 1) % 4);
    }, 1500);
    return () => clearInterval(timer);
  }, []);

  const distributions = [
    [20, 20, 20, 20, 20],
    [10, 40, 10, 30, 10],
    [5, 80, 5, 5, 5],
    [20, 20, 20, 20, 20],
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="w-full max-w-md h-64 flex flex-col justify-end gap-4 p-8"
    >
      <div className="flex justify-between items-end h-full gap-2 border-b border-white/10 pb-2">
        {distributions[step].map((h, i) => (
          <motion.div
            key={i}
            animate={{ height: `${h}%`, backgroundColor: h > 50 ? "#E07A5F" : "#A8A29E" }}
            transition={{ type: "spring", stiffness: 100, damping: 15 }}
            className="w-12 rounded-t-sm shadow-xl"
          />
        ))}
      </div>
      <div className="text-center text-xs font-mono text-muted uppercase tracking-widest">
        Expected Information Gain
      </div>
    </motion.div>
  );
}

function ClusteringVisual() {
  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="w-full max-w-md aspect-square relative"
    >
      {Array.from({ length: 40 }).map((_, i) => {
        const cluster = i % 3;
        const targetX = cluster === 0 ? "20%" : cluster === 1 ? "80%" : "50%";
        const targetY = cluster === 0 ? "20%" : cluster === 1 ? "30%" : "80%";
        const color = cluster === 0 ? "#E07A5F" : cluster === 1 ? "#F4A261" : "#8C7868";
        return (
          <motion.div
            key={i}
            initial={{ 
              top: `${Math.random() * 100}%`, 
              left: `${Math.random() * 100}%`,
              opacity: 0
            }}
            animate={{ 
              top: targetY, 
              left: targetX,
              opacity: 0.8
            }}
            transition={{ 
              duration: 3, 
              ease: "circOut",
              repeat: Infinity,
              repeatType: "reverse"
            }}
            style={{ backgroundColor: color }}
            className="absolute w-3 h-3 rounded-full blur-[1px]"
          />
        );
      })}
      <div className="absolute bottom-0 text-center w-full text-xs font-mono text-muted uppercase tracking-widest">
        Latent Space Embedding
      </div>
    </motion.div>
  );
}

export default function JudgeMode() {
  const [currentScene, setCurrentScene] = useState(0);
  const router = useRouter();

  // Cinematic Autoplay Logic (40 seconds total, 8 seconds per slide)
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentScene(prev => {
        if (prev < scenes.length - 1) {
          return prev + 1;
        }
        clearInterval(timer);
        setTimeout(() => router.push("/demo"), 3000); // Wait 3s on final slide then auto-redirect
        return prev;
      });
    }, SLIDE_DURATION);

    return () => clearInterval(timer);
  }, [router]);

  return (
    <div className="h-screen w-full bg-background overflow-hidden relative text-foreground">
      {/* Background ambient noise */}
      <div 
        className="fixed inset-0 pointer-events-none opacity-20 -z-20 mix-blend-multiply"
        style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")` }}
      />
      
      {/* Cinematic Top Progress Bar (40s complete fill) */}
      <motion.div 
        initial={{ width: "0%" }}
        animate={{ width: "100%" }}
        transition={{ duration: TOTAL_DURATION / 1000, ease: "linear" }}
        className="absolute top-0 left-0 h-1 bg-accent z-50 shadow-[0_0_10px_rgba(224,122,95,0.8)]"
      />

      <Link href="/" className="absolute top-8 left-8 z-50 text-muted hover:text-foreground transition-colors flex items-center gap-2 text-sm font-medium">
        <ArrowLeft size={16} /> Exit Presentation
      </Link>

      <div className="absolute inset-0 z-0 opacity-40">
        <Scene />
      </div>

      <div className="relative z-10 h-full flex items-center justify-between max-w-7xl mx-auto px-12 lg:px-24">
        {/* Left side: Text Pitch */}
        <div className="w-1/2">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentScene}
              initial={{ opacity: 0, x: 20, filter: "blur(4px)" }}
              animate={{ opacity: 1, x: 0, filter: "blur(0px)" }}
              exit={{ opacity: 0, x: -20, filter: "blur(4px)" }}
              transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
              className="max-w-xl"
            >
              <div className="text-accent font-mono text-sm tracking-widest uppercase mb-6 flex items-center gap-4">
                <span className="w-8 h-px bg-accent/50" />
                {scenes[currentScene].eyebrow}
              </div>
              <h1 className="font-display text-5xl md:text-6xl font-bold leading-tight mb-8 drop-shadow-xl text-foreground">
                {scenes[currentScene].headline}
              </h1>
              
              {scenes[currentScene].body && (
                <p className="text-xl md:text-2xl text-foreground/80 leading-relaxed font-light">
                  {scenes[currentScene].body}
                </p>
              )}
              
              {/* Special rendering for the final slide's bullet points */}
              {scenes[currentScene].bullets && (
                <ul className="space-y-4">
                  {scenes[currentScene].bullets.map((bullet, idx) => (
                    <motion.li 
                      key={idx}
                      initial={{ opacity: 0, x: 10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.2 + idx * 0.15, duration: 0.5 }}
                      className="flex items-start gap-4 text-lg md:text-xl text-foreground/90 font-medium"
                    >
                      <span className="text-accent mt-1">●</span>
                      {bullet}
                    </motion.li>
                  ))}
                </ul>
              )}
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Right side: ML Visualizations */}
        <div className="w-1/2 flex justify-center items-center h-full pointer-events-none">
          <AnimatePresence mode="wait">
            {currentScene === 1 && <NeuroSymbolicVisual key="ns" />}
            {currentScene === 2 && <BayesianVisual key="bayes" />}
            {currentScene === 3 && <ClusteringVisual key="cluster" />}
          </AnimatePresence>
        </div>
      </div>

      <div className="absolute bottom-12 left-0 right-0 flex justify-center items-center px-12 lg:px-24 z-50">
        {/* Cinematic slide indicators */}
        <div className="flex gap-3">
          {scenes.map((_, idx) => (
            <div 
              key={idx} 
              className="relative h-1.5 w-12 bg-border overflow-hidden rounded-full"
            >
              <motion.div
                className="absolute top-0 left-0 bottom-0 bg-accent"
                initial={{ width: idx < currentScene ? "100%" : "0%" }}
                animate={{ width: idx === currentScene ? "100%" : idx < currentScene ? "100%" : "0%" }}
                transition={{ duration: idx === currentScene ? SLIDE_DURATION / 1000 : 0.5, ease: "linear" }}
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
