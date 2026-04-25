"""
Prompt Templates for the Generative AI Narrative Engine

This module contains all the prompt templates used to generate
personalized, explainable health narratives and guidance.

DESIGN PRINCIPLES:
1. Prompts explicitly instruct the AI to reason FROM the data
2. Prompts emphasize personalization and specificity
3. Prompts discourage generic medical advice
4. Prompts require explanation of reasoning
5. Prompts maintain appropriate disclaimers
"""


class PromptTemplates:
    """Collection of prompt templates for various narrative types"""
    
    # System prompt that establishes the AI's role
    SYSTEM_PROMPT = """You are DiabeTwin, an AI health companion embedded in a Healthcare Digital Twin system 
for Type 2 Diabetes management. You have access to a virtual patient's complete health history, 
current metrics, lifestyle data, and simulated future trajectories.

Your role is to:
1. EXPLAIN health changes in simple, understandable language
2. PERSONALIZE all insights based on THIS specific patient's data
3. CONNECT lifestyle choices to health outcomes with clear reasoning
4. MOTIVATE positive behavior change through empathetic communication
5. GENERATE specific, actionable guidance grounded in the patient's situation

CRITICAL RULES:
- NEVER provide generic diabetes advice - always reference specific data points
- ALWAYS explain the "why" behind health changes
- Be empathetic and supportive, never judgmental
- Use analogies to make complex concepts understandable
- Include specific numbers from the patient's data
- Acknowledge uncertainty where appropriate
- End with clear, achievable action items when appropriate

DISCLAIMER: You must remind users that this is a simulation for educational purposes 
and not a substitute for professional medical advice."""

    # Template for explaining current health state
    HEALTH_STATE_EXPLANATION = """Based on the following patient data, provide a clear, personalized explanation 
of their current health status. Focus on what the numbers mean and why they matter.

PATIENT PROFILE:
- Name: {patient_name}
- Age: {age} years
- Years with diabetes: {years_diagnosed}
- Current risk category: {risk_category}

CURRENT HEALTH METRICS:
- HbA1c: {hba1c}% (Target: <7%)
- Fasting Glucose: {fasting_glucose} mg/dL (Target: 80-130)
- Weight: {weight} kg (BMI: {bmi})
- Blood Pressure: {systolic}/{diastolic} mmHg (Target: <130/80)
- Overall Health Score: {health_score}/100

CURRENT LIFESTYLE:
- Activity Level: {activity_level}
- Diet Quality: {diet_quality}
- Medication Adherence: {medication_adherence}%
- Stress Level: {stress_level}
- Lifestyle Score: {lifestyle_score}%

Provide a 2-3 paragraph explanation that:
1. Summarizes their current diabetes control status
2. Highlights the most important metric to focus on
3. Explains how their lifestyle is affecting their health
4. Ends with an encouraging, actionable insight"""

    # Template for explaining trajectory comparison
    TRAJECTORY_COMPARISON = """Analyze and explain the following simulated health trajectories for this patient.
Help them understand what each path means for their future health.

PATIENT: {patient_name}, {age} years old, {years_diagnosed} years with Type 2 Diabetes

CURRENT STATE:
- HbA1c: {current_hba1c}%
- Weight: {current_weight} kg

SIMULATED TRAJECTORIES OVER {months} MONTHS:

{trajectory_summaries}

Please provide:
1. A clear comparison of the different futures (2-3 sentences each)
2. The MOST IMPACTFUL change they could make and why
3. What specifically would happen differently in the best-case scenario
4. A motivating message that references their specific numbers
5. One concrete first step they could take this week"""

    # Template for counterfactual storytelling (CORE INNOVATION)
    COUNTERFACTUAL_NARRATIVE = """Generate a compelling counterfactual health story for this patient.
This is about what COULD HAVE BEEN if they had made different choices in the past.

PATIENT: {patient_name}

THE PAST ({months_ago} months ago):
- HbA1c was: {past_hba1c}%
- Weight was: {past_weight} kg
- Lifestyle was: Activity={past_activity}, Diet={past_diet}

WHAT ACTUALLY HAPPENED (Today):
- HbA1c is now: {current_hba1c}%
- Weight is now: {current_weight} kg
- HbA1c change: {actual_hba1c_change:+.1f}%
- Weight change: {actual_weight_change:+.1f} kg

WHAT IF they had maintained: {alternative_lifestyle}

SIMULATED ALTERNATIVE (If they had made better choices):
- HbA1c would be: {counterfactual_hba1c}%
- Weight would be: {counterfactual_weight} kg
- Difference from reality: HbA1c {hba1c_difference:+.1f}%, Weight {weight_difference:+.1f} kg

Create a 3-4 paragraph narrative that:
1. Acknowledges what happened without blame ("The path you took...")
2. Paints a vivid picture of the alternative future they could have had
3. Explains the specific mechanisms (why exercise/diet would have helped)
4. Pivots to HOPE: "Starting today, here's how you can still get there..."
5. Provides specific, achievable next steps based on the alternative lifestyle

The tone should be:
- Reflective but not regretful
- Educational about the cause-and-effect
- Ultimately hopeful and forward-looking
- Personalized with their specific numbers"""

    # Template for conversational responses
    CONVERSATIONAL_RESPONSE = """You are responding to a question from a patient using their Healthcare Digital Twin.
You have access to their complete health history and simulated projections.

PATIENT CONTEXT:
{patient_summary}

RECENT HEALTH TRENDS:
{recent_trends}

PATIENT'S QUESTION:
"{user_question}"

Provide a helpful, personalized response that:
1. Directly addresses their question using their specific data
2. Explains any relevant health concepts in simple terms
3. Connects the answer to their personal health journey
4. Offers practical, actionable advice if appropriate
5. Suggests what to explore next in their digital twin

Keep the response conversational, warm, and under 200 words unless the question requires more detail."""

    # Template for generating personalized action plan
    ACTION_PLAN_GENERATION = """Generate a personalized, prioritized action plan for this patient based on their 
digital twin analysis.

PATIENT: {patient_name}

CURRENT CHALLENGES:
- Primary concern: {primary_concern}
- HbA1c: {hba1c}% ({hba1c_status} target)
- Weight trend: {weight_trend}
- Lifestyle score: {lifestyle_score}%

SIMULATION INSIGHTS:
{simulation_insights}

DETECTED PATTERNS:
{detected_patterns}

Create a structured action plan with:

1. TOP PRIORITY (This Week):
   - One specific, measurable action
   - Why this matters for their diabetes (reference their numbers)
   - Expected impact

2. SHORT-TERM GOALS (This Month):
   - 2-3 achievable targets
   - How these connect to their simulation results

3. MEDIUM-TERM VISION (3 Months):
   - What their numbers could look like
   - The lifestyle habits to maintain

4. PROGRESS MARKERS:
   - What to watch for to know it's working
   - When to check back with their digital twin

Make all recommendations specific to this patient's situation and grounded in their data."""

    # Template for explaining why a metric changed
    METRIC_CHANGE_EXPLANATION = """Explain why this patient's {metric_name} changed from {old_value} to {new_value} 
over the past {time_period}.

PATIENT CONTEXT:
{patient_context}

LIFESTYLE DURING THIS PERIOD:
{lifestyle_summary}

MODEL EXPLANATIONS:
{model_explanations}

Provide a clear, educational explanation that:
1. States what happened (the change)
2. Explains the primary cause(s) from their lifestyle
3. Uses an analogy to make the mechanism understandable
4. Describes what this means for their overall diabetes management
5. Suggests what would reverse or continue this trend

Keep the explanation under 150 words and use simple language."""

    # Template for milestone celebration
    MILESTONE_CELEBRATION = """The patient has achieved a health milestone! Generate an encouraging, 
celebratory message that acknowledges their achievement.

MILESTONE: {milestone_type}
DETAILS: {milestone_details}

PATIENT JOURNEY:
- Started: {journey_start}
- Current: {current_state}
- Improvement: {improvement}

WHAT CONTRIBUTED:
{contributing_factors}

Create a warm, celebratory message that:
1. Congratulates them specifically on what they achieved
2. Acknowledges the effort and lifestyle changes that made it possible
3. Puts this achievement in context of their diabetes journey
4. Encourages them to maintain momentum
5. Hints at what the next milestone could be

Keep it positive, personal, and under 100 words."""

    # Template for warning/concern notification
    WARNING_EXPLANATION = """A concerning trend has been detected in the patient's health data.
Generate an empathetic but clear warning message.

CONCERN: {concern_type}
DETAILS: {concern_details}

TREND DATA:
- Previous: {previous_value}
- Current: {current_value}
- Direction: {direction}

POSSIBLE CAUSES:
{possible_causes}

Generate a message that:
1. Clearly states the concern without causing panic
2. Explains why this matters for diabetes management
3. Identifies likely contributing factors from their data
4. Provides immediate, actionable steps
5. Encourages them to consult their healthcare provider if appropriate
6. Ends on a supportive, hopeful note

Balance honesty with empathy. Be direct but not alarmist."""

    @classmethod
    def get_all_templates(cls) -> dict:
        """Return all templates as a dictionary"""
        return {
            "system": cls.SYSTEM_PROMPT,
            "health_state": cls.HEALTH_STATE_EXPLANATION,
            "trajectory": cls.TRAJECTORY_COMPARISON,
            "counterfactual": cls.COUNTERFACTUAL_NARRATIVE,
            "conversation": cls.CONVERSATIONAL_RESPONSE,
            "action_plan": cls.ACTION_PLAN_GENERATION,
            "metric_change": cls.METRIC_CHANGE_EXPLANATION,
            "milestone": cls.MILESTONE_CELEBRATION,
            "warning": cls.WARNING_EXPLANATION
        }
