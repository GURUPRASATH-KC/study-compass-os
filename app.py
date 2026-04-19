import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from dotenv import load_dotenv
import anthropic
import time

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="StudyCompass | AI Student OS",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for UI tricks and beautiful aesthetic
st.markdown("""
<style>
    .score-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .badge-strong { background-color: #d4edda; color: #155724; padding: 5px 10px; border-radius: 12px; font-weight: bold; }
    .badge-moderate { background-color: #fff3cd; color: #856404; padding: 5px 10px; border-radius: 12px; font-weight: bold; }
    .badge-low { background-color: #f8d7da; color: #721c24; padding: 5px 10px; border-radius: 12px; font-weight: bold; }
    
    .stProgress .st-bo { background-color: #4CAF50; }
    
    .loan-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if 'profile' not in st.session_state:
    st.session_state.profile = {
        'name': '',
        'cgpa': 0.0,
        'budget': 0,
        'goal': '',
        'target_country': '',
        'gre_score': 0,
        'ielts_score': 0.0,
        'collateral_available': False,
        'financial_savings': 0
    }

if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

# Initialize Anthropic Client
@st.cache_resource
def get_claude_client():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    return anthropic.Anthropic(api_key=api_key)

client = get_claude_client()
CLAUDE_MODEL = "claude-3-5-sonnet-20240620"

# Helper function to call Claude
def call_claude(prompt, system_prompt="You are a helpful AI assistant."):
    if not client:
        time.sleep(1.5) # Mock latency
        return "⚠️ Please add your Anthropic API Key in the `.env` file to see AI generated responses. (This is a mock response)."
    
    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1500,
            system=system_prompt,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
    except Exception as e:
        return f"Error connecting to AI: {str(e)}"

# Calculate profile strength
def calculate_profile_strength():
    p = st.session_state.profile
    score = 20 # Base score for opening app
    if p['name']: score += 10
    if p['cgpa'] > 0: score += 15
    if p['goal']: score += 15
    if p['target_country']: score += 15
    if p['budget'] > 0: score += 10
    if p['gre_score'] > 0: score += 10
    if p['ielts_score'] > 0: score += 5
    return min(100, score)

def get_academic_rating():
    cgpa = st.session_state.profile.get('cgpa', 0)
    if cgpa >= 8.5: return "Strong", "badge-strong"
    elif cgpa >= 7.0: return "Moderate", "badge-moderate"
    else: return "Needs Work", "badge-low"

def get_financial_rating():
    budget = st.session_state.profile.get('budget', 0)
    if budget >= 4000000: return "Strong", "badge-strong"
    elif budget >= 2000000: return "Medium", "badge-moderate"
    else: return "Self-funding Low", "badge-low"

def calculate_loan_readiness():
    elig_score = 40
    if st.session_state.profile.get('cgpa', 0) > 8: elig_score += 20
    if st.session_state.profile.get('gre_score', 0) > 315: elig_score += 15
    if st.session_state.profile.get('collateral_available', False): elig_score += 25
    return min(100, elig_score)

# UI: Sidebar Engagement Engine
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2942/2942784.png", width=60) # Placeholder logo
    st.title("StudyCompass")
    st.markdown("### AI Student OS")
    
    st.divider()
    
    # Engagement Nudge / Next Best Action
    st.markdown("### 🎯 Your Next Best Action")
    profile_score = calculate_profile_strength()
    
    if profile_score < 50:
        st.info("👋 Complete your **Profile Tab** today to unlock smart loan matching!")
    elif profile_score < 80:
        st.warning("⚡ **Action:** Set your target country & exams to generate an SOP.")
    else:
        st.success("🔥 **Ready:** Generate your Timeline. Fall 2026 deadlines are near!")
        
    st.progress(profile_score / 100, text=f"Profile Strength: {profile_score}/100")
    
    st.divider()
    
    # Proactive Copilot Mentor (Real presence)
    st.markdown("### 🤖 Your AI Mentor")
    
    budget_lakhs = st.session_state.profile.get('budget', 0) / 100000
    target_c = st.session_state.profile.get('target_country', '')
    
    if target_c == 'USA' and budget_lakhs > 0 and budget_lakhs < 40:
        st.info(f"👋 You previously mentioned ₹{budget_lakhs:g}L budget — I suggest exploring Germany or European options over the USA for better ROI!")
    elif target_c == 'Germany':
        st.info("👋 I see you're aiming for Germany! Public universities have zero tuition. Want me to draft a timeline?")
    elif budget_lakhs > 0 and budget_lakhs < 15:
        st.info(f"👋 Your budget of ₹{budget_lakhs:g}L is tight, but your CGPA is good. Should we look at fully funded programs in Europe?")
    else:
        st.info("👋 Hi! I'm Claude, your AI Mentor. Let me know if you need help deciding on a course or evaluating a loan.")

# Main Application Layout
tabs = st.tabs(["Profile Dashboard", "Generators (SOP & Timeline)", "Finance & Loans", "AI Copilot"])

# --- TAB 1: PROFILE DASHBOARD ---
with tabs[0]:
    st.header("Home Dashboard")
    
    # WOW Feature: Profile Score Card
    st.markdown("<div class='score-card'>", unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    
    aca_text, aca_badge = get_academic_rating()
    fin_text, fin_badge = get_financial_rating()
    loan_readiness = calculate_loan_readiness()
    
    with col1:
        st.metric(label="Profile Strength", value=f"{profile_score}/100", delta="+5 this week")
    with col2:
        st.metric(label="Loan Readiness", value=f"{loan_readiness}%", delta="High Intent", delta_color="normal")
    with col3:
        st.markdown(f"**Academics:**<br><span class='{aca_badge}'>{aca_text}</span>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"**Exams:**<br><span class='badge-moderate'>Moderate</span>", unsafe_allow_html=True)
    with col5:
        st.markdown(f"**Financial Prep:**<br><span class='{fin_badge}'>{fin_text}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # "Explain My Profile" logic
    if st.button("🎤 Explain My Profile"):
        with st.spinner("Analyzing your profile..."):
            prof_prompt = f"Explain this student's profile strength and weaknesses and suggest next steps. Profile: Course {st.session_state.profile.get('goal')}, CGPA {st.session_state.profile.get('cgpa')}, GRE {st.session_state.profile.get('gre_score')}, Budget {st.session_state.profile.get('budget')} INR."
            sys_p = "You are an admissions expert evaluating an applicant."
            analysis = call_claude(prof_prompt, sys_p)
            st.info(analysis)
    
    # Data Input Section
    with st.expander("📝 Update Your Profile Details", expanded=(profile_score < 50)):
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.profile['name'] = st.text_input("Full Name", st.session_state.profile['name'])
            st.session_state.profile['goal'] = st.text_input("Target Course (e.g. MS CS, MBA)", st.session_state.profile['goal'])
            st.session_state.profile['target_country'] = st.selectbox("Preferred Country", ["", "USA", "UK", "Canada", "Germany", "Australia", "Other"], index=0 if not st.session_state.profile['target_country'] else ["", "USA", "UK", "Canada", "Germany", "Australia", "Other"].index(st.session_state.profile['target_country']))
        with c2:
            st.session_state.profile['cgpa'] = st.number_input("CGPA (out of 10)", min_value=0.0, max_value=10.0, step=0.1, value=st.session_state.profile['cgpa'])
            st.session_state.profile['gre_score'] = st.number_input("GRE / GMAT Score", min_value=0, max_value=800, step=1, value=st.session_state.profile['gre_score'])
            st.session_state.profile['budget'] = st.number_input("Amount you can self-fund (INR)", min_value=0, step=100000, value=st.session_state.profile['budget'])
        
        st.session_state.profile['collateral_available'] = st.checkbox("I have property/assets for loan collateral", value=st.session_state.profile['collateral_available'])

# --- TAB 2: GENERATORS ---
with tabs[1]:
    st.header("⚡ AI Generators")
    
    if profile_score < 40:
        st.warning("Please fill out more of your profile on the Dashboard to use AI features.")
    else:
        system_prompt = f"""You are a master study abroad advisor. 
        Student Profile: 
        Course: {st.session_state.profile.get('goal', 'Unknown')}
        Target Country: {st.session_state.profile.get('target_country', 'Unknown')}
        CGPA: {st.session_state.profile.get('cgpa', 'Unknown')}"""

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Timeline Generator")
            target_term = st.selectbox("Target Intake", ["Fall 2025", "Spring 2026", "Fall 2026"])
            if st.button("Generate Timeline", type="primary"):
                with st.spinner("Claude is crafting your perfect timeline..."):
                    prompt = f"Create a detailed, month-by-month application timeline for {target_term} intake."
                    result = call_claude(prompt, system_prompt)
                    st.markdown(result)
        
        with col2:
            st.subheader("SOP Architect")
            bullet_points = st.text_area("List 3 key experiences/strengths to include:")
            if st.button("Draft SOP Concept", type="primary"):
                with st.spinner("Structuring your Statement of Purpose..."):
                    prompt = f"Draft an SOP outline and introductory paragraph using these points: {bullet_points}"
                    result = call_claude(prompt, system_prompt)
                    st.info(result)

        st.divider()
        st.subheader("📥 Export Center")
        mock_pdf_content = "StudyCompass Generated Plan\n==========================\nBased on your profile, here are your strategic timeline and recommendations."
        st.download_button(
            label="Download Study Plan (PDF)",
            data=mock_pdf_content,
            file_name="StudyCompass_Plan.pdf",
            mime="application/pdf",
            type="primary"
        )

# --- TAB 3: FINANCE & LOANS ---
with tabs[2]:
    st.header("💰 Smart Loan Funnel")
    st.write("Determine your funding capability and get AI-advised loan offers.")
    
    # Financial Analytics logic
    req_funding = 6000000 # Mock average cost
    shortfall = max(0, req_funding - st.session_state.profile['budget'])
    
    colA, colB = st.columns([1, 2])
    with colA:
        st.markdown(f"### Eligibility Score")
        
        # Calculate Mock Eligibility
        elig_score = calculate_loan_readiness()
        
        st.progress(elig_score/100, text=f"{elig_score}/100")
        
        if elig_score >= 80: st.markdown("Risk Level: <span class='badge-strong'>Low Risk 🟢</span>", unsafe_allow_html=True)
        elif elig_score >= 60: st.markdown("Risk Level: <span class='badge-moderate'>Medium Risk 🟡</span>", unsafe_allow_html=True)
        else: st.markdown("Risk Level: <span class='badge-low'>High Risk 🔴</span>", unsafe_allow_html=True)
            
        st.metric("Estimated Shortfall", f"₹ {shortfall:,.0f}")
        
    with colB:
        st.markdown("### Top Recommended Loan")
        if st.session_state.profile['collateral_available']:
            offer = "SBI Global Ed-Vantage (Secured)"
            rate = "8.65% p.a."
            why = "Lowest interest rate using your collateral."
        else:
            offer = "Prodigy Finance / HDFC Credila (Unsecured)"
            rate = "11.5% - 13.5% p.a."
            why = "No collateral needed, evaluated based on target university and GRE."
            
        st.markdown(f"""
        <div class="loan-card">
            <h2 style="margin:0; color:white;">{offer}</h2>
            <h4 style="margin:5px 0; color:#e2e8f0;">Interest Rate: {rate}</h4>
            <br>
            <p style="margin:0;"><i>Why this fits you: {why}</i></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.success("💡 **Pro-tip:** You can reduce EMI by choosing an NBFC + partial self-funding!")
        if st.button("Apply / Learn More"):
            st.balloons()
            st.write("Mock conversion successful! Redirecting to partner...")

    st.divider()
    st.subheader("💬 AI Loan Advisor")
    st.write("Have doubts? Ask Claude about collateral, co-signers, or interest rates.")
    
    finance_q = st.text_input("Ask a question (e.g. How does moratorium period work?)")
    if st.button("Ask Advisor"):
        with st.spinner("Consulting..."):
            sys_prompt = f"You are an expert Indian Education Loan advisor. Speak to a student heading to {st.session_state.profile.get('target_country','abroad')}."
            ans = call_claude(finance_q, sys_prompt)
            st.info(ans)

# --- TAB 4: AI COPILOT ---
with tabs[3]:
    st.header("🤖 Continuous Chat Mentor")
    st.write("Your personal advisor who remembers your context.")
    
    # Render chat history
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    # Input
    user_q = st.chat_input("E.g., Which universities are good for my profile?")
    
    if user_q:
        # Add to state
        st.session_state.chat_messages.append({"role": "user", "content": user_q})
        with st.chat_message("user"):
            st.write(user_q)
            
        # Get AI response
        sys_context = f"""You are StudyCompass AI, a study abroad mentor. 
        Student info: 
        Name: {st.session_state.profile.get('name','Student')}
        Course: {st.session_state.profile.get('goal')}
        CGPA: {st.session_state.profile.get('cgpa')}
        Budget: {st.session_state.profile.get('budget')} INR
        Always be encouraging, concise, and proactive."""
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = call_claude(user_q, sys_context)
                st.write(response)
        
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
