"""
DiabeTwin - Healthcare Digital Twin for Type 2 Diabetes
Main Streamlit Application

This is the entry point for the DiabeTwin application.
Run with: streamlit run app.py
"""

import streamlit as st
import os
import uuid
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import core modules
from core.virtual_patient import (
    VirtualPatient, 
    PatientProfile, 
    LifestyleFactors,
    create_synthetic_patient,
    ActivityLevel,
    DietQuality,
    StressLevel
)
from core.health_state import HealthState, HealthStateModel
from core.temporal_engine import TemporalEvolutionEngine, ScenarioType
from core.health_memory import HealthMemory, HealthSnapshot

# Import GenAI modules
from genai.narrative_engine import NarrativeEngine
from genai.counterfactual import CounterfactualStoryGenerator

# Import UI modules
from ui.components import (
    render_metric_card,
    render_patient_profile,
    render_lifestyle_controls,
    render_health_metrics_dashboard,
    render_scenario_selector,
    render_time_horizon_selector,
    render_counterfactual_selector,
    render_disclaimer,
    render_sidebar_info
)
from ui.visualizations import (
    create_trajectory_chart,
    create_comparison_chart,
    create_hba1c_gauge,
    create_health_score_gauge,
    create_lifestyle_radar,
    create_counterfactual_comparison
)
from ui.chat_interface import render_chat_interface


