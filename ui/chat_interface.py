"""
Chat Interface for DiabeTwin

Implements the conversational "Ask Your Twin" feature that allows
patients to interact naturally with their digital twin.
"""

import streamlit as st
from typing import Dict, Any, List, Optional
from datetime import datetime


def render_chat_interface(
    patient_summary: Dict[str, Any],
    trends: List[Dict[str, Any]],
    narrative_engine: Any,
    key_prefix: str = "chat"
):
    """
    Render the conversational chat interface.
    
    Args:
        patient_summary: Summary of patient health state
        trends: Recent health trends
        narrative_engine: The GenAI narrative engine
        key_prefix: Unique key prefix for session state
    """
    
    st.markdown("### 💬 Ask Your Digital Twin")
    st.caption("Ask questions about your health, get personalized explanations")
    
    # Initialize chat history in session state
    if f"{key_prefix}_messages" not in st.session_state:
        st.session_state[f"{key_prefix}_messages"] = [
            {
                "role": "assistant",
                "content": _get_greeting(patient_summary),
                "timestamp": datetime.now().isoformat()
            }
        ]
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state[f"{key_prefix}_messages"]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Suggested questions
    st.markdown("**Suggested questions:**")
    suggestions = [
        "Why is my HbA1c at this level?",
        "What's affecting my health the most?",
        "How can I improve my health score?",
        "What would happen if I exercised more?",
        "Explain my risk category to me"
    ]
    
    cols = st.columns(len(suggestions))
    for i, suggestion in enumerate(suggestions):
        with cols[i]:
            if st.button(suggestion, key=f"{key_prefix}_suggest_{i}", use_container_width=True):
                _handle_user_message(
                    suggestion,
                    patient_summary,
                    trends,
                    narrative_engine,
                    key_prefix
                )
                st.rerun()
    
    # Chat input
    user_input = st.chat_input("Ask your digital twin anything...")
    
    if user_input:
        _handle_user_message(
            user_input,
            patient_summary,
            trends,
            narrative_engine,
            key_prefix
        )
        st.rerun()
    
    # Clear chat button
    if st.button("Clear Chat History", key=f"{key_prefix}_clear"):
        st.session_state[f"{key_prefix}_messages"] = [
            {
                "role": "assistant",
                "content": _get_greeting(patient_summary),
                "timestamp": datetime.now().isoformat()
            }
        ]
        st.rerun()


def _handle_user_message(
    user_message: str,
    patient_summary: Dict[str, Any],
    trends: List[Dict[str, Any]],
    narrative_engine: Any,
    key_prefix: str
):
    """Process a user message and generate response"""
    
    # Add user message to history
    st.session_state[f"{key_prefix}_messages"].append({
        "role": "user",
        "content": user_message,
        "timestamp": datetime.now().isoformat()
    })
    
    # Generate response
    try:
        if narrative_engine and hasattr(narrative_engine, 'generate_conversational_response'):
            response = narrative_engine.generate_conversational_response(
                user_question=user_message,
                patient_summary=patient_summary,
                recent_trends=trends
            )
            response_text = response.content
        else:
            response_text = _generate_fallback_response(user_message, patient_summary)
    except Exception as e:
        response_text = f"I apologize, but I encountered an issue generating a response. Please try again. (Error: {str(e)})"
    
    # Add assistant response to history
    st.session_state[f"{key_prefix}_messages"].append({
        "role": "assistant",
        "content": response_text,
        "timestamp": datetime.now().isoformat()
    })


def _get_greeting(patient_summary: Dict[str, Any]) -> str:
    """Generate a personalized greeting"""
    
    name = patient_summary.get("current_state", {}).get("name", "there")
    hba1c = patient_summary.get("current_state", {}).get("hba1c", 7.0)
    health_score = patient_summary.get("current_state", {}).get("health_score", 60)
    
    if health_score >= 70:
        status = "You're doing well"
    elif health_score >= 50:
        status = "There's room for improvement"
    else:
        status = "Let's work together on improving your health"
    
    return f"""
👋 Hello! I'm your personal DiabeTwin - a virtual representation of your health journey.

Based on my latest analysis:
- Your HbA1c is at **{hba1c:.1f}%**
- Your overall health score is **{health_score:.0f}/100**
- {status}

I'm here to help you understand your health data, explore what-if scenarios, 
and provide personalized guidance. Feel free to ask me anything about your health!

*What would you like to know?*
"""


