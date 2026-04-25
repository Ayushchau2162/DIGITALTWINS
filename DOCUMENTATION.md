# DiabeTwin: Technical Documentation

## Complete System Architecture & Design Decisions

---

## 1. Concept Overview & Motivation

### The Problem
Traditional health dashboards show data but don't help patients understand:
- *Why* their health is changing
- *What* would happen if they made different choices
- *How* to take actionable steps toward improvement

### Our Solution: A "Thinking" Digital Twin
DiabeTwin is not a dashboard—it's a **virtual patient** that:
- **Simulates** health evolution based on lifestyle choices
- **Explains** the reasoning behind health changes
- **Predicts** multiple future scenarios with narrative comparison
- **Remembers** past states for counterfactual analysis
- **Guides** with personalized, actionable recommendations

### Core Innovation: Temporal Health Memory with Counterfactual Storytelling
Our breakthrough feature answers the question: *"What if I had made different choices X months ago?"*

This creates a "health time machine" experience that:
1. Shows patients what could have been
2. Explains the mechanisms behind the difference
3. Pivots to hope by showing how to achieve those outcomes starting today

---

## 2. Why Type 2 Diabetes?

Type 2 Diabetes is ideal for demonstrating a thinking digital twin:

| Factor | Why It Matters |
|--------|----------------|
| **Lifestyle-Modifiable** | Diet, exercise, stress directly impact outcomes |
| **Multi-Factorial** | Multiple interacting biomarkers create rich simulation |
| **Temporal Dynamics** | Changes happen gradually over months |
| **Clear Metrics** | HbA1c, glucose, weight, BP are interpretable |
| **Global Impact** | 537M people affected—massive relevance |

---

## 3. Virtual Patient Definition

### PatientProfile (Static Attributes)
```python
@dataclass
class PatientProfile:
    patient_id: str          # Unique identifier
    name: str                # Display name
    age: int                 # Years (affects risk calculations)
    biological_sex: str      # male/female
    height_cm: float         # For BMI calculation
    years_since_diagnosis: int   # Duration of diabetes
    family_history_diabetes: bool
    has_hypertension: bool
    has_dyslipidemia: bool
    has_cardiovascular_disease: bool
    genetic_risk_factor: float   # 0-1 scale
```

### LifestyleFactors (Modifiable Behaviors)
```python
@dataclass
class LifestyleFactors:
    # Physical Activity
    exercise_minutes_per_week: int   # Target: 150+
    activity_level: ActivityLevel    # sedentary → very_active
    
    # Nutrition
    diet_quality: DietQuality        # poor → excellent
    daily_carb_intake_grams: int
    sugary_drinks_per_week: int
    
    # Sleep & Stress
    average_sleep_hours: float       # Target: 7-8
    stress_score: float              # 0-1 (higher = worse)
    
    # Treatment
    medication_adherence: float      # 0-1 (target: >0.9)
```

### Health Metrics (Biomarkers)
```python
# Core metrics tracked:
- hba1c_percent         # 2-3 month glucose average (target <7%)
- fasting_glucose_mgdl  # Morning glucose (target 80-130)
- weight_kg             # Body weight
- systolic_bp           # Blood pressure systolic
- diastolic_bp          # Blood pressure diastolic
- ldl_cholesterol_mgdl  # "Bad" cholesterol
- hdl_cholesterol_mgdl  # "Good" cholesterol
- triglycerides_mgdl    # Blood fats
```

---

## 4. Health State Model & Evolution Logic

### Design Philosophy
The model is designed to be:
- **Interpretable**: Every calculation can be explained
- **Physiologically Plausible**: Based on established relationships
- **Simplified**: Educational model, not clinical precision

### HbA1c Evolution Model

