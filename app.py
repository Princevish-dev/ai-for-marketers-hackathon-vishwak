import streamlit as st
import google.generativeai as genai
from bs4 import BeautifulSoup
import requests
import json
import datetime
import pandas as pd
import os
import time
import streamlit.components.v1 as components
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# --- SETUP & CONFIG ---
st.set_page_config(page_title="GROWTHOS | AI Marketing Suite", page_icon="🚀", layout="wide")

# Custom CSS for SaaS-style Modern UI
st.markdown("""
<style>
    /* Color Variables & Base */
    :root {
        --primary: #6C63FF;
        --secondary: #FF6584;
        --accent: #00D2FF;
        --success: #00C9A7;
        --bg-light: #F8F9FE;
        --bg-dark: #0D1117;
        --card-light: #FFFFFF;
        --card-dark: #161B22;
        --text-light: #333333;
        --text-dark: #E6E6E6;
    }
    
    /* Responsive & Overflow Fixes */
    .stApp { word-wrap: break-word; overflow-wrap: break-word; }
    
    /* Gradient Header */
    .gradient-header {
        background: linear-gradient(90deg, #6C63FF, #00D2FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        font-size: 3.5rem;
        margin-bottom: 0px;
        text-align: center;
        letter-spacing: -1px;
    }
    
    .tagline {
        text-align: center;
        font-size: 1.2rem;
        color: #888;
        margin-bottom: 30px;
        font-weight: 500;
    }

    /* Cards with Shadows & Hover */
    .saas-card {
        background-color: var(--card-light);
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(0,0,0,0.05);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 100%;
        margin-bottom: 20px;
        position: relative;
        overflow: hidden;
    }
    .saas-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(108, 99, 255, 0.15);
    }
    
    @media (prefers-color-scheme: dark) {
        .saas-card {
            background-color: var(--card-dark);
            border: 1px solid rgba(255,255,255,0.05);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            color: var(--text-dark);
        }
        .saas-card:hover {
            box-shadow: 0 15px 35px rgba(0, 210, 255, 0.2);
        }
    }
    
    /* Content Boxes */
    .content-box {
        background: var(--card-light);
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 16px;
        border-left: 5px solid var(--primary);
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        font-size: 0.95rem;
        line-height: 1.5;
    }
    @media (prefers-color-scheme: dark) {
        .content-box {
            background: #21262d;
            color: var(--text-dark);
            border-left: 5px solid var(--primary);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
    }
    
    /* Specific Borders */
    .border-pink { border-left-color: var(--secondary) !important; }
    .border-cyan { border-left-color: var(--accent) !important; }
    .border-green { border-left-color: var(--success) !important; }
    
    /* Metrics */
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: var(--primary);
        margin: 10px 0;
        background: linear-gradient(45deg, var(--primary), var(--secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Pulse animation for primary buttons */
    .stButton>button[kind="primary"] {
        animation: pulse 2s infinite;
        background: linear-gradient(90deg, #6C63FF, #FF6584) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(108, 99, 255, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(108, 99, 255, 0); }
        100% { box-shadow: 0 0 0 0 rgba(108, 99, 255, 0); }
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'metrics' not in st.session_state:
    st.session_state.metrics = {'generated': 0, 'time_saved_hours': 0, 'roi_inr': 0}
if 'push_to_ad_studio' not in st.session_state:
    st.session_state.push_to_ad_studio = False
if 'ad_product_info' not in st.session_state:
    st.session_state.ad_product_info = ""
if 'use_insights' not in st.session_state:
    st.session_state.use_insights = False
if 'insight_text' not in st.session_state:
    st.session_state.insight_text = ""
if 'dashboard_data' not in st.session_state:
    st.session_state.dashboard_data = []

# --- GEMINI HELPER ---
def get_gemini_model():
    valid_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    if valid_models:
        return genai.GenerativeModel(valid_models[0])
    return genai.GenerativeModel('gemini-1.5-flash')

def call_gemini(prompt, api_key):
    try:
        genai.configure(api_key=api_key)
        model = get_gemini_model()
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith('```json'): text = text[7:-3]
        elif text.startswith('```'): text = text[3:-3]
        return json.loads(text.strip())
    except Exception as e:
        return None

# --- DUMMY FALLBACK DATA ---
def dummy_content():
    return {
        "twitter": [
            "🚀 Boost your growth with GrowthOS! #Marketing #Growth",
            "Stop wasting time on manual content creation. Let AI do the heavy lifting. 🤖💡 #AI",
            "10x your output today with our latest suite. #Tech",
            "Content is king, but distribution is queen. 👑",
            "Data-driven decisions win the market. 📊",
            "Are you utilizing competitor intel? You should be. 🕵️",
            "Landing pages that convert > Landing pages that just look pretty. 💸",
            "Engagement dropping? Try repurposing your top blogs! ♻️",
            "The future of marketing is personalized and automated. 🌟",
            "Grow your audience effortlessly. 🌱 #GrowthOS"
        ],
        "linkedin": [
            "In today's fast-paced digital world, leveraging AI for marketing is essential. Our latest findings show a 300% increase in productivity for teams using AI suites. 📈 #MarketingStrategy #AI",
            "Data-driven insights reveal that repurposing content can extend its lifespan by up to 3x. Maximize the reach of your best assets. 💡 #ContentMarketing",
            "Competitor analysis is often overlooked. By understanding the gaps, you can position your brand as the undeniable solution. 🔍 #MarketResearch",
            "Building a landing page shouldn't take weeks. Deploy high-converting pages in minutes for rapid A/B testing. ⚡ #WebDevelopment",
            "Marketing teams are saving 15 hours/week by automating content pipelines. ⏰ #Productivity"
        ],
        "instagram": [
            "Transform your marketing game today! 🚀✨ #marketing #growth #ai #business #success #digitalmarketing",
            "Data never lies. 📊📈 Stay ahead of the curve with actionable insights. #data #analytics #insights #businessintelligence",
            "Work smarter, not harder. 🤖💼 Automate the mundane and focus on what matters. #automation #ai #worksmart"
        ],
        "newsletter": {
            "subject": "🚀 How to 10x your Marketing ROI this month",
            "body": "Hello Marketer,\n\nAre you struggling to keep up with the endless demand for fresh content? You're not alone.\n\nBy repurposing existing blog posts into dozens of social media assets, you can maintain a consistent presence without burnout. Combining this with automated ad generation and competitor intelligence ensures your messaging is targeted and effective.\n\nReady to elevate your game? Let us know your biggest bottleneck.\n\nBest,\nYour Growth Partner"
        }
    }

def dummy_ads():
    html_page = '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: 'Inter', sans-serif; margin: 0; padding: 0; background: #f8f9fe; color: #333; }
            .hero { background: linear-gradient(135deg, #6C63FF, #00D2FF); padding: 80px 20px; text-align: center; color: white; }
            .hero h1 { font-size: 3em; margin-bottom: 10px; }
            .cta-btn { display: inline-block; background: linear-gradient(45deg, #FF6584, #FF8E53); color: white; padding: 15px 30px; text-decoration: none; border-radius: 30px; font-weight: bold; margin-top: 20px; box-shadow: 0 4px 15px rgba(255,101,132,0.4); }
            .features { display: flex; justify-content: center; gap: 20px; padding: 50px 20px; flex-wrap: wrap; }
            .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); width: 280px; text-align: center; }
            .countdown { font-size: 1.2em; font-weight: bold; margin-top: 30px; color: #ffeb3b; }
            .testimonials { background: white; padding: 50px 20px; text-align: center; }
        </style>
    </head>
    <body>
        <div class="hero">
            <h1>Supercharge Your Growth</h1>
            <p>The all-in-one AI marketing suite that saves you time and drives revenue.</p>
            <a href="#" class="cta-btn">Get Started Now</a>
            <div class="countdown">⏳ Offer ends in: 02:15:30</div>
        </div>
        <div class="features">
            <div class="card"><h2>🚀</h2><h3>Fast Execution</h3><p>Generate campaigns in seconds.</p></div>
            <div class="card"><h2>🎯</h2><h3>Targeted Ads</h3><p>Reach the right audience.</p></div>
            <div class="card"><h2>📈</h2><h3>High ROI</h3><p>Maximize your returns.</p></div>
        </div>
        <div class="testimonials">
            <h2>What Our Users Say</h2>
            <p><i>"GrowthOS completely transformed our marketing pipeline!"</i> - Sarah J., CMO</p>
        </div>
    </body>
    </html>
    '''
    return {
        "google_ads": ["Grow Your Business Faster", "AI Marketing Suite 2024", "Automate Content Creation", "Beat Your Competitors Today", "Maximize Your Ad ROI"],
        "facebook_ads": ["Struggling with content creation? Let GrowthOS do the heavy lifting! Start your free trial today and 10x your output. 🚀", "Your competitors use AI. Don't get left behind! Discover the ultimate marketing suite designed for growth. 📈", "Create a week's worth of content in 5 minutes. With GrowthOS, it's possible! ⏰", "Ready to scale? Our Ad Studio generates high-converting copy. 🎯", "Unlock competitor intelligence and position your brand to win. 🕵️‍♂️"],
        "instagram_ads": ["Stunning visuals paired with AI-generated copy. Stop the scroll! 📸✨ #marketing", "Swipe left to see how much time you could save this week. ⏱️🚀", "Your next viral campaign is just a click away. 🎯🔥"],
        "landing_page": html_page
    }

def dummy_intel():
    return {
        "complaints": ["Customer service is extremely slow.", "The pricing model is confusing.", "The mobile app crashes frequently."],
        "topics": ["How Our 24/7 Support Team Ensures You're Never Left Waiting", "Transparent Pricing: What You See Is What You Pay", "A Seamless Mobile Experience", "Why Fast Resolution Times Matter", "Avoiding Hidden Fees: A Buyer's Guide"],
        "positioning": "While competitors struggle with reliability, our brand offers a straightforward, seamless experience with guaranteed fast support and crystal-clear pricing.",
        "sentiment": {"score": 45, "positive": 30, "neutral": 25, "negative": 45},
        "viral_tweets": ["Ever waited 3 days for a support reply? 🙄 We don't do that. Average response time: 5 minutes. ⚡", "Hidden fees are the worst plot twist. 📉 With us, pricing is 100% transparent. 🤝", "Your shopping app shouldn't crash. 🛒 Enjoy our buttery-smooth mobile experience! 📱✨"]
    }

# --- HELPER FUNCTIONS ---
def update_metrics(items=1, hours=2):
    st.session_state.metrics['generated'] += items
    st.session_state.metrics['time_saved_hours'] += hours
    st.session_state.dashboard_data.append({
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "items_generated": items,
        "hours_saved": hours
    })

def scrape_content(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        text = " ".join([p.get_text() for p in paragraphs])
        return text[:4000] if text else None
    except:
        return None

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #6C63FF;'>⚙️ Settings</h2>", unsafe_allow_html=True)
    gemini_key = st.text_input("🔑 Gemini API Key", type="password", value=os.getenv("GEMINI_API_KEY", ""))
    st.markdown("---")
    st.info("💡 **GrowthOS** automatically falls back to beautiful placeholder data if the API key is missing or invalid.")
    st.success("✅ 100% Powered by Google Gemini")

# --- MAIN APP HEADER ---
st.markdown('<div class="gradient-header">GROWTHOS</div>', unsafe_allow_html=True)
st.markdown('<div class="tagline">The Ultimate AI Marketing Suite</div>', unsafe_allow_html=True)

# Define Tabs
tab1, tab2, tab3, tab4 = st.tabs(["✍️ Content Repurposer", "🎯 Ad Studio", "🕵️ Competitor Intel", "📊 Unified Dashboard"])

# ----------------- MODULE 1: CONTENT REPURPOSER -----------------
with tab1:
    st.markdown("### ✍️ Repurpose any blog into a full social campaign")
    st.markdown("Convert a single article into dozens of high-quality social posts instantly.")
    
    input_text = ""
    if st.session_state.use_insights:
        st.success("💡 Pre-filled with insights from Competitor Intelligence!")
        input_text = st.session_state.insight_text
        
    c1, c2 = st.columns(2)
    with c1:
        url_input = st.text_input("🔗 Paste a Blog URL:")
    with c2:
        text_input = st.text_area("📝 OR Paste Article Text:", value=input_text, height=68)
    
    if st.button("🚀 Generate Campaign", type="primary", use_container_width=True):
        progress_text = "Scraping and analyzing content..."
        my_bar = st.progress(0, text=progress_text)
        
        content_to_process = ""
        if url_input:
            content_to_process = scrape_content(url_input)
            if not content_to_process:
                st.toast("Could not scrape URL. Please check the link.", icon="❌")
        elif text_input:
            content_to_process = text_input
            
        my_bar.progress(30, text="Generating with Gemini AI...")
        
        if content_to_process:
            if not gemini_key:
                st.toast("API Key missing. Using dummy data.", icon="⚠️")
                result = dummy_content()
                time.sleep(1.5)
            else:
                prompt = f'''
                You are a world-class AI marketing engineer. Repurpose this content into:
                1. 10 Twitter posts (<280 chars, viral hooks)
                2. 5 LinkedIn posts (professional, data-driven)
                3. 3 Instagram captions (with emojis, 15 hashtags each)
                4. 1 Newsletter (subject line + 200 word body)
                
                Return ONLY a valid JSON object without markdown formatting:
                {{
                    "twitter": ["...", "..."],
                    "linkedin": ["...", "..."],
                    "instagram": ["...", "..."],
                    "newsletter": {{"subject": "...", "body": "..."}}
                }}
                
                Content: {content_to_process[:4000]}
                '''
                res = call_gemini(prompt, gemini_key)
                result = res if res else dummy_content()
                if not res: st.toast("API Error, falling back to dummy data.", icon="⚠️")
            
            my_bar.progress(100, text="Done!")
            time.sleep(0.5)
            my_bar.empty()
            st.balloons()
            
            update_metrics(items=19, hours=5)
            st.session_state.ad_product_info = content_to_process[:500]
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 🐦 Twitter (10 Posts)")
                with st.container(height=500):
                    for t in result.get('twitter', []):
                        st.markdown(f'<div class="content-box">{t}</div>', unsafe_allow_html=True)
                    
                st.markdown("#### 📸 Instagram (3 Captions)")
                with st.container(height=400):
                    for i in result.get('instagram', []):
                        st.markdown(f'<div class="content-box border-pink">{i}</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### 💼 LinkedIn (5 Posts)")
                with st.container(height=500):
                    for l in result.get('linkedin', []):
                        st.markdown(f'<div class="content-box border-cyan">{l}</div>', unsafe_allow_html=True)
                    
                st.markdown("#### 📧 Newsletter")
                with st.container(height=400):
                    nl = result.get('newsletter', {})
                    st.markdown(f'<div class="content-box border-green"><b>Subject:</b> {nl.get("subject", "")}<br><br>{nl.get("body", "").replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
            
            st.markdown("---")
            if st.button("🚀 Push to Ad Studio (Pre-fill Context)", use_container_width=True):
                st.session_state.push_to_ad_studio = True
                st.rerun()

# ----------------- MODULE 2: AD STUDIO -----------------
with tab2:
    st.markdown("### 🎯 Generate High-Converting Ads & Landing Pages")
    st.markdown("Input your product details, or push them directly from the Content Repurposer.")
    
    prod_name = ""
    prod_desc = ""
    if st.session_state.push_to_ad_studio:
        st.success("💡 Pre-filled with context from Content Repurposer!")
        prod_name = "Imported Campaign"
        prod_desc = st.session_state.ad_product_info
        
    colA, colB = st.columns(2)
    with colA:
        p_name = st.text_input("🏷️ Product Name:", value=prod_name)
        p_audience = st.text_input("🎯 Target Audience:", value="Marketers, Founders")
    with colB:
        p_tone = st.selectbox("🎭 Tone:", ["Professional", "Casual", "Humor", "Urgent"])
        p_desc = st.text_area("📝 Description:", value=prod_desc)
        
    if st.button("🎨 Generate Ad Campaign", type="primary", use_container_width=True):
        with st.spinner("Crafting ads and coding landing page with Gemini..."):
            if not gemini_key:
                st.toast("API Key missing. Using dummy data.", icon="⚠️")
                ad_result = dummy_ads()
                time.sleep(1.5)
            else:
                prompt = f'''
                You are an elite performance marketer and web developer. Create ad copy and a COMPLETE HTML landing page.
                Product: {p_name}, Desc: {p_desc}, Audience: {p_audience}, Tone: {p_tone}
                
                Return ONLY valid JSON without markdown formatting:
                {{
                    "google_ads": ["5 headlines, max 30 chars"],
                    "facebook_ads": ["5 ad copies, ~125 chars with CTAs"],
                    "instagram_ads": ["3 visual descriptions with CTAs"],
                    "landing_page": "<!DOCTYPE html><html>...complete html/css code...</html>"
                }}
                
                HTML page must be self-contained, modern CSS, responsive, gradient buttons, hero section, 3 benefit cards with emojis, testimonials, countdown timer.
                '''
                res = call_gemini(prompt, gemini_key)
                ad_result = res if res else dummy_ads()
                if not res: st.toast("API Error, falling back to dummy data.", icon="⚠️")
            
            update_metrics(items=14, hours=8)
            st.balloons()
            st.toast("Ad Studio Generation Complete!", icon="✅")
            
            ac1, ac2, ac3 = st.columns(3)
            with ac1:
                st.markdown("#### 🔍 Google Ads")
                with st.container(height=400):
                    for g in ad_result.get('google_ads', []):
                        st.markdown(f'<div class="content-box">{g}</div>', unsafe_allow_html=True)
            with ac2:
                st.markdown("#### 📘 Facebook Ads")
                with st.container(height=400):
                    for f in ad_result.get('facebook_ads', []):
                        st.markdown(f'<div class="content-box border-cyan">{f}</div>', unsafe_allow_html=True)
            with ac3:
                st.markdown("#### 📸 Instagram Ads")
                with st.container(height=400):
                    for i in ad_result.get('instagram_ads', []):
                        st.markdown(f'<div class="content-box border-pink">{i}</div>', unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### 🌐 Live Landing Page Preview")
            html_code = ad_result.get('landing_page', '<h1>Error generating page</h1>')
            
            # Download button for HTML
            st.download_button("📥 Download HTML Source", data=html_code, file_name="landing_page.html", mime="text/html", use_container_width=True)
            
            components.html(html_code, height=600, scrolling=True)


# ----------------- MODULE 3: COMPETITOR INTEL -----------------
with tab3:
    st.markdown("### 🕵️ Extract Competitor Weaknesses")
    st.markdown("Analyze any brand to find their weak points and exploit them with better content.")
    
    c_col1, c_col2 = st.columns([3, 1])
    with c_col1:
        comp_brand = st.text_input("🔍 Competitor Brand Name or Twitter Handle:")
    
    if st.button("📊 Analyze Competitor", type="primary", use_container_width=True):
        if comp_brand:
            with st.spinner("Analyzing market sentiment and weaknesses with Gemini..."):
                if not gemini_key:
                    st.toast("API Key missing. Using dummy data.", icon="⚠️")
                    intel_result = dummy_intel()
                    time.sleep(1.5)
                else:
                    prompt = f'''
                    Analyze the competitor '{comp_brand}'.
                    Return ONLY a valid JSON object, NO markdown formatting:
                    {{
                        "complaints": ["Top 3 customer complaints"],
                        "topics": ["5 content topics countering these complaints"],
                        "positioning": "Competitive positioning statement",
                        "sentiment": {{"score": 50, "positive": 20, "neutral": 30, "negative": 50}},
                        "viral_tweets": ["3 viral tweet ideas targeting their audience"]
                    }}
                    '''
                    res = call_gemini(prompt, gemini_key)
                    intel_result = res if res else dummy_intel()
                    if not res: st.toast("API Error, falling back to dummy data.", icon="⚠️")
                
                update_metrics(items=1, hours=10)
                st.toast("Analysis Complete!", icon="✅")
                
                st.markdown(f"## 📉 Analysis for **{comp_brand}**")
                
                # Sentiment metrics
                scol1, scol2, scol3, scol4 = st.columns(4)
                sent = intel_result.get('sentiment', {})
                with scol1: st.markdown(f'<div class="saas-card"><h4 style="color:#888;">Overall Sentiment</h4><div class="metric-value">{sent.get("score", 0)}/100</div></div>', unsafe_allow_html=True)
                with scol2: st.markdown(f'<div class="saas-card"><h4 style="color:#888;">Positive</h4><div class="metric-value" style="color:var(--success); background:none; -webkit-text-fill-color:var(--success);">{sent.get("positive", 0)}%</div></div>', unsafe_allow_html=True)
                with scol3: st.markdown(f'<div class="saas-card"><h4 style="color:#888;">Neutral</h4><div class="metric-value" style="color:var(--accent); background:none; -webkit-text-fill-color:var(--accent);">{sent.get("neutral", 0)}%</div></div>', unsafe_allow_html=True)
                with scol4: st.markdown(f'<div class="saas-card"><h4 style="color:#888;">Negative (Opportunity)</h4><div class="metric-value" style="color:var(--secondary); background:none; -webkit-text-fill-color:var(--secondary);">{sent.get("negative", 0)}%</div></div>', unsafe_allow_html=True)
                
                ic1, ic2 = st.columns(2)
                with ic1:
                    st.markdown('### <span style="color:var(--secondary);">🚨 Top Complaints</span>', unsafe_allow_html=True)
                    with st.container(height=300):
                        for c in intel_result.get('complaints', []):
                            st.markdown(f'<div class="content-box border-pink">🚩 {c}</div>', unsafe_allow_html=True)
                        
                    st.markdown('### <span style="color:var(--success);">💡 Counter Topics</span>', unsafe_allow_html=True)
                    with st.container(height=300):
                        for t in intel_result.get('topics', []):
                            st.markdown(f'<div class="content-box border-green">✅ {t}</div>', unsafe_allow_html=True)
                        
                with ic2:
                    st.markdown('### <span style="color:var(--primary);">🎯 Positioning Statement</span>', unsafe_allow_html=True)
                    st.markdown(f'<div class="saas-card" style="font-size:1.1rem; border-left: 5px solid var(--primary);">{intel_result.get("positioning", "")}</div>', unsafe_allow_html=True)
                    
                    st.markdown('### <span style="color:var(--accent);">🦅 Viral Tweet Ideas</span>', unsafe_allow_html=True)
                    with st.container(height=400):
                        for vt in intel_result.get('viral_tweets', []):
                            st.markdown(f'<div class="content-box border-cyan">🐦 {vt}</div>', unsafe_allow_html=True)
                
                st.markdown("---")
                if st.button("♻️ Use Insights in Content Repurposer", use_container_width=True):
                    st.session_state.use_insights = True
                    topics_text = chr(10).join(intel_result.get('topics', []))
                    st.session_state.insight_text = f"We need to write content focusing on these topics to beat {comp_brand}:\\n{topics_text}"
                    st.rerun()


# ----------------- MODULE 4: UNIFIED DASHBOARD -----------------
with tab4:
    st.markdown("### 📊 Marketing ROI Calculator & Dashboard")
    st.markdown("Track your output and calculate the exact monetary value of the time saved by GrowthOS.")
    
    st.markdown('<div class="saas-card">', unsafe_allow_html=True)
    dcol1, dcol2 = st.columns(2)
    with dcol1:
        team_size = st.slider("👥 Marketing Team Size", 1, 50, 5)
    with dcol2:
        monthly_salary = st.number_input("💵 Average Monthly Salary per Marketer (₹)", value=50000)
    st.markdown('</div>', unsafe_allow_html=True)
    
    hourly_rate = monthly_salary / (4 * 40) # Assuming 4 weeks, 40 hrs
    roi = st.session_state.metrics['time_saved_hours'] * hourly_rate * team_size
    st.session_state.metrics['roi_inr'] = round(roi, 2)
    
    mc1, mc2, mc3 = st.columns(3)
    with mc1:
        st.markdown('<div class="saas-card"><h4 style="color:#888;">📝 Total Content Generated</h4><div class="metric-value">{}</div></div>'.format(st.session_state.metrics['generated']), unsafe_allow_html=True)
    with mc2:
        st.markdown('<div class="saas-card"><h4 style="color:#888;">⏱️ Time Saved (Hours)</h4><div class="metric-value">{}</div></div>'.format(st.session_state.metrics['time_saved_hours']), unsafe_allow_html=True)
    with mc3:
        st.markdown('<div class="saas-card"><h4 style="color:#888;">💰 Estimated ROI Saved</h4><div class="metric-value">₹{:,}</div></div>'.format(st.session_state.metrics['roi_inr']), unsafe_allow_html=True)
        
    st.markdown("---")
    
    if st.session_state.dashboard_data:
        st.markdown("### 📜 Generation History")
        df = pd.DataFrame(st.session_state.dashboard_data)
        st.dataframe(df, use_container_width=True)
        
        json_str = json.dumps(st.session_state.dashboard_data, indent=2)
        st.download_button(
            label="⬇️ Export Data as JSON",
            data=json_str,
            file_name="growthos_export.json",
            mime="application/json",
            use_container_width=True
        )
    else:
        st.info("No content generated yet. Use the other tabs to start saving time and money!")
