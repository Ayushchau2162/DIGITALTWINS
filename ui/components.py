"""
UI Components for DiabeTwin

Reusable Streamlit components for the digital twin interface.
"""

import streamlit as st
from typing import Dict, Any, Optional, Callable


def render_metric_card(
    title: str,
    value: Any,
    unit: str = "",
    status: str = "",
    delta: Optional[float] = None,
    delta_color: str = "normal",
    help_text: str = ""
):
    """
    Render a styled metric card.
    
    Args:
        title: Metric name
        value: Current value
        unit: Unit of measurement
        status: Status text (e.g., "Good", "Needs Attention")
        delta: Change from previous value
        delta_color: "normal", "inverse", or "off"
        help_text: Tooltip text
    """
    
    # Determine status color
    status_colors = {
        "excellent": "🟢",
        "good": "🟢", 
        "normal": "🟢",
        "fair": "🟡",
        "moderate": "🟡",
        "elevated": "🟡",
        "poor": "🔴",
        "high": "🔴",
        "critical": "🔴"
    }
    
    status_emoji = status_colors.get(status.lower(), "⚪")
    
    if delta is not None:
        st.metric(
            label=f"{title} {help_text}",
            value=f"{value} {unit}",
            delta=f"{delta:+.1f} {unit}" if delta != 0 else "No change",
            delta_color=delta_color
        )
    else:
        st.metric(
            label=f"{title}",
            value=f"{value} {unit}"
        )
    
    if status:
        st.caption(f"{status_emoji} {status}")


