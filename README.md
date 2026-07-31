<p align="center">
  <img src="packages/faultline_core/faultline_thumbnail.png" alt="FaultLine Logo" width="120" />
</p>

<h1 align="center">FaultLine</h1>

<p align="center">
  <strong>See the procedure behind the mistake.</strong><br/>
  Neuro-symbolic diagnosis that finds the exact cognitive error a student made — not just a score.
</p>

<p align="center">
  <a href="https://frontend-seven-mu-58.vercel.app"><img src="https://img.shields.io/badge/🚀 Live Demo-Vercel-orange?style=for-the-badge" alt="Live Demo"/></a>
  <a href="https://frontend-seven-mu-58.vercel.app/judge"><img src="https://img.shields.io/badge/🎬 Judge Mode-40s Cinematic-red?style=for-the-badge" alt="Judge Mode"/></a>
  <img src="https://img.shields.io/badge/Tests-33 passing-brightgreen?style=for-the-badge" alt="Tests"/>
  <img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="License"/>
</p>

---

## The Problem

A failing grade tells a teacher that a student failed. It **never** tells them why.

When a student consistently writes `1/2 + 1/3 = 2/5` — adding the denominators — a standard grading system records a wrong answer and moves on. The underlying procedural defect, *the exact systematic error that will compound across every future math topic*, remains invisible.

**FaultLine surfaces it.**

---

## 🎬 Live Demo