def _generate_fallback_response(
    question: str,
    patient_summary: Dict[str, Any]
) -> str:
    """Generate a response without the AI engine"""
    
    current = patient_summary.get("current_state", {})
    hba1c = current.get("hba1c", 7.0)
    weight = current.get("weight", 85)
    health_score = current.get("health_score", 60)
    
    question_lower = question.lower()
    
    # Simple keyword matching for common questions
    if "hba1c" in question_lower or "a1c" in question_lower:
        if hba1c < 7.0:
            status = "Your HbA1c is currently well-controlled, which is great!"
        elif hba1c < 8.0:
            status = "Your HbA1c is slightly above target. Small lifestyle adjustments can help."
        else:
            status = "Your HbA1c indicates room for improvement. Let's focus on key changes."
        
        return f"""
Your current HbA1c is **{hba1c:.1f}%**.

{status}

HbA1c reflects your average blood sugar over the past 2-3 months. The target for most 
people with Type 2 Diabetes is **below 7%**.

**What affects HbA1c:**
- 🥗 Diet quality and carbohydrate intake
- 🏃 Physical activity levels
- 💊 Medication adherence
- 😰 Stress and sleep quality

Would you like to explore how different lifestyle changes might affect your HbA1c? 
Try the "Simulate Future" feature!
"""
    
    elif "weight" in question_lower or "bmi" in question_lower:
        return f"""
Your current weight is **{weight:.1f} kg**.

Weight management is crucial for Type 2 Diabetes because:
- Even a 5-7% weight reduction can significantly improve blood sugar control
- Lower weight reduces insulin resistance
- It helps lower blood pressure and cholesterol

**Tips for weight management:**
- Focus on portion control, not restrictive diets
- Aim for gradual weight loss (0.5-1 kg per week)
- Combine dietary changes with increased physical activity

Use the lifestyle sliders to see how weight changes might affect your trajectory!
"""
    
    elif "exercise" in question_lower or "activity" in question_lower or "physical" in question_lower:
        return f"""
Physical activity is one of the most powerful tools for managing Type 2 Diabetes!

**How exercise helps:**
- Improves insulin sensitivity (your body uses insulin more effectively)
- Helps lower blood sugar, even hours after exercise
- Supports weight management
- Reduces cardiovascular risk
- Improves mood and reduces stress

**Recommendations:**
- Aim for **150 minutes per week** of moderate activity
- Start small: even 10-minute walks after meals help
- Mix aerobic exercise (walking, swimming) with resistance training

Try adjusting the exercise slider to see how increased activity could change your health trajectory!
"""
    
    elif "risk" in question_lower:
        return f"""
Your health score is currently **{health_score:.0f}/100**, which reflects your overall diabetes management status.

**Factors affecting your risk:**
- HbA1c level (current: {hba1c:.1f}%)
- Blood pressure control
- Weight and BMI
- Lifestyle factors
- Duration of diabetes

**To reduce risk:**
1. Keep HbA1c below 7%
2. Maintain blood pressure under 130/80
3. Stay physically active
4. Follow a balanced diet
5. Take medications as prescribed

Explore the simulation features to see how changes can improve your risk profile!
"""
    
    elif "improve" in question_lower or "better" in question_lower:
        suggestions = []
        
        if hba1c >= 7.0:
            suggestions.append("Lower your HbA1c through diet and exercise")
        if health_score < 70:
            suggestions.append("Increase your overall lifestyle score")
        
        suggestions.extend([
            "Try the 'Comprehensive Lifestyle Change' scenario in simulations",
            "Focus on one change at a time for sustainable improvement",
            "Use the what-if scenarios to find the most impactful changes"
        ])
        
        return f"""
Great question! Here are personalized suggestions based on your data:

**Priority Improvements:**
{chr(10).join(f'• {s}' for s in suggestions)}

**Quick Wins:**
1. Add a 15-minute walk after dinner
2. Reduce sugary drinks by half
3. Improve sleep to 7-8 hours

Your digital twin simulations show that the **Comprehensive Lifestyle Change** 
scenario could have the biggest impact. Try it in the simulation panel!
"""
    
    else:
        # Generic response
        return f"""
Thanks for your question! Based on your current health profile:

- **HbA1c:** {hba1c:.1f}%
- **Weight:** {weight:.1f} kg
- **Health Score:** {health_score:.0f}/100

I can help you understand:
- 📊 What your metrics mean
- 🔮 How different scenarios affect your future
- 💡 Specific ways to improve
- ⏰ What could have been different (counterfactual analysis)

Try asking more specific questions like:
- "Why is my HbA1c at this level?"
- "What would happen if I exercised more?"
- "How can I lower my risk?"

*For the best experience, connect an AI service in your .env file for fully personalized responses!*
"""


def render_mini_chat(
    patient_summary: Dict[str, Any],
    narrative_engine: Any
) -> Optional[str]:
    """
    Render a minimal chat input for quick questions.
    
    Returns the AI response if a question was asked.
    """
    
    quick_question = st.text_input(
        "Quick question for your twin:",
        placeholder="e.g., Why is my health score low?",
        key="mini_chat_input"
    )
    
    if quick_question:
        try:
            if narrative_engine and hasattr(narrative_engine, 'generate_conversational_response'):
                response = narrative_engine.generate_conversational_response(
                    user_question=quick_question,
                    patient_summary=patient_summary,
                    recent_trends=[]
                )
                return response.content
            else:
                return _generate_fallback_response(quick_question, patient_summary)
        except Exception as e:
            return f"Error: {str(e)}"
    
    return None
