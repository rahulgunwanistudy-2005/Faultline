"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Upload, FileText, CheckCircle2, AlertCircle, RefreshCw, Lock, Unlock, Zap } from "lucide-react";
import Navigation from "@/components/Navigation";
import { FaultlineAPI, Student } from "@/lib/api";

export default function DemoDashboard() {
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null);
  const [predictionResult, setPredictionResult] = useState<any>(null);
  const [proofToken, setProofToken] = useState<string | null>(null);
  const [revealResult, setRevealResult] = useState<any>(null);
  const [uploadStatus, setUploadStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");

  useEffect(() => {
    async function loadData() {
      try {
        const data = await FaultlineAPI.getDemoClass("period-3");
        setStudents(data.students || []);
      } catch (err) {
        console.error("Failed to fetch class data:", err);
        // We avoid mock data as instructed, but if backend is down, we handle gracefully.
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    setUploadStatus("uploading");
    try {
      await FaultlineAPI.uploadWorksheet(file);
      setUploadStatus("success");
      setTimeout(() => setUploadStatus("idle"), 3000);
    } catch (err) {
      console.error(err);
      setUploadStatus("error");
      setTimeout(() => setUploadStatus("idle"), 3000);
    }
  };

  const handlePredict = async (studentId: string) => {
    try {
      const data = await FaultlineAPI.lockPrediction(studentId);
      setPredictionResult(data);
      if (data.proof_token) setProofToken(data.proof_token);
    } catch (err) {
      console.error(err);
    }
  };

  const handleReveal = async (studentId: string) => {
    if (!proofToken) return;
    try {
      const data = await FaultlineAPI.revealPrediction(studentId, proofToken);
      setRevealResult(data);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main className="max-w-7xl mx-auto px-6 pt-32 pb-24">
        <div className="mb-12 flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div>
            <h1 className="font-display text-4xl font-bold text-foreground mb-4">Class Analysis</h1>
            <p className="text-muted text-lg max-w-2xl">
              Upload structural fractions worksheets to automatically reconstruct exact student errors. 
              The system predicts the held-out answer based on the structural diagnosis.
            </p>
          </div>
          
          <div className="flex-shrink-0">
            <input 
              type="file" 
              id="upload" 
              className="hidden" 
              accept="image/png, image/jpeg" 
              onChange={handleUpload}
            />
            <label 
              htmlFor="upload"
              className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium cursor-pointer transition-all shadow-sm
                ${uploadStatus === "uploading" ? "bg-muted text-white cursor-wait" : 
                  uploadStatus === "success" ? "bg-green-600 text-white" : 
                  uploadStatus === "error" ? "bg-red-600 text-white" : 
                  "bg-accent text-white hover:bg-accent-hover hover:shadow-md"}`}
            >
              {uploadStatus === "uploading" && <RefreshCw size={18} className="animate-spin" />}
              {uploadStatus === "success" && <CheckCircle2 size={18} />}
              {uploadStatus === "error" && <AlertCircle size={18} />}
              {uploadStatus === "idle" && <Upload size={18} />}
              {uploadStatus === "idle" ? "Upload Worksheet" : uploadStatus.charAt(0).toUpperCase() + uploadStatus.slice(1)}
            </label>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Student List */}
          <div className="lg:col-span-1 bg-card border border-border rounded-2xl overflow-hidden shadow-sm flex flex-col h-[600px]">
            <div className="p-6 border-b border-border bg-card-hover">
              <h2 className="font-display font-semibold text-lg flex items-center gap-2">
                <FileText size={18} className="text-accent" /> Period 3 Students
              </h2>
            </div>
            <div className="overflow-y-auto flex-1 p-4 space-y-2">
              {loading ? (
                <div className="flex justify-center py-12"><RefreshCw className="animate-spin text-muted" /></div>
              ) : students.length > 0 ? (
                students.map((student) => (
                  <button
                    key={student.student_id}
                    onClick={() => {
                      setSelectedStudent(student);
                      setPredictionResult(null);
                      setProofToken(null);
                      setRevealResult(null);
                    }}
                    className={`w-full text-left px-5 py-4 rounded-xl transition-colors ${
                      selectedStudent?.student_id === student.student_id ? "bg-accent/10 border-accent/20 border" : "hover:bg-card-hover border border-transparent"
                    }`}
                  >
                    <div className="font-medium text-foreground">{student.name || `Student ${student.student_id}`}</div>
                    <div className="text-xs text-muted mt-1 font-mono">{student.student_id}</div>
                  </button>
                ))
              ) : (
                <div className="text-center py-12 text-muted">No students available. Ensure backend is running.</div>
              )}
            </div>
          </div>

          {/* Student Details & Prediction Engine */}
          <div className="lg:col-span-2 space-y-8">
            {!selectedStudent ? (
              <div className="h-full flex flex-col items-center justify-center border-2 border-dashed border-border rounded-2xl p-12 text-center bg-card/50">
                <div className="w-16 h-16 rounded-full bg-accent/10 flex items-center justify-center text-accent mb-4">
                  <Zap size={24} />
                </div>
                <h3 className="font-display font-semibold text-xl mb-2">Select a Student</h3>
                <p className="text-muted max-w-md">Select a student from the list to view their structural diagnosis and run the held-out prediction proof.</p>
              </div>
            ) : (
              <motion.div 
                initial={{ opacity: 0, y: 10 }} 
                animate={{ opacity: 1, y: 0 }}
                className="bg-card border border-border rounded-2xl p-8 shadow-sm"
              >
                <div className="flex justify-between items-start mb-8">
                  <div>
                    <h2 className="font-display text-3xl font-bold mb-2">{selectedStudent.name || `Student ${selectedStudent.student_id}`}</h2>
                    <p className="text-muted font-mono text-sm">{selectedStudent.student_id}</p>
                  </div>
                </div>

                <div className="bg-card-hover rounded-xl p-6 border border-border mb-8">
                  <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
                    <Lock size={18} className="text-accent" /> Held-out Prediction Workflow
                  </h3>
                  
                  {!predictionResult ? (
                    <div className="space-y-4">
                      <p className="text-muted text-sm">Lock the prediction to receive a cryptographic proof token based on visible work.</p>
                      <button 
                        onClick={() => handlePredict(selectedStudent.student_id)}
                        className="px-6 py-2.5 bg-foreground text-background rounded-lg font-medium hover:bg-foreground/90 transition-colors shadow-sm"
                      >
                        Lock Prediction
                      </button>
                    </div>
                  ) : !revealResult ? (
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
                      <div className="p-4 bg-accent/10 border border-accent/20 rounded-lg text-accent-hover text-sm font-mono break-all">
                        <strong>Token Issued:</strong> {predictionResult.proof_token}
                      </div>
                      <p className="text-muted text-sm">Submit the token to securely verify and reveal the separately stored answer.</p>
                      <button 
                        onClick={() => handleReveal(selectedStudent.student_id)}
                        className="px-6 py-2.5 bg-accent text-white rounded-lg font-medium hover:bg-accent-hover transition-colors shadow-sm flex items-center gap-2"
                      >
                        <Unlock size={18} /> Reveal Answer
                      </button>
                    </motion.div>
                  ) : (
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
                      <div className="grid md:grid-cols-2 gap-4">
                        <div className="p-5 bg-background border border-border rounded-xl">
                          <div className="text-xs text-muted uppercase font-semibold mb-2 tracking-wider">Predicted Answer</div>
                          <div className="font-mono text-xl">{revealResult.predicted_answer || "N/A"}</div>
                        </div>
                        <div className="p-5 bg-background border border-border rounded-xl">
                          <div className="text-xs text-muted uppercase font-semibold mb-2 tracking-wider">Actual Answer</div>
                          <div className="font-mono text-xl">{revealResult.actual_answer || "N/A"}</div>
                        </div>
                      </div>
                      <div className="p-3 bg-green-500/10 border border-green-500/20 text-green-700 rounded-lg flex items-center gap-2 text-sm">
                        <CheckCircle2 size={16} /> Token verified. Cryptographic proof accepted.
                      </div>
                    </motion.div>
                  )}
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