```python
def compute_hba1c_change(lifestyle_factors, current_hba1c, time_delta):
    # Natural drift (beta-cell decline)
    natural_drift = 0.02 * genetic_risk * time_delta
    
    # Diet effect: ±0.3% per month maximum
    diet_effect = (0.5 - diet_score) * 0.3 * time_delta
    
    # Activity effect: ±0.2% per month maximum
    activity_effect = (0.5 - activity_score) * 0.2 * time_delta
    
    # Medication effect: scales with distance from target
    medication_effect = -adherence * 0.15 * distance_from_target * time_delta
    
    return natural_drift + diet_effect + activity_effect + medication_effect
```

### Key Relationships Modeled

| Input Factor | Effect on HbA1c | Effect on Weight | Effect on BP |
|--------------|-----------------|------------------|--------------|
| Better Diet | ↓ 0.3%/month | ↓ 1.5kg/month | ↓ indirect |
| More Exercise | ↓ 0.2%/month | ↓ 1.0kg/month | ↓ 4mmHg/month |
| Less Stress | ↓ indirect | ↓ 0.5kg/month | ↓ 5mmHg/month |
| Better Meds | ↓ 0.15-0.5% | - | ↓ 5mmHg/month |

### Biological Variability
The model includes realistic variability:
```python
variability = random.gauss(0, scale * variability_factor)
```

This ensures simulations look realistic, not perfectly smooth.

---

## 5. Generative AI Explanation Mechanism

### Architecture

```
Patient Data → Prompt Construction → LLM Call → Response Parsing → Narrative
      ↓              ↓                   ↓              ↓
 Structured     Template-based      GPT-4 or      Post-processing
   JSON         with data slots    Fallback mode   and validation
```

### Key Design Decisions

1. **Data-Grounded Prompts**: Every prompt explicitly includes patient data
   - AI must reason FROM the data, not give generic advice

2. **Fallback Mode**: Works without API keys
   - Template-based responses for demo purposes
   - Full functionality with OpenAI/Azure OpenAI

3. **Prompt Templates**: Specialized for each narrative type
   - Health explanation
   - Trajectory comparison
   - Counterfactual storytelling
   - Conversational response
   - Action plan generation

### Example: Counterfactual Prompt Structure

```python
COUNTERFACTUAL_NARRATIVE = """
THE PAST ({months_ago} months ago):
- HbA1c was: {past_hba1c}%
- Lifestyle was: {past_lifestyle}

WHAT ACTUALLY HAPPENED (Today):
- HbA1c is now: {current_hba1c}%
- Change: {actual_change}

WHAT IF they had followed: {alternative_lifestyle}

SIMULATED ALTERNATIVE:
- HbA1c would be: {counterfactual_hba1c}%

Create a narrative that:
1. Acknowledges what happened without blame
2. Paints the alternative future vividly
3. Explains the mechanisms
4. Pivots to HOPE: how to still achieve this
"""
```

---

## 6. Interactive Digital Twin Exploration

### Lifestyle Controls
Interactive sliders and selectors for:
- Exercise minutes per week (0-300)
- Diet quality (poor → excellent)
- Medication adherence (0-100%)
- Stress level (low → severe)
- Sleep hours (4-10)

### What-If Scenarios
Pre-defined scenarios:
- **Baseline**: Continue current behavior
- **Better Nutrition**: Improved diet
- **Active Lifestyle**: More exercise
- **Comprehensive**: All improvements
- **Warning: Decline**: What if habits worsen

### User Interaction Flow
```
1. View Current Status → Understand baseline
2. Adjust Lifestyle Sliders → Define intervention
3. Run Simulation → See projected trajectory
4. Compare Scenarios → Evaluate options
5. Explore Counterfactual → "What if I had..."
6. Ask Your Twin → Get explanations
7. Generate Action Plan → Take next steps
```

---

## 7. Innovation Highlight: Counterfactual Health Storytelling

### The Concept
Most health apps show: "Here's where you are, here's what you should do."

DiabeTwin adds: **"Here's where you could have been, and here's how to get there."**

### How It Works

1. **Health Memory Store**: Complete history of health states
   ```python
   class HealthMemory:
       snapshots: List[HealthSnapshot]  # All past states
       milestones: List[Milestone]      # Achievements/concerns
       predictions: List[Prediction]    # Past predictions + outcomes
   ```