# Page configuration
st.set_page_config(
    page_title="DiabeTwin - Healthcare Digital Twin",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS for Beautiful UI
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Header Styles */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f64f59 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1.5rem 0;
        letter-spacing: -0.02em;
        animation: fadeIn 1s ease-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .sub-header {
        text-align: center;
        color: #6b7280;
        margin-bottom: 2rem;
        font-size: 1.1rem;
        font-weight: 400;
    }
    
    /* Card Styles */
    .glass-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    .metric-card-new {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 1.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.4);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card-new:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 50px rgba(102, 126, 234, 0.5);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Gradient Cards for different metrics */
    .card-hba1c {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    .card-glucose {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    
    .card-weight {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    }
    
    .card-bp {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    }
    
    .card-health {
        background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%);
    }
    
    /* Tab Styles */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: linear-gradient(90deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        padding: 0.5rem;
        border-radius: 16px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 24px;
        background-color: transparent;
        border-radius: 12px;
        font-weight: 500;
        color: #4b5563;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(102, 126, 234, 0.2);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Button Styles */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    /* Sidebar Styles */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1c2e 0%, #2d1f3d 100%);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #e5e7eb;
    }
    
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: white !important;
    }
    
    /* Profile Card Styles */
    .profile-card {
        background: linear-gradient(135deg, #1a1c2e 0%, #2d1f3d 100%);
        border-radius: 20px;
        padding: 2rem;
        color: white;
        margin-bottom: 1.5rem;
    }
    
    .profile-avatar {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        margin: 0 auto 1rem;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
    }
    
    .profile-name {
        font-size: 1.5rem;
        font-weight: 600;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .profile-info {
        text-align: center;
        opacity: 0.8;
        font-size: 0.9rem;
    }
    
    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .status-good {
        background: rgba(16, 185, 129, 0.2);
        color: #10b981;
    }
    
    .status-warning {
        background: rgba(245, 158, 11, 0.2);
        color: #f59e0b;
    }
    
    .status-critical {
        background: rgba(239, 68, 68, 0.2);
        color: #ef4444;
    }
    
    /* Progress Bar */
    .progress-container {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        height: 8px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    
    .progress-bar {
        height: 100%;
        border-radius: 10px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        transition: width 0.5s ease;
    }
    
    /* Chat Interface */
    .chat-message {
        padding: 1rem;
        border-radius: 16px;
        margin-bottom: 1rem;
        animation: slideIn 0.3s ease;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-10px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 20%;
    }
    
    .ai-message {
        background: #f3f4f6;
        color: #1f2937;
        margin-right: 20%;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div {
        border-radius: 12px !important;
        border: 2px solid #e5e7eb !important;
        transition: border-color 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* Slider */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: linear-gradient(90deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-radius: 12px;
        font-weight: 500;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.3), transparent);
        margin: 2rem 0;
    }
    
    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Animations */
    .animate-pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* Feature Cards */
    .feature-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        border: 1px solid #f3f4f6;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
        border-color: #667eea;
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    .feature-title {
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    
    .feature-desc {
        color: #6b7280;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize all session state variables"""
    
    if 'patient' not in st.session_state:
        st.session_state.patient = None
    
    if 'profile_created' not in st.session_state:
        st.session_state.profile_created = False
    
    if 'saved_profiles' not in st.session_state:
        # Load any saved profiles
        st.session_state.saved_profiles = {}
    
    if 'health_memory' not in st.session_state:
        st.session_state.health_memory = None
    
    if 'narrative_engine' not in st.session_state:
        # Initialize narrative engine
        st.session_state.narrative_engine = NarrativeEngine(
            fallback_mode=True
        )
    
    if 'counterfactual_generator' not in st.session_state:
        st.session_state.counterfactual_generator = CounterfactualStoryGenerator()
    
    if 'temporal_engine' not in st.session_state:
        st.session_state.temporal_engine = TemporalEvolutionEngine(variability=0.08)
    
    if 'current_trajectories' not in st.session_state:
        st.session_state.current_trajectories = {}
    
    if 'modified_lifestyle' not in st.session_state:
        st.session_state.modified_lifestyle = None


def create_patient_from_form(form_data: dict) -> VirtualPatient:
    """Create a VirtualPatient from form data"""
    
    profile = PatientProfile(
        patient_id=str(uuid.uuid4())[:8],
        name=form_data['name'],
        age=form_data['age'],
        biological_sex=form_data['sex'],
        height_cm=form_data['height'],
        years_since_diagnosis=form_data['years_diagnosed'],
        family_history_diabetes=form_data['family_history'],
        has_hypertension=form_data['has_hypertension'],
        has_dyslipidemia=form_data['has_dyslipidemia'],
        has_cardiovascular_disease=form_data['has_cvd'],
        genetic_risk_factor=form_data.get('genetic_risk', 0.5)
    )
    
    lifestyle = LifestyleFactors(
        exercise_minutes_per_week=form_data['exercise_mins'],
        activity_level=ActivityLevel(form_data['activity_level']),
        diet_quality=DietQuality(form_data['diet_quality']),
        daily_carb_intake_grams=form_data.get('carb_intake', 200),
        sugary_drinks_per_week=form_data.get('sugary_drinks', 3),
        average_sleep_hours=form_data['sleep_hours'],
        stress_score={"low": 0.2, "moderate": 0.5, "high": 0.7, "severe": 0.9}[form_data['stress_level']],
        stress_level=StressLevel(form_data['stress_level']),
        medication_adherence=form_data['medication_adherence'] / 100
    )
    
    # Create VirtualPatient with individual health metrics
    return VirtualPatient(
        profile=profile,
        lifestyle=lifestyle,
        weight_kg=form_data['weight'],
        hba1c_percent=form_data['hba1c'],
        fasting_glucose_mgdl=form_data['fasting_glucose'],
        systolic_bp=form_data['systolic_bp'],
        diastolic_bp=form_data['diastolic_bp'],
        ldl_cholesterol_mgdl=form_data.get('ldl', 130.0),
        hdl_cholesterol_mgdl=form_data.get('hdl', 45.0),
        triglycerides_mgdl=form_data.get('triglycerides', 180.0)
    )


def initialize_health_memory():
    """Initialize health memory for the current patient"""
    
    if st.session_state.patient is None:
        return
    
    patient = st.session_state.patient
    memory = HealthMemory(patient_id=patient.profile.patient_id)
    engine = TemporalEvolutionEngine(variability=0.05)
    
    # Simulate past 6 months
    baseline_traj = engine.simulate_trajectory(
        patient=patient,
        months=6,
        scenario_type=ScenarioType.BASELINE
    )
    
    # Add trajectory points to memory
    for point in baseline_traj.points:
        snapshot = HealthSnapshot(
            timestamp=datetime.now() - timedelta(days=30 * (6 - point.time_step)),
            time_step=point.time_step,
            hba1c_percent=point.health_state.hba1c_percent,
            fasting_glucose_mgdl=point.health_state.fasting_glucose_mgdl,
            weight_kg=point.health_state.weight_kg,
            systolic_bp=point.health_state.systolic_bp,
            diastolic_bp=point.health_state.diastolic_bp,
            ldl_cholesterol_mgdl=point.health_state.ldl_cholesterol_mgdl,
            hdl_cholesterol_mgdl=point.health_state.hdl_cholesterol_mgdl,
            triglycerides_mgdl=point.health_state.triglycerides_mgdl,
            cardiovascular_risk_score=point.health_state.cardiovascular_risk_score,
            diabetes_progression_score=point.health_state.diabetes_progression_score,
            overall_health_score=point.health_state.overall_health_score,
            lifestyle_score=patient.lifestyle.get_overall_lifestyle_score(),
            activity_level=patient.lifestyle.activity_level.value,
            diet_quality=patient.lifestyle.diet_quality.value,
            medication_adherence=patient.lifestyle.medication_adherence,
            stress_level=patient.lifestyle.stress_level.value,
            explanations=point.explanations
        )
        memory.add_snapshot(snapshot)
    
    st.session_state.health_memory = memory


def render_profile_creation():
    """Render the dynamic profile creation interface"""
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">🏥</div>
        <h1 style="font-size: 2.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;">
            Welcome to DiabeTwin (RECM)
        </h1>
        <p style="color: #6b7280; font-size: 1.1rem; max-width: 600px; margin: 0 auto;">
            Create your personalized Healthcare Digital Twin for Type 2 Diabetes management.
            Your data stays private and is used only for simulation.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature highlights
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔮</div>
            <div class="feature-title">Future Simulation</div>
            <div class="feature-desc">See how lifestyle changes affect your health</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">⏰</div>
            <div class="feature-title">Counterfactual</div>
            <div class="feature-desc">Explore "what if" scenarios</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <div class="feature-title">AI Guidance</div>
            <div class="feature-desc">Get personalized explanations</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📋</div>
            <div class="feature-title">Action Plans</div>
            <div class="feature-desc">Receive tailored recommendations</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Profile creation options
    create_tab, load_tab, demo_tab = st.tabs(["✨ Create New Profile", "📂 Load Sample Profile", "🎮 Quick Demo"])
    
    with create_tab:
        render_new_profile_form()
    
    with load_tab:
        render_sample_profiles()
    
    with demo_tab:
        render_quick_demo()


def render_new_profile_form():
    """Render the new profile creation form"""
    
    st.markdown("### 👤 Create Your Digital Twin Profile")
    st.markdown("*All fields with * are required. Your data is synthetic and for demonstration only.*")
    
    with st.form("profile_form", clear_on_submit=False):
        # Personal Information
        st.markdown("#### 📋 Personal Information")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            name = st.text_input("Full Name *", placeholder="Enter your name")
        with col2:
            age = st.number_input("Age *", min_value=18, max_value=100, value=50)
        with col3:
            sex = st.selectbox("Biological Sex *", ["male", "female"])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            height = st.number_input("Height (cm) *", min_value=100, max_value=250, value=170)
        with col2:
            weight = st.number_input("Weight (kg) *", min_value=30.0, max_value=250.0, value=85.0)
        with col3:
            years_diagnosed = st.number_input("Years Since Diagnosis *", min_value=0, max_value=50, value=5)
        
        st.markdown("---")
        
        # Health Metrics
        st.markdown("#### 🩺 Current Health Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            hba1c = st.number_input("HbA1c (%) *", min_value=4.0, max_value=15.0, value=7.5, step=0.1,
                                    help="Your average blood sugar over 2-3 months. Target: <7%")
        with col2:
            fasting_glucose = st.number_input("Fasting Glucose (mg/dL) *", min_value=50, max_value=400, value=140,
                                               help="Blood sugar after fasting. Target: 80-130")
        with col3:
            systolic_bp = st.number_input("Systolic BP *", min_value=80, max_value=220, value=135,
                                          help="Top number. Target: <130")
        with col4:
            diastolic_bp = st.number_input("Diastolic BP *", min_value=40, max_value=140, value=85,
                                           help="Bottom number. Target: <80")
        
        st.markdown("---")
        
        # Lifestyle Factors
        st.markdown("#### 🏃 Lifestyle & Habits")
        col1, col2 = st.columns(2)
        
        with col1:
            exercise_mins = st.slider("Weekly Exercise (minutes)", 0, 300, 60,
                                      help="Moderate intensity exercise like brisk walking. Target: 150+")
            
            activity_level = st.select_slider(
                "Overall Activity Level",
                options=["sedentary", "lightly_active", "moderately_active", "active", "very_active"],
                value="lightly_active",
                format_func=lambda x: {
                    "sedentary": "🪑 Sedentary",
                    "lightly_active": "🚶 Lightly Active",
                    "moderately_active": "🚴 Moderately Active",
                    "active": "🏃 Active",
                    "very_active": "🏋️ Very Active"
                }[x]
            )
            
            diet_quality = st.select_slider(
                "Diet Quality",
                options=["poor", "fair", "good", "excellent"],
                value="fair",
                format_func=lambda x: {
                    "poor": "🍔 Poor",
                    "fair": "🍕 Fair",
                    "good": "🥗 Good",
                    "excellent": "🥬 Excellent"
                }[x]
            )
        
        with col2:
            medication_adherence = st.slider("Medication Adherence (%)", 0, 100, 70,
                                             help="How consistently you take prescribed medications")
            
            stress_level = st.select_slider(
                "Stress Level",
                options=["low", "moderate", "high", "severe"],
                value="moderate",
                format_func=lambda x: {
                    "low": "😌 Low",
                    "moderate": "😐 Moderate",
                    "high": "😰 High",
                    "severe": "😫 Severe"
                }[x]
            )
            
            sleep_hours = st.slider("Average Sleep (hours)", 4.0, 10.0, 6.5, 0.5,
                                    help="Target: 7-8 hours")
        
        st.markdown("---")
        
        # Medical History
        st.markdown("#### 🏥 Medical History")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            family_history = st.checkbox("Family History of Diabetes")
        with col2:
            has_hypertension = st.checkbox("Hypertension")
        with col3:
            has_dyslipidemia = st.checkbox("Dyslipidemia")
        with col4:
            has_cvd = st.checkbox("Cardiovascular Disease")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Submit button
        submitted = st.form_submit_button("🚀 Create My Digital Twin", type="primary", use_container_width=True)
        
        if submitted:
            if not name:
                st.error("Please enter your name to continue.")
            else:
                form_data = {
                    'name': name,
                    'age': age,
                    'sex': sex,
                    'height': height,
                    'weight': weight,
                    'years_diagnosed': years_diagnosed,
                    'hba1c': hba1c,
                    'fasting_glucose': fasting_glucose,
                    'systolic_bp': systolic_bp,
                    'diastolic_bp': diastolic_bp,
                    'exercise_mins': exercise_mins,
                    'activity_level': activity_level,
                    'diet_quality': diet_quality,
                    'medication_adherence': medication_adherence,
                    'stress_level': stress_level,
                    'sleep_hours': sleep_hours,
                    'family_history': family_history,
                    'has_hypertension': has_hypertension,
                    'has_dyslipidemia': has_dyslipidemia,
                    'has_cvd': has_cvd
                }
                
                st.session_state.patient = create_patient_from_form(form_data)
                st.session_state.profile_created = True
                initialize_health_memory()
                st.success(f"✨ Digital Twin created for {name}!")
                st.rerun()


def render_sample_profiles():
    """Render sample profile selection"""
    
    st.markdown("### 📂 Load a Sample Profile")
    st.markdown("*Choose from pre-configured profiles to explore the system*")
    
    profiles = {
        "moderate": {
            "name": "Alex Morgan",
            "description": "45-year-old with moderate diabetes control, room for lifestyle improvement",
            "emoji": "👤",
            "hba1c": "7.5%",
            "status": "Moderate Control"
        },
        "mild": {
            "name": "Sarah Chen",
            "description": "52-year-old with well-controlled diabetes, active lifestyle",
            "emoji": "👩",
            "hba1c": "6.8%",
            "status": "Good Control"
        },
        "severe": {
            "name": "James Wilson",
            "description": "58-year-old with poor control, multiple comorbidities",
            "emoji": "👨",
            "hba1c": "9.2%",
            "status": "Needs Attention"
        },
        "improving": {
            "name": "Maria Garcia",
            "description": "48-year-old making positive lifestyle changes",
            "emoji": "👩‍🦱",
            "hba1c": "7.8%",
            "status": "Improving"
        }
    }
    
    cols = st.columns(2)
    
    for idx, (key, profile) in enumerate(profiles.items()):
        with cols[idx % 2]:
            status_class = {
                "Good Control": "status-good",
                "Moderate Control": "status-warning",
                "Needs Attention": "status-critical",
                "Improving": "status-good"
            }.get(profile["status"], "status-warning")
            
            st.markdown(f"""
            <div class="glass-card" style="height: 160px;">
                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
                    <span style="font-size: 2rem;">{profile['emoji']}</span>
                    <div>
                        <div style="font-weight: 600; font-size: 1.1rem;">{profile['name']}</div>
                        <span class="status-badge {status_class}">{profile['status']}</span>
                    </div>
                </div>
                <p style="color: #6b7280; font-size: 0.9rem; margin-bottom: 0.5rem;">{profile['description']}</p>
                <div style="color: #4b5563; font-size: 0.85rem;">HbA1c: <strong>{profile['hba1c']}</strong></div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Load {profile['name']}'s Profile", key=f"load_{key}", use_container_width=True):
                st.session_state.patient = create_synthetic_patient(
                    name=profile['name'],
                    scenario=key
                )
                st.session_state.profile_created = True
                initialize_health_memory()
                st.success(f"✨ Loaded {profile['name']}'s profile!")
                st.rerun()


def render_quick_demo():
    """Render quick demo option"""
    
    st.markdown("### 🎮 Quick Demo Mode")
    st.markdown("*Jump right in with a pre-configured profile to explore all features*")
    
    st.markdown("""
    <div class="glass-card" style="text-align: center; padding: 2rem;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">🚀</div>
        <h3 style="margin-bottom: 0.5rem;">Ready to Explore?</h3>
        <p style="color: #6b7280; max-width: 400px; margin: 0 auto 1rem;">
            Start with our demo patient to see how DiabeTwin helps you understand 
            and manage Type 2 Diabetes through AI-powered simulations.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🎮 Start Demo Now", type="primary", use_container_width=True):
        st.session_state.patient = create_synthetic_patient(
            name="Demo Patient",
            scenario="moderate"
        )
        st.session_state.profile_created = True
        initialize_health_memory()
        st.balloons()
        st.success("🎉 Welcome to DiabeTwin! Explore all the features.")
        st.rerun()


def render_header():
    """Render the application header"""
    
    st.markdown('<h1 class="main-header">🏥 DiabeTwin</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Your AI-Powered Healthcare Digital Twin for Type 2 Diabetes</p>',
        unsafe_allow_html=True
    )


def render_beautiful_metrics(patient):
    """Render beautiful metric cards"""
    
    # Get risk status
    hba1c = patient.hba1c_percent
    if hba1c < 7:
        hba1c_status = "On Target"
        hba1c_class = "status-good"
    elif hba1c < 8:
        hba1c_status = "Slightly Elevated"
        hba1c_class = "status-warning"
    else:
        hba1c_status = "Needs Attention"
        hba1c_class = "status-critical"
    
    glucose = patient.fasting_glucose_mgdl
    if glucose < 130:
        glucose_status = "Normal"
    elif glucose < 180:
        glucose_status = "Elevated"
    else:
        glucose_status = "High"
    
    lifestyle_score = patient.lifestyle.get_overall_lifestyle_score() * 100
    
    st.markdown(f"""
    <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 1rem; margin-bottom: 2rem;">
        <div class="metric-card-new card-hba1c">
            <div class="metric-label">HbA1c</div>
            <div class="metric-value">{hba1c:.1f}%</div>
            <span class="status-badge" style="background: rgba(255,255,255,0.2); color: white;">{hba1c_status}</span>
        </div>
        <div class="metric-card-new card-glucose">
            <div class="metric-label">Fasting Glucose</div>
            <div class="metric-value">{glucose:.0f}</div>
            <span style="font-size: 0.8rem; opacity: 0.9;">mg/dL</span>
        </div>
        <div class="metric-card-new card-weight">
            <div class="metric-label">Weight</div>
            <div class="metric-value">{patient.weight_kg:.1f}</div>
            <span style="font-size: 0.8rem; opacity: 0.9;">kg (BMI: {patient.bmi:.1f})</span>
        </div>
        <div class="metric-card-new card-bp">
            <div class="metric-label">Blood Pressure</div>
            <div class="metric-value">{patient.systolic_bp}/{patient.diastolic_bp}</div>
            <span style="font-size: 0.8rem; opacity: 0.9;">mmHg</span>
        </div>
        <div class="metric-card-new card-health">
            <div class="metric-label">Lifestyle Score</div>
            <div class="metric-value">{lifestyle_score:.0f}</div>
            <span style="font-size: 0.8rem; opacity: 0.9;">/ 100</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_profile_card(patient):
    """Render a beautiful profile card"""
    
    risk_category = patient.get_risk_category().value.replace('_', ' ').title()
    risk_class = {
        "Low Risk": "status-good",
        "Moderate Risk": "status-warning",
        "High Risk": "status-critical",
        "Very High Risk": "status-critical"
    }.get(risk_category, "status-warning")
    
    # Get initials for avatar
    initials = "".join([n[0].upper() for n in patient.profile.name.split()[:2]])
    
    st.markdown(f"""
    <div class="profile-card">
        <div class="profile-avatar">{initials}</div>
        <div class="profile-name">{patient.profile.name}</div>
        <div class="profile-info">
            {patient.profile.age} years old • {patient.profile.years_since_diagnosis} years with T2D
        </div>
        <div style="text-align: center; margin-top: 1rem;">
            <span class="status-badge {risk_class}">{risk_category}</span>
        </div>
        <div style="margin-top: 1.5rem; display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; text-align: center;">
            <div>
                <div style="opacity: 0.7; font-size: 0.8rem;">Height</div>
                <div style="font-weight: 600;">{patient.profile.height_cm} cm</div>
            </div>
            <div>
                <div style="opacity: 0.7; font-size: 0.8rem;">BMI</div>
                <div style="font-weight: 600;">{patient.bmi:.1f}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Comorbidities
    comorbidities = []
    if patient.profile.has_hypertension:
        comorbidities.append("🫀 Hypertension")
    if patient.profile.has_dyslipidemia:
        comorbidities.append("🩸 Dyslipidemia")
    if patient.profile.has_cardiovascular_disease:
        comorbidities.append("❤️ CVD")
    if patient.profile.family_history_diabetes:
        comorbidities.append("🧬 Family History")
    
    if comorbidities:
        st.markdown("**Health Conditions:**")
        st.markdown(" • ".join(comorbidities))


def render_current_status_tab():
    """Render the current health status tab"""
    
    patient = st.session_state.patient
    
    # Beautiful metrics at top
    render_beautiful_metrics(patient)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Profile card
        render_profile_card(patient)
        
        # Lifestyle radar
        st.plotly_chart(
            create_lifestyle_radar(patient.lifestyle.to_dict()),
            use_container_width=True
        )
    
    with col2:
        # Gauges row
        gauge_col1, gauge_col2 = st.columns(2)
        
        with gauge_col1:
            st.plotly_chart(
                create_hba1c_gauge(patient.hba1c_percent),
                use_container_width=True
            )
        
        with gauge_col2:
            st.plotly_chart(
                create_health_score_gauge(
                    patient.get_summary_metrics()["lifestyle_score"]["value"]
                ),
                use_container_width=True
            )
        
        st.markdown("---")
        
        # AI Explanation
        st.markdown("### 🤖 AI Health Analysis")
        
        with st.spinner("Generating personalized analysis..."):
            response = st.session_state.narrative_engine.generate_health_explanation(
                patient_data=patient.profile.to_dict(),
                health_metrics={
                    "hba1c": patient.hba1c_percent,
                    "fasting_glucose": patient.fasting_glucose_mgdl,
                    "weight": patient.weight_kg,
                    "bmi": patient.bmi,
                    "systolic_bp": patient.systolic_bp,
                    "diastolic_bp": patient.diastolic_bp,
                    "overall_health_score": patient.lifestyle.get_overall_lifestyle_score() * 100,
                    "risk_category": patient.get_risk_category().value
                },
                lifestyle_data=patient.lifestyle.to_dict()
            )
        
        st.markdown(f"""
        <div class="glass-card">
            {response.content}
        </div>
        """, unsafe_allow_html=True)


def render_simulate_future_tab():
    """Render the future simulation tab"""
    
    patient = st.session_state.patient
    engine = st.session_state.temporal_engine
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### ⚙️ Simulation Settings")
        
        # Time horizon
        months = render_time_horizon_selector()
        
        st.markdown("---")
        
        # Scenario selection
        st.markdown("### 📊 Scenarios to Compare")
        
        scenarios_to_run = []
        
        if st.checkbox("📍 Current Path (Baseline)", value=True):
            scenarios_to_run.append(ScenarioType.BASELINE)
        
        if st.checkbox("🥗 Better Nutrition", value=True):
            scenarios_to_run.append(ScenarioType.IMPROVED_DIET)
        
        if st.checkbox("🏃 More Exercise", value=True):
            scenarios_to_run.append(ScenarioType.INCREASED_EXERCISE)
        
        if st.checkbox("⭐ Comprehensive Change", value=False):
            scenarios_to_run.append(ScenarioType.COMPREHENSIVE)
        
        if st.checkbox("⚠️ Warning: Deterioration", value=False):
            scenarios_to_run.append(ScenarioType.DETERIORATION)
        
        st.markdown("---")
        
        # Run simulation button
        if st.button("🔮 Run Simulation", type="primary", use_container_width=True):
            with st.spinner("Simulating health trajectories..."):
                trajectories = {}
                for scenario in scenarios_to_run:
                    traj = engine.simulate_trajectory(
                        patient=patient,
                        months=months,
                        scenario_type=scenario
                    )
                    trajectories[scenario.value] = traj.to_dict()
                
                st.session_state.current_trajectories = trajectories
            
            st.success("Simulation complete!")
    
    with col2:
        if st.session_state.current_trajectories:
            trajectories = st.session_state.current_trajectories
            
            # Trajectory chart
            st.markdown("### 📈 Health Trajectory Projections")
            
            metric_choice = st.selectbox(
                "Select Metric to View",
                options=["hba1c_percent", "weight_kg", "systolic_bp", "overall_health_score"],
                format_func=lambda x: {
                    "hba1c_percent": "HbA1c (%)",
                    "weight_kg": "Weight (kg)",
                    "systolic_bp": "Systolic Blood Pressure",
                    "overall_health_score": "Health Score"
                }.get(x, x)
            )
            
            st.plotly_chart(
                create_trajectory_chart(trajectories, metric=metric_choice),
                use_container_width=True
            )
            
            # Comparison chart
            engine_obj = st.session_state.temporal_engine
            comparison = engine_obj.compare_trajectories({
                k: type('obj', (object,), {
                    'scenario_name': v.get('scenario_name'),
                    'end_hba1c': v.get('summary', {}).get('end_hba1c', 7.0),
                    'hba1c_change': v.get('summary', {}).get('hba1c_change', 0),
                    'end_weight': v.get('summary', {}).get('end_weight', 85),
                    'weight_change': v.get('summary', {}).get('weight_change', 0),
                    'risk_trend': v.get('summary', {}).get('risk_trend', 'stable')
                })()
                for k, v in trajectories.items()
            })
            
            st.plotly_chart(
                create_comparison_chart(comparison),
                use_container_width=True
            )
            
            # AI Narrative
            st.markdown("### 🤖 AI Analysis of Scenarios")
            
            with st.spinner("Analyzing trajectories..."):
                response = st.session_state.narrative_engine.generate_trajectory_narrative(
                    patient_data=patient.profile.to_dict(),
                    trajectories=trajectories,
                    months=months
                )
            
            st.markdown(response.content)
        else:
            st.info("👈 Select scenarios and click 'Run Simulation' to see trajectory projections")


def render_counterfactual_tab():
    """Render the counterfactual analysis tab (INNOVATION HIGHLIGHT)"""
    
    patient = st.session_state.patient
    memory = st.session_state.health_memory
    generator = st.session_state.counterfactual_generator
    engine = st.session_state.temporal_engine
    
    st.markdown("""
    ### ⏰ Counterfactual Health Storytelling
    
    > *"The best time to plant a tree was 20 years ago. The second best time is now."*
    
    This innovative feature shows you **what could have been** if you had made different 
    choices in the past - then helps you chart a path forward.
    """)
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Counterfactual settings
        cf_config = render_counterfactual_selector()
        
        # Get scenario details
        scenarios = generator.get_counterfactual_scenarios()
        selected_scenario = next(
            (s for s in scenarios if s['id'] == cf_config['alternative_scenario']),
            scenarios[0]
        )
        
        st.markdown("---")
        
        st.markdown("**Selected Scenario:**")
        st.markdown(f"**{selected_scenario['name']}**")
        st.caption(selected_scenario['description'])
        st.caption(f"*{selected_scenario['expected_impact']}*")
        
        st.markdown("---")
        
        if st.button("🔮 Generate Counterfactual Story", type="primary", use_container_width=True):
            with st.spinner("Generating your health story..."):
                # Get past state from memory
                months_back = cf_config['months_back']
                current_time_step = memory.snapshots[-1].time_step if memory.snapshots else 6
                past_time_step = max(0, current_time_step - months_back)
                
                past_snapshot = memory.get_snapshot_at(past_time_step)
                if not past_snapshot and memory.snapshots:
                    past_snapshot = memory.snapshots[0]
                
                current_snapshot = memory.get_latest_snapshot()
                
                # Simulate counterfactual trajectory
                # Create alternative lifestyle based on scenario
                alternative_lifestyle = LifestyleFactors(
                    exercise_minutes_per_week=150 if 'exercise' in cf_config['alternative_scenario'] else 90,
                    activity_level=ActivityLevel.MODERATELY_ACTIVE,
                    diet_quality=DietQuality.GOOD if 'diet' in cf_config['alternative_scenario'] else DietQuality.FAIR,
                    medication_adherence=0.95 if 'medication' in cf_config['alternative_scenario'] else 0.85,
                    stress_score=0.3 if 'stress' in cf_config['alternative_scenario'] else 0.4,
                    average_sleep_hours=7.5
                )
                
                if cf_config['alternative_scenario'] == 'comprehensive':
                    alternative_lifestyle = LifestyleFactors(
                        exercise_minutes_per_week=180,
                        activity_level=ActivityLevel.ACTIVE,
                        diet_quality=DietQuality.EXCELLENT,
                        medication_adherence=0.95,
                        stress_score=0.25,
                        average_sleep_hours=8.0
                    )
                
                # Run counterfactual simulation
                cf_trajectory = engine.simulate_trajectory(
                    patient=patient,
                    months=months_back,
                    scenario_type=ScenarioType.CUSTOM,
                    lifestyle_overrides=alternative_lifestyle.to_dict()
                )
                
                # Generate story
                past_state = {
                    "hba1c": past_snapshot.hba1c_percent if past_snapshot else patient.hba1c_percent,
                    "weight": past_snapshot.weight_kg if past_snapshot else patient.weight_kg,
                    "activity_level": past_snapshot.activity_level if past_snapshot else "lightly_active",
                    "diet_quality": past_snapshot.diet_quality if past_snapshot else "fair"
                }
                
                current_state = {
                    "hba1c": patient.hba1c_percent,
                    "weight": patient.weight_kg
                }
                
                cf_end = cf_trajectory.points[-1] if cf_trajectory.points else None
                counterfactual_state = {
                    "hba1c": cf_end.health_state.hba1c_percent if cf_end else patient.hba1c_percent - 0.5,
                    "weight": cf_end.health_state.weight_kg if cf_end else patient.weight_kg - 3
                }
                
                story = generator.generate_counterfactual_story(
                    patient_name=patient.profile.name,
                    months_ago=months_back,
                    past_state=past_state,
                    current_state=current_state,
                    counterfactual_state=counterfactual_state,
                    alternative_lifestyle_description=selected_scenario['lifestyle_changes']
                )
                
                st.session_state.current_counterfactual = {
                    "story": story,
                    "actual_trajectory": [{"time_step": p.time_step, "health_state": p.health_state.to_dict()} 
                                         for p in engine.simulate_trajectory(patient, months_back, ScenarioType.BASELINE).points],
                    "counterfactual_trajectory": [{"time_step": p.time_step, "health_state": p.health_state.to_dict()} 
                                                  for p in cf_trajectory.points]
                }
            
            st.success("Story generated!")
            st.rerun()
    
    with col2:
        if 'current_counterfactual' in st.session_state:
            cf_data = st.session_state.current_counterfactual
            story = cf_data['story']
            
            # Comparison chart
            st.plotly_chart(
                create_counterfactual_comparison(
                    cf_data['actual_trajectory'],
                    cf_data['counterfactual_trajectory'],
                    metric="hba1c_percent"
                ),
                use_container_width=True
            )
            
            # Key metrics comparison
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.metric(
                    "HbA1c Gap",
                    f"{abs(story.hba1c_difference):.1f}%",
                    delta=f"Could be {story.hba1c_difference:.1f}% lower" if story.hba1c_difference > 0 else None,
                    delta_color="inverse"
                )
            
            with col_b:
                st.metric(
                    "Weight Gap",
                    f"{abs(story.weight_difference):.1f} kg",
                    delta=f"Could be {story.weight_difference:.1f} kg lower" if story.weight_difference > 0 else None,
                    delta_color="inverse"
                )
            
            with col_c:
                st.metric(
                    "Missed Opportunity",
                    f"{story.missed_opportunity_score:.0f}/100",
                    help="Higher = bigger gap between actual and potential"
                )
            
            st.markdown("---")
            
            # The narrative
            st.markdown("### 📖 Your Health Story")
            st.markdown(story.narrative)
            
            st.markdown("---")
            
            # Recovery path
            st.markdown("### 🛤️ Your Path Forward")
            st.markdown(story.recovery_path)
            
            st.markdown("**First Steps:**")
            for i, step in enumerate(story.first_steps, 1):
                st.markdown(f"{i}. {step}")
            
            st.info(f"⏱️ **Recovery Timeline:** {story.recovery_timeline}")
        else:
            st.info("👈 Configure your counterfactual scenario and click 'Generate' to see your health story")


def render_lifestyle_lab_tab():
    """Render the interactive lifestyle modification lab"""
    
    patient = st.session_state.patient
    engine = st.session_state.temporal_engine
    
    st.markdown("""
    ### 🧪 Lifestyle Lab
    
    Experiment with different lifestyle settings and see immediate effects on your projected health trajectory.
    """)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Interactive lifestyle controls
        modified_lifestyle = render_lifestyle_controls(patient.lifestyle.to_dict())
        st.session_state.modified_lifestyle = modified_lifestyle
        
        st.markdown("---")
        
        months = st.slider("Projection Period", 3, 24, 12, 3, format="%d months")
        
        if st.button("🔬 Apply & Simulate", type="primary", use_container_width=True):
            with st.spinner("Running simulation with modified lifestyle..."):
                # Create custom trajectory with modified lifestyle
                custom_traj = engine.simulate_trajectory(
                    patient=patient,
                    months=months,
                    scenario_type=ScenarioType.CUSTOM,
                    lifestyle_overrides=modified_lifestyle
                )
                
                baseline_traj = engine.simulate_trajectory(
                    patient=patient,
                    months=months,
                    scenario_type=ScenarioType.BASELINE
                )
                
                st.session_state.lab_trajectories = {
                    "baseline": baseline_traj.to_dict(),
                    "modified": {
                        **custom_traj.to_dict(),
                        "scenario_name": "Your Modified Lifestyle"
                    }
                }
            
            st.success("Simulation complete!")
            st.rerun()
    
    with col2:
        if 'lab_trajectories' in st.session_state:
            trajectories = st.session_state.lab_trajectories
            
            # Show trajectory comparison
            st.plotly_chart(
                create_trajectory_chart(
                    trajectories,
                    metric="hba1c_percent",
                    title="HbA1c: Current vs Modified Lifestyle"
                ),
                use_container_width=True
            )
            
            # Compare outcomes
            baseline = trajectories['baseline']['summary']
            modified = trajectories['modified']['summary']
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown("**Current Path:**")
                st.metric("Final HbA1c", f"{baseline['end_hba1c']:.1f}%")
                st.metric("Weight Change", f"{baseline['weight_change']:+.1f} kg")
            
            with col_b:
                st.markdown("**Modified Path:**")
                st.metric(
                    "Final HbA1c",
                    f"{modified['end_hba1c']:.1f}%",
                    delta=f"{modified['end_hba1c'] - baseline['end_hba1c']:+.2f}%",
                    delta_color="inverse"
                )
                st.metric(
                    "Weight Change",
                    f"{modified['weight_change']:+.1f} kg",
                    delta=f"{modified['weight_change'] - baseline['weight_change']:+.1f} kg",
                    delta_color="inverse"
                )
            
            # Impact summary
            hba1c_improvement = baseline['end_hba1c'] - modified['end_hba1c']
            
            if hba1c_improvement > 0.3:
                st.success(f"""
                ✨ **Great choices!** Your modified lifestyle could reduce HbA1c by **{hba1c_improvement:.1f}%** 
                over {len(trajectories['baseline']['points'])-1} months. This is a meaningful improvement!
                """)
            elif hba1c_improvement > 0:
                st.info(f"""
                👍 **Positive direction!** Your changes could improve HbA1c by **{hba1c_improvement:.2f}%**.
                Consider adding more improvements for bigger impact.
                """)
            else:
                st.warning("""
                ⚠️ **These changes may not improve outcomes.** Try increasing exercise or improving diet quality.
                """)
        else:
            st.info("👈 Adjust the lifestyle controls and click 'Apply & Simulate' to see the effects")


def render_ask_twin_tab():
    """Render the conversational AI interface"""
    
    patient = st.session_state.patient
    memory = st.session_state.health_memory
    
    # Get recent trends
    trends = memory.get_all_trends()
    trend_dicts = [
        {
            "metric": t.metric_name,
            "direction": t.direction,
            "narrative": t.to_narrative()
        }
        for t in trends
    ]
    
    # Create patient summary
    patient_summary = {
        "patient_id": patient.profile.patient_id,
        "current_state": {
            "name": patient.profile.name,
            "hba1c": patient.hba1c_percent,
            "weight": patient.weight_kg,
            "health_score": patient.lifestyle.get_overall_lifestyle_score() * 100,
            "risk_category": patient.get_risk_category().value
        },
        "lifestyle": patient.lifestyle.to_dict()
    }
    
    render_chat_interface(
        patient_summary=patient_summary,
        trends=trend_dicts,
        narrative_engine=st.session_state.narrative_engine,
        key_prefix="main_chat"
    )


def render_action_plan_tab():
    """Render the personalized action plan"""
    
    patient = st.session_state.patient
    memory = st.session_state.health_memory
    narrative_engine = st.session_state.narrative_engine
    
    st.markdown("### 📋 Your Personalized Action Plan")
    
    # Get simulation insights if available
    if st.session_state.current_trajectories:
        trajectories = st.session_state.current_trajectories
        best_scenario = min(
            trajectories.items(),
            key=lambda x: x[1].get('summary', {}).get('end_hba1c', 100)
        )
        simulation_insights = f"""
Best projected outcome: {best_scenario[1].get('scenario_name', 'Unknown')} scenario
- Could achieve HbA1c of {best_scenario[1].get('summary', {}).get('end_hba1c', 7.0):.1f}%
- Weight change: {best_scenario[1].get('summary', {}).get('weight_change', 0):+.1f} kg
"""
    else:
        simulation_insights = "Run simulations to get personalized insights"
    
    # Get detected patterns from memory
    trends = memory.get_all_trends()
    patterns = "\n".join([t.to_narrative() for t in trends]) if trends else "Collecting data for pattern detection..."
    
    with st.spinner("Generating your personalized action plan..."):
        response = narrative_engine.generate_action_plan(
            patient_data=patient.profile.to_dict(),
            health_metrics={
                "hba1c": patient.hba1c_percent,
                "weight_change": 0,  # Would come from memory
                "lifestyle_score": patient.lifestyle.get_overall_lifestyle_score()
            },
            simulation_insights=simulation_insights,
            detected_patterns=patterns
        )
    
    st.markdown(response.content)
    
    st.markdown("---")
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔮 Simulate Best Scenario", use_container_width=True):
            st.session_state.active_tab = "simulate"
            st.rerun()
    
    with col2:
        if st.button("⏰ See What Could Have Been", use_container_width=True):
            st.session_state.active_tab = "counterfactual"
            st.rerun()
    
    with col3:
        if st.button("🧪 Experiment in Lifestyle Lab", use_container_width=True):
            st.session_state.active_tab = "lab"
            st.rerun()


def main():
    """Main application entry point"""
    
    # Initialize session state
    initialize_session_state()
    
    # Check if profile is created
    if not st.session_state.profile_created or st.session_state.patient is None:
        # Show profile creation page
        render_profile_creation()
        return
    
    # Render sidebar with profile info
    render_enhanced_sidebar()
    
    # Render header
    render_header()
    
    # Main content tabs
    tabs = st.tabs([
        "📊 Current Status",
        "🔮 Simulate Future",
        "⏰ Counterfactual",
        "🧪 Lifestyle Lab",
        "💬 Ask Your Twin",
        "📋 Action Plan"
    ])
    
    with tabs[0]:
        render_current_status_tab()
    
    with tabs[1]:
        render_simulate_future_tab()
    
    with tabs[2]:
        render_counterfactual_tab()
    
    with tabs[3]:
        render_lifestyle_lab_tab()
    
    with tabs[4]:
        render_ask_twin_tab()
    
    with tabs[5]:
        render_action_plan_tab()
    
    # Footer
    render_disclaimer()


def render_enhanced_sidebar():
    """Render enhanced sidebar with profile management"""
    
    patient = st.session_state.patient
    
    with st.sidebar:
        # Profile summary
        initials = "".join([n[0].upper() for n in patient.profile.name.split()[:2]])
        
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem 0;">
            <div style="width: 60px; height: 60px; border-radius: 50%; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        display: flex; align-items: center; justify-content: center;
                        font-size: 1.5rem; color: white; margin: 0 auto 0.5rem;
                        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);">
                {initials}
            </div>
            <div style="font-weight: 600; font-size: 1.1rem; color: white;">{patient.profile.name}</div>
            <div style="opacity: 0.7; font-size: 0.85rem; color: #e5e7eb;">{patient.profile.age} years • T2D</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick stats
        st.markdown("### 📊 Quick Stats")
        
        hba1c = patient.hba1c_percent
        status_color = "🟢" if hba1c < 7 else "🟡" if hba1c < 8 else "🔴"
        
        st.markdown(f"""
        {status_color} **HbA1c:** {hba1c:.1f}%  
        ⚖️ **Weight:** {patient.weight_kg:.1f} kg  
        💓 **BP:** {patient.systolic_bp}/{patient.diastolic_bp}  
        🎯 **Score:** {patient.lifestyle.get_overall_lifestyle_score() * 100:.0f}/100
        """)
        
        st.markdown("---")
        
        # AI Status
        if st.session_state.narrative_engine.is_available():
            st.success("🟢 AI Connected")
        else:
            st.warning("🟡 AI Fallback Mode")
            st.caption("Add OPENAI_API_KEY for full AI")
        
        st.markdown("---")
        
        # Profile management
        st.markdown("### ⚙️ Profile")
        
        if st.button("✏️ Edit Profile", use_container_width=True):
            st.session_state.show_edit_profile = True
        
        if st.button("🔄 Switch Profile", use_container_width=True):
            st.session_state.profile_created = False
            st.session_state.patient = None
            st.rerun()
        
        st.markdown("---")
        
        # Innovation highlight
        st.markdown("""
        ### 🏆 Innovation
        
        **Counterfactual Health Storytelling**
        
        See "what could have been" if you'd made different choices - 
        then learn how to get there starting today.
        """)
        
        st.markdown("---")
        
        # Quick guide
        with st.expander("📖 Quick Guide"):
            st.markdown("""
            1. **Current Status** - View your health metrics
            2. **Simulate Future** - Project health trajectories
            3. **Counterfactual** - Explore "what if" scenarios
            4. **Lifestyle Lab** - Experiment with changes
            5. **Ask Your Twin** - Get AI explanations
            6. **Action Plan** - Get personalized guidance
            """)


if __name__ == "__main__":
    main()
