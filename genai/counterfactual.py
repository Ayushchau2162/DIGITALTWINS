"""
Counterfactual Story Generator

This module implements the NOVEL INNOVATION: Counterfactual Health Storytelling.

The concept: "What if you had made different choices X months ago?"

This feature transforms the digital twin from a forward-looking prediction tool
into a reflective health companion that can:
1. Look back at past health states
2. Simulate alternative timelines with different lifestyle choices
3. Generate compelling narratives comparing "what happened" vs "what could have been"
4. Pivot to hope by showing how to get back on track

This is the KEY DIFFERENTIATOR that makes DiabeTwin unique.
"""

from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
from datetime import datetime, timedelta

try:
    from openai import OpenAI, AzureOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

import os
from .prompts import PromptTemplates


@dataclass
class CounterfactualStory:
    """
    A complete counterfactual narrative comparing actual vs alternative history.
    """
    
    # The comparison data
    months_back: int
    actual_start: Dict[str, Any]
    actual_end: Dict[str, Any]
    counterfactual_end: Dict[str, Any]
    alternative_lifestyle: str
    
    # The generated narrative
    narrative: str
    
    # Key insights
    hba1c_difference: float
    weight_difference: float
    missed_opportunity_score: float  # 0-100, how much better things could have been
    
    # Hope/recovery section
    recovery_path: str
    first_steps: List[str]
    recovery_timeline: str
    
    generated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "months_back": self.months_back,
            "actual_start": self.actual_start,
            "actual_end": self.actual_end,
            "counterfactual_end": self.counterfactual_end,
            "alternative_lifestyle": self.alternative_lifestyle,
            "narrative": self.narrative,
            "insights": {
                "hba1c_difference": self.hba1c_difference,
                "weight_difference": self.weight_difference,
                "missed_opportunity_score": self.missed_opportunity_score
            },
            "recovery": {
                "path": self.recovery_path,
                "first_steps": self.first_steps,
                "timeline": self.recovery_timeline
            },
            "generated_at": self.generated_at.isoformat()
        }