| Link | Description |
|------|-------------|
| **[frontend-seven-mu-58.vercel.app](https://frontend-seven-mu-58.vercel.app)** | Full interactive teacher dashboard |
| **[/judge](https://frontend-seven-mu-58.vercel.app/judge)** | 40-second cinematic pitch (autoplay) |
| **[/demo](https://frontend-seven-mu-58.vercel.app/demo)** | 12-student diagnostic class view |

---

## 🧠 The Core Innovation: Neuro-Symbolic AI

Most EdTech today wraps a generative LLM around a math problem and hopes it doesn't hallucinate. FaultLine takes the opposite approach: a **Neuro-Symbolic Architecture** where Machine Learning and deterministic arithmetic cover each other's weaknesses.

> **Key distinction:** The LLM never names a diagnosis. It strictly acts as a heuristic to shrink the search space. The **deterministic engine** makes the final call. Zero hallucinations by design.

### Neuro-Symbolic Pipeline

```mermaid
flowchart LR
    A["🧑‍🎓 Student Answer\n1/2 + 1/3 = 2/5"] --> B

    subgraph Neuro["⚡ Neuro Layer  —  LLM / Sequence Model"]
        B["Predict likely bugs\nfrom error history"]
        B --> C["Top-K candidates\nadd_denominators 85%\ncross_multiply 10%\nforget_reduce 5%"]
    end

    subgraph Symbolic["🔢 Symbolic Layer  —  Deterministic Arithmetic Engine"]
        C --> D["Execute each candidate\nwith exact rational math"]
        D --> E{"Match\nfound?"}
        E -->|Yes| F["✅ Named Diagnosis\nadd_denominators\nPosterior: 0.91"]
        E -->|No| G["Bayesian Updater\nP(H|E) = P(E|H)·P(H)/P(E)"]
        G --> H["Max Expected\nInformation Gain\nH = -Σ P·log₂P"]
        H --> I["🎯 Adaptive Question\nSelected for student"]
        I --> D
    end

    F --> J["👩‍🏫 Teacher Dashboard\nImmediate action item"]
```

---

## ⚙️ How It Works

### 1. Neuro-Symbolic Hypothesis Generation (Search Space Shrinker)
Instead of brute-forcing all ~50 possible procedural bugs, FaultLine uses a lightweight sequence model (trained on historical student error patterns) to rank the top-K most likely bugs. The deterministic arithmetic engine then **proves or disproves** each candidate with exact math.

### 2. Bayesian Active Learning (Exact Expected Information Gain)
When evidence is ambiguous, the system computes a posterior probability distribution across all hypotheses and selects the **exact next question** that maximizes Shannon Entropy reduction:

```
H(X) = -Σ P(x) · log₂(P(x))     ← Current uncertainty
EIG  = H_current - E[H_posterior] ← Expected reduction per question
```

The student answers one targeted question. The bug is isolated. No 20-question quiz required.

### 3. Confidence-Aware Gating (Not Confidently Wrong)
If evidence doesn't reach a confidence threshold, FaultLine **refuses to name a diagnosis**. It explicitly withholds its answer and issues a follow-up question instead. In our fixture: 11/12 named, 1/12 deliberately withheld.

### 4. Held-Out Prediction Proof (Tamper-Proof Fairness)
FaultLine locks a prediction **before** the student's answer is revealed, returns a signed cryptographic proof token, and only reveals the stored answer when that exact token is submitted.

---

## 📊 System Architecture

### Full Stack Overview

```mermaid
graph TB
    subgraph Client["🌐 Client Layer — Vercel CDN"]
        FE["Next.js 16 Frontend\nThree.js 3D Hero · Framer Motion\nfrontend-seven-mu-58.vercel.app"]
    end

    subgraph API["⚙️ API Layer"]
        FP["FastAPI · Uvicorn ASGI\nPort 8000"]
        MW["RequestSafetyMiddleware\nCORS · Rate Limiter"]
    end

    subgraph Core["🧠 Core Intelligence"]
        INF["inference.py\nDeterministic Procedure Engine"]
        ML["ml_engine.py\nNeuro-Symbolic Heuristic\nBayesian Active Learner"]
        IG["information_gain.py\nShannon Entropy · EIG"]
        MAL["malrules.py\nProcedural Bug DSL"]
        SYN["synthesis.py\nQuestion Generator"]
    end

    subgraph Data["💾 Data Layer"]
        STORE["In-Memory Job Store"]
        DATA["data/demo_class.json\n12-Student Fixture"]
    end

    subgraph External["🤖 External"]
        LLM["LLM / Vision Model\nHandwriting Parser\n(boundary interface)"]
    end

    FE -->|"REST JSON"| MW
    MW --> FP
    FP --> INF
    FP --> STORE
    STORE --> DATA
    INF --> ML
    INF --> MAL
    ML --> IG
    ML --> SYN
    FE -->|"Upload PNG/JPEG"| FP
    FP --> LLM
    LLM -->|"Structured expressions"| INF
```

---

### Request Flow — Worksheet Analysis

```mermaid
sequenceDiagram
    participant T as 👩‍🏫 Teacher
    participant FE as Next.js Frontend
    participant API as FastAPI
    participant SEG as segmentation.py
    participant LLM as LLM Parser
    participant ML as ml_engine.py
    participant INF as inference.py
    participant IG as information_gain.py

    T->>FE: Upload worksheet image
    FE->>API: POST /v1/analyses
    API->>SEG: normalize + crop (8 regions)
    SEG-->>API: Cropped student work
    API->>LLM: Parse handwriting
    LLM-->>API: Structured expressions
    API->>ML: predict_likely_bugs()
    Note over ML: LLM prunes 50 bugs → top 3
    ML-->>INF: Ranked candidates
    INF->>INF: Execute each deterministically
    alt Match found
        INF-->>API: Named diagnosis + posterior
    else Ambiguous
        INF->>IG: compute EIG
        IG-->>INF: Best next question
        INF-->>API: Follow-up question
    end
    API-->>FE: Diagnosis + actions
    FE-->>T: Dashboard view
```

---

### Held-Out Prediction Proof

```mermaid
sequenceDiagram
    participant J as 🧑‍⚖️ Judge
    participant API as FastAPI
    participant HOL as held_out.py

    J->>API: POST /v1/students/:id/held-out-prediction
    API->>HOL: create_prediction(student_id)
    Note over HOL: Prediction locked BEFORE answer revealed.<br/>Cryptographic proof_token generated.
    HOL-->>API: {hypothesis, confidence, proof_token}
    API-->>J: Return prediction + token
    Note over J: Judge verifies student's actual answer independently
    J->>API: POST /v1/students/:id/held-out-reveal {proof_token}
    API->>HOL: reveal_prediction(student_id, token)
    Note over HOL: Signature + student + age verified.<br/>Cross-student reuse rejected.
    HOL-->>API: {prediction_was, actual_was, match}
    API-->>J: ✅ Proof verified — no retroactive fitting
```

---

## 🏗️ Repository Structure

```mermaid
graph TD
    subgraph Repo["📦 Monorepo"]
        subgraph FE2["apps/frontend — Next.js 16"]
            P1["/ Landing + 3D Hero"]
            P2["/demo Teacher Dashboard"]
            P3["/judge 40s Cinematic Mode"]
        end
        subgraph BE["apps/api — FastAPI"]
            R["routes/api.py"]
            S["services/ demo · held_out · jobs"]
        end
        subgraph PKG["packages/faultline_core"]
            IN["inference.py"]
            ML2["ml_engine.py"]
            IG2["information_gain.py"]
            MR["malrules.py"]
        end
        subgraph D["data/"]
            DJ["demo_class.json"]
        end
    end

    subgraph Deploy["☁️ Deployment"]
        VCL["Vercel — Frontend"]
        SRV["Render / Docker — API"]
    end

    FE2 --> BE
    BE --> PKG
    PKG --> D
    FE2 --> VCL
    BE --> SRV
```

---

## 🔌 API Reference

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/health` | Health check and runtime mode |
| `GET` | `/v1/demo/classes/period-3` | 12-student synthetic class analysis |
| `POST` | `/v1/analyses?template_id=fractions-v1` | Upload worksheet PNG/JPEG |
| `GET` | `/v1/analyses/{id}` | Poll analysis job status |
| `PATCH` | `/v1/analyses/{id}/readings/{reading_id}` | Correct a reading, recompute |
| `GET` | `/v1/students/{id}/diagnostic-items` | Max-information-gain questions |
| `POST` | `/v1/students/{id}/held-out-prediction` | Lock prediction + issue proof token |
| `POST` | `/v1/students/{id}/held-out-reveal` | Verify token, reveal stored answer |

---

## 📈 Evaluation Results

> These are **regression results** on a deterministic synthetic fixture — not classroom accuracy or learning-impact claims.

| Metric | Result |
|--------|--------|
| Assigned-procedure top-rank identification | **12 / 12** |
| Named-diagnosis after confidence gating | **11 / 12** |
| Deliberate withheld diagnoses | **1 / 12** |
| Held-out answer leakage | **0** (blocked by tests) |
| Token tampering / cross-student reuse | **0** (blocked by tests) |
| Test suite | **33 / 33 passing** |

---

## 🔒 Security

- **Signed, expiring, student-bound proof tokens** — tampered tokens are rejected
- **Raw-body image upload** — no multipart parser dependency
- **Streaming 8MB size enforcement** — decompression bombs rejected
- **Real image byte verification** — MIME spoofing rejected
- **Zero image retention** — uploaded bytes are never stored
- **Sliding-window rate limits** on all write endpoints
- **CSP, anti-framing, MIME-sniffing, referrer, permissions headers**
- **Non-root Docker runtime** with read-only Compose filesystem
- **CORS opt-in only** via environment variable

See [`SECURITY.md`](SECURITY.md) for full details.

---

## 🚀 Run Locally

```bash
# 1. Clone and set up Python environment
git clone https://github.com/rahulgunwanistudy-2005/Faultline.git
cd Faultline
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

# 2. Start the backend API (port 8000)
./start.sh

# 3. Start the frontend (new terminal)
cd apps/frontend
npm install && npm run dev

# 4. Open
# Frontend:   http://localhost:3000
# API:        http://localhost:8000
# Judge Mode: http://localhost:3000/judge
# Health:     http://localhost:8000/health
```

### Environment Variables

```bash
# Required for production / multi-worker deployment
FAULTLINE_PROOF_SECRET=$(python -c "import secrets; print(secrets.token_urlsafe(48))")

# Optional: CORS origins (comma-separated)
FAULTLINE_CORS_ORIGINS=https://your-frontend.vercel.app
```

### Docker

```bash
docker-compose up --build
```

---

## ✅ Verify the Release

```bash
./scripts/verify_submission.sh
```

Checks:
1. Python compilation and categorical source sweeps
2. JavaScript syntax validation
3. Sanitized generated-fixture integrity
4. Core and API test suite (33 tests)
5. Project dependency-closure consistency
6. Reproducible fixture evaluation
7. Live HTTP and signed-proof smoke test
8. Deterministic release-manifest integrity

---

## 🎯 Deliberate Non-Claims

FaultLine is honest about what it is and isn't:

- ❌ No arbitrary worksheet-layout recognition
- ❌ No verified handwriting accuracy claims
- ❌ No causal learning-improvement percentages
- ❌ No mastery forecast or longitudinal learner model
- ❌ No autonomous LLM diagnosis *(LLM guides; math engine decides)*
- ✅ Exact deterministic diagnosis on the verified fixture
- ✅ Confidence-gated — refuses to guess when evidence is weak
- ✅ Cryptographically provable — no retroactive answer fitting

---

## 📄 License

MIT © FaultLine Team
