"use client";

import dynamic from "next/dynamic";
import { motion } from "framer-motion";
import { ArrowRight, ChevronRight, Activity, Database, CheckCircle2 } from "lucide-react";
import Link from "next/link";
import Navigation from "@/components/Navigation";

// Dynamically import the 3D Scene so it doesn't SSR and cause hydration errors
const Scene = dynamic(() => import("@/components/Scene"), {
  ssr: false,
  loading: () => <div className="absolute right-0 top-0 w-full h-[600px] lg:h-[800px] -z-10 animate-pulse bg-card" />
});

export default function Home() {
  return (
    <div className="min-h-screen relative overflow-hidden">
      <Navigation />
      
      {/* Background grain texture for premium editorial feel */}
      <div 
        className="fixed inset-0 pointer-events-none opacity-20 -z-20 mix-blend-multiply"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`
        }}
      />

      {/* The 3D Hero */}
      <Scene />

      <main className="max-w-7xl mx-auto px-6 pt-32 lg:pt-48 pb-24">
        {/* HERO SECTION */}
        <section className="relative min-h-[60vh] flex flex-col justify-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
            className="max-w-2xl"
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-card border border-border text-xs font-semibold text-accent mb-6 uppercase tracking-widest shadow-sm">
              <span className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
              Determinism over probability
            </div>
            
            <h1 className="font-display text-5xl md:text-7xl font-bold leading-[1.05] tracking-tight mb-8 text-foreground">
              See the procedure <br/>
              <span className="text-muted font-normal italic">behind the error.</span>
            </h1>
            
            <p className="text-lg md:text-xl text-foreground/80 mb-10 max-w-lg leading-relaxed">
              FaultLine reconstructs the exact procedure behind a student&apos;s fraction errors. 
              No LLM hallucinations. No generic score claims. Just exact rational arithmetic.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center gap-4">
              <Link href="/judge" className="w-full sm:w-auto px-8 py-3.5 rounded-lg bg-accent text-white font-medium flex items-center justify-center gap-2 hover:bg-accent-hover transition-colors shadow-lg hover:shadow-xl hover:-translate-y-0.5 duration-300">
                Play Presentation
                <ArrowRight size={18} />
              </Link>
              <Link href="/demo" className="w-full sm:w-auto px-8 py-3.5 rounded-lg bg-card text-foreground font-medium border border-border flex items-center justify-center gap-2 hover:bg-card-hover transition-colors shadow-sm">
                Interactive Dashboard
              </Link>
            </div>
          </motion.div>
        </section>

        {/* FEATURES GRID */}
        <section className="mt-32 lg:mt-48">
          <motion.div 
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.8 }}
            className="mb-16"
          >
            <h2 className="font-display text-3xl font-bold mb-4">Why FaultLine?</h2>
            <p className="text-muted max-w-xl">
              Traditional platforms grade answers. FaultLine reverse-engineers the student&apos;s exact misstep, finding the structural flaw in their arithmetic procedure.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard 
              icon={<Activity size={24} className="text-accent" />}
              title="Deterministic Inference"
              description="Executes six deterministic fraction procedures against visible student work to report the full posterior with exact confidence gating."
              delay={0}
            />
            <FeatureCard 
              icon={<Database size={24} className="text-accent" />}
              title="Held-out Proof Workflow"
              description="Server issues a signed, expiring proof token based on the prediction. Answers are revealed only upon valid token submission."
              delay={0.1}
            />
            <FeatureCard 
              icon={<CheckCircle2 size={24} className="text-accent" />}
              title="Exact Information Gain"
              description="Refuses to name a diagnosis when evidence is weak, instead selecting follow-up questions mathematically proven to resolve ambiguity."
              delay={0.2}
            />
          </div>
        </section>

        {/* ARCHITECTURE SECTION */}
        <section className="mt-32 lg:mt-48 pb-20">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.8 }}
            >
              <h2 className="font-display text-3xl font-bold mb-6">Verified Architecture</h2>
              <ul className="space-y-6">
                {[
                  "Raw bounded PNG/JPEG upload with segmentation",
                  "Fixed-template validation avoiding multipart parsers",
                  "Process-local sliding-window rate limiting",
                  "Strict correction schemas and feature vocabulary"
                ].map((item, i) => (
                  <li key={i} className="flex gap-4">
                    <div className="mt-1 flex-shrink-0 w-5 h-5 rounded-full bg-accent/20 flex items-center justify-center">
                      <div className="w-2 h-2 rounded-full bg-accent" />
                    </div>
                    <span className="text-foreground/80 leading-relaxed">{item}</span>
                  </li>
                ))}
              </ul>
              
              <Link href="/judge" className="inline-flex items-center gap-2 mt-10 text-accent font-medium hover:text-accent-hover transition-colors">
                View the Cinematic Experience
                <ChevronRight size={18} />
              </Link>
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.8 }}
              className="relative p-1 rounded-2xl bg-gradient-to-br from-border to-transparent"
            >
              <div className="absolute inset-0 bg-card rounded-2xl -z-10" />
              <div className="bg-card rounded-xl border border-border p-8 shadow-md">
                <div className="space-y-4 font-mono text-sm">
                  <div className="p-3 bg-background border border-border rounded-lg text-muted">Client &rarr; Raw bytes (max 8MB)</div>
                  <div className="flex justify-center"><div className="w-px h-4 bg-border" /></div>
                  <div className="p-3 bg-background border border-border rounded-lg text-accent text-center font-medium shadow-sm">FastAPI Pipeline</div>
                  <div className="flex justify-center"><div className="w-px h-4 bg-border" /></div>
                  <div className="p-3 bg-background border border-border rounded-lg text-muted">Decompression Bomb Check</div>
                  <div className="flex justify-center"><div className="w-px h-4 bg-border" /></div>
                  <div className="p-3 bg-background border border-border rounded-lg text-muted">Fixed-Template Segmentation</div>
                  <div className="flex justify-center"><div className="w-px h-4 bg-border" /></div>
                  <div className="p-3 bg-background border border-border rounded-lg text-foreground font-medium text-center">Faultline Core: Inference Engine</div>
                </div>
              </div>
            </motion.div>
          </div>
        </section>
      </main>
    </div>
  );
}

function FeatureCard({ icon, title, description, delay }: { icon: React.ReactNode, title: string, description: string, delay: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-50px" }}
      transition={{ duration: 0.6, delay }}
      whileHover={{ y: -5, transition: { duration: 0.2 } }}
      className="p-8 rounded-2xl bg-card border border-border shadow-sm hover:shadow-md transition-shadow group cursor-default"
    >
      <div className="w-12 h-12 rounded-xl bg-background border border-border flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
        {icon}
      </div>
      <h3 className="font-display font-bold text-xl mb-3 text-foreground">{title}</h3>
      <p className="text-muted leading-relaxed">{description}</p>
    </motion.div>
  );
}