2. **Counterfactual Simulation**: Run alternative timeline
   ```python
   # Simulate what would have happened with different choices
   counterfactual_trajectory = engine.simulate_trajectory(
       patient=patient,
       months=months_back,
       lifestyle_overrides=alternative_lifestyle
   )
   ```

3. **Narrative Generation**: AI creates compelling story
   - "The path you took..."
   - "The road not taken..."
   - "The good news: starting today..."

### Psychological Impact
This approach:
- Creates emotional engagement through storytelling
- Avoids blame while showing consequences
- Provides hope through actionable recovery paths
- Motivates behavior change through vivid future visualization

---

## 8. Limitations & Assumptions

### Model Limitations
- **Simplified Physiology**: Real diabetes is more complex
- **Linear Relationships**: Actual effects are non-linear
- **Missing Factors**: Genetics, medications, comorbidities simplified
- **No Acute Events**: Doesn't model hypoglycemia, illness, etc.

### Data Limitations
- **Synthetic Only**: All data is generated, not real
- **No Validation**: Model not validated against clinical data
- **Limited Demographics**: Simplified patient profiles

### Scope Limitations
- **Educational Only**: Not for clinical decisions
- **Single Condition**: Focused on T2D only
- **Time Granularity**: Monthly steps, not daily

### Important Disclaimers
```
⚠️ This is a RESEARCH PROTOTYPE for DEMONSTRATION purposes only.
- Uses synthetic data and simplified models
- NOT intended for clinical diagnosis or treatment
- NOT a substitute for professional medical advice
- Always consult healthcare providers for medical decisions
```

---

## 9. Hackathon Pitch Summary

> **DiabeTwin** is a Generative AI-powered Healthcare Digital Twin that doesn't just show you health data—it **thinks**, **explains**, and **guides** like a personal health companion.
>
> **Our Innovation**: Counterfactual Health Storytelling. The twin remembers your entire health journey and answers questions like *"What if I had started walking daily 6 months ago?"* with a personalized narrative showing exactly where you'd be today—and how to get there starting now.
>
> We transform abstract HbA1c numbers into **personal health stories** that motivate real behavior change. This is the future of patient-centered chronic disease management.
>
> **Key Differentiators**:
> - 🧠 AI that reasons FROM patient data, never generic
> - ⏰ Temporal memory enables counterfactual analysis
> - 📖 Storytelling creates emotional engagement
> - 🎯 Actionable guidance grounded in simulations
> - 💡 Fully explainable model logic

---

## 10. Running the Application

### Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. (Optional) Configure AI
cp .env.example .env
# Add your OPENAI_API_KEY to .env

# 3. Run the application
streamlit run app.py
```

### Features by Tab

| Tab | Description |
|-----|-------------|
| **Current Status** | View patient metrics, AI analysis |
| **Simulate Future** | Project health trajectories |
| **Counterfactual** | "What if" historical analysis |
| **Lifestyle Lab** | Interactive experimentation |
| **Ask Your Twin** | Conversational AI interface |
| **Action Plan** | Personalized next steps |

---

## Appendix: Code Structure

```
DIGITAL_TWIN/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── README.md                  # Quick start guide
├── DOCUMENTATION.md           # This file
│
├── core/                      # Core simulation engine
│   ├── __init__.py
│   ├── virtual_patient.py     # Patient representation
│   ├── health_state.py        # Health state model
│   ├── temporal_engine.py     # Time evolution
│   └── health_memory.py       # Temporal memory store
│
├── genai/                     # Generative AI components
│   ├── __init__.py
│   ├── narrative_engine.py    # Main AI engine
│   ├── counterfactual.py      # Counterfactual generator
│   └── prompts.py             # Prompt templates
│
├── ui/                        # User interface
│   ├── __init__.py
│   ├── components.py          # UI components
│   ├── visualizations.py      # Charts
│   └── chat_interface.py      # Conversational UI
│
└── data/                      # Sample data
    └── synthetic_profiles.json
```

---

*DiabeTwin: Transforming health data into personal health stories.*
