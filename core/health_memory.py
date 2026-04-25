"""
Health Memory Module

This module implements the novel "Health Memory" feature - a temporal store
that maintains complete history of the patient's health journey.

KEY INNOVATION:
The Health Memory enables:
1. Counterfactual analysis ("What if I had...")
2. Trend detection over arbitrary time windows
3. Pattern recognition in lifestyle-outcome relationships
4. Personalized insights based on individual history

This transforms the digital twin from a snapshot viewer into a
longitudinal health companion that truly "knows" the patient.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json


class MemoryEventType(Enum):
    """Types of events stored in health memory"""
    STATE_SNAPSHOT = "state_snapshot"      # Regular health check
    LIFESTYLE_CHANGE = "lifestyle_change"   # Patient changed behavior
    INTERVENTION_START = "intervention_start"  # New treatment/program
    MILESTONE = "milestone"                 # Achievement or concern
    PREDICTION_MADE = "prediction_made"     # System made a prediction
    PREDICTION_OUTCOME = "prediction_outcome"  # How prediction turned out


@dataclass
class HealthSnapshot:
    """
    A complete snapshot of health state at a point in time.
    This is the atomic unit of health memory.
    """
    
    # Temporal information
    timestamp: datetime
    time_step: int  # Simulation step (months from start)
    
    # Health metrics
    hba1c_percent: float
    fasting_glucose_mgdl: float
    weight_kg: float
    systolic_bp: int
    diastolic_bp: int
    ldl_cholesterol_mgdl: float
    hdl_cholesterol_mgdl: float
    triglycerides_mgdl: float
    
    # Computed scores at this time
    cardiovascular_risk_score: float
    diabetes_progression_score: float
    overall_health_score: float
    
    # Lifestyle at this time
    lifestyle_score: float
    activity_level: str
    diet_quality: str
    medication_adherence: float
    stress_level: str
    
    # Context and notes
    event_type: MemoryEventType = MemoryEventType.STATE_SNAPSHOT
    notes: str = ""
    explanations: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "time_step": self.time_step,
            "metrics": {
                "hba1c_percent": self.hba1c_percent,
                "fasting_glucose_mgdl": self.fasting_glucose_mgdl,
                "weight_kg": self.weight_kg,
                "systolic_bp": self.systolic_bp,
                "diastolic_bp": self.diastolic_bp,
                "ldl_cholesterol_mgdl": self.ldl_cholesterol_mgdl,
                "hdl_cholesterol_mgdl": self.hdl_cholesterol_mgdl,
                "triglycerides_mgdl": self.triglycerides_mgdl
            },
            "scores": {
                "cardiovascular_risk_score": self.cardiovascular_risk_score,
                "diabetes_progression_score": self.diabetes_progression_score,
                "overall_health_score": self.overall_health_score
            },
            "lifestyle": {
                "lifestyle_score": self.lifestyle_score,
                "activity_level": self.activity_level,
                "diet_quality": self.diet_quality,
                "medication_adherence": self.medication_adherence,
                "stress_level": self.stress_level
            },
            "context": {
                "event_type": self.event_type.value,
                "notes": self.notes,
                "explanations": self.explanations
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HealthSnapshot':
        metrics = data.get("metrics", {})
        scores = data.get("scores", {})
        lifestyle = data.get("lifestyle", {})
        context = data.get("context", {})
        
        return cls(
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            time_step=data.get("time_step", 0),
            hba1c_percent=metrics.get("hba1c_percent", 7.0),
            fasting_glucose_mgdl=metrics.get("fasting_glucose_mgdl", 140.0),
            weight_kg=metrics.get("weight_kg", 85.0),
            systolic_bp=metrics.get("systolic_bp", 135),
            diastolic_bp=metrics.get("diastolic_bp", 85),
            ldl_cholesterol_mgdl=metrics.get("ldl_cholesterol_mgdl", 120.0),
            hdl_cholesterol_mgdl=metrics.get("hdl_cholesterol_mgdl", 45.0),
            triglycerides_mgdl=metrics.get("triglycerides_mgdl", 170.0),
            cardiovascular_risk_score=scores.get("cardiovascular_risk_score", 0.3),
            diabetes_progression_score=scores.get("diabetes_progression_score", 0.5),
            overall_health_score=scores.get("overall_health_score", 60.0),
            lifestyle_score=lifestyle.get("lifestyle_score", 0.5),
            activity_level=lifestyle.get("activity_level", "lightly_active"),
            diet_quality=lifestyle.get("diet_quality", "fair"),
            medication_adherence=lifestyle.get("medication_adherence", 0.7),
            stress_level=lifestyle.get("stress_level", "moderate"),
            event_type=MemoryEventType(context.get("event_type", "state_snapshot")),
            notes=context.get("notes", ""),
            explanations=context.get("explanations", {})
        )


@dataclass
class HealthTrend:
    """Represents a detected trend in health metrics over time"""
    metric_name: str
    direction: str  # "improving", "stable", "worsening"
    magnitude: float  # Rate of change per month
    confidence: float  # 0-1, how confident we are in this trend
    start_value: float
    end_value: float
    period_months: int
    contributing_factors: List[str] = field(default_factory=list)
    
    def to_narrative(self) -> str:
        """Generate human-readable description of the trend"""
        if self.direction == "improving":
            verb = "improved"
            emoji = "📈"
        elif self.direction == "worsening":
            verb = "worsened"
            emoji = "📉"
        else:
            verb = "remained stable"
            emoji = "➡️"
        
        factors_str = ""
        if self.contributing_factors:
            factors_str = f" This appears related to: {', '.join(self.contributing_factors)}."
        
        return (
            f"{emoji} Your {self.metric_name} has {verb} over the past {self.period_months} months, "
            f"going from {self.start_value:.1f} to {self.end_value:.1f}.{factors_str}"
        )


class HealthMemory:
    """
    The Health Memory store - a complete temporal record of the patient's
    health journey that enables intelligent retrospection and counterfactual analysis.
    
    CAPABILITIES:
    - Store and retrieve health snapshots
    - Detect trends over time
    - Support counterfactual queries
    - Generate historical summaries
    - Identify patterns and correlations
    """
    
    def __init__(self, patient_id: str = ""):
        """Initialize the health memory for a patient"""
        self.patient_id = patient_id
        self.snapshots: List[HealthSnapshot] = []
        self.milestones: List[Dict[str, Any]] = []
        self.predictions: List[Dict[str, Any]] = []
        self.created_at = datetime.now()
    
    def add_snapshot(self, snapshot: HealthSnapshot) -> None:
        """Add a new health snapshot to memory"""
        self.snapshots.append(snapshot)
        self.snapshots.sort(key=lambda s: s.timestamp)
        
        # Check for automatic milestone detection
        self._detect_milestones(snapshot)
    
    def add_snapshot_from_state(
        self,
        health_state: 'HealthState',  # Forward reference
        lifestyle: 'LifestyleFactors',
        time_step: int,
        timestamp: Optional[datetime] = None,
        notes: str = "",
        explanations: Optional[Dict[str, str]] = None
    ) -> HealthSnapshot:
        """Create and add a snapshot from current state"""
        
        if timestamp is None:
            timestamp = datetime.now()
        
        snapshot = HealthSnapshot(
            timestamp=timestamp,
            time_step=time_step,
            hba1c_percent=health_state.hba1c_percent,
            fasting_glucose_mgdl=health_state.fasting_glucose_mgdl,
            weight_kg=health_state.weight_kg,
            systolic_bp=health_state.systolic_bp,
            diastolic_bp=health_state.diastolic_bp,
            ldl_cholesterol_mgdl=health_state.ldl_cholesterol_mgdl,
            hdl_cholesterol_mgdl=health_state.hdl_cholesterol_mgdl,
            triglycerides_mgdl=health_state.triglycerides_mgdl,
            cardiovascular_risk_score=health_state.cardiovascular_risk_score,
            diabetes_progression_score=health_state.diabetes_progression_score,
            overall_health_score=health_state.overall_health_score,
            lifestyle_score=lifestyle.get_overall_lifestyle_score(),
            activity_level=lifestyle.activity_level.value,
            diet_quality=lifestyle.diet_quality.value,
            medication_adherence=lifestyle.medication_adherence,
            stress_level=lifestyle.stress_level.value,
            notes=notes,
            explanations=explanations or {}
        )
        
        self.add_snapshot(snapshot)
        return snapshot
    
    def get_snapshot_at(self, time_step: int) -> Optional[HealthSnapshot]:
        """Retrieve snapshot at a specific time step"""
        for snapshot in self.snapshots:
            if snapshot.time_step == time_step:
                return snapshot
        return None
    
    def get_latest_snapshot(self) -> Optional[HealthSnapshot]:
        """Get the most recent snapshot"""
        if self.snapshots:
            return self.snapshots[-1]
        return None
    
    def get_snapshots_in_range(
        self,
        start_step: int,
        end_step: int
    ) -> List[HealthSnapshot]:
        """Get all snapshots within a time range"""
        return [
            s for s in self.snapshots 
            if start_step <= s.time_step <= end_step
        ]
    
    def detect_trends(
        self,
        metric: str,
        window_months: int = 6
    ) -> Optional[HealthTrend]:
        """
        Detect trend for a specific metric over a time window.
        
        Args:
            metric: Name of metric to analyze
            window_months: How many months to look back
            
        Returns:
            HealthTrend object if enough data, None otherwise
        """
        
        if len(self.snapshots) < 2:
            return None
        
        # Get relevant snapshots
        latest = self.snapshots[-1]
        earliest_step = max(0, latest.time_step - window_months)
        
        relevant = [s for s in self.snapshots if s.time_step >= earliest_step]
        
        if len(relevant) < 2:
            return None
        
        # Extract metric values
        values = []
        for snapshot in relevant:
            if hasattr(snapshot, metric):
                values.append((snapshot.time_step, getattr(snapshot, metric)))
        
        if len(values) < 2:
            return None
        
        first_step, first_val = values[0]
        last_step, last_val = values[-1]
        
        # Calculate change
        total_change = last_val - first_val
        period = last_step - first_step
        if period == 0:
            period = 1
        
        rate = total_change / period
        
        # Determine direction based on metric
        # For most metrics, lower is better (except HDL)
        if metric == "hdl_cholesterol_mgdl" or metric == "overall_health_score":
            # Higher is better
            if rate > 0.1:
                direction = "improving"
            elif rate < -0.1:
                direction = "worsening"
            else:
                direction = "stable"
        else:
            # Lower is better
            if rate < -0.1:
                direction = "improving"
            elif rate > 0.1:
                direction = "worsening"
            else:
                direction = "stable"
        
        # Identify contributing factors
        factors = self._identify_contributing_factors(relevant, metric, direction)
        
        return HealthTrend(
            metric_name=self._get_metric_display_name(metric),
            direction=direction,
            magnitude=abs(rate),
            confidence=min(1.0, len(relevant) / 6),  # More data = more confidence
            start_value=first_val,
            end_value=last_val,
            period_months=period,
            contributing_factors=factors
        )
    
    def get_all_trends(self, window_months: int = 6) -> List[HealthTrend]:
        """Get trends for all major metrics"""
        metrics = [
            "hba1c_percent",
            "fasting_glucose_mgdl",
            "weight_kg",
            "systolic_bp",
            "overall_health_score"
        ]
        
        trends = []
        for metric in metrics:
            trend = self.detect_trends(metric, window_months)
            if trend:
                trends.append(trend)
        
        return trends
    
    def get_counterfactual_data(
        self,
        alternative_start_step: int
    ) -> Dict[str, Any]:
        """
        Get data needed for counterfactual analysis.
        
        "What if lifestyle had been different starting from step X?"
        """
        
        # Get snapshot at the counterfactual start point
        start_snapshot = self.get_snapshot_at(alternative_start_step)
        if not start_snapshot:
            # Find closest
            for s in self.snapshots:
                if s.time_step >= alternative_start_step:
                    start_snapshot = s
                    break
        
        if not start_snapshot:
            return {}
        
        latest = self.get_latest_snapshot()
        if not latest:
            return {}
        
        # Calculate what actually happened
        actual_trajectory = self.get_snapshots_in_range(
            alternative_start_step, 
            latest.time_step
        )
        
        return {
            "start_point": start_snapshot.to_dict(),
            "current_point": latest.to_dict(),
            "actual_trajectory_length": len(actual_trajectory),
            "months_elapsed": latest.time_step - start_snapshot.time_step,
            "actual_hba1c_change": latest.hba1c_percent - start_snapshot.hba1c_percent,
            "actual_weight_change": latest.weight_kg - start_snapshot.weight_kg,
            "lifestyle_at_start": {
                "activity": start_snapshot.activity_level,
                "diet": start_snapshot.diet_quality,
                "stress": start_snapshot.stress_level
            },
            "lifestyle_now": {
                "activity": latest.activity_level,
                "diet": latest.diet_quality,
                "stress": latest.stress_level
            }
        }
    
    def generate_memory_summary(self) -> Dict[str, Any]:
        """
        Generate a comprehensive summary of the patient's health memory.
        This is the primary input for AI narrative generation.
        """
        
        if not self.snapshots:
            return {"status": "empty", "message": "No health history recorded yet."}
        
        first = self.snapshots[0]
        latest = self.snapshots[-1]
        
        # Calculate overall journey
        journey_months = latest.time_step - first.time_step
        
        # Get all trends
        trends = self.get_all_trends()
        
        # Find best and worst periods
        best_health_score = max(s.overall_health_score for s in self.snapshots)
        worst_health_score = min(s.overall_health_score for s in self.snapshots)
        best_step = next(s.time_step for s in self.snapshots if s.overall_health_score == best_health_score)
        worst_step = next(s.time_step for s in self.snapshots if s.overall_health_score == worst_health_score)
        
        # Lifestyle patterns
        avg_lifestyle_score = sum(s.lifestyle_score for s in self.snapshots) / len(self.snapshots)
        
        return {
            "patient_id": self.patient_id,
            "total_snapshots": len(self.snapshots),
            "journey_months": journey_months,
            "journey_start": first.timestamp.isoformat(),
            "journey_current": latest.timestamp.isoformat(),
            
            "initial_state": {
                "hba1c": first.hba1c_percent,
                "weight": first.weight_kg,
                "health_score": first.overall_health_score
            },
            
            "current_state": {
                "hba1c": latest.hba1c_percent,
                "weight": latest.weight_kg,
                "health_score": latest.overall_health_score
            },
            
            "overall_changes": {
                "hba1c_change": round(latest.hba1c_percent - first.hba1c_percent, 2),
                "weight_change": round(latest.weight_kg - first.weight_kg, 1),
                "health_score_change": round(latest.overall_health_score - first.overall_health_score, 1)
            },
            
            "trends": [
                {
                    "metric": t.metric_name,
                    "direction": t.direction,
                    "narrative": t.to_narrative()
                }
                for t in trends
            ],
            
            "peak_health": {
                "score": best_health_score,
                "month": best_step
            },
            
            "lowest_health": {
                "score": worst_health_score,
                "month": worst_step
            },
            
            "average_lifestyle_score": round(avg_lifestyle_score, 2),
            
            "milestones": self.milestones[-5:],  # Last 5 milestones
            
            "current_lifestyle": {
                "activity": latest.activity_level,
                "diet": latest.diet_quality,
                "medication_adherence": latest.medication_adherence,
                "stress": latest.stress_level
            }
        }
    
    def _detect_milestones(self, new_snapshot: HealthSnapshot) -> None:
        """Automatically detect and record significant milestones"""
        
        if len(self.snapshots) < 2:
            return
        
        prev = self.snapshots[-2]
        
        # HbA1c milestones
        if prev.hba1c_percent >= 7.0 and new_snapshot.hba1c_percent < 7.0:
            self.milestones.append({
                "type": "achievement",
                "metric": "hba1c",
                "message": "🎉 HbA1c dropped below 7% - well-controlled diabetes!",
                "time_step": new_snapshot.time_step,
                "timestamp": new_snapshot.timestamp.isoformat()
            })
        elif prev.hba1c_percent < 8.0 and new_snapshot.hba1c_percent >= 8.0:
            self.milestones.append({
                "type": "concern",
                "metric": "hba1c",
                "message": "⚠️ HbA1c rose above 8% - attention needed",
                "time_step": new_snapshot.time_step,
                "timestamp": new_snapshot.timestamp.isoformat()
            })
        
        # Weight milestones (5% changes)
        weight_change_pct = (new_snapshot.weight_kg - prev.weight_kg) / prev.weight_kg * 100
        if weight_change_pct <= -5:
            self.milestones.append({
                "type": "achievement",
                "metric": "weight",
                "message": "🎉 Significant weight loss achieved!",
                "time_step": new_snapshot.time_step,
                "timestamp": new_snapshot.timestamp.isoformat()
            })
        
        # Blood pressure milestones
        if prev.systolic_bp >= 140 and new_snapshot.systolic_bp < 130:
            self.milestones.append({
                "type": "achievement",
                "metric": "blood_pressure",
                "message": "🎉 Blood pressure now in target range!",
                "time_step": new_snapshot.time_step,
                "timestamp": new_snapshot.timestamp.isoformat()
            })
    
    def _identify_contributing_factors(
        self,
        snapshots: List[HealthSnapshot],
        metric: str,
        direction: str
    ) -> List[str]:
        """Identify lifestyle factors that may have contributed to a trend"""
        
        factors = []
        
        if len(snapshots) < 2:
            return factors
        
        first = snapshots[0]
        last = snapshots[-1]
        
        # Check lifestyle changes
        if last.lifestyle_score > first.lifestyle_score + 0.1:
            factors.append("improved overall lifestyle")
        elif last.lifestyle_score < first.lifestyle_score - 0.1:
            factors.append("decreased lifestyle score")
        
        if last.activity_level != first.activity_level:
            factors.append(f"activity level changed to {last.activity_level}")
        
        if last.diet_quality != first.diet_quality:
            factors.append(f"diet quality changed to {last.diet_quality}")
        
        if abs(last.medication_adherence - first.medication_adherence) > 0.1:
            if last.medication_adherence > first.medication_adherence:
                factors.append("improved medication adherence")
            else:
                factors.append("decreased medication adherence")
        
        return factors
    
    def _get_metric_display_name(self, metric: str) -> str:
        """Convert metric code to display name"""
        names = {
            "hba1c_percent": "HbA1c",
            "fasting_glucose_mgdl": "Fasting Glucose",
            "weight_kg": "Weight",
            "systolic_bp": "Systolic Blood Pressure",
            "diastolic_bp": "Diastolic Blood Pressure",
            "ldl_cholesterol_mgdl": "LDL Cholesterol",
            "hdl_cholesterol_mgdl": "HDL Cholesterol",
            "triglycerides_mgdl": "Triglycerides",
            "overall_health_score": "Overall Health Score"
        }
        return names.get(metric, metric)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize entire health memory"""
        return {
            "patient_id": self.patient_id,
            "created_at": self.created_at.isoformat(),
            "snapshots": [s.to_dict() for s in self.snapshots],
            "milestones": self.milestones,
            "predictions": self.predictions
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HealthMemory':
        """Deserialize health memory"""
        memory = cls(patient_id=data.get("patient_id", ""))
        memory.created_at = datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
        memory.snapshots = [HealthSnapshot.from_dict(s) for s in data.get("snapshots", [])]
        memory.milestones = data.get("milestones", [])
        memory.predictions = data.get("predictions", [])
        return memory
    
    def save_to_file(self, filepath: str) -> None:
        """Save health memory to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'HealthMemory':
        """Load health memory from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
