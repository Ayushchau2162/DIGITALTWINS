"""
Virtual Patient Representation Module

This module defines the synthetic patient profile for the DiabeTwin system.
A Virtual Patient encapsulates all attributes needed to simulate a Type 2 Diabetes
patient's health trajectory.

DESIGN PHILOSOPHY:
- Every attribute is explainable and interpretable
- Values are synthetic but physiologically plausible
- The patient is a "living entity" that evolves over time
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from enum import Enum
import random
import json


class DiabetesRiskCategory(Enum):
    """Risk stratification for diabetes progression"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class ActivityLevel(Enum):
    """Physical activity classification"""
    SEDENTARY = "sedentary"           # <30 min/week
    LIGHTLY_ACTIVE = "lightly_active"  # 30-90 min/week
    MODERATELY_ACTIVE = "moderately_active"  # 90-150 min/week
    ACTIVE = "active"                  # 150-300 min/week
    VERY_ACTIVE = "very_active"        # >300 min/week


class DietQuality(Enum):
    """Diet quality score classification"""
    POOR = "poor"           # High processed foods, sugary drinks
    FAIR = "fair"           # Mixed diet, some processed foods
    GOOD = "good"           # Balanced diet, moderate portions
    EXCELLENT = "excellent"  # Mediterranean-style, whole foods


