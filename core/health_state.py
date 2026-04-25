"""
Health State Model Module

This module implements the computational model for health state evolution
in Type 2 Diabetes. The model is designed to be:
- INTERPRETABLE: Every calculation can be explained
- PHYSIOLOGICALLY PLAUSIBLE: Based on established relationships
- MODULAR: Easy to extend or modify individual components

KEY PRINCIPLE: This is a simplified simulation model for demonstration.
It captures qualitative relationships, not clinical precision.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Tuple, List, Optional
from enum import Enum
import math
import random


class HealthMetric(Enum):
    """Enumeration of tracked health metrics"""
    HBA1C = "hba1c"
    FASTING_GLUCOSE = "fasting_glucose"
    WEIGHT = "weight"
    SYSTOLIC_BP = "systolic_bp"
    DIASTOLIC_BP = "diastolic_bp"
    LDL = "ldl"
    HDL = "hdl"
    TRIGLYCERIDES = "triglycerides"


@dataclass
class HealthState:
    """
    Represents a complete health state snapshot at a point in time.
    
    This is the core data structure that flows through the temporal engine.
    """
    
    # Primary diabetes metrics
    hba1c_percent: float
    fasting_glucose_mgdl: float
    
    # Weight and body composition
    weight_kg: float
    
    # Cardiovascular metrics
    systolic_bp: int
    diastolic_bp: int
    
    # Lipid panel
    ldl_cholesterol_mgdl: float
    hdl_cholesterol_mgdl: float
    triglycerides_mgdl: float
    
    # Computed risk scores
    cardiovascular_risk_score: float = 0.0
    diabetes_progression_score: float = 0.0
    overall_health_score: float = 0.0
    
    # Metadata
    time_step: int = 0  # Which time step this state represents
    
    def compute_derived_scores(self, lifestyle_score: float = 0.5) -> None:
        """
        Calculate derived risk and health scores.
        Called after metrics are updated.
        """
        # Cardiovascular risk (simplified Framingham-inspired)
        cv_risk = 0.0
        
        # HbA1c contribution
        if self.hba1c_percent >= 9.0:
            cv_risk += 0.25
        elif self.hba1c_percent >= 7.5:
            cv_risk += 0.15
        elif self.hba1c_percent >= 6.5:
            cv_risk += 0.08
        
        # Blood pressure contribution
        if self.systolic_bp >= 160:
            cv_risk += 0.25
        elif self.systolic_bp >= 140:
            cv_risk += 0.15
        elif self.systolic_bp >= 130:
            cv_risk += 0.08
        
        # Lipid contribution
        if self.ldl_cholesterol_mgdl >= 160:
            cv_risk += 0.15
        elif self.ldl_cholesterol_mgdl >= 130:
            cv_risk += 0.08
        
        if self.hdl_cholesterol_mgdl < 40:
            cv_risk += 0.10
        elif self.hdl_cholesterol_mgdl > 60:
            cv_risk -= 0.05
        
        self.cardiovascular_risk_score = min(1.0, max(0.0, cv_risk))
        
        # Diabetes progression score (higher = worse control, faster progression)
        prog_score = 0.0
        if self.hba1c_percent >= 9.0:
            prog_score = 0.9
        elif self.hba1c_percent >= 8.0:
            prog_score = 0.7
        elif self.hba1c_percent >= 7.0:
            prog_score = 0.5
        elif self.hba1c_percent >= 6.5:
            prog_score = 0.3
        else:
            prog_score = 0.1
        
        # Adjust for glucose variability (simplified)
        if self.fasting_glucose_mgdl > 180:
            prog_score += 0.1
        
        self.diabetes_progression_score = min(1.0, prog_score)
        
        # Overall health score (0-100, higher = better)
        # Inverse of risk factors + lifestyle contribution
        health = 100.0
        health -= self.cardiovascular_risk_score * 30
        health -= self.diabetes_progression_score * 30
        health += lifestyle_score * 20
        
        # Weight penalty
        # Assuming height of 1.75m for BMI calculation
        bmi = self.weight_kg / (1.75 ** 2)
        if bmi >= 35:
            health -= 15
        elif bmi >= 30:
            health -= 10
        elif bmi >= 25:
            health -= 5
        
        self.overall_health_score = max(0.0, min(100.0, health))
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize health state"""
        return {
            "hba1c_percent": self.hba1c_percent,
            "fasting_glucose_mgdl": self.fasting_glucose_mgdl,
            "weight_kg": self.weight_kg,
            "systolic_bp": self.systolic_bp,
            "diastolic_bp": self.diastolic_bp,
            "ldl_cholesterol_mgdl": self.ldl_cholesterol_mgdl,
            "hdl_cholesterol_mgdl": self.hdl_cholesterol_mgdl,
            "triglycerides_mgdl": self.triglycerides_mgdl,
            "cardiovascular_risk_score": self.cardiovascular_risk_score,
            "diabetes_progression_score": self.diabetes_progression_score,
            "overall_health_score": self.overall_health_score,
            "time_step": self.time_step
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HealthState':
        """Deserialize health state"""
        return cls(
            hba1c_percent=data.get("hba1c_percent", 7.0),
            fasting_glucose_mgdl=data.get("fasting_glucose_mgdl", 140.0),
            weight_kg=data.get("weight_kg", 85.0),
            systolic_bp=data.get("systolic_bp", 135),
            diastolic_bp=data.get("diastolic_bp", 85),
            ldl_cholesterol_mgdl=data.get("ldl_cholesterol_mgdl", 120.0),
            hdl_cholesterol_mgdl=data.get("hdl_cholesterol_mgdl", 45.0),
            triglycerides_mgdl=data.get("triglycerides_mgdl", 170.0),
            cardiovascular_risk_score=data.get("cardiovascular_risk_score", 0.0),
            diabetes_progression_score=data.get("diabetes_progression_score", 0.0),
            overall_health_score=data.get("overall_health_score", 0.0),
            time_step=data.get("time_step", 0)
        )
    
    def copy(self) -> 'HealthState':
        """Create a copy of this health state"""
        return HealthState.from_dict(self.to_dict())


class HealthStateModel:
    """
    The computational engine that updates health states based on
    lifestyle factors, interventions, and time.
    
    DESIGN PHILOSOPHY:
    - Each update rule is documented and explainable
    - Effects are cumulative over time
    - There's natural biological variability
    - Positive changes take time to show results
    - Negative patterns accelerate deterioration
    """
    
    # Time constants (in "months" as our time unit)
    HBA1C_RESPONSE_TIME = 3  # HbA1c changes reflect ~3 month average
    WEIGHT_RESPONSE_TIME = 1  # Weight can change faster
    BP_RESPONSE_TIME = 2  # BP responds in weeks to months
    
    # Physiological limits
    MIN_HBA1C = 4.0
    MAX_HBA1C = 14.0
    MIN_FASTING_GLUCOSE = 70
    MAX_FASTING_GLUCOSE = 400
    MIN_WEIGHT = 40.0
    MAX_WEIGHT = 200.0
    
    def __init__(self, variability: float = 0.1):
        """
        Initialize the health state model.
        
        Args:
            variability: Amount of random biological variability (0-1)
        """
        self.variability = variability
    
    def compute_next_state(
        self,
        current_state: HealthState,
        lifestyle_score: float,
        activity_score: float,
        diet_score: float,
        stress_score: float,
        medication_adherence: float,
        genetic_risk: float = 0.5,
        time_delta: int = 1  # months
    ) -> Tuple[HealthState, Dict[str, str]]:
        """
        Compute the next health state based on current state and factors.
        
        Returns:
            Tuple of (new_health_state, explanation_dict)
            
        The explanation dict contains human-readable reasons for each change.
        """
        
        new_state = current_state.copy()
        new_state.time_step = current_state.time_step + time_delta
        explanations = {}
        
        # === HbA1c EVOLUTION ===
        hba1c_change, hba1c_reason = self._compute_hba1c_change(
            current_state.hba1c_percent,
            lifestyle_score,
            diet_score,
            activity_score,
            medication_adherence,
            genetic_risk,
            time_delta
        )
        new_state.hba1c_percent = self._clamp(
            current_state.hba1c_percent + hba1c_change,
            self.MIN_HBA1C,
            self.MAX_HBA1C
        )
        explanations["hba1c"] = hba1c_reason
        
        # === FASTING GLUCOSE EVOLUTION ===
        # Glucose correlates with HbA1c but has more variability
        glucose_change, glucose_reason = self._compute_glucose_change(
            current_state.fasting_glucose_mgdl,
            new_state.hba1c_percent,
            diet_score,
            stress_score,
            time_delta
        )
        new_state.fasting_glucose_mgdl = self._clamp(
            current_state.fasting_glucose_mgdl + glucose_change,
            self.MIN_FASTING_GLUCOSE,
            self.MAX_FASTING_GLUCOSE
        )
        explanations["fasting_glucose"] = glucose_reason
        
        # === WEIGHT EVOLUTION ===
        weight_change, weight_reason = self._compute_weight_change(
            current_state.weight_kg,
            diet_score,
            activity_score,
            stress_score,
            time_delta
        )
        new_state.weight_kg = self._clamp(
            current_state.weight_kg + weight_change,
            self.MIN_WEIGHT,
            self.MAX_WEIGHT
        )
        new_state.weight_kg = round(new_state.weight_kg, 1)
        explanations["weight"] = weight_reason
        
        # === BLOOD PRESSURE EVOLUTION ===
        bp_changes, bp_reason = self._compute_bp_change(
            current_state.systolic_bp,
            current_state.diastolic_bp,
            current_state.weight_kg,
            new_state.weight_kg,
            activity_score,
            stress_score,
            medication_adherence,
            time_delta
        )
        new_state.systolic_bp = int(self._clamp(
            current_state.systolic_bp + bp_changes[0], 90, 200
        ))
        new_state.diastolic_bp = int(self._clamp(
            current_state.diastolic_bp + bp_changes[1], 60, 130
        ))
        explanations["blood_pressure"] = bp_reason
        
        # === LIPID PANEL EVOLUTION ===
        lipid_changes, lipid_reason = self._compute_lipid_changes(
            current_state,
            diet_score,
            activity_score,
            medication_adherence,
            time_delta
        )
        new_state.ldl_cholesterol_mgdl = self._clamp(
            current_state.ldl_cholesterol_mgdl + lipid_changes[0], 50, 250
        )
        new_state.hdl_cholesterol_mgdl = self._clamp(
            current_state.hdl_cholesterol_mgdl + lipid_changes[1], 25, 100
        )
        new_state.triglycerides_mgdl = self._clamp(
            current_state.triglycerides_mgdl + lipid_changes[2], 50, 500
        )
        explanations["lipids"] = lipid_reason
        
        # Compute derived scores
        new_state.compute_derived_scores(lifestyle_score)
        
        return new_state, explanations
    
    def _compute_hba1c_change(
        self,
        current_hba1c: float,
        lifestyle_score: float,
        diet_score: float,
        activity_score: float,
        medication_adherence: float,
        genetic_risk: float,
        time_delta: int
    ) -> Tuple[float, str]:
        """
        Compute HbA1c change based on multiple factors.
        
        Key relationships modeled:
        - Diet quality directly impacts glucose control
        - Physical activity improves insulin sensitivity
        - Medication adherence is crucial for management
        - Genetic factors influence baseline trajectory
        """
        
        # Base drift (natural progression if untreated)
        # Diabetes tends to progress over time due to beta-cell decline
        natural_drift = 0.02 * genetic_risk * time_delta
        
        # Diet effect: Good diet reduces HbA1c, poor diet increases it
        # Maximum effect: ±0.3% per month
        diet_effect = (0.5 - diet_score) * 0.3 * time_delta
        
        # Activity effect: Exercise improves insulin sensitivity
        # Maximum effect: -0.2% per month for very active
        activity_effect = (0.5 - activity_score) * 0.2 * time_delta
        
        # Medication effect: Good adherence maintains/improves control
        # Effect scaled by how far from target (more room to improve)
        distance_from_target = max(0, current_hba1c - 6.5)
        medication_effect = -medication_adherence * 0.15 * min(distance_from_target / 2, 1) * time_delta
        
        # Combine effects
        total_change = natural_drift + diet_effect + activity_effect + medication_effect
        
        # Add biological variability
        variability = self._add_variability(0.05)
        total_change += variability
        
        # Generate explanation
        reasons = []
        if diet_effect > 0.05:
            reasons.append("dietary patterns increasing glucose levels")
        elif diet_effect < -0.05:
            reasons.append("healthy diet improving glucose control")
        
        if activity_effect > 0.03:
            reasons.append("low physical activity reducing insulin sensitivity")
        elif activity_effect < -0.03:
            reasons.append("regular exercise improving insulin sensitivity")
        
        if medication_effect < -0.05:
            reasons.append("good medication adherence helping control")
        elif medication_adherence < 0.5:
            reasons.append("inconsistent medication affecting control")
        
        if not reasons:
            reasons.append("relatively stable metabolic state")
        
        explanation = f"HbA1c {'increased' if total_change > 0 else 'decreased'} due to: {', '.join(reasons)}."
        
        return round(total_change, 2), explanation
    
    def _compute_glucose_change(
        self,
        current_glucose: float,
        target_hba1c: float,
        diet_score: float,
        stress_score: float,
        time_delta: int
    ) -> Tuple[float, str]:
        """
        Compute fasting glucose change.
        
        Glucose is more variable day-to-day but trends with HbA1c.
        Stress hormones (cortisol) can acutely raise glucose.
        """
        
        # Glucose tends to correlate with HbA1c
        # Approximate relationship: FG ≈ 28.7 × HbA1c - 46.7
        expected_glucose = 28.7 * target_hba1c - 46.7
        
        # Move toward expected value
        glucose_drift = (expected_glucose - current_glucose) * 0.3 * time_delta
        
        # Stress effect: High stress raises glucose
        stress_effect = (stress_score - 0.5) * 15 * time_delta
        
        # Diet effect on acute glucose
        diet_effect = (0.5 - diet_score) * 10 * time_delta
        
        total_change = glucose_drift + stress_effect + diet_effect
        
        # Higher variability for glucose
        variability = self._add_variability(5)
        total_change += variability
        
        reasons = []
        if stress_effect > 5:
            reasons.append("elevated stress hormones raising blood sugar")
        if diet_effect > 5:
            reasons.append("dietary carbohydrates affecting glucose")
        if abs(glucose_drift) > 5:
            reasons.append("glucose adjusting to match overall metabolic state")
        
        if not reasons:
            reasons.append("normal daily fluctuations")
        
        explanation = f"Fasting glucose {'rose' if total_change > 0 else 'dropped'}: {', '.join(reasons)}."
        
        return round(total_change, 1), explanation
    
    def _compute_weight_change(
        self,
        current_weight: float,
        diet_score: float,
        activity_score: float,
        stress_score: float,
        time_delta: int
    ) -> Tuple[float, str]:
        """
        Compute weight change based on energy balance factors.
        
        Weight change is modeled as a function of:
        - Caloric intake (diet quality as proxy)
        - Energy expenditure (activity level)
        - Stress eating / cortisol effects
        """
        
        # Energy balance model (simplified)
        # Positive = weight gain, negative = weight loss
        
        # Diet effect: Poor diet → weight gain, good diet → loss
        # Max effect: ±1.5 kg per month
        diet_effect = (0.5 - diet_score) * 1.5 * time_delta
        
        # Activity effect: More activity → weight loss
        # Max effect: -1.0 kg per month
        activity_effect = (0.5 - activity_score) * 1.0 * time_delta
        
        # Stress effect: High stress → stress eating → weight gain
        stress_effect = (stress_score - 0.5) * 0.5 * time_delta
        
        total_change = diet_effect + activity_effect + stress_effect
        
        # Variability
        variability = self._add_variability(0.3)
        total_change += variability
        
        # Cap monthly change at reasonable levels
        total_change = max(-2.0, min(2.0, total_change))
        
        reasons = []
        if diet_effect > 0.3:
            reasons.append("caloric intake exceeding expenditure")
        elif diet_effect < -0.3:
            reasons.append("balanced nutrition supporting weight management")
        
        if activity_effect > 0.3:
            reasons.append("low activity limiting calorie burn")
        elif activity_effect < -0.3:
            reasons.append("regular exercise burning calories")
        
        if stress_effect > 0.2:
            reasons.append("stress-related eating patterns")
        
        if not reasons:
            reasons.append("weight relatively stable")
        
        direction = "gain" if total_change > 0 else "loss"
        explanation = f"Weight {direction} influenced by: {', '.join(reasons)}."
        
        return round(total_change, 1), explanation
    
    def _compute_bp_change(
        self,
        current_systolic: int,
        current_diastolic: int,
        old_weight: float,
        new_weight: float,
        activity_score: float,
        stress_score: float,
        medication_adherence: float,
        time_delta: int
    ) -> Tuple[Tuple[int, int], str]:
        """
        Compute blood pressure changes.
        
        BP is affected by:
        - Weight changes (strong relationship)
        - Physical activity (lowers BP)
        - Stress (raises BP acutely and chronically)
        - Medication adherence
        """
        
        # Weight effect: Each kg change affects BP
        weight_change = new_weight - old_weight
        weight_effect_systolic = weight_change * 1.0  # ~1 mmHg per kg
        weight_effect_diastolic = weight_change * 0.5
        
        # Activity effect: Regular exercise lowers BP
        activity_effect_systolic = (0.5 - activity_score) * 4 * time_delta
        activity_effect_diastolic = (0.5 - activity_score) * 2 * time_delta
        
        # Stress effect
        stress_effect_systolic = (stress_score - 0.5) * 5 * time_delta
        stress_effect_diastolic = (stress_score - 0.5) * 3 * time_delta
        
        # Medication effect (if on BP meds, which we assume for hypertensive patients)
        med_effect_systolic = -medication_adherence * 5 * time_delta
        med_effect_diastolic = -medication_adherence * 3 * time_delta
        
        # If BP is already in normal range, reduce medication effect
        if current_systolic < 130:
            med_effect_systolic *= 0.3
            med_effect_diastolic *= 0.3
        
        total_systolic = (weight_effect_systolic + activity_effect_systolic + 
                         stress_effect_systolic + med_effect_systolic)
        total_diastolic = (weight_effect_diastolic + activity_effect_diastolic + 
                          stress_effect_diastolic + med_effect_diastolic)
        
        # Variability
        total_systolic += self._add_variability(2)
        total_diastolic += self._add_variability(1)
        
        reasons = []
        if abs(weight_effect_systolic) > 1:
            reasons.append(f"weight change affecting cardiovascular load")
        if activity_effect_systolic > 2:
            reasons.append("reduced physical activity")
        elif activity_effect_systolic < -2:
            reasons.append("regular exercise improving vascular health")
        if stress_effect_systolic > 2:
            reasons.append("chronic stress elevating blood pressure")
        
        if not reasons:
            reasons.append("blood pressure relatively stable")
        
        explanation = f"Blood pressure changes due to: {', '.join(reasons)}."
        
        return (int(total_systolic), int(total_diastolic)), explanation
    
    def _compute_lipid_changes(
        self,
        current_state: HealthState,
        diet_score: float,
        activity_score: float,
        medication_adherence: float,
        time_delta: int
    ) -> Tuple[Tuple[float, float, float], str]:
        """
        Compute changes in lipid panel (LDL, HDL, Triglycerides).
        
        - Diet strongly affects all lipids
        - Exercise particularly improves HDL
        - Weight loss improves triglycerides
        """
        
        # LDL: Diet is primary driver
        ldl_change = (0.5 - diet_score) * 5 * time_delta
        ldl_change += self._add_variability(2)
        
        # HDL: Exercise is primary driver (increases HDL)
        hdl_change = (activity_score - 0.5) * 3 * time_delta
        hdl_change += self._add_variability(1)
        
        # Triglycerides: Diet (especially carbs) and weight
        trig_change = (0.5 - diet_score) * 10 * time_delta
        trig_change += self._add_variability(5)
        
        reasons = []
        if ldl_change > 2:
            reasons.append("dietary saturated fat affecting LDL")
        elif ldl_change < -2:
            reasons.append("heart-healthy diet lowering LDL")
        
        if hdl_change > 1:
            reasons.append("physical activity boosting HDL")
        elif hdl_change < -1:
            reasons.append("sedentary behavior reducing HDL")
        
        if abs(trig_change) > 5:
            reasons.append("dietary patterns affecting triglycerides")
        
        if not reasons:
            reasons.append("lipid levels relatively stable")
        
        explanation = f"Lipid changes: {', '.join(reasons)}."
        
        return (ldl_change, hdl_change, trig_change), explanation
    
    def _add_variability(self, scale: float) -> float:
        """Add random biological variability"""
        return random.gauss(0, scale * self.variability)
    
    def _clamp(self, value: float, min_val: float, max_val: float) -> float:
        """Clamp value within physiological bounds"""
        return max(min_val, min(max_val, value))
    
    def get_model_explanation(self) -> str:
        """
        Return a human-readable explanation of how the model works.
        This supports the explainability requirement.
        """
        return """
        === DiabeTwin Health State Model ===
        
        This model simulates how Type 2 Diabetes progresses over time based on 
        lifestyle factors and interventions. Here's how it works:
        
        🔬 HbA1c (Glycated Hemoglobin):
        - Reflects average blood sugar over 2-3 months
        - Improves with: good diet, regular exercise, medication adherence
        - Worsens with: poor diet, sedentary lifestyle, genetic predisposition
        - Target: < 7.0% for most patients
        
        🩸 Fasting Glucose:
        - More variable day-to-day than HbA1c
        - Strongly affected by recent meals and stress
        - Correlates with HbA1c over time
        - Target: 80-130 mg/dL
        
        ⚖️ Weight:
        - Changes based on energy balance (calories in vs. out)
        - Diet quality and physical activity are main drivers
        - Stress can trigger emotional eating
        - Even 5-7% weight loss significantly improves diabetes control
        
        ❤️ Blood Pressure:
        - Closely linked to weight (each kg matters)
        - Exercise has direct BP-lowering effect
        - Chronic stress elevates BP
        - Target: < 130/80 mmHg for diabetic patients
        
        🧪 Lipid Panel:
        - LDL: Primarily diet-driven
        - HDL: Improves with exercise
        - Triglycerides: Affected by carbs and weight
        
        ⏱️ Time Dynamics:
        - Changes accumulate over months
        - Positive changes take time to show
        - Negative patterns accelerate decline
        - The model includes natural biological variability
        
        ⚠️ Important: This is a simplified educational model.
        Real disease progression is more complex.
        """
