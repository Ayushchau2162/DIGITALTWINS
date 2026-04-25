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






🩺 Why Type 2 Diabetes?
Type 2 Diabetes is the ideal condition for demonstrating a thinking digital twin because:

Lifestyle-Modifiable: Diet, exercise, stress, and sleep directly impact outcomes
Multi-Factorial: Multiple interacting biomarkers create rich simulation space
Temporal Dynamics: Health changes gradually, enabling meaningful trajectory modeling
Global Impact: 537M people affected worldwide - massive real-world relevance
Clear Metrics: HbA1c, fasting glucose, weight, blood pressure are interpretable


🚀 Quick Start
Prerequisites

💡 Developer Tip (important for your project)
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python -m streamlit run app.py

🚀 Streamlit
Streamlit is an open-source Python framework used to build interactive web applications and dashboards. It allows developers to convert simple Python scripts into user-friendly web apps without needing frontend technologies like HTML, CSS, or JavaScript. Streamlit provides built-in components such as charts, buttons, and file uploaders, making development fast and efficient. It is widely used for data visualization, machine learning applications, and rapid prototyping.