class CounterfactualStoryGenerator:
    """
    Generates counterfactual health narratives by comparing
    actual health trajectories with simulated alternative histories.
    
    CORE INNOVATION:
    This creates a "health time machine" experience - showing patients
    what could have been if they had made different choices, then
    pivoting to show how they can still achieve those outcomes.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        use_azure: bool = False,
        azure_endpoint: Optional[str] = None,
        azure_deployment: Optional[str] = None,
        model: str = "gpt-4o"
    ):
        """Initialize the counterfactual generator"""
        self.model = model
        self.use_azure = use_azure
        self.client = None
        
        if OPENAI_AVAILABLE:
            if use_azure:
                endpoint = azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
                key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
                self.deployment = azure_deployment or os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
                
                if endpoint and key:
                    self.client = AzureOpenAI(
                        azure_endpoint=endpoint,
                        api_key=key,
                        api_version="2024-02-15-preview"
                    )
            else:
                key = api_key or os.getenv("OPENAI_API_KEY")
                if key:
                    self.client = OpenAI(api_key=key)
    
    def generate_counterfactual_story(
        self,
        patient_name: str,
        months_ago: int,
        past_state: Dict[str, Any],
        current_state: Dict[str, Any],
        counterfactual_state: Dict[str, Any],
        alternative_lifestyle_description: str
    ) -> CounterfactualStory:
        """
        Generate a complete counterfactual health story.
        
        Args:
            patient_name: Name of the patient
            months_ago: How far back the counterfactual starts
            past_state: Health state from months_ago
            current_state: Current health state (what actually happened)
            counterfactual_state: Simulated state if alternative lifestyle was followed
            alternative_lifestyle_description: Description of the alternative lifestyle
            
        Returns:
            Complete CounterfactualStory with narrative and insights
        """
        
        # Calculate differences
        actual_hba1c_change = current_state.get("hba1c", 7.0) - past_state.get("hba1c", 7.0)
        actual_weight_change = current_state.get("weight", 85) - past_state.get("weight", 85)
        
        counterfactual_hba1c = counterfactual_state.get("hba1c", 7.0)
        counterfactual_weight = counterfactual_state.get("weight", 85)
        
        hba1c_difference = current_state.get("hba1c", 7.0) - counterfactual_hba1c
        weight_difference = current_state.get("weight", 85) - counterfactual_weight
        
        # Calculate missed opportunity score
        # Higher score = bigger gap between actual and potential
        missed_score = min(100, abs(hba1c_difference) * 20 + abs(weight_difference) * 3)
        
        # Generate the narrative
        narrative = self._generate_narrative(
            patient_name=patient_name,
            months_ago=months_ago,
            past_hba1c=past_state.get("hba1c", 7.0),
            past_weight=past_state.get("weight", 85),
            past_activity=past_state.get("activity_level", "lightly_active"),
            past_diet=past_state.get("diet_quality", "fair"),
            current_hba1c=current_state.get("hba1c", 7.0),
            current_weight=current_state.get("weight", 85),
            actual_hba1c_change=actual_hba1c_change,
            actual_weight_change=actual_weight_change,
            alternative_lifestyle=alternative_lifestyle_description,
            counterfactual_hba1c=counterfactual_hba1c,
            counterfactual_weight=counterfactual_weight,
            hba1c_difference=hba1c_difference,
            weight_difference=weight_difference
        )
        
        # Generate recovery path
        recovery_path, first_steps, timeline = self._generate_recovery_path(
            current_state=current_state,
            target_state=counterfactual_state,
            alternative_lifestyle=alternative_lifestyle_description
        )
        
        return CounterfactualStory(
            months_back=months_ago,
            actual_start=past_state,
            actual_end=current_state,
            counterfactual_end=counterfactual_state,
            alternative_lifestyle=alternative_lifestyle_description,
            narrative=narrative,
            hba1c_difference=hba1c_difference,
            weight_difference=weight_difference,
            missed_opportunity_score=missed_score,
            recovery_path=recovery_path,
            first_steps=first_steps,
            recovery_timeline=timeline,
            generated_at=datetime.now()
        )
    
    def _generate_narrative(
        self,
        patient_name: str,
        months_ago: int,
        past_hba1c: float,
        past_weight: float,
        past_activity: str,
        past_diet: str,
        current_hba1c: float,
        current_weight: float,
        actual_hba1c_change: float,
        actual_weight_change: float,
        alternative_lifestyle: str,
        counterfactual_hba1c: float,
        counterfactual_weight: float,
        hba1c_difference: float,
        weight_difference: float
    ) -> str:
        """Generate the main counterfactual narrative using LLM or fallback"""
        
        prompt = PromptTemplates.COUNTERFACTUAL_NARRATIVE.format(
            patient_name=patient_name,
            months_ago=months_ago,
            past_hba1c=past_hba1c,
            past_weight=past_weight,
            past_activity=past_activity,
            past_diet=past_diet,
            current_hba1c=current_hba1c,
            current_weight=current_weight,
            actual_hba1c_change=actual_hba1c_change,
            actual_weight_change=actual_weight_change,
            alternative_lifestyle=alternative_lifestyle,
            counterfactual_hba1c=counterfactual_hba1c,
            counterfactual_weight=counterfactual_weight,
            hba1c_difference=hba1c_difference,
            weight_difference=weight_difference
        )
        
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
                        max_tokens=1200
                    )
                else:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": PromptTemplates.SYSTEM_PROMPT},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=1200
                    )
                
                return response.choices[0].message.content
            
            except Exception as e:
                return self._generate_fallback_narrative(
                    patient_name, months_ago, past_hba1c, current_hba1c,
                    counterfactual_hba1c, hba1c_difference, weight_difference,
                    alternative_lifestyle
                )
        else:
            return self._generate_fallback_narrative(
                patient_name, months_ago, past_hba1c, current_hba1c,
                counterfactual_hba1c, hba1c_difference, weight_difference,
                alternative_lifestyle
            )
    
    def _generate_fallback_narrative(
        self,
        patient_name: str,
        months_ago: int,
        past_hba1c: float,
        current_hba1c: float,
        counterfactual_hba1c: float,
        hba1c_difference: float,
        weight_difference: float,
        alternative_lifestyle: str
    ) -> str:
        """Generate a template-based fallback narrative"""
        
        direction = "risen" if current_hba1c > past_hba1c else "dropped"
        
        narrative = f"""
