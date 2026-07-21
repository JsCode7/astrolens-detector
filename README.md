# AstroLens Detector

**AstroLens Detector** is a full-stack, machine learning-powered platform designed to automatically identify and analyze strong gravitational lensing events from telescope imagery (such as the Sloan Digital Sky Survey - SDSS). 

Gravitational lensing occurs when a massive foreground object warps spacetime, bending the light of a background source and creating observable phenomena like Einstein rings. Finding these rare occurrences usually requires extensive manual labor. AstroLens automates this search pipeline using computer vision.

---

## 🔬 Scientific Context & The "Sim-to-Real" Gap

AstroLens employs a ResNet18 Convolutional Neural Network (CNN) to process astronomical images in the FITS (Flexible Image Transport System) format. 

### Synthetic Dataset Generation
To bypass the scarcity of labeled gravitational lens data, the system leverages a robust synthetic dataset generator. The physical simulations use `lenstronomy` to model:
- **Singular Isothermal Ellipsoid (SIE)** mass distributions.
- **External Shear** parameters to account for environmental gravitational pull.
- **Atmospheric Point Spread Functions (PSF)** mimicking the blurring effects of ground-based observatories.

### Domain Adaptation Challenge
A critical challenge in this pipeline is the **Sim-to-Real Gap**. Neural networks trained exclusively on mathematically pristine backgrounds (pure Poisson/Gaussian noise) experience catastrophic performance degradation (nearly 100% false negative rates) when exposed to real sky surveys. 

True telescope data contains background galaxies, star diffraction spikes, cosmic ray hits, and sensor read noise. To close this gap, AstroLens implements a hybrid training strategy: downloading real, empty-sky SDSS cutouts via `astroquery` and directly superimposing our simulated Einstein rings onto these authentic noisy backgrounds. This forces the model to learn geometry over simple photometric intensity (preventing data leakage).

---

## 🏗️ System Architecture (E2E)

AstroLens operates on a decoupled, highly asynchronous End-to-End architecture:

1. **Frontend (Next.js / React)**
   - Modern, reactive UI providing candidate visualization, sorting algorithms, and real-time inference polling.
2. **Backend API (FastAPI / Python)**
   - RESTful API handling incoming workloads.
   - Integrated with **Supabase** (PostgreSQL & Storage) to persist inference history, user data, and processed image previews.
3. **Inference Worker (PyTorch)**
   - Asynchronous worker node polling for jobs. 
   - Uses `astroquery` to fetch required FITS files.
   - Applies robust astronomical normalization algorithms (`ZScaleInterval`).
   - Executes the ResNet18 forward pass. 
   - If a lens is detected with high confidence, triggers a dynamic mass reconstruction simulation.
4. **Machine Learning Training Pipeline**
   - High-performance PyTorch training scripts utilizing DirectML for hardware-agnostic GPU acceleration on local hardware (e.g., AMD GPUs).

---

## 🚀 Local Development Setup

To run the full stack locally, you need three separate terminal instances (ensure you configure your `.env` variables with the required Supabase keys prior to launch).

### 1. Backend API (FastAPI)
```powershell
cd backend_worker
# Activate your virtual environment
.\venv\Scripts\activate
uvicorn main:app --reload
```

### 2. Inference Worker (PyTorch)
```powershell
cd backend_worker
# Activate your virtual environment
.\venv\Scripts\activate
python worker.py
```

### 3. Frontend (Next.js)
```powershell
cd frontend
npm install
npm run dev
```

---

*Note: This repository does not contain sensitive API keys or large model weight files (`.pth`), as they are excluded by design.*
