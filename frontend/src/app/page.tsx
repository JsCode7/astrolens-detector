"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Telescope, Send, Orbit, Activity, ShieldAlert, Sparkles, RefreshCcw, HelpCircle } from "lucide-react";

interface Candidate {
  id: number;
  job_id: number;
  candidate_name: string;
  confidence_score: number;
  image_url: string;
  redshift?: number;
  magnitude?: number;
  attention_image_url?: string;
}

interface Job {
  id: number;
  job_name: string;
  status: string;
  created_at: string;
}

export default function Dashboard() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [jobName, setJobName] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [countdown, setCountdown] = useState(5);
  const [sortBy, setSortBy] = useState("newest");
  const [activeJobs, setActiveJobs] = useState<Job[]>([]);

  useEffect(() => {
    async function fetchCandidates() {
      try {
        const res = await fetch("http://localhost:8000/api/candidates");
        if (!res.ok) {
          throw new Error("Failed to fetch candidates");
        }
        const data = await res.json();
        setCandidates(data);
        setError(null);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    
    async function fetchActiveJobs() {
      try {
        const res = await fetch("http://localhost:8000/api/jobs/active");
        if (res.ok) {
          const data = await res.json();
          setActiveJobs(data);
        }
      } catch (err) {
        console.error("Failed to fetch active jobs:", err);
      }
    }
    
    fetchCandidates();
    fetchActiveJobs();
    const fetchInterval = 5000;
    
    const interval = setInterval(() => {
      setCountdown(fetchInterval / 1000);
      fetchCandidates();
      fetchActiveJobs();
    }, fetchInterval);

    const countdownInterval = setInterval(() => {
      setCountdown((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);

    return () => {
      clearInterval(interval);
      clearInterval(countdownInterval);
    };
  }, []);

  async function handleSubmitJob(e: React.FormEvent) {
    e.preventDefault();
    if (!jobName.trim()) return;
    setSubmitting(true);
    try {
      const res = await fetch("http://localhost:8000/api/jobs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job_name: jobName }),
      });
      if (!res.ok) {
        throw new Error("Failed to submit job");
      }
      setJobName("");
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-slate-200 font-sans relative overflow-hidden">
      {/* Background Nebula Effects */}
      <div className="absolute top-0 left-0 w-[500px] h-[500px] bg-purple-600/20 rounded-full blur-[120px] pointer-events-none mix-blend-screen" />
      <div className="absolute bottom-0 right-0 w-[600px] h-[600px] bg-blue-600/10 rounded-full blur-[150px] pointer-events-none mix-blend-screen" />

      <main className="max-w-7xl mx-auto p-8 relative z-10 flex flex-col gap-10">
        <header className="flex flex-col md:flex-row justify-between items-center gap-6 pb-6 border-b border-white/10">
          <div className="flex items-center gap-4 w-full md:w-1/3">
            <div className="p-3 bg-white/5 rounded-2xl border border-white/10 backdrop-blur-sm shadow-xl">
              <Telescope className="w-8 h-8 text-purple-400" />
            </div>
            <div>
              <h1 className="text-4xl font-extrabold bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 bg-clip-text text-transparent tracking-tight">
                AstroLens
              </h1>
              <p className="text-slate-400 text-sm mt-1 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-pink-400/70" />
                Deep Space Neural Detection
              </p>
            </div>
          </div>

          <div className="flex justify-center w-full md:w-1/3">
            <Link href="/about" className="text-sm font-medium bg-purple-500/10 hover:bg-purple-500/20 transition-all border border-purple-500/30 px-5 py-2.5 rounded-full text-purple-200 flex items-center gap-2 shadow-lg backdrop-blur-md shadow-purple-500/10 hover:scale-105">
              <HelpCircle className="w-4 h-4 text-purple-300" />
              Science & Q&A
            </Link>
          </div>

          <form onSubmit={handleSubmitJob} className="flex items-center justify-end gap-3 w-full md:w-1/3">
            <div className="relative flex-1 md:w-64">
              <input
                type="text"
                placeholder="RA DEC (e.g. 179.689 -0.454)"
                value={jobName}
                onChange={(e) => setJobName(e.target.value)}
                className="w-full bg-black/40 border border-white/10 rounded-xl py-2.5 pl-4 pr-10 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-transparent placeholder:text-slate-500 backdrop-blur-md transition-all"
              />
            </div>
            <button
              type="submit"
              disabled={submitting}
              className="bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white p-2.5 rounded-xl transition-all shadow-lg shadow-purple-500/25 flex items-center justify-center border border-purple-400/30"
            >
              {submitting ? <RefreshCcw className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
            </button>
          </form>
        </header>
        
        {loading && (
          <div className="flex items-center justify-center py-20">
            <div className="animate-pulse flex flex-col items-center gap-4">
              <Orbit className="w-12 h-12 text-purple-400 animate-spin-slow" />
              <p className="text-purple-400/60 tracking-widest text-sm font-medium uppercase">Scanning Sectors...</p>
            </div>
          </div>
        )}
        
        {/* Active Jobs Progress Bar */}
        {activeJobs.length > 0 && (
          <div className="bg-purple-900/20 border border-purple-500/30 rounded-xl p-5 mb-4 backdrop-blur-md shadow-lg shadow-purple-900/20 relative overflow-hidden">
            {/* Animated progress background */}
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-purple-500/10 to-transparent animate-[shimmer_2s_infinite] -translate-x-full" />
            
            <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-4">
                <div className="bg-purple-500/20 p-2.5 rounded-full animate-pulse border border-purple-500/40">
                  <Activity className="w-6 h-6 text-purple-400" />
                </div>
                <div>
                  <h3 className="text-purple-100 font-semibold flex items-center gap-2">
                    Processing Anomalies 
                    <span className="bg-purple-500 text-white text-[10px] px-2 py-0.5 rounded-full animate-pulse">
                      {activeJobs.length} ACTIVE
                    </span>
                  </h3>
                  <p className="text-xs text-purple-300/70 mt-1">
                    Worker is running sliding window inference. This may take up to 20 seconds per sector...
                  </p>
                </div>
              </div>
              
              <div className="w-full md:w-64 flex flex-col gap-2">
                <div className="flex justify-between text-[10px] text-purple-300/80 font-mono uppercase">
                  <span>AI Scanning</span>
                  <span className="animate-pulse">Running</span>
                </div>
                <div className="h-2 w-full bg-black/50 rounded-full overflow-hidden border border-white/5">
                  <div className="h-full bg-gradient-to-r from-purple-600 to-pink-500 rounded-full w-full animate-[indeterminate_2s_infinite_ease-in-out] origin-left" />
                </div>
              </div>
            </div>
          </div>
        )}

        {!loading && !error && candidates.length > 0 && (
          <div className="flex flex-col md:flex-row justify-between items-center text-xs text-slate-400 bg-white/[0.02] border border-white/5 p-3 rounded-xl">
            <div className="flex items-center gap-4">
              <p className="flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-purple-400" />
                Physics Engine (Lenstronomy) only triggers for candidates with &gt; 85% AI Probability.
              </p>
              
              <select 
                value={sortBy} 
                onChange={(e) => setSortBy(e.target.value)}
                className="bg-black/50 border border-white/10 rounded-lg px-3 py-1.5 text-slate-300 focus:outline-none focus:ring-1 focus:ring-purple-500"
              >
                <option value="newest">Newest First</option>
                <option value="oldest">Oldest First</option>
                <option value="prob_high">Highest Probability</option>
                <option value="prob_low">Lowest Probability</option>
              </select>
            </div>
            
            <div className="flex items-center gap-2 mt-2 md:mt-0 font-mono">
              <RefreshCcw className={`w-3 h-3 ${countdown === 0 ? 'animate-spin text-purple-400' : 'text-slate-500'}`} />
              Auto-refreshing in {countdown}s...
            </div>
          </div>
        )}
        
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 flex items-center gap-3 text-red-400">
            <ShieldAlert className="w-5 h-5" />
            <p>{error}</p>
          </div>
        )}
        
        {!loading && !error && candidates.length === 0 && (
          <div className="flex flex-col items-center justify-center py-32 text-slate-500 border border-white/5 rounded-3xl bg-white/[0.02] backdrop-blur-sm">
            <Telescope className="w-16 h-16 mb-4 opacity-20" />
            <p className="text-lg">No anomalies detected in the current sector.</p>
            <p className="text-sm mt-2 opacity-60">Submit a new job to commence scanning.</p>
          </div>
        )}

        {!loading && !error && candidates.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            {[...candidates].sort((a, b) => {
              if (sortBy === 'newest') return b.id - a.id;
              if (sortBy === 'oldest') return a.id - b.id;
              if (sortBy === 'prob_high') return b.confidence_score - a.confidence_score;
              if (sortBy === 'prob_low') return a.confidence_score - b.confidence_score;
              return 0;
            }).map((candidate) => (
              <div key={candidate.id} className="group relative bg-white/[0.03] border border-white/10 rounded-2xl overflow-hidden hover:bg-white/[0.05] transition-all duration-500 backdrop-blur-md shadow-2xl hover:shadow-purple-500/10 hover:-translate-y-1">
                {/* Images Container */}
                <div className="flex h-48 border-b border-white/10 bg-black/50">
                  <div className="w-1/2 relative border-r border-white/10 overflow-hidden">
                    {candidate.image_url ? (
                      <a href={candidate.image_url} target="_blank" rel="noopener noreferrer" className="block w-full h-full cursor-zoom-in">
                        <img src={candidate.image_url} alt="Source" className="object-cover w-full h-full opacity-80 group-hover:opacity-100 transition-opacity duration-500 hover:scale-105 transition-transform" />
                      </a>
                    ) : (
                      <div className="flex items-center justify-center h-full text-slate-600 text-xs">No Source</div>
                    )}
                    <div className="absolute top-2 left-2 bg-black/60 backdrop-blur-md text-[10px] px-2 py-1 rounded text-slate-300 font-mono uppercase tracking-wider">Source</div>
                  </div>
                  <div className="w-1/2 relative overflow-hidden">
                    {candidate.attention_image_url ? (
                      <a href={candidate.attention_image_url} target="_blank" rel="noopener noreferrer" className="block w-full h-full cursor-zoom-in">
                        <img src={candidate.attention_image_url} alt="Attention" className="object-cover w-full h-full opacity-80 group-hover:opacity-100 transition-opacity duration-500 mix-blend-screen hover:scale-105 transition-transform" />
                      </a>
                    ) : (
                      <div className="flex items-center justify-center h-full text-slate-600 text-xs">No Attention Map</div>
                    )}
                    <div className="absolute top-2 right-2 bg-purple-500/20 border border-purple-500/30 backdrop-blur-md text-[10px] px-2 py-1 rounded text-purple-300 font-mono uppercase tracking-wider">AI Vision</div>
                  </div>
                </div>

                {/* Content */}
                <div className="p-5 flex flex-col gap-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="text-xl font-semibold text-slate-100 group-hover:text-purple-300 transition-colors">
                        {candidate.candidate_name}
                      </h3>
                      <p className="text-xs text-slate-500 font-mono mt-1">
                        JOB ID: #{candidate.job_id} • CANDIDATE: #{candidate.id}
                      </p>
                    </div>
                    
                    {/* Confidence Badge */}
                    <div className={`flex flex-col items-end`}>
                      <span className={`text-2xl font-bold ${candidate.confidence_score > 0.8 ? 'text-green-400' : candidate.confidence_score > 0.5 ? 'text-yellow-400' : 'text-slate-400'}`}>
                        {(candidate.confidence_score * 100).toFixed(1)}%
                      </span>
                      <span className="text-[9px] uppercase tracking-widest text-slate-500">Probability</span>
                    </div>
                  </div>

                  {/* Physics Metrics */}
                  <div className="grid grid-cols-2 gap-3 mt-2">
                    <div className="bg-black/30 border border-white/5 rounded-xl p-3 flex items-center gap-3">
                      <Orbit className="w-4 h-4 text-blue-400/70" />
                      <div>
                        <p className="text-[10px] text-slate-500 uppercase tracking-wider">Redshift (z)</p>
                        <p className="text-sm font-mono text-slate-300">
                          {candidate.redshift !== null && candidate.redshift !== undefined ? candidate.redshift.toFixed(4) : 'N/A'}
                        </p>
                      </div>
                    </div>
                    <div className="bg-black/30 border border-white/5 rounded-xl p-3 flex items-center gap-3">
                      <Activity className="w-4 h-4 text-pink-400/70" />
                      <div>
                        <p className="text-[10px] text-slate-500 uppercase tracking-wider">Apparent Mag (g)</p>
                        <p className="text-sm font-mono text-slate-300">
                          {candidate.magnitude !== null && candidate.magnitude !== undefined ? candidate.magnitude.toFixed(2) : 'N/A'}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Accent glow on hover */}
                <div className="absolute inset-0 bg-gradient-to-t from-purple-500/5 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