## ⏰ Your Health Time Machine: A Tale of Two Paths

### The Path You Took

{patient_name}, let's look back at where you were {months_ago} months ago. Your HbA1c was at {past_hba1c:.1f}%. 
Since then, your HbA1c has {direction} to {current_hba1c:.1f}%.

This change reflects the cumulative effect of your daily choices over this period - 
your diet patterns, physical activity levels, medication adherence, and stress management 
all played a role in this trajectory.

### The Road Not Taken

Now, let's imagine an alternate timeline. What if, {months_ago} months ago, you had 
committed to {alternative_lifestyle}?

Our simulation suggests that with these changes, your HbA1c today could have been 
**{counterfactual_hba1c:.1f}%** instead of {current_hba1c:.1f}%. That's a difference 
of **{abs(hba1c_difference):.1f}%** in your diabetes control.

In terms of weight, you could have been approximately **{abs(weight_difference):.1f} kg** 
{"lighter" if weight_difference > 0 else "at a different weight"} than you are today.

### Why This Matters

Each percentage point of HbA1c matters. Research shows that reducing HbA1c by just 1% 
can lower the risk of diabetes complications by up to 40%. The path not taken would have 
put you in a stronger position for long-term health.

### The Good News: Your Path Forward

**Here's what's important: the best time to start was {months_ago} months ago. 
The second best time is today.**

The same lifestyle changes that would have helped then can still help now. Your body 
responds to positive changes at any point. While we can't change the past, your 
digital twin simulation shows that starting {alternative_lifestyle} TODAY can put 
you on a trajectory toward similar outcomes.

In the next {months_ago} months, with consistent effort, you could achieve the health 
state that the counterfactual showed - and possibly even better.

*Let's focus on what you can control: your next choice, your next meal, your next walk.*
"""
        
        return narrative
    
    def _generate_recovery_path(
        self,
        current_state: Dict[str, Any],
        target_state: Dict[str, Any],
        alternative_lifestyle: str
    ) -> Tuple[str, List[str], str]:
        """
        Generate the recovery path section of the counterfactual.
        
        Returns:
            Tuple of (recovery_path_description, first_steps_list, timeline)
        """
        
        hba1c_gap = current_state.get("hba1c", 7.0) - target_state.get("hba1c", 7.0)
        
        # Estimate recovery timeline based on gap
        if hba1c_gap > 1.5:
            timeline = "6-12 months with consistent effort"
        elif hba1c_gap > 0.5:
            timeline = "3-6 months with dedicated changes"
        else:
            timeline = "2-4 months with focused improvements"
        
        recovery_path = f"""
The gap between where you are and where you could be is bridgeable. Based on your 
digital twin's analysis, here's your path to recovery:

**Target**: Reduce HbA1c by approximately {abs(hba1c_gap):.1f}% 
**Timeline**: {timeline}
**Approach**: {alternative_lifestyle}

