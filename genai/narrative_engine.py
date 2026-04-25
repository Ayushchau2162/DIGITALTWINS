"""
Generative AI Narrative Engine

This is the CORE of the DiabeTwin's intelligence - the engine that transforms
raw health data into meaningful, personalized narratives and guidance.

The Narrative Engine:
1. Takes structured health data as input
2. Constructs appropriate prompts using templates
3. Calls the LLM (OpenAI GPT-4) to generate responses
4. Post-processes and validates outputs
5. Returns human-readable explanations and guidance

CRITICAL: The AI reasons FROM the data - it never generates generic advice.
"""

import os
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

try:
    from openai import OpenAI, AzureOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Try to import streamlit for secrets management
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

from .prompts import PromptTemplates


def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get secret from Streamlit secrets or environment variables"""
    # First try Streamlit secrets (for cloud deployment)
    if STREAMLIT_AVAILABLE:
        try:
            return st.secrets.get(key, None)
        except Exception:
            pass
    
    # Fall back to environment variables
    return os.getenv(key, default)


@dataclass
class NarrativeResponse:
    """Structured response from the narrative engine"""
    content: str
    narrative_type: str
    tokens_used: int
    generated_at: datetime
    patient_id: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "narrative_type": self.narrative_type,
            "tokens_used": self.tokens_used,
            "generated_at": self.generated_at.isoformat(),
            "patient_id": self.patient_id,
            "metadata": self.metadata
        }


class NarrativeEngine:
    """
    The Generative AI engine that produces personalized health narratives.
    
    This engine is responsible for:
    - Explaining health states in understandable language
    - Comparing trajectories and explaining differences
    - Generating actionable, personalized guidance
    - Answering patient questions conversationally
    - Creating counterfactual narratives
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        use_azure: bool = False,
        azure_endpoint: Optional[str] = None,
        azure_deployment: Optional[str] = None,
        model: str = "gpt-4o",
        fallback_mode: bool = True
    ):
        """
        Initialize the narrative engine.
        
        Args:
            api_key: OpenAI API key (or Azure OpenAI key)
            use_azure: Whether to use Azure OpenAI
            azure_endpoint: Azure OpenAI endpoint
            azure_deployment: Azure OpenAI deployment name
            model: Model to use (default: gpt-4o)
            fallback_mode: If True, generate template responses when API unavailable
        """
        self.model = model
        self.fallback_mode = fallback_mode
        self.use_azure = use_azure
        self.client = None
        
        # Try to initialize the API client
        if OPENAI_AVAILABLE:
            if use_azure:
                endpoint = azure_endpoint or get_secret("AZURE_OPENAI_ENDPOINT")
                key = api_key or get_secret("AZURE_OPENAI_API_KEY")
                self.deployment = azure_deployment or get_secret("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
                
                if endpoint and key:
                    self.client = AzureOpenAI(
                        azure_endpoint=endpoint,
                        api_key=key,
                        api_version="2024-02-15-preview"
                    )
            else:
                key = api_key or get_secret("OPENAI_API_KEY")
                if key:
                    self.client = OpenAI(api_key=key)
        
        self.prompts = PromptTemplates()
    
    def is_available(self) -> bool:
        """Check if the AI backend is available"""
        return self.client is not None
    
    def generate_health_explanation(
        self,
        patient_data: Dict[str, Any],
        health_metrics: Dict[str, Any],
        lifestyle_data: Dict[str, Any]
    ) -> NarrativeResponse:
        """
        Generate a personalized explanation of the patient's current health state.
        
        This is the primary function for explaining "where you are now."
        """
        
        # Construct the prompt with patient data
        prompt = PromptTemplates.HEALTH_STATE_EXPLANATION.format(
            patient_name=patient_data.get("name", "Patient"),
            age=patient_data.get("age", 50),
            years_diagnosed=patient_data.get("years_since_diagnosis", 3),
            risk_category=health_metrics.get("risk_category", "moderate"),
            hba1c=health_metrics.get("hba1c", 7.0),
            fasting_glucose=health_metrics.get("fasting_glucose", 140),
            weight=health_metrics.get("weight", 85),
            bmi=health_metrics.get("bmi", 27.8),
            systolic=health_metrics.get("systolic_bp", 135),
            diastolic=health_metrics.get("diastolic_bp", 85),
            health_score=health_metrics.get("overall_health_score", 65),
            activity_level=lifestyle_data.get("activity_level", "lightly_active"),
            diet_quality=lifestyle_data.get("diet_quality", "fair"),
            medication_adherence=int(lifestyle_data.get("medication_adherence", 0.7) * 100),
            stress_level=lifestyle_data.get("stress_level", "moderate"),
            lifestyle_score=int(lifestyle_data.get("overall_score", 0.5) * 100)
        )
        
        response_text = self._call_llm(prompt, "health_explanation")
        
        return NarrativeResponse(
            content=response_text,
            narrative_type="health_explanation",
            tokens_used=len(response_text.split()) * 2,  # Rough estimate
            generated_at=datetime.now(),
            patient_id=patient_data.get("patient_id", ""),
            metadata={
                "metrics_snapshot": health_metrics,
                "lifestyle_snapshot": lifestyle_data
            }
        )
    
    def generate_trajectory_narrative(
        self,
        patient_data: Dict[str, Any],
        trajectories: Dict[str, Dict[str, Any]],
        months: int = 12
    ) -> NarrativeResponse:
        """
        Generate a narrative comparing multiple future trajectories.
        
        This explains "what could happen" under different scenarios.
        """
        
        # Format trajectory summaries
        trajectory_summaries = []
        for scenario_name, traj_data in trajectories.items():
            summary = traj_data.get("summary", {})
            scenario_text = f"""
SCENARIO: {traj_data.get('scenario_name', scenario_name)}
- Description: {traj_data.get('description', 'N/A')}
- Final HbA1c: {summary.get('end_hba1c', 7.0):.1f}% (change: {summary.get('hba1c_change', 0):+.2f}%)
- Final Weight: {summary.get('end_weight', 85):.1f} kg (change: {summary.get('weight_change', 0):+.1f} kg)
- Risk Trend: {summary.get('risk_trend', 'stable')}
"""
            trajectory_summaries.append(scenario_text)
        
        current = trajectories.get("baseline", {}).get("summary", {})
        
        prompt = PromptTemplates.TRAJECTORY_COMPARISON.format(
            patient_name=patient_data.get("name", "Patient"),
            age=patient_data.get("age", 50),
            years_diagnosed=patient_data.get("years_since_diagnosis", 3),
            current_hba1c=current.get("start_hba1c", 7.0),
            current_weight=current.get("start_weight", 85),
            months=months,
            trajectory_summaries="\n".join(trajectory_summaries)
        )
        
        response_text = self._call_llm(prompt, "trajectory_comparison")
        
        return NarrativeResponse(
            content=response_text,
            narrative_type="trajectory_comparison",
            tokens_used=len(response_text.split()) * 2,
            generated_at=datetime.now(),
            patient_id=patient_data.get("patient_id", ""),
            metadata={
                "scenarios_compared": list(trajectories.keys()),
                "simulation_months": months
            }
        )
    
    def generate_conversational_response(
        self,
        user_question: str,
        patient_summary: Dict[str, Any],
        recent_trends: List[Dict[str, Any]]
    ) -> NarrativeResponse:
        """
        Generate a conversational response to a patient's question.
        
        This enables the "Ask Your Twin" feature.
        """
        
        # Format patient summary
        summary_text = json.dumps(patient_summary, indent=2)
        
        # Format trends
        trends_text = "\n".join([
            f"- {t.get('metric', 'Unknown')}: {t.get('direction', 'stable')} - {t.get('narrative', '')}"
            for t in recent_trends
        ]) if recent_trends else "No significant trends detected recently."
        
        prompt = PromptTemplates.CONVERSATIONAL_RESPONSE.format(
            patient_summary=summary_text,
            recent_trends=trends_text,
            user_question=user_question
        )
        
        response_text = self._call_llm(prompt, "conversation")
        
        return NarrativeResponse(
            content=response_text,
            narrative_type="conversation",
            tokens_used=len(response_text.split()) * 2,
            generated_at=datetime.now(),
            patient_id=patient_summary.get("patient_id", ""),
            metadata={
                "question": user_question,
                "trends_used": len(recent_trends)
            }
        )
    
    def generate_action_plan(
        self,
        patient_data: Dict[str, Any],
        health_metrics: Dict[str, Any],
        simulation_insights: str,
        detected_patterns: str
    ) -> NarrativeResponse:
        """
        Generate a personalized, prioritized action plan.
        """
        
        # Determine primary concern
        hba1c = health_metrics.get("hba1c", 7.0)
        if hba1c >= 9.0:
            primary_concern = "Very high HbA1c requiring urgent attention"
        elif hba1c >= 8.0:
            primary_concern = "Elevated HbA1c needing improvement"
        elif hba1c >= 7.0:
            primary_concern = "HbA1c slightly above target"
        else:
            primary_concern = "Maintaining good control"
        
        # Determine weight trend
        weight_change = health_metrics.get("weight_change", 0)
        if weight_change > 2:
            weight_trend = "increasing (up {:.1f} kg)".format(weight_change)
        elif weight_change < -2:
            weight_trend = "decreasing (down {:.1f} kg)".format(abs(weight_change))
        else:
            weight_trend = "stable"
        
        hba1c_status = "above" if float(hba1c) > 7.0 else "at or below"
        
        prompt = PromptTemplates.ACTION_PLAN_GENERATION.format(
            patient_name=patient_data.get("name", "Patient"),
            primary_concern=primary_concern,
            hba1c=hba1c,
            hba1c_status=hba1c_status,
            weight_trend=weight_trend,
            lifestyle_score=int(health_metrics.get("lifestyle_score", 0.5) * 100),
            simulation_insights=simulation_insights,
            detected_patterns=detected_patterns
        )
        
        response_text = self._call_llm(prompt, "action_plan")
        
        return NarrativeResponse(
            content=response_text,
            narrative_type="action_plan",
            tokens_used=len(response_text.split()) * 2,
            generated_at=datetime.now(),
            patient_id=patient_data.get("patient_id", ""),
            metadata={
                "primary_concern": primary_concern,
                "weight_trend": weight_trend
            }
        )
    
    def explain_metric_change(
        self,
        metric_name: str,
        old_value: float,
        new_value: float,
        time_period: str,
        patient_context: str,
        lifestyle_summary: str,
        model_explanations: str
    ) -> NarrativeResponse:
        """
        Explain why a specific health metric changed.
        """
        
        prompt = PromptTemplates.METRIC_CHANGE_EXPLANATION.format(
            metric_name=metric_name,
            old_value=old_value,
            new_value=new_value,
            time_period=time_period,
            patient_context=patient_context,
            lifestyle_summary=lifestyle_summary,
            model_explanations=model_explanations
        )
        
        response_text = self._call_llm(prompt, "metric_explanation")
        
        return NarrativeResponse(
            content=response_text,
            narrative_type="metric_explanation",
            tokens_used=len(response_text.split()) * 2,
            generated_at=datetime.now(),
            patient_id="",
            metadata={
                "metric": metric_name,
                "old_value": old_value,
                "new_value": new_value,
                "change": new_value - old_value
            }
        )
    
    def _call_llm(self, prompt: str, narrative_type: str) -> str:
        """
        Call the LLM with the given prompt.
        Falls back to template responses if API is unavailable.
        """
        
        if self.client:
            try:
                if self.use_azure:
                    response = self.client.chat.completions.create(
                        model=self.deployment,
                        messages=[
                            {"role": "system", "content": PromptTemplates.SYSTEM_PROMPT},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=1000
                    )
                else:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": PromptTemplates.SYSTEM_PROMPT},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=1000
                    )
                
                return response.choices[0].message.content
            
            except Exception as e:
                if self.fallback_mode:
                    return self._generate_fallback_response(prompt, narrative_type, str(e))
                else:
                    raise
        
        elif self.fallback_mode:
            return self._generate_fallback_response(prompt, narrative_type)
        
        else:
            return "AI narrative generation is not available. Please configure an API key."
    
    def _generate_fallback_response(
        self, 
        prompt: str, 
        narrative_type: str,
        error: str = ""
    ) -> str:
        """
        Generate a template-based fallback response when AI is unavailable.
        
        This ensures the demo still works without API keys.
        """
        
        fallback_responses = {
            "health_explanation": """
📊 **Your Current Health Summary**

Based on your digital twin's analysis, here's what your health metrics indicate:

**Diabetes Control**: Your HbA1c level reflects your average blood sugar over the past 2-3 months. 
The target for most people with Type 2 Diabetes is below 7%. Your current level indicates 
{status} of your diabetes.

**Key Observations**:
• Your lifestyle score suggests there's room for improvement in daily habits
• Blood pressure and weight are important factors that influence your overall diabetes risk
• Consistent medication adherence is crucial for maintaining good control

**What This Means For You**:
The good news is that Type 2 Diabetes responds well to lifestyle modifications. 
Small, consistent changes in diet and activity can lead to meaningful improvements 
in your health metrics over the next few months.

**Suggested Focus Area**: Consider starting with one small change this week - 
perhaps a 15-minute walk after dinner or swapping one sugary drink for water.

*Note: This is a demonstration response. Connect an AI service for personalized insights.*
""",
            
            "trajectory_comparison": """
📈 **Your Simulated Health Futures**

Your digital twin has modeled several possible paths your health could take over the coming months:

**Current Path (Baseline)**:
If you continue with your current lifestyle, your health metrics are projected to 
follow their current trends. Small changes compound over time, both positive and negative.

**With Lifestyle Improvements**:
The simulation shows that meaningful improvements in diet and exercise could lead to:
• Lower HbA1c levels (better blood sugar control)
• Gradual weight reduction
• Reduced cardiovascular risk

**Key Insight**:
The biggest impact comes from combining multiple small changes rather than one dramatic shift. 
Regular physical activity paired with mindful eating creates a positive feedback loop.

**Your Most Impactful Change**:
Based on your current profile, increasing physical activity appears to offer the 
most benefit with the most sustainable approach.

**First Step This Week**:
Try adding 10 minutes of walking to your daily routine. This small start builds 
the habit foundation for bigger changes.

*Note: This is a demonstration response. Connect an AI service for personalized trajectory analysis.*
""",
            
            "conversation": """
Thank you for your question! As your health companion, I'm here to help you understand 
your diabetes journey.

Based on your digital twin's data, your health metrics tell an important story about 
how your daily choices affect your wellbeing. The simulation models show that consistent 
small improvements in lifestyle factors like diet, activity, and stress management 
can lead to meaningful changes in your HbA1c and overall health score.

I'd encourage you to explore the "What-If Scenarios" feature to see how different 
lifestyle changes might affect your future health trajectory.

*Note: This is a demonstration response. Connect an AI service for personalized answers to your questions.*
""",
            
            "action_plan": """
📋 **Your Personalized Action Plan**

**🎯 TOP PRIORITY (This Week)**:
Start with one achievable goal: Add 10 minutes of walking after one meal each day.
• Why it matters: Physical activity directly improves insulin sensitivity
• Expected impact: Even small amounts of movement help lower blood sugar

**📅 SHORT-TERM GOALS (This Month)**:
1. Gradually increase walking to 20-30 minutes daily
2. Reduce sugary beverages by half
3. Maintain medication adherence above 90%

**🔮 MEDIUM-TERM VISION (3 Months)**:
With consistent effort, your simulation suggests:
• HbA1c could decrease by 0.5-1.0%
• Weight could decrease by 2-4 kg
• Overall health score could improve significantly

**📊 PROGRESS MARKERS**:
• Energy levels should improve within 2 weeks
• Fasting glucose may start trending down within 4 weeks
• HbA1c changes visible at next lab test (2-3 months)

Check back with your digital twin weekly to track progress and adjust your plan!

*Note: This is a demonstration response. Connect an AI service for a fully personalized action plan.*
""",
            
            "metric_explanation": """
**Understanding This Change**

Health metrics like HbA1c, weight, and blood pressure don't change randomly - 
they respond to your daily choices and behaviors.

When we see changes in your numbers, it's usually because of shifts in:
• **Diet patterns**: What and how much you eat
• **Physical activity**: How much you move
• **Stress and sleep**: Recovery and hormonal balance
• **Medication adherence**: Consistency with prescribed treatments

Think of your body like a complex system where everything is connected. 
Improving one area often creates positive ripple effects in others.

The simulation model tracks these relationships to help you understand 
cause and effect in your health journey.

*Note: This is a demonstration response. Connect an AI service for specific explanations.*
"""
        }
        
        base_response = fallback_responses.get(
            narrative_type, 
            "Analysis in progress. Connect an AI service for detailed insights."
        )
        
        if error:
            base_response += f"\n\n*[API connection issue: {error}]*"
        
        return base_response