def render_patient_profile(patient_data: Dict[str, Any]):
    """
    Render the patient profile card.
    """
    
    profile = patient_data.get("profile", {})
    metrics = patient_data.get("health_metrics", {})
    computed = patient_data.get("computed", {})
    
    st.markdown("### 👤 Patient Profile")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **Name:** {profile.get('name', 'Virtual Patient')}  
        **Age:** {profile.get('age', 50)} years  
        **Diagnosis Duration:** {profile.get('years_since_diagnosis', 0)} years  
        """)
    
    with col2:
        st.markdown(f"""
        **Height:** {profile.get('height_cm', 170)} cm  
        **BMI:** {computed.get('bmi', 27.0):.1f}  
        **Risk Category:** {computed.get('risk_category', 'moderate').replace('_', ' ').title()}
        """)
    
    # Comorbidities
    comorbidities = []
    if profile.get('has_hypertension'):
        comorbidities.append("Hypertension")
    if profile.get('has_dyslipidemia'):
        comorbidities.append("Dyslipidemia")
    if profile.get('has_cardiovascular_disease'):
        comorbidities.append("Cardiovascular Disease")
    
    if comorbidities:
        st.markdown(f"**Comorbidities:** {', '.join(comorbidities)}")
    
    if profile.get('family_history_diabetes'):
        st.caption("📌 Family history of diabetes")


def render_lifestyle_controls(
    current_lifestyle: Dict[str, Any],
    on_change: Optional[Callable] = None
) -> Dict[str, Any]:
    """
    Render interactive lifestyle modification controls.
    
    Returns the modified lifestyle settings.
    """
    
    st.markdown("### 🎛️ Lifestyle Controls")
    st.caption("Adjust these to see how changes affect your health trajectory")
    
    modified = {}
    
    # Exercise
    st.markdown("**Physical Activity**")
    col1, col2 = st.columns(2)
    
    with col1:
        exercise_mins = st.slider(
            "Weekly Exercise (minutes)",
            min_value=0,
            max_value=300,
            value=current_lifestyle.get("exercise_minutes_per_week", 60),
            step=15,
            help="Moderate intensity exercise like brisk walking"
        )
        modified["exercise_minutes_per_week"] = exercise_mins
        
        # Map to activity level
        if exercise_mins < 30:
            modified["activity_level"] = "sedentary"
        elif exercise_mins < 90:
            modified["activity_level"] = "lightly_active"
        elif exercise_mins < 150:
            modified["activity_level"] = "moderately_active"
        elif exercise_mins < 300:
            modified["activity_level"] = "active"
        else:
            modified["activity_level"] = "very_active"
    
    with col2:
        activity_text = {
            "sedentary": "🪑 Sedentary",
            "lightly_active": "🚶 Lightly Active",
            "moderately_active": "🚴 Moderately Active",
            "active": "🏃 Active",
            "very_active": "🏋️ Very Active"
        }
        st.info(f"Activity Level: {activity_text.get(modified['activity_level'], '🚶')}")
    
    # Diet
    st.markdown("**Nutrition**")
    col1, col2 = st.columns(2)
    
    with col1:
        diet_quality = st.select_slider(
            "Diet Quality",
            options=["poor", "fair", "good", "excellent"],
            value=current_lifestyle.get("diet_quality", "fair"),
            help="Overall quality of your diet"
        )
        modified["diet_quality"] = diet_quality
    
    with col2:
        sugary_drinks = st.slider(
            "Sugary Drinks per Week",
            min_value=0,
            max_value=15,
            value=current_lifestyle.get("sugary_drinks_per_week", 5),
            help="Sodas, sweetened coffees, juices"
        )
        modified["sugary_drinks_per_week"] = sugary_drinks
    
    # Medication
    st.markdown("**Medication Adherence**")
    medication = st.slider(
        "Medication Adherence",
        min_value=0,
        max_value=100,
        value=int(current_lifestyle.get("medication_adherence", 0.7) * 100),
        format="%d%%",
        help="How consistently you take prescribed medications"
    )
    modified["medication_adherence"] = medication / 100
    
    # Stress & Sleep
    st.markdown("**Stress & Sleep**")
    col1, col2 = st.columns(2)
    
    with col1:
        stress = st.select_slider(
            "Stress Level",
            options=["low", "moderate", "high", "severe"],
            value=current_lifestyle.get("stress_level", "moderate")
        )
        modified["stress_level"] = stress
        stress_scores = {"low": 0.2, "moderate": 0.5, "high": 0.7, "severe": 0.9}
        modified["stress_score"] = stress_scores.get(stress, 0.5)
    
    with col2:
        sleep = st.slider(
            "Average Sleep (hours)",
            min_value=4.0,
            max_value=10.0,
            value=current_lifestyle.get("average_sleep_hours", 6.5),
            step=0.5
        )
        modified["average_sleep_hours"] = sleep
    
    return modified


def render_health_metrics_dashboard(health_metrics: Dict[str, Any]):
    """
    Render the main health metrics dashboard.
    """
    
    st.markdown("### 📊 Current Health Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        hba1c = health_metrics.get("hba1c", {})
        status = "Good" if hba1c.get("value", 7) < 7 else "Needs Attention" if hba1c.get("value", 7) < 8 else "High"
        render_metric_card(
            title="HbA1c",
            value=f"{hba1c.get('value', 7.0):.1f}",
            unit="%",
            status=status
        )
    
    with col2:
        glucose = health_metrics.get("fasting_glucose", {})
        status = "Normal" if glucose.get("value", 140) < 130 else "Elevated"
        render_metric_card(
            title="Fasting Glucose",
            value=f"{glucose.get('value', 140):.0f}",
            unit="mg/dL",
            status=status
        )
    
    with col3:
        weight = health_metrics.get("weight", {})
        render_metric_card(
            title="Weight",
            value=f"{weight.get('value', 85):.1f}",
            unit="kg",
            status=weight.get("category", "")
        )
    
    with col4:
        bp = health_metrics.get("blood_pressure", {})
        render_metric_card(
            title="Blood Pressure",
            value=f"{bp.get('systolic', 135)}/{bp.get('diastolic', 85)}",
            unit="mmHg",
            status=bp.get("category", "")
        )


def render_scenario_selector() -> str:
    """
    Render scenario selection for what-if analysis.
    
    Returns selected scenario key.
    """
    
    scenarios = {
        "baseline": "📍 Current Path (No Changes)",
        "improved_diet": "🥗 Better Nutrition",
        "increased_exercise": "🏃 More Physical Activity",
        "better_medication": "💊 Better Medication Adherence",
        "stress_reduction": "🧘 Stress & Sleep Improvement",
        "comprehensive": "⭐ Comprehensive Lifestyle Change",
        "deterioration": "⚠️ Warning: If Things Get Worse"
    }
    
    selected = st.selectbox(
        "Select What-If Scenario",
        options=list(scenarios.keys()),
        format_func=lambda x: scenarios.get(x, x),
        help="See how different lifestyle changes would affect your health"
    )
    
    return selected


def render_time_horizon_selector() -> int:
    """
    Render time horizon selection for simulation.
    
    Returns number of months.
    """
    
    months = st.slider(
        "Simulation Time Horizon",
        min_value=3,
        max_value=24,
        value=12,
        step=3,
        format="%d months",
        help="How far into the future to simulate"
    )
    
    return months


def render_counterfactual_selector() -> Dict[str, Any]:
    """
    Render counterfactual scenario selector.
    
    Returns counterfactual configuration.
    """
    
    st.markdown("### ⏰ Counterfactual: What If...?")
    
    months_back = st.slider(
        "Look back how many months?",
        min_value=3,
        max_value=12,
        value=6,
        step=3,
        help="Compare your current state to what could have been"
    )
    
    alternative = st.selectbox(
        "If you had followed...",
        options=[
            "diet_focus",
            "exercise_focus", 
            "medication_focus",
            "comprehensive",
            "stress_sleep"
        ],
        format_func=lambda x: {
            "diet_focus": "🥗 A Better Diet",
            "exercise_focus": "🏃 An Active Lifestyle",
            "medication_focus": "💊 Perfect Medication Adherence",
            "comprehensive": "⭐ A Complete Lifestyle Change",
            "stress_sleep": "🧘 Better Stress & Sleep Habits"
        }.get(x, x)
    )
    
    return {
        "months_back": months_back,
        "alternative_scenario": alternative
    }


def render_disclaimer():
    """Render the medical disclaimer"""
    
    st.markdown("""
    ---
    ⚠️ **Important Disclaimer**
    
    This is a **research prototype** for educational and demonstration purposes only.
    It uses synthetic data and simplified models. DiabeTwin is NOT intended for:
    - Clinical diagnosis or treatment decisions
    - Replacement of professional medical advice
    - Actual patient care
    
    Always consult with healthcare professionals for medical decisions.
    """)


def render_sidebar_info():
    """Render sidebar information"""
    
    with st.sidebar:
        st.markdown("## 🏥 DiabeTwin")
        st.markdown("*Your AI-Powered Digital Twin*")
        
        st.markdown("---")
        
        st.markdown("""
        ### About
        
        DiabeTwin creates a virtual representation of your health journey with Type 2 Diabetes.
        
        **Features:**
        - 📊 Real-time health metrics
        - 🔮 Future trajectory simulation
        - ⏰ Counterfactual analysis
        - 💬 AI-powered explanations
        - 📋 Personalized guidance
        """)
        
        st.markdown("---")
        
        st.markdown("""
        ### Quick Guide
        
        1. **View Metrics**: See current health status
        2. **Adjust Lifestyle**: Use sliders to modify behaviors
        3. **Simulate Futures**: See how changes affect outcomes
        4. **Ask Your Twin**: Get personalized explanations
        5. **Explore What-Ifs**: See counterfactual scenarios
        """)
        
        st.markdown("---")
        
        st.markdown("""
        ### 🏆 Innovation
        
        **Counterfactual Health Storytelling**
        
        Our novel feature shows you "what could have been" 
        if you had made different choices - then pivots 
        to show how you can still get there.
        """)