class StressLevel(Enum):
    """Chronic stress level classification"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"


@dataclass
class LifestyleFactors:
    """
    Modifiable lifestyle factors that directly influence diabetes outcomes.
    
    These are the PRIMARY INTERVENTION POINTS for the digital twin.
    Each factor has documented impact on glycemic control.
    """
    
    # Physical Activity (weekly minutes of moderate exercise)
    exercise_minutes_per_week: int = 60
    activity_level: ActivityLevel = ActivityLevel.LIGHTLY_ACTIVE
    
    # Nutrition
    diet_quality: DietQuality = DietQuality.FAIR
    daily_carb_intake_grams: int = 250  # Average carbohydrate intake
    daily_fiber_intake_grams: int = 15   # Fiber intake
    sugary_drinks_per_week: int = 5      # Number of sugary beverages
    
    # Sleep
    average_sleep_hours: float = 6.5
    sleep_quality_score: float = 0.6  # 0-1 scale
    
    # Stress & Mental Health
    stress_level: StressLevel = StressLevel.MODERATE
    stress_score: float = 0.5  # 0-1 scale (higher = more stressed)
    
    # Medication Adherence (if on medication)
    medication_adherence: float = 0.7  # 0-1 scale
    
    # Other Behaviors
    smoking_status: bool = False
    alcohol_drinks_per_week: int = 3
    
    def get_activity_score(self) -> float:
        """Convert activity level to 0-1 score for calculations"""
        mapping = {
            ActivityLevel.SEDENTARY: 0.1,
            ActivityLevel.LIGHTLY_ACTIVE: 0.3,
            ActivityLevel.MODERATELY_ACTIVE: 0.5,
            ActivityLevel.ACTIVE: 0.7,
            ActivityLevel.VERY_ACTIVE: 0.9
        }
        return mapping.get(self.activity_level, 0.3)
    
    def get_diet_score(self) -> float:
        """Convert diet quality to 0-1 score"""
        mapping = {
            DietQuality.POOR: 0.2,
            DietQuality.FAIR: 0.4,
            DietQuality.GOOD: 0.7,
            DietQuality.EXCELLENT: 0.95
        }
        return mapping.get(self.diet_quality, 0.4)
    
    def get_overall_lifestyle_score(self) -> float:
        """
        Compute composite lifestyle score (0-1).
        Higher = healthier lifestyle choices.
        """
        activity = self.get_activity_score() * 0.25
        diet = self.get_diet_score() * 0.25
        sleep = min(self.average_sleep_hours / 8.0, 1.0) * self.sleep_quality_score * 0.15
        stress = (1 - self.stress_score) * 0.15
        adherence = self.medication_adherence * 0.10
        smoking = (0.0 if self.smoking_status else 0.05)
        alcohol = max(0, 0.05 - (self.alcohol_drinks_per_week * 0.005))
        
        return min(1.0, activity + diet + sleep + stress + adherence + smoking + alcohol)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize lifestyle factors"""
        return {
            "exercise_minutes_per_week": self.exercise_minutes_per_week,
            "activity_level": self.activity_level.value,
            "diet_quality": self.diet_quality.value,
            "daily_carb_intake_grams": self.daily_carb_intake_grams,
            "daily_fiber_intake_grams": self.daily_fiber_intake_grams,
            "sugary_drinks_per_week": self.sugary_drinks_per_week,
            "average_sleep_hours": self.average_sleep_hours,
            "sleep_quality_score": self.sleep_quality_score,
            "stress_level": self.stress_level.value,
            "stress_score": self.stress_score,
            "medication_adherence": self.medication_adherence,
            "smoking_status": self.smoking_status,
            "alcohol_drinks_per_week": self.alcohol_drinks_per_week,
            "overall_score": self.get_overall_lifestyle_score()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LifestyleFactors':
        """Deserialize lifestyle factors"""
        return cls(
            exercise_minutes_per_week=data.get("exercise_minutes_per_week", 60),
            activity_level=ActivityLevel(data.get("activity_level", "lightly_active")),
            diet_quality=DietQuality(data.get("diet_quality", "fair")),
            daily_carb_intake_grams=data.get("daily_carb_intake_grams", 250),
            daily_fiber_intake_grams=data.get("daily_fiber_intake_grams", 15),
            sugary_drinks_per_week=data.get("sugary_drinks_per_week", 5),
            average_sleep_hours=data.get("average_sleep_hours", 6.5),
            sleep_quality_score=data.get("sleep_quality_score", 0.6),
            stress_level=StressLevel(data.get("stress_level", "moderate")),
            stress_score=data.get("stress_score", 0.5),
            medication_adherence=data.get("medication_adherence", 0.7),
            smoking_status=data.get("smoking_status", False),
            alcohol_drinks_per_week=data.get("alcohol_drinks_per_week", 3)
        )


@dataclass
class PatientProfile:
    """
    Static patient demographics and baseline characteristics.
    
    These represent non-modifiable or slowly-changing attributes.
    """
    
    # Unique identifier
    patient_id: str = ""
    name: str = "Virtual Patient"
    
    # Demographics
    age: int = 52
    biological_sex: str = "male"  # male/female (affects some risk calculations)
    height_cm: float = 175.0
    
    # Diabetes-specific history
    years_since_diagnosis: int = 3
    family_history_diabetes: bool = True
    
    # Comorbidities (simplified)
    has_hypertension: bool = True
    has_dyslipidemia: bool = False
    has_cardiovascular_disease: bool = False
    
    # Genetic risk modifier (0-1, higher = more genetic predisposition)
    genetic_risk_factor: float = 0.6
    
    # Creation timestamp
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_age_risk_factor(self) -> float:
        """Age-based risk multiplier for diabetes progression"""
        if self.age < 40:
            return 0.8
        elif self.age < 50:
            return 1.0
        elif self.age < 60:
            return 1.2
        elif self.age < 70:
            return 1.4
        else:
            return 1.6
    
    def get_comorbidity_risk_factor(self) -> float:
        """Cumulative risk from comorbid conditions"""
        risk = 1.0
        if self.has_hypertension:
            risk += 0.15
        if self.has_dyslipidemia:
            risk += 0.10
        if self.has_cardiovascular_disease:
            risk += 0.25
        return risk
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize patient profile"""
        return {
            "patient_id": self.patient_id,
            "name": self.name,
            "age": self.age,
            "biological_sex": self.biological_sex,
            "height_cm": self.height_cm,
            "years_since_diagnosis": self.years_since_diagnosis,
            "family_history_diabetes": self.family_history_diabetes,
            "has_hypertension": self.has_hypertension,
            "has_dyslipidemia": self.has_dyslipidemia,
            "has_cardiovascular_disease": self.has_cardiovascular_disease,
            "genetic_risk_factor": self.genetic_risk_factor,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PatientProfile':
        """Deserialize patient profile"""
        profile = cls(
            patient_id=data.get("patient_id", ""),
            name=data.get("name", "Virtual Patient"),
            age=data.get("age", 52),
            biological_sex=data.get("biological_sex", "male"),
            height_cm=data.get("height_cm", 175.0),
            years_since_diagnosis=data.get("years_since_diagnosis", 3),
            family_history_diabetes=data.get("family_history_diabetes", True),
            has_hypertension=data.get("has_hypertension", True),
            has_dyslipidemia=data.get("has_dyslipidemia", False),
            has_cardiovascular_disease=data.get("has_cardiovascular_disease", False),
            genetic_risk_factor=data.get("genetic_risk_factor", 0.6)
        )
        if "created_at" in data:
            profile.created_at = datetime.fromisoformat(data["created_at"])
        return profile


@dataclass
class VirtualPatient:
    """
    Complete Virtual Patient representation for the DiabeTwin.
    
    This is the central entity that combines:
    - Static profile (demographics, history)
    - Current lifestyle factors (modifiable behaviors)
    - Current health metrics (biomarkers)
    
    The Virtual Patient is a "living" entity that evolves over time.
    """
    
    profile: PatientProfile
    lifestyle: LifestyleFactors
    
    # Current health metrics (these are updated by the health state model)
    weight_kg: float = 88.0
    hba1c_percent: float = 7.2          # Glycated hemoglobin (target <7%)
    fasting_glucose_mgdl: float = 145.0  # Fasting blood glucose
    systolic_bp: int = 138              # Systolic blood pressure
    diastolic_bp: int = 88              # Diastolic blood pressure
    ldl_cholesterol_mgdl: float = 120.0 # LDL cholesterol
    hdl_cholesterol_mgdl: float = 42.0  # HDL cholesterol
    triglycerides_mgdl: float = 180.0   # Triglycerides
    
    # Calculated metrics
    @property
    def bmi(self) -> float:
        """Body Mass Index calculation"""
        height_m = self.profile.height_cm / 100
        return round(self.weight_kg / (height_m ** 2), 1)
    
    @property
    def diabetes_control_status(self) -> str:
        """Interpret HbA1c level"""
        if self.hba1c_percent < 5.7:
            return "Normal"
        elif self.hba1c_percent < 6.5:
            return "Prediabetes Range"
        elif self.hba1c_percent < 7.0:
            return "Well Controlled"
        elif self.hba1c_percent < 8.0:
            return "Moderately Controlled"
        elif self.hba1c_percent < 9.0:
            return "Poorly Controlled"
        else:
            return "Very Poorly Controlled"
    
    @property
    def blood_pressure_category(self) -> str:
        """Categorize blood pressure"""
        if self.systolic_bp < 120 and self.diastolic_bp < 80:
            return "Normal"
        elif self.systolic_bp < 130 and self.diastolic_bp < 80:
            return "Elevated"
        elif self.systolic_bp < 140 or self.diastolic_bp < 90:
            return "High Blood Pressure Stage 1"
        elif self.systolic_bp < 180 or self.diastolic_bp < 120:
            return "High Blood Pressure Stage 2"
        else:
            return "Hypertensive Crisis"
    
    @property
    def weight_category(self) -> str:
        """Categorize BMI"""
        bmi = self.bmi
        if bmi < 18.5:
            return "Underweight"
        elif bmi < 25:
            return "Normal Weight"
        elif bmi < 30:
            return "Overweight"
        elif bmi < 35:
            return "Obese Class I"
        elif bmi < 40:
            return "Obese Class II"
        else:
            return "Obese Class III"
    
    def get_risk_category(self) -> DiabetesRiskCategory:
        """
        Calculate overall diabetes complication risk category.
        Based on multiple factors including HbA1c, BP, lipids, and lifestyle.
        """
        risk_score = 0
        
        # HbA1c contribution (major factor)
        if self.hba1c_percent >= 9.0:
            risk_score += 4
        elif self.hba1c_percent >= 8.0:
            risk_score += 3
        elif self.hba1c_percent >= 7.0:
            risk_score += 2
        elif self.hba1c_percent >= 6.5:
            risk_score += 1
        
        # Blood pressure contribution
        if self.systolic_bp >= 160:
            risk_score += 2
        elif self.systolic_bp >= 140:
            risk_score += 1
        
        # BMI contribution
        if self.bmi >= 35:
            risk_score += 2
        elif self.bmi >= 30:
            risk_score += 1
        
        # Lifestyle contribution (inverse - good lifestyle reduces risk)
        lifestyle_score = self.lifestyle.get_overall_lifestyle_score()
        if lifestyle_score < 0.3:
            risk_score += 2
        elif lifestyle_score < 0.5:
            risk_score += 1
        elif lifestyle_score > 0.7:
            risk_score -= 1
        
        # Duration of diabetes
        if self.profile.years_since_diagnosis > 10:
            risk_score += 2
        elif self.profile.years_since_diagnosis > 5:
            risk_score += 1
        
        # Map to category
        if risk_score <= 2:
            return DiabetesRiskCategory.LOW
        elif risk_score <= 5:
            return DiabetesRiskCategory.MODERATE
        elif risk_score <= 8:
            return DiabetesRiskCategory.HIGH
        else:
            return DiabetesRiskCategory.VERY_HIGH
    
    def get_summary_metrics(self) -> Dict[str, Any]:
        """Get key metrics summary for display"""
        return {
            "hba1c": {
                "value": self.hba1c_percent,
                "unit": "%",
                "status": self.diabetes_control_status,
                "target": "< 7.0%"
            },
            "fasting_glucose": {
                "value": self.fasting_glucose_mgdl,
                "unit": "mg/dL",
                "status": "High" if self.fasting_glucose_mgdl > 130 else "Normal",
                "target": "80-130 mg/dL"
            },
            "weight": {
                "value": self.weight_kg,
                "unit": "kg",
                "bmi": self.bmi,
                "category": self.weight_category
            },
            "blood_pressure": {
                "systolic": self.systolic_bp,
                "diastolic": self.diastolic_bp,
                "category": self.blood_pressure_category,
                "target": "< 130/80"
            },
            "lifestyle_score": {
                "value": round(self.lifestyle.get_overall_lifestyle_score() * 100),
                "unit": "%",
                "interpretation": self._interpret_lifestyle_score()
            },
            "risk_category": self.get_risk_category().value
        }
    
    def _interpret_lifestyle_score(self) -> str:
        """Interpret lifestyle score for display"""
        score = self.lifestyle.get_overall_lifestyle_score()
        if score >= 0.8:
            return "Excellent - Keep it up!"
        elif score >= 0.6:
            return "Good - Room for improvement"
        elif score >= 0.4:
            return "Fair - Consider lifestyle changes"
        else:
            return "Needs attention - Significant changes recommended"
    
    def to_dict(self) -> Dict[str, Any]:
        """Complete serialization of virtual patient"""
        return {
            "profile": self.profile.to_dict(),
            "lifestyle": self.lifestyle.to_dict(),
            "health_metrics": {
                "weight_kg": self.weight_kg,
                "hba1c_percent": self.hba1c_percent,
                "fasting_glucose_mgdl": self.fasting_glucose_mgdl,
                "systolic_bp": self.systolic_bp,
                "diastolic_bp": self.diastolic_bp,
                "ldl_cholesterol_mgdl": self.ldl_cholesterol_mgdl,
                "hdl_cholesterol_mgdl": self.hdl_cholesterol_mgdl,
                "triglycerides_mgdl": self.triglycerides_mgdl
            },
            "computed": {
                "bmi": self.bmi,
                "diabetes_control_status": self.diabetes_control_status,
                "blood_pressure_category": self.blood_pressure_category,
                "weight_category": self.weight_category,
                "risk_category": self.get_risk_category().value
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VirtualPatient':
        """Deserialize virtual patient"""
        profile = PatientProfile.from_dict(data.get("profile", {}))
        lifestyle = LifestyleFactors.from_dict(data.get("lifestyle", {}))
        metrics = data.get("health_metrics", {})
        
        return cls(
            profile=profile,
            lifestyle=lifestyle,
            weight_kg=metrics.get("weight_kg", 88.0),
            hba1c_percent=metrics.get("hba1c_percent", 7.2),
            fasting_glucose_mgdl=metrics.get("fasting_glucose_mgdl", 145.0),
            systolic_bp=metrics.get("systolic_bp", 138),
            diastolic_bp=metrics.get("diastolic_bp", 88),
            ldl_cholesterol_mgdl=metrics.get("ldl_cholesterol_mgdl", 120.0),
            hdl_cholesterol_mgdl=metrics.get("hdl_cholesterol_mgdl", 42.0),
            triglycerides_mgdl=metrics.get("triglycerides_mgdl", 180.0)
        )
    
    def copy(self) -> 'VirtualPatient':
        """Create a deep copy of the virtual patient"""
        return VirtualPatient.from_dict(self.to_dict())


def create_synthetic_patient(
    name: str = "Alex Morgan",
    scenario: str = "moderate"
) -> VirtualPatient:
    """
    Factory function to create synthetic patients for different scenarios.
    
    Scenarios:
    - "mild": Early-stage, well-controlled diabetes
    - "moderate": Typical T2D patient with room for improvement  
    - "severe": Poorly controlled with multiple risk factors
    - "improving": Patient who is making positive changes
    """
    
    if scenario == "mild":
        return VirtualPatient(
            profile=PatientProfile(
                patient_id=f"SYN-{random.randint(1000, 9999)}",
                name=name,
                age=45,
                years_since_diagnosis=1,
                family_history_diabetes=False,
                has_hypertension=False,
                genetic_risk_factor=0.4
            ),
            lifestyle=LifestyleFactors(
                exercise_minutes_per_week=120,
                activity_level=ActivityLevel.MODERATELY_ACTIVE,
                diet_quality=DietQuality.GOOD,
                daily_carb_intake_grams=200,
                sugary_drinks_per_week=2,
                average_sleep_hours=7.5,
                stress_score=0.3,
                medication_adherence=0.9
            ),
            weight_kg=78.0,
            hba1c_percent=6.4,
            fasting_glucose_mgdl=118.0,
            systolic_bp=125,
            diastolic_bp=80
        )
    
    elif scenario == "severe":
        return VirtualPatient(
            profile=PatientProfile(
                patient_id=f"SYN-{random.randint(1000, 9999)}",
                name=name,
                age=62,
                years_since_diagnosis=12,
                family_history_diabetes=True,
                has_hypertension=True,
                has_dyslipidemia=True,
                has_cardiovascular_disease=True,
                genetic_risk_factor=0.8
            ),
            lifestyle=LifestyleFactors(
                exercise_minutes_per_week=20,
                activity_level=ActivityLevel.SEDENTARY,
                diet_quality=DietQuality.POOR,
                daily_carb_intake_grams=350,
                sugary_drinks_per_week=10,
                average_sleep_hours=5.5,
                stress_score=0.8,
                medication_adherence=0.5,
                smoking_status=True
            ),
            weight_kg=105.0,
            hba1c_percent=9.2,
            fasting_glucose_mgdl=195.0,
            systolic_bp=158,
            diastolic_bp=98,
            ldl_cholesterol_mgdl=160.0,
            hdl_cholesterol_mgdl=35.0,
            triglycerides_mgdl=250.0
        )
    
    elif scenario == "improving":
        return VirtualPatient(
            profile=PatientProfile(
                patient_id=f"SYN-{random.randint(1000, 9999)}",
                name=name,
                age=48,
                years_since_diagnosis=4,
                family_history_diabetes=True,
                has_hypertension=True,
                genetic_risk_factor=0.55
            ),
            lifestyle=LifestyleFactors(
                exercise_minutes_per_week=90,
                activity_level=ActivityLevel.MODERATELY_ACTIVE,
                diet_quality=DietQuality.GOOD,
                daily_carb_intake_grams=220,
                sugary_drinks_per_week=3,
                average_sleep_hours=7.0,
                stress_score=0.4,
                medication_adherence=0.85
            ),
            weight_kg=85.0,
            hba1c_percent=7.0,
            fasting_glucose_mgdl=135.0,
            systolic_bp=132,
            diastolic_bp=84
        )
    
    else:  # moderate (default)
        return VirtualPatient(
            profile=PatientProfile(
                patient_id=f"SYN-{random.randint(1000, 9999)}",
                name=name,
                age=52,
                years_since_diagnosis=3,
                family_history_diabetes=True,
                has_hypertension=True,
                genetic_risk_factor=0.6
            ),
            lifestyle=LifestyleFactors(
                exercise_minutes_per_week=60,
                activity_level=ActivityLevel.LIGHTLY_ACTIVE,
                diet_quality=DietQuality.FAIR,
                daily_carb_intake_grams=260,
                sugary_drinks_per_week=5,
                average_sleep_hours=6.5,
                stress_score=0.5,
                medication_adherence=0.7
            ),
            weight_kg=88.0,
            hba1c_percent=7.2,
            fasting_glucose_mgdl=145.0,
            systolic_bp=138,
            diastolic_bp=88
        )
