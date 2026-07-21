import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Code, Briefcase, Globe } from "lucide-react";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AstroLens - Deep Space Neural Detection",
  description: "AI-powered gravitational lens detector using SDSS data",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-[#0a0a0f] text-slate-200">
        <div className="flex-1">{children}</div>
        
        {/* Global Footer */}
        <footer className="border-t border-white/10 py-8 relative z-20 bg-[#0a0a0f]/80 backdrop-blur-md">
          <div className="max-w-7xl mx-auto px-8 flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="flex items-center gap-6 text-slate-400">
              <a href="https://portafolio-jscode7.vercel.app/" target="_blank" rel="noopener noreferrer" className="hover:text-purple-400 transition-colors flex items-center gap-2 text-sm">
                <Globe className="w-4 h-4" /> Portafolio
              </a>
              <a href="https://github.com/JsCode7" target="_blank" rel="noopener noreferrer" className="hover:text-purple-400 transition-colors flex items-center gap-2 text-sm">
                <Code className="w-4 h-4" /> GitHub
              </a>
              <a href="https://www.linkedin.com/in/jdsmdeveloper/" target="_blank" rel="noopener noreferrer" className="hover:text-purple-400 transition-colors flex items-center gap-2 text-sm">
                <Briefcase className="w-4 h-4" /> LinkedIn
              </a>
            </div>
            
            <div className="text-slate-500 text-sm font-mono text-center md:text-right">
              Desarrollado en conjunto con <span className="text-slate-300 font-semibold tracking-wide">Antigravity</span> <span className="text-purple-400">by Google</span>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
