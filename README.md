# 🏥 DiabeTwin: Generative AI-Enabled Healthcare Digital Twin

## A "Thinking" Virtual Patient for Type 2 Diabetes Management

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red)
![GenAI](https://img.shields.io/badge/GenAI-Enabled-green)

---

## 🎯 Concept Overview & Motivation

**DiabeTwin** is a revolutionary Healthcare Digital Twin that creates a *living virtual patient* for Type 2 Diabetes management. Unlike traditional health dashboards that merely display data, DiabeTwin:

- **Simulates** health evolution over time based on lifestyle choices
- **Explains** why health metrics are changing using Generative AI
- **Predicts** multiple future scenarios with narrative comparisons
- **Remembers** past health states for counterfactual storytelling
- **Guides** patients with personalized, explainable recommendations

### The Core Innovation: Temporal Health Memory with Counterfactual Storytelling

Our novel contribution is **"Health Memory with Counterfactual Narratives"** - the digital twin maintains a complete temporal memory of all health states and can generate compelling counterfactual stories:

> *"If you had maintained your exercise routine from 3 months ago, your HbA1c would likely be 6.2% instead of 7.1% today. Here's what happened and how we can course-correct..."*

This transforms abstract health data into **personal health stories** that resonate emotionally and motivate behavior change.

---

## 🩺 Why Type 2 Diabetes?

Type 2 Diabetes is the ideal condition for demonstrating a thinking digital twin because:

1. **Lifestyle-Modifiable**: Diet, exercise, stress, and sleep directly impact outcomes
2. **Multi-Factorial**: Multiple interacting biomarkers create rich simulation space
3. **Temporal Dynamics**: Health changes gradually, enabling meaningful trajectory modeling
4. **Global Impact**: 537M people affected worldwide - massive real-world relevance
5. **Clear Metrics**: HbA1c, fasting glucose, weight, blood pressure are interpretable

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DiabeTwin Architecture                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────┐ │
│  │ Virtual Patient │    │  Health State   │    │ Temporal Evolution  │ │
│  │  Representation │───▶│     Model       │───▶│      Engine         │ │
│  │                 │    │                 │    │                     │ │
│  │ • Demographics  │    │ • Metabolic Sim │    │ • Time Stepping     │ │
│  │ • Baseline Vitals│   │ • Risk Scoring  │    │ • Trajectory Calc   │ │
│  │ • Lifestyle     │    │ • State Updates │    │ • Scenario Compare  │ │
│  └─────────────────┘    └─────────────────┘    └──────────┬──────────┘ │
│                                                           │             │
│                                                           ▼             │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    HEALTH MEMORY STORE                          │   │
│  │  [State₀] → [State₁] → [State₂] → ... → [Stateₙ] → [Futureₖ]   │   │
│  │                                                                 │   │
│  │  Enables: Counterfactual Analysis • Trend Detection • Memory    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                           │             │
│                                                           ▼             │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │              GENERATIVE AI NARRATIVE ENGINE                     │   │
│  │                                                                 │   │
│  │  • Health State Explainer    • Counterfactual Story Generator  │   │
│  │  • Personalized Guidance     • What-If Scenario Narrator       │   │
│  │  • Conversational Interface  • Trend Interpretation            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                           │             │
│                                                           ▼             │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                   INTERACTIVE INTERFACE                         │   │
│  │                                                                 │   │
│  │  🎛️ Lifestyle Sliders    📊 Trajectory Visualization           │   │
│  │  💬 Ask Your Twin        🔮 Parallel Futures Explorer          │   │
│  │  ⏪ Counterfactual View  📝 Personalized Action Plan           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

```bash
Python 3.9+
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file with your API key:

```env
OPENAI_API_KEY=your_openai_api_key_here
# OR for Azure OpenAI:
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_key
AZURE_OPENAI_DEPLOYMENT=gpt-4
```

### Run the Application

```bash
streamlit run app.py
```

---

## ☁️ Deploy to Streamlit Cloud

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit - DiabeTwin Healthcare Digital Twin"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/diabetwin.git
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"**
3. Connect your GitHub repository
4. Set:
   - **Repository**: `YOUR_USERNAME/diabetwin`
   - **Branch**: `main`
   - **Main file path**: `app.py`
5. Click **"Deploy"**

### Step 3: Add Secrets

1. Go to your app's **Settings** → **Secrets**
2. Add your OpenAI API key:

```toml
OPENAI_API_KEY = "sk-your-api-key-here"
```

3. Save and reboot the app

> 💡 **Note**: The app works in fallback mode without an API key, using template-based responses for demo purposes.

---

## 📁 Project Structure

```
DIGITAL_TWIN/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── README.md                  # This file
│
├── core/
│   ├── __init__.py
│   ├── virtual_patient.py     # Virtual patient representation
│   ├── health_state.py        # Health state model & calculations
│   ├── temporal_engine.py     # Time evolution & trajectory simulation
│   └── health_memory.py       # Temporal health memory store
│
├── genai/
│   ├── __init__.py
│   ├── narrative_engine.py    # Generative AI explanation engine
│   ├── counterfactual.py      # Counterfactual story generator
│   └── prompts.py             # Prompt templates
│
├── ui/
│   ├── __init__.py
│   ├── components.py          # Reusable UI components
│   ├── visualizations.py      # Charts and trajectory plots
│   └── chat_interface.py      # Conversational twin interface
│
└── data/
    └── synthetic_profiles.json # Pre-built patient profiles
```

---

## 🏆 Hackathon Pitch (30-Second Version)

> **DiabeTwin** is a Generative AI-powered Healthcare Digital Twin that doesn't just show you health data—it **thinks**, **explains**, and **guides** like a personal health companion.
>
> Our innovation: **Counterfactual Health Storytelling**. The twin remembers your entire health journey and can answer questions like *"What if I had started walking daily 6 months ago?"* with a personalized narrative showing exactly where you'd be today.
>
> We transform abstract HbA1c numbers into **personal health stories** that motivate real behavior change. This is the future of patient-centered chronic disease management.

---

## ⚠️ Disclaimer

This is a **research prototype** for demonstration purposes only. It uses synthetic data and simplified models. It is NOT intended for clinical use or medical decision-making.

---

## 📜 License

MIT License - Built for Healthcare AI Innovation
