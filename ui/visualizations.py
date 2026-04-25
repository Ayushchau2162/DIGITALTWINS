"""
Visualization Module for DiabeTwin

Creates interactive charts and visualizations for the digital twin interface
using Plotly for rich, interactive graphics.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd


# Modern color palette
COLORS = {
    "primary": "#667eea",
    "secondary": "#764ba2",
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "info": "#3b82f6",
    "baseline": "#ef4444",
    "improved_diet": "#10b981",
    "increased_exercise": "#3b82f6",
    "comprehensive": "#8b5cf6",
    "deterioration": "#dc2626",
    "better_medication": "#6366f1",
    "stress_reduction": "#f59e0b",
    "custom": "#ec4899"
}

GRADIENT_COLORS = [
    "#667eea", "#764ba2", "#f093fb", "#f5576c", 
    "#4facfe", "#00f2fe", "#43e97b", "#38f9d7"
]


def create_trajectory_chart(
    trajectories: Dict[str, Any],
    metric: str = "hba1c_percent",
    title: str = "Health Trajectory Projection"
) -> go.Figure:
    """
    Create an interactive trajectory comparison chart with modern styling.
    """
    
    fig = go.Figure()
    
    metric_labels = {
        "hba1c_percent": "HbA1c (%)",
        "weight_kg": "Weight (kg)",
        "fasting_glucose_mgdl": "Fasting Glucose (mg/dL)",
        "systolic_bp": "Systolic BP (mmHg)",
        "overall_health_score": "Health Score"
    }
    
    for idx, (scenario_name, traj_data) in enumerate(trajectories.items()):
        points = traj_data.get("points", [])
        if not points:
            continue
        
        x_values = [p.get("time_step", 0) for p in points]
        y_values = []
        
        for p in points:
            state = p.get("health_state", {})
            y_values.append(state.get(metric, 0))
        
        color = COLORS.get(scenario_name, GRADIENT_COLORS[idx % len(GRADIENT_COLORS)])
        display_name = traj_data.get("scenario_name", scenario_name)
        
        # Add filled area under line
        fig.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            mode='lines',
            name=display_name,
            line=dict(color=color, width=3, shape='spline'),
            fill='tozeroy',
            fillcolor=f'rgba{tuple(list(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + [0.1])}',
            hovertemplate=f"<b>{display_name}</b><br>" +
                         "Month: %{x}<br>" +
                         f"{metric_labels.get(metric, metric)}: %{{y:.1f}}<extra></extra>"
        ))
        
        # Add markers on top
        fig.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            mode='markers',
            name=display_name,
            marker=dict(size=10, color=color, line=dict(width=2, color='white')),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Add target zone for HbA1c
    if metric == "hba1c_percent":
        fig.add_hline(
            y=7.0, 
            line_dash="dash", 
            line_color=COLORS["success"],
            annotation_text="🎯 Target: <7%",
            annotation_position="right",
            annotation_font=dict(size=12, color=COLORS["success"])
        )
    
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=20, color="#1f2937"),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title="Months",
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)',
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            title=metric_labels.get(metric, metric),
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)',
            tickfont=dict(size=12)
        ),
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=11),
            bgcolor='rgba(255,255,255,0.8)'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=450,
        margin=dict(t=80, b=60, l=60, r=40)
    )
    
    return fig


def create_comparison_chart(
    comparison_data: Dict[str, Any]
) -> go.Figure:
    """
    Create a comparison bar chart for trajectory outcomes.
    """
    
    trajectories = comparison_data.get("trajectories", {})
    if not trajectories:
        return go.Figure()
    
    scenarios = list(trajectories.keys())
    hba1c_values = [t.get("final_hba1c", 7.0) for t in trajectories.values()]
    weight_changes = [t.get("weight_change", 0) for t in trajectories.values()]
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Final HbA1c by Scenario", "Weight Change by Scenario")
    )
    
    # HbA1c comparison
    colors = ['#2ECC71' if v < 7 else '#F39C12' if v < 8 else '#E74C3C' for v in hba1c_values]
    
    fig.add_trace(
        go.Bar(
            x=scenarios,
            y=hba1c_values,
            marker_color=colors,
            text=[f"{v:.1f}%" for v in hba1c_values],
            textposition='auto',
            name="HbA1c"
        ),
        row=1, col=1
    )
    
    # Weight change comparison
    weight_colors = ['#2ECC71' if w < 0 else '#E74C3C' for w in weight_changes]
    
    fig.add_trace(
        go.Bar(
            x=scenarios,
            y=weight_changes,
            marker_color=weight_colors,
            text=[f"{w:+.1f} kg" for w in weight_changes],
            textposition='auto',
            name="Weight Change"
        ),
        row=1, col=2
    )
    
    # Add target line for HbA1c
    fig.add_hline(y=7.0, line_dash="dash", line_color="green", row=1, col=1)
    
    fig.update_layout(
        title="Scenario Comparison",
        showlegend=False,
        template="plotly_white",
        height=350
    )
    
    return fig


def create_gauge_chart(
    value: float,
    title: str,
    min_val: float = 0,
    max_val: float = 100,
    thresholds: Optional[List[Tuple[float, str, str]]] = None
) -> go.Figure:
    """
    Create a modern gauge chart for a single metric.
    """
    
    if thresholds is None:
        thresholds = [
            (40, "#ef4444", "Poor"),
            (60, "#f59e0b", "Fair"),
            (80, "#10b981", "Good"),
            (100, "#059669", "Excellent")
        ]
    
    steps = []
    prev = min_val
    for threshold, color, label in thresholds:
        steps.append(dict(range=[prev, threshold], color=color, name=label))
        prev = threshold
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': f"<b>{title}</b>", 'font': {'size': 18, 'color': '#1f2937'}},
        number={'font': {'size': 36, 'color': '#1f2937'}, 'suffix': '%' if 'HbA1c' in title else ''},
        gauge={
            'axis': {
                'range': [min_val, max_val],
                'tickwidth': 2,
                'tickcolor': "#d1d5db",
                'tickfont': {'size': 10}
            },
            'bar': {'color': COLORS["primary"], 'thickness': 0.3},
            'bgcolor': "white",
            'borderwidth': 0,
            'steps': steps,
            'threshold': {
                'line': {'color': "#1f2937", 'width': 4},
                'thickness': 0.8,
                'value': value
            }
        }
    ))
    
    fig.update_layout(
        height=280,
        margin=dict(l=30, r=30, t=60, b=30),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#1f2937'}
    )
    
    return fig


def create_hba1c_gauge(hba1c: float) -> go.Figure:
    """Create a modern gauge for HbA1c"""
    
    thresholds = [
        (5.7, "#10b981", "Normal"),
        (6.5, "#84cc16", "Prediabetes"),
        (7.0, "#eab308", "Target"),
        (8.0, "#f59e0b", "Moderate"),
        (9.0, "#ef4444", "Poor"),
        (14.0, "#dc2626", "Critical")
    ]
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=hba1c,
        title={'text': "<b>HbA1c</b>", 'font': {'size': 18, 'color': '#1f2937'}},
        number={'font': {'size': 42, 'color': '#1f2937'}, 'suffix': '%'},
        gauge={
            'axis': {
                'range': [4.0, 12.0],
                'tickwidth': 2,
                'tickcolor': "#d1d5db",
                'tickvals': [4, 5.7, 7, 8, 10, 12],
                'tickfont': {'size': 11}
            },
            'bar': {'color': COLORS["secondary"], 'thickness': 0.25},
            'bgcolor': "#f3f4f6",
            'borderwidth': 0,
            'steps': [
                {'range': [4, 5.7], 'color': '#10b981'},
                {'range': [5.7, 6.5], 'color': '#84cc16'},
                {'range': [6.5, 7], 'color': '#eab308'},
                {'range': [7, 8], 'color': '#f59e0b'},
                {'range': [8, 9], 'color': '#ef4444'},
                {'range': [9, 12], 'color': '#dc2626'},
            ],
            'threshold': {
                'line': {'color': '#1f2937', 'width': 4},
                'thickness': 0.8,
                'value': hba1c
            }
        }
    ))
    
    # Add target annotation
    target_status = "🎯 On Target!" if hba1c < 7 else "⚠️ Above Target" if hba1c < 8 else "🚨 Needs Attention"
    
    fig.update_layout(
        height=280,
        margin=dict(l=30, r=30, t=60, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#1f2937'},
        annotations=[
            dict(
                text=target_status,
                x=0.5, y=-0.1,
                xref='paper', yref='paper',
                showarrow=False,
                font=dict(size=14)
            )
        ]
    )
    
    return fig


def create_health_score_gauge(score: float) -> go.Figure:
    """Create a modern gauge for overall health score"""
    
    # Determine color based on score
    if score >= 80:
        bar_color = "#10b981"
        status = "Excellent"
    elif score >= 65:
        bar_color = "#84cc16"
        status = "Good"
    elif score >= 50:
        bar_color = "#f59e0b"
        status = "Fair"
    else:
        bar_color = "#ef4444"
        status = "Needs Work"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': "<b>Lifestyle Score</b>", 'font': {'size': 18, 'color': '#1f2937'}},
        number={'font': {'size': 42, 'color': '#1f2937'}, 'suffix': '/100'},
        gauge={
            'axis': {
                'range': [0, 100],
                'tickwidth': 2,
                'tickcolor': "#d1d5db",
                'tickvals': [0, 25, 50, 75, 100],
                'tickfont': {'size': 11}
            },
            'bar': {'color': bar_color, 'thickness': 0.25},
            'bgcolor': "#f3f4f6",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 30], 'color': '#fecaca'},
                {'range': [30, 50], 'color': '#fed7aa'},
                {'range': [50, 65], 'color': '#fef08a'},
                {'range': [65, 80], 'color': '#bbf7d0'},
                {'range': [80, 100], 'color': '#86efac'},
            ],
            'threshold': {
                'line': {'color': '#1f2937', 'width': 4},
                'thickness': 0.8,
                'value': score
            }
        }
    ))
    
    fig.update_layout(
        height=280,
        margin=dict(l=30, r=30, t=60, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#1f2937'},
        annotations=[
            dict(
                text=f"✨ {status}",
                x=0.5, y=-0.1,
                xref='paper', yref='paper',
                showarrow=False,
                font=dict(size=14)
            )
        ]
    )
    
    return fig


def create_trend_sparkline(
    data_points: List[Tuple[int, float]],
    color: str = "#3498DB"
) -> go.Figure:
    """Create a small sparkline chart for trend visualization"""
    
    if not data_points:
        return go.Figure()
    
    x_vals = [p[0] for p in data_points]
    y_vals = [p[1] for p in data_points]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode='lines',
        line=dict(color=color, width=2),
        fill='tozeroy',
        fillcolor=f'rgba{tuple(list(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + [0.1])}'
    ))
    
    fig.update_layout(
        height=60,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def create_lifestyle_radar(lifestyle_data: Dict[str, Any]) -> go.Figure:
    """Create a modern radar chart showing lifestyle factors"""
    
    categories = ['🏃 Exercise', '🥗 Diet', '😴 Sleep', '💊 Medication', '🧘 Stress Mgmt']
    
    # Convert lifestyle data to 0-100 scores
    values = [
        min(100, lifestyle_data.get("exercise_minutes_per_week", 60) / 1.5),
        lifestyle_data.get("overall_score", 0.5) * 100 * 1.5,
        min(100, (lifestyle_data.get("average_sleep_hours", 6) / 8) * 100),
        lifestyle_data.get("medication_adherence", 0.7) * 100,
        (1 - lifestyle_data.get("stress_score", 0.5)) * 100
    ]
    
    values = [min(100, max(0, v)) for v in values]
    
    # Close the radar
    values.append(values[0])
    categories.append(categories[0])
    
    fig = go.Figure()
    
    # Current lifestyle
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(102, 126, 234, 0.3)',
        line=dict(color=COLORS["primary"], width=3),
        name='Your Lifestyle',
        marker=dict(size=8, color=COLORS["primary"])
    ))
    
    # Ideal reference
    ideal = [100, 100, 100, 100, 100, 100]
    fig.add_trace(go.Scatterpolar(
        r=ideal,
        theta=categories,
        fill='none',
        line=dict(color=COLORS["success"], width=2, dash='dot'),
        name='Ideal Target'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10),
                gridcolor='rgba(0,0,0,0.1)'
            ),
            angularaxis=dict(
                tickfont=dict(size=12),
                gridcolor='rgba(0,0,0,0.1)'
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5
        ),
        title=dict(
            text="<b>Lifestyle Assessment</b>",
            font=dict(size=18, color='#1f2937'),
            x=0.5,
            xanchor='center'
        ),
        height=380,
        margin=dict(t=60, b=60, l=60, r=60),
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def create_counterfactual_comparison(
    actual_trajectory: List[Dict],
    counterfactual_trajectory: List[Dict],
    metric: str = "hba1c_percent"
) -> go.Figure:
    """Create a chart comparing actual vs counterfactual trajectories"""
    
    fig = go.Figure()
    
    # Actual trajectory
    actual_x = [p.get("time_step", 0) for p in actual_trajectory]
    actual_y = [p.get("health_state", {}).get(metric, 0) for p in actual_trajectory]
    
    fig.add_trace(go.Scatter(
        x=actual_x,
        y=actual_y,
        mode='lines+markers',
        name='What Happened',
        line=dict(color='#E74C3C', width=3),
        marker=dict(size=8)
    ))
    
    # Counterfactual trajectory
    cf_x = [p.get("time_step", 0) for p in counterfactual_trajectory]
    cf_y = [p.get("health_state", {}).get(metric, 0) for p in counterfactual_trajectory]
    
    fig.add_trace(go.Scatter(
        x=cf_x,
        y=cf_y,
        mode='lines+markers',
        name='What Could Have Been',
        line=dict(color='#2ECC71', width=3, dash='dot'),
        marker=dict(size=8, symbol='diamond')
    ))
    
    # Add shaded area between them
    fig.add_trace(go.Scatter(
        x=actual_x + cf_x[::-1],
        y=actual_y + cf_y[::-1],
        fill='toself',
        fillcolor='rgba(255, 200, 200, 0.3)',
        line=dict(color='rgba(255,255,255,0)'),
        name='Gap',
        showlegend=False
    ))
    
    metric_labels = {
        "hba1c_percent": "HbA1c (%)",
        "weight_kg": "Weight (kg)",
        "overall_health_score": "Health Score"
    }
    
    fig.update_layout(
        title="Counterfactual Comparison: Your Path vs. Alternative Path",
        xaxis_title="Months",
        yaxis_title=metric_labels.get(metric, metric),
        hovermode="x unified",
        template="plotly_white",
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    if metric == "hba1c_percent":
        fig.add_hline(y=7.0, line_dash="dash", line_color="green",
                      annotation_text="Target: <7%")
    
    return fig


def create_metric_history_chart(
    memory_snapshots: List[Dict],
    metrics: List[str] = None
) -> go.Figure:
    """Create a multi-metric history chart from health memory"""
    
    if metrics is None:
        metrics = ["hba1c_percent", "weight_kg"]
    
    if not memory_snapshots:
        return go.Figure()
    
    fig = make_subplots(
        rows=len(metrics), 
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=[m.replace("_", " ").title() for m in metrics]
    )
    
    colors = ["#3498DB", "#E74C3C", "#2ECC71", "#F39C12"]
    
    x_vals = [s.get("time_step", 0) for s in memory_snapshots]
    
    for i, metric in enumerate(metrics, 1):
        y_vals = [s.get("metrics", {}).get(metric, 0) for s in memory_snapshots]
        
        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=y_vals,
                mode='lines+markers',
                name=metric.replace("_", " ").title(),
                line=dict(color=colors[i-1 % len(colors)], width=2),
                marker=dict(size=6)
            ),
            row=i, col=1
        )
    
    fig.update_layout(
        title="Health History from Memory",
        height=200 * len(metrics),
        showlegend=False,
        template="plotly_white"
    )
    
    fig.update_xaxes(title_text="Months", row=len(metrics), col=1)
    
    return fig