Your body will begin responding to positive changes within weeks. Blood glucose 
levels can start improving in days, and HbA1c - which reflects a 2-3 month average - 
will begin trending downward within the first month of sustained effort.
"""
        
        # Generate specific first steps
        first_steps = [
            "Start with a 15-minute walk after your largest meal each day",
            "Replace one sugary drink with water daily",
            "Set a medication reminder to improve adherence to 90%+",
            "Try one new vegetable this week",
            "Schedule your next HbA1c test for 3 months from now"
        ]
        
        return recovery_path, first_steps, timeline
    
    def generate_quick_counterfactual(
        self,
        current_hba1c: float,
        current_weight: float,
        months_back: int = 6,
        improvement_scenario: str = "moderate"
    ) -> Dict[str, Any]:
        """
        Generate a quick counterfactual summary without full narrative.
        
        Useful for UI display and quick insights.
        
        Args:
            current_hba1c: Current HbA1c value
            current_weight: Current weight
            months_back: How far to look back
            improvement_scenario: "mild", "moderate", or "aggressive"
            
        Returns:
            Dictionary with counterfactual metrics
        """
        
        # Estimate what could have been based on scenario
        improvements = {
            "mild": {"hba1c": 0.3, "weight": 2.0},
            "moderate": {"hba1c": 0.6, "weight": 4.0},
            "aggressive": {"hba1c": 1.0, "weight": 7.0}
        }
        
        imp = improvements.get(improvement_scenario, improvements["moderate"])
        
        # Scale by months
        scale = min(1.0, months_back / 6)
        
        counterfactual_hba1c = current_hba1c - (imp["hba1c"] * scale)
        counterfactual_weight = current_weight - (imp["weight"] * scale)
        
        # Ensure reasonable bounds
        counterfactual_hba1c = max(5.5, counterfactual_hba1c)
        counterfactual_weight = max(50, counterfactual_weight)
        
        return {
            "months_back": months_back,
            "scenario": improvement_scenario,
            "current": {
                "hba1c": current_hba1c,
                "weight": current_weight
            },
            "counterfactual": {
                "hba1c": round(counterfactual_hba1c, 1),
                "weight": round(counterfactual_weight, 1)
            },
            "difference": {
                "hba1c": round(current_hba1c - counterfactual_hba1c, 1),
                "weight": round(current_weight - counterfactual_weight, 1)
            },
            "message": f"With {improvement_scenario} lifestyle improvements over {months_back} months, "
                      f"your HbA1c could be {counterfactual_hba1c:.1f}% instead of {current_hba1c:.1f}%."
        }
    
    def get_counterfactual_scenarios(self) -> List[Dict[str, Any]]:
        """
        Return available counterfactual scenarios for the UI.
        """
        return [
            {
                "id": "diet_focus",
                "name": "Better Nutrition Path",
                "description": "What if you had focused on improving diet quality?",
                "lifestyle_changes": "balanced diet with more fiber, less processed foods, and portion control",
                "expected_impact": "HbA1c: -0.5 to -0.8%, Weight: -3 to -5 kg over 6 months"
            },
            {
                "id": "exercise_focus",
                "name": "Active Lifestyle Path",
                "description": "What if you had maintained regular physical activity?",
                "lifestyle_changes": "150+ minutes of moderate exercise per week, daily walks",
                "expected_impact": "HbA1c: -0.4 to -0.6%, Weight: -2 to -4 kg over 6 months"
            },
            {
                "id": "medication_focus",
                "name": "Consistent Treatment Path",
                "description": "What if you had achieved 95%+ medication adherence?",
                "lifestyle_changes": "taking medications exactly as prescribed, never missing doses",
                "expected_impact": "HbA1c: -0.5 to -1.0% over 6 months"
            },
            {
                "id": "comprehensive",
                "name": "Full Commitment Path",
                "description": "What if you had made comprehensive lifestyle changes?",
                "lifestyle_changes": "improved diet, regular exercise, stress management, and perfect medication adherence",
                "expected_impact": "HbA1c: -1.0 to -1.5%, Weight: -5 to -8 kg over 6 months"
            },
            {
                "id": "stress_sleep",
                "name": "Wellness & Recovery Path",
                "description": "What if you had prioritized stress and sleep?",
                "lifestyle_changes": "stress reduction techniques, 7-8 hours quality sleep, mindfulness practices",
                "expected_impact": "HbA1c: -0.3 to -0.5%, improved energy and wellbeing"
            }
        ]
