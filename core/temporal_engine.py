"""
Temporal Evolution Engine Module

This module handles the simulation of health trajectories over time.
It orchestrates the health state model to produce:
- Baseline trajectories (current behavior continued)
- Intervention trajectories (what-if scenarios)
- Parallel future comparisons

KEY FEATURE: This engine enables counterfactual analysis -
"What would have happened if..."
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import copy

from .health_state import HealthState, HealthStateModel
from .virtual_patient import VirtualPatient, LifestyleFactors


class ScenarioType(Enum):
    """Types of simulation scenarios"""
    BASELINE = "baseline"           # Continue current behavior
    IMPROVED_DIET = "improved_diet"
    INCREASED_EXERCISE = "increased_exercise"
    BETTER_MEDICATION = "better_medication"
    STRESS_REDUCTION = "stress_reduction"
    COMPREHENSIVE = "comprehensive"  # All improvements combined
    DETERIORATION = "deterioration"  # What if things get worse
    CUSTOM = "custom"


@dataclass
class TrajectoryPoint:
    """A single point in a health trajectory"""
    time_step: int  # Month number
    date: datetime
    health_state: HealthState
    explanations: Dict[str, str]
    lifestyle_snapshot: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "time_step": self.time_step,
            "date": self.date.isoformat(),
            "health_state": self.health_state.to_dict(),
            "explanations": self.explanations,
            "lifestyle_snapshot": self.lifestyle_snapshot
        }


@dataclass 
class Trajectory:
    """
    A complete health trajectory over time.
    
    Contains multiple trajectory points and metadata about the scenario.
    """
    scenario_type: ScenarioType
    scenario_name: str
    description: str
    points: List[TrajectoryPoint] = field(default_factory=list)
    
    # Summary statistics
    start_hba1c: float = 0.0
    end_hba1c: float = 0.0
    hba1c_change: float = 0.0
    
    start_weight: float = 0.0
    end_weight: float = 0.0
    weight_change: float = 0.0
    
    risk_trend: str = ""  # "improving", "stable", "worsening"
    
    def compute_summary(self) -> None:
        """Compute summary statistics for the trajectory"""
        if not self.points:
            return
        
        first = self.points[0]
        last = self.points[-1]
        
        self.start_hba1c = first.health_state.hba1c_percent
        self.end_hba1c = last.health_state.hba1c_percent
        self.hba1c_change = self.end_hba1c - self.start_hba1c
        
        self.start_weight = first.health_state.weight_kg
        self.end_weight = last.health_state.weight_kg
        self.weight_change = self.end_weight - self.start_weight
        
        # Determine risk trend
        start_risk = first.health_state.cardiovascular_risk_score
        end_risk = last.health_state.cardiovascular_risk_score
        
        if end_risk < start_risk - 0.05:
            self.risk_trend = "improving"
        elif end_risk > start_risk + 0.05:
            self.risk_trend = "worsening"
        else:
            self.risk_trend = "stable"
    
    def get_metric_series(self, metric: str) -> List[Tuple[int, float]]:
        """Extract time series for a specific metric"""
        series = []
        for point in self.points:
            state = point.health_state
            if hasattr(state, metric):
                value = getattr(state, metric)
                series.append((point.time_step, value))
        return series
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario_type": self.scenario_type.value,
            "scenario_name": self.scenario_name,
            "description": self.description,
            "points": [p.to_dict() for p in self.points],
            "summary": {
                "start_hba1c": self.start_hba1c,
                "end_hba1c": self.end_hba1c,
                "hba1c_change": self.hba1c_change,
                "start_weight": self.start_weight,
                "end_weight": self.end_weight,
                "weight_change": self.weight_change,
                "risk_trend": self.risk_trend
            }
        }


class TemporalEvolutionEngine:
    """
    The engine that runs health simulations over time.
    
    This is the heart of the "what-if" capability:
    - Simulate baseline continuation
    - Simulate intervention scenarios
    - Compare parallel futures
    - Support counterfactual analysis
    """
    
    def __init__(self, variability: float = 0.1):
        """
        Initialize the evolution engine.
        
        Args:
            variability: Amount of random variation in simulations
        """
        self.health_model = HealthStateModel(variability=variability)
        self.variability = variability
    
    def simulate_trajectory(
        self,
        patient: VirtualPatient,
        months: int = 12,
        scenario_type: ScenarioType = ScenarioType.BASELINE,
        lifestyle_overrides: Optional[Dict[str, Any]] = None,
        start_date: Optional[datetime] = None
    ) -> Trajectory:
        """
        Simulate a health trajectory for the given scenario.
        
        Args:
            patient: The virtual patient to simulate
            months: Number of months to simulate
            scenario_type: Type of scenario to simulate
            lifestyle_overrides: Optional custom lifestyle changes
            start_date: Starting date for the simulation
            
        Returns:
            Complete trajectory with all time points
        """
        
        if start_date is None:
            start_date = datetime.now()
        
        # Create working copy of patient
        working_patient = patient.copy()
        
        # Apply scenario-specific lifestyle modifications
        scenario_lifestyle = self._get_scenario_lifestyle(
            working_patient.lifestyle,
            scenario_type,
            lifestyle_overrides
        )
        
        # Get scenario description
        scenario_name, description = self._get_scenario_description(scenario_type)
        
        # Initialize trajectory
        trajectory = Trajectory(
            scenario_type=scenario_type,
            scenario_name=scenario_name,
            description=description
        )
        
        # Create initial health state from patient
        current_state = HealthState(
            hba1c_percent=working_patient.hba1c_percent,
            fasting_glucose_mgdl=working_patient.fasting_glucose_mgdl,
            weight_kg=working_patient.weight_kg,
            systolic_bp=working_patient.systolic_bp,
            diastolic_bp=working_patient.diastolic_bp,
            ldl_cholesterol_mgdl=working_patient.ldl_cholesterol_mgdl,
            hdl_cholesterol_mgdl=working_patient.hdl_cholesterol_mgdl,
            triglycerides_mgdl=working_patient.triglycerides_mgdl,
            time_step=0
        )
        current_state.compute_derived_scores(scenario_lifestyle.get_overall_lifestyle_score())
        
        # Add initial point
        initial_point = TrajectoryPoint(
            time_step=0,
            date=start_date,
            health_state=current_state.copy(),
            explanations={"initial": "Starting point - current health status"},
            lifestyle_snapshot=scenario_lifestyle.to_dict()
        )
        trajectory.points.append(initial_point)
        
        # Simulate each month
        for month in range(1, months + 1):
            # Compute next state
            next_state, explanations = self.health_model.compute_next_state(
                current_state=current_state,
                lifestyle_score=scenario_lifestyle.get_overall_lifestyle_score(),
                activity_score=scenario_lifestyle.get_activity_score(),
                diet_score=scenario_lifestyle.get_diet_score(),
                stress_score=scenario_lifestyle.stress_score,
                medication_adherence=scenario_lifestyle.medication_adherence,
                genetic_risk=working_patient.profile.genetic_risk_factor,
                time_delta=1
            )
            
            # Create trajectory point
            point = TrajectoryPoint(
                time_step=month,
                date=start_date + timedelta(days=30 * month),
                health_state=next_state.copy(),
                explanations=explanations,
                lifestyle_snapshot=scenario_lifestyle.to_dict()
            )
            trajectory.points.append(point)
            
            current_state = next_state
        
        # Compute summary statistics
        trajectory.compute_summary()
        
        return trajectory
    
    def simulate_parallel_futures(
        self,
        patient: VirtualPatient,
        months: int = 12,
        scenarios: Optional[List[ScenarioType]] = None
    ) -> Dict[str, Trajectory]:
        """
        Simulate multiple scenarios in parallel for comparison.
        
        Args:
            patient: The virtual patient
            months: Simulation duration
            scenarios: List of scenarios to simulate
            
        Returns:
            Dictionary mapping scenario names to trajectories
        """
        
        if scenarios is None:
            scenarios = [
                ScenarioType.BASELINE,
                ScenarioType.IMPROVED_DIET,
                ScenarioType.INCREASED_EXERCISE,
                ScenarioType.COMPREHENSIVE
            ]
        
        results = {}
        start_date = datetime.now()
        
        for scenario in scenarios:
            trajectory = self.simulate_trajectory(
                patient=patient,
                months=months,
                scenario_type=scenario,
                start_date=start_date
            )
            results[scenario.value] = trajectory
        
        return results
    
    def simulate_counterfactual(
        self,
        patient: VirtualPatient,
        historical_months: int,
        alternative_lifestyle: LifestyleFactors,
        future_months: int = 6
    ) -> Tuple[Trajectory, Trajectory]:
        """
        Simulate a counterfactual: "What if lifestyle had been different?"
        
        This creates two trajectories:
        1. What actually happened (baseline)
        2. What would have happened (counterfactual)
        
        Args:
            patient: Current patient state
            historical_months: How far back to start the counterfactual
            alternative_lifestyle: The lifestyle that "could have been"
            future_months: Additional months to project forward
            
        Returns:
            Tuple of (actual_trajectory, counterfactual_trajectory)
        """
        
        total_months = historical_months + future_months
        
        # Simulate what actually happened (baseline)
        actual = self.simulate_trajectory(
            patient=patient,
            months=total_months,
            scenario_type=ScenarioType.BASELINE
        )
        
        # Simulate counterfactual with alternative lifestyle
        counterfactual = self.simulate_trajectory(
            patient=patient,
            months=total_months,
            scenario_type=ScenarioType.CUSTOM,
            lifestyle_overrides=alternative_lifestyle.to_dict()
        )
        counterfactual.scenario_name = "Counterfactual"
        counterfactual.description = f"What if you had maintained better habits for {historical_months} months?"
        
        return actual, counterfactual
    
    def _get_scenario_lifestyle(
        self,
        base_lifestyle: LifestyleFactors,
        scenario_type: ScenarioType,
        overrides: Optional[Dict[str, Any]] = None
    ) -> LifestyleFactors:
        """
        Create lifestyle factors for a specific scenario.
        """
        
        # Start with a copy of base lifestyle
        lifestyle_dict = base_lifestyle.to_dict()
        
        if scenario_type == ScenarioType.BASELINE:
            # No changes
            pass
        
        elif scenario_type == ScenarioType.IMPROVED_DIET:
            lifestyle_dict["diet_quality"] = "good"
            lifestyle_dict["daily_carb_intake_grams"] = 180
            lifestyle_dict["daily_fiber_intake_grams"] = 30
            lifestyle_dict["sugary_drinks_per_week"] = 1
        
        elif scenario_type == ScenarioType.INCREASED_EXERCISE:
            lifestyle_dict["exercise_minutes_per_week"] = 180
            lifestyle_dict["activity_level"] = "active"
        
        elif scenario_type == ScenarioType.BETTER_MEDICATION:
            lifestyle_dict["medication_adherence"] = 0.95
        
        elif scenario_type == ScenarioType.STRESS_REDUCTION:
            lifestyle_dict["stress_level"] = "low"
            lifestyle_dict["stress_score"] = 0.25
            lifestyle_dict["average_sleep_hours"] = 7.5
            lifestyle_dict["sleep_quality_score"] = 0.8
        
        elif scenario_type == ScenarioType.COMPREHENSIVE:
            lifestyle_dict["diet_quality"] = "good"
            lifestyle_dict["daily_carb_intake_grams"] = 180
            lifestyle_dict["sugary_drinks_per_week"] = 1
            lifestyle_dict["exercise_minutes_per_week"] = 150
            lifestyle_dict["activity_level"] = "moderately_active"
            lifestyle_dict["medication_adherence"] = 0.9
            lifestyle_dict["stress_score"] = 0.3
            lifestyle_dict["average_sleep_hours"] = 7.5
        
        elif scenario_type == ScenarioType.DETERIORATION:
            lifestyle_dict["diet_quality"] = "poor"
            lifestyle_dict["daily_carb_intake_grams"] = 350
            lifestyle_dict["sugary_drinks_per_week"] = 10
            lifestyle_dict["exercise_minutes_per_week"] = 15
            lifestyle_dict["activity_level"] = "sedentary"
            lifestyle_dict["medication_adherence"] = 0.4
            lifestyle_dict["stress_score"] = 0.8
        
        elif scenario_type == ScenarioType.CUSTOM and overrides:
            lifestyle_dict.update(overrides)
        
        return LifestyleFactors.from_dict(lifestyle_dict)
    
    def _get_scenario_description(
        self,
        scenario_type: ScenarioType
    ) -> Tuple[str, str]:
        """Get human-readable name and description for a scenario."""
        
        descriptions = {
            ScenarioType.BASELINE: (
                "Current Path",
                "Continue with current lifestyle and behaviors unchanged"
            ),
            ScenarioType.IMPROVED_DIET: (
                "Better Nutrition",
                "Switch to a balanced, low-glycemic diet with more fiber and fewer processed foods"
            ),
            ScenarioType.INCREASED_EXERCISE: (
                "Active Lifestyle",
                "Increase physical activity to 150+ minutes per week of moderate exercise"
            ),
            ScenarioType.BETTER_MEDICATION: (
                "Consistent Medication",
                "Take medications as prescribed with 95%+ adherence"
            ),
            ScenarioType.STRESS_REDUCTION: (
                "Stress Management",
                "Implement stress reduction techniques and improve sleep quality"
            ),
            ScenarioType.COMPREHENSIVE: (
                "Full Lifestyle Change",
                "Combine improved diet, increased exercise, better medication adherence, and stress management"
            ),
            ScenarioType.DETERIORATION: (
                "Warning: Decline",
                "What happens if healthy habits are abandoned"
            ),
            ScenarioType.CUSTOM: (
                "Custom Scenario",
                "User-defined lifestyle modifications"
            )
        }
        
        return descriptions.get(scenario_type, ("Unknown", "No description available"))
    
    def compare_trajectories(
        self,
        trajectories: Dict[str, Trajectory]
    ) -> Dict[str, Any]:
        """
        Compare multiple trajectories and generate comparison insights.
        
        Returns structured comparison data for visualization and AI narration.
        """
        
        comparison = {
            "trajectories": {},
            "best_outcome": None,
            "worst_outcome": None,
            "key_differences": []
        }
        
        best_hba1c = float('inf')
        worst_hba1c = float('-inf')
        
        for name, traj in trajectories.items():
            summary = {
                "scenario_name": traj.scenario_name,
                "final_hba1c": traj.end_hba1c,
                "hba1c_change": traj.hba1c_change,
                "final_weight": traj.end_weight,
                "weight_change": traj.weight_change,
                "risk_trend": traj.risk_trend
            }
            comparison["trajectories"][name] = summary
            
            if traj.end_hba1c < best_hba1c:
                best_hba1c = traj.end_hba1c
                comparison["best_outcome"] = name
            
            if traj.end_hba1c > worst_hba1c:
                worst_hba1c = traj.end_hba1c
                comparison["worst_outcome"] = name
        
        # Calculate key differences
        if "baseline" in trajectories and len(trajectories) > 1:
            baseline = trajectories["baseline"]
            for name, traj in trajectories.items():
                if name != "baseline":
                    hba1c_diff = baseline.end_hba1c - traj.end_hba1c
                    weight_diff = baseline.end_weight - traj.end_weight
                    comparison["key_differences"].append({
                        "scenario": name,
                        "hba1c_improvement": round(hba1c_diff, 2),
                        "weight_improvement": round(weight_diff, 1)
                    })
        
        return comparison
    
    def get_trajectory_narrative_data(
        self,
        trajectory: Trajectory
    ) -> Dict[str, Any]:
        """
        Extract key data points for AI narrative generation.
        """
        
        if not trajectory.points:
            return {}
        
        first = trajectory.points[0]
        last = trajectory.points[-1]
        
        # Find significant changes
        significant_changes = []
        for point in trajectory.points[1:]:
            for metric, explanation in point.explanations.items():
                if "improving" in explanation.lower() or "worsening" in explanation.lower():
                    significant_changes.append({
                        "month": point.time_step,
                        "metric": metric,
                        "explanation": explanation
                    })
        
        return {
            "scenario": trajectory.scenario_name,
            "description": trajectory.description,
            "duration_months": len(trajectory.points) - 1,
            "initial_state": {
                "hba1c": first.health_state.hba1c_percent,
                "weight": first.health_state.weight_kg,
                "blood_pressure": f"{first.health_state.systolic_bp}/{first.health_state.diastolic_bp}",
                "health_score": first.health_state.overall_health_score
            },
            "final_state": {
                "hba1c": last.health_state.hba1c_percent,
                "weight": last.health_state.weight_kg,
                "blood_pressure": f"{last.health_state.systolic_bp}/{last.health_state.diastolic_bp}",
                "health_score": last.health_state.overall_health_score
            },
            "changes": {
                "hba1c_change": round(trajectory.hba1c_change, 2),
                "weight_change": round(trajectory.weight_change, 1),
                "risk_trend": trajectory.risk_trend
            },
            "significant_events": significant_changes[:5],  # Top 5
            "lifestyle_maintained": trajectory.points[-1].lifestyle_snapshot if trajectory.points else {}
        }
