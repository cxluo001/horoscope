from __future__ import annotations
import base64
import os
import random
import time
from datetime import datetime
from pathlib import Path

import streamlit as st

# =============================
# ----- Config & Constants -----
# =============================

st.set_page_config(
    page_title="Sustainable Public Procurement Horoscope",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

ZODIAC_ORDER = [
    "aries", "taurus", "gemini", "cancer", "leo", "virgo",
    "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces",
]

ZODIAC_EMOJI = {
    "aries": "♈️", "taurus": "♉️", "gemini": "♊️", "cancer": "♋️",
    "leo": "♌️", "virgo": "♍️", "libra": "♎️", "scorpio": "♏️",
    "sagittarius": "♐️", "capricorn": "♑️", "aquarius": "♒️", "pisces": "♓️",
}

ZODIAC_DISPLAY_NAMES = {
    "aries": "Aries", "taurus": "Taurus", "gemini": "Gemini", "cancer": "Cancer",
    "leo": "Leo", "virgo": "Virgo", "libra": "Libra", "scorpio": "Scorpio",
    "sagittarius": "Sagittarius", "capricorn": "Capricorn", "aquarius": "Aquarius", "pisces": "Pisces",
}

# Dictionary of zodiac sources
ZODIAC_SOURCES = {
    "virgo": "https://www.wgea.org/news-events/un-acknowledges-the-role-of-supreme-audit-institutions-in-environmental-sustainability/?utm",
    "libra": "https://procurementmag.com/news/albania-ai-procurement-minister",
    "scorpio": "https://www.un.org/en/energy/page/Plan-of-Action-Towards-2025",
    "sagittarius": "https://www.worldbank.org/en/news/press-release/2025/07/18/world-bank-group-strengthens-procurement-requirements-to-support-job-creation-skills-development?utm_source=chatgpt.com",
    "capricorn": "https://www.unido.org/news/unido-development-dialogue-advances-global-efforts-productive-resilient-and-sustainable-supply-chains?utm_source=chatgpt.com",
    "aquarius": "https://www.adb.org/news/adb-gsa-sign-deal-open-green-data-center-thailand",
    "pisces": "https://bb-reg-net.org.uk/wp-content/uploads/2025/09/BB-REG-NET-Procurement-Paper.pdf",
    "aries": "https://circularandfairictpact.com/news/new-manual-available-promoting-due-diligence/",
    "taurus": "https://www.ucl.ac.uk/bartlett/publications/2025/sep/mission-oriented-approach-school-meals",
    "gemini": "https://ghgprotocol.org/blog/release-iso-and-ghg-protocol-announce-strategic-partnership-deliver-unified-global-standards",
    "cancer": "https://www.who.int/news/item/19-08-2025-theories-of-change-can-anchor-our-collective-efforts-and-trigger-real-change-in-people-s-lives",
    "leo": "https://smartfreightcentre.org/en/about-sfc/news/smart-freight-centre-publishes-guide-to-unlocking-sustainable-aviation-fuel-for-cargo-decarbonization/"
}

DEFAULT_FOLDER = "."

# Enhanced CSS with mobile-first design
MOBILE_FRIENDLY_CSS = """
<style>
/***** Hide sidebar completely *****/
[data-testid="stSidebar"] {
    display: none !important;
}

/***** Main content full width *****/
[data-testid="stAppViewContainer"] > div {
    padding: 0.5rem !important;
    width: 100% !important;
    max-width: 100% !important;
}
[data-testid="stAppViewContainer"] > div > div {
    max-width: none;
}

/***** Page background *****/
[data-testid="stAppViewContainer"] {
  background: radial-gradient(1200px 600px at 10% 10%, rgba(255,255,255,0.08), rgba(0,0,0,0) 60%),
              radial-gradient(800px 400px at 90% 20%, rgba(255,255,255,0.06), rgba(0,0,0,0) 60%),
              linear-gradient(180deg, #0b1020 0%, #0a0f1a 100%);
  color: #e7e9ef;
}

/***** Clean header styling *****/
.header-glass {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  box-shadow: 0 5px 15px rgba(0,0,0,0.2);
  border-radius: 15px;
  padding: 1rem;
  margin-bottom: 1rem;
  text-align: center;
}

h1, h2, h3 { color: #f6f7fb; text-align: center; }
.small { opacity: 0.8; font-size: 0.9rem; text-align: center; }
.kicker { letter-spacing: .2em; text-transform: uppercase; opacity: .7; font-size: .8rem; text-align: center; }

/***** Buttons - LARGER FOR MOBILE *****/
.stButton>button {
  border-radius: 999px;
  padding: 1rem 1.5rem !important;
  border: 1px solid rgba(255,255,255,.15);
  background: linear-gradient(180deg, rgba(255,255,255,.08), rgba(255,255,255,.04));
  font-size: 1.1rem !important;
  min-height: 50px;
  margin: 0.5rem 0;
}

/***** Landing page button styling *****/
.landing-button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border: none !important;
    font-size: 1.3rem !important;
    font-weight: bold !important;
    padding: 1.2rem 2rem !important;
    margin: 1rem 0;
}

/***** Footer button styling *****/
.footer-button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border: none !important;
    font-size: 1.1rem !important;
    padding: 0.8rem 1.8rem !important;
    margin: 1rem 0;
}

/***** Zodiac Selection Grid *****/
.zodiac-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin: 1.5rem 0;
    padding: 0 10px;
}

.zodiac-option {
    background: rgba(255,255,255,0.1);
    border: 2px solid rgba(255,255,255,0.2);
    border-radius: 15px;
    padding: 15px 10px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    min-height: 80px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.zodiac-option:hover {
    background: rgba(255,255,255,0.2);
    transform: scale(1.05);
}

.zodiac-option.selected {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-color: rgba(255,255,255,0.4);
    transform: scale(1.05);
}

.zodiac-emoji {
    font-size: 2rem;
    margin-bottom: 5px;
}

.zodiac-name {
    font-size: 0.9rem;
    font-weight: bold;
}

/***** Navigation Arrows - VERTICAL STACK FOR MOBILE *****/
.mobile-nav {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    margin: 1rem 0;
}

.nav-arrow {
    font-size: 2rem;
    background: rgba(255,255,255,0.1);
    border: 2px solid rgba(255,255,255,0.2);
    border-radius: 50%;
    width: 60px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s ease;
}

.nav-arrow:hover {
    background: rgba(255,255,255,0.2);
    transform: scale(1.1);
}

/***** Current Selection Display *****/
.current-selection {
    text-align: center;
    padding: 1rem;
    background: rgba(255,255,255,0.1);
    border-radius: 15px;
    border: 2px solid rgba(255,255,255,0.3);
    margin: 1rem 0;
}

/***** Image styling - MOBILE OPTIMIZED *****/
.horoscope-image-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  margin: 1rem 0;
}

.horoscope-image {
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,.12);
  box-shadow: 0 8px 25px rgba(0,0,0,0.3);
  width: 100% !important;
  max-width: 100% !important;
}

/***** Landing page image styling *****/
.landing-image-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  margin: 1.5rem 0;
}

.landing-image {
  border-radius: 15px;
  overflow: hidden;
  border: 2px solid rgba(255,255,255,.2);
  box-shadow: 0 10px 25px rgba(0,0,0,0.3);
  width: 100% !important;
  max-width: 100% !important;
}

/***** End page image styling *****/
.end-image-container {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    margin: 1.5rem 0;
}

.end-image {
    border-radius: 15px;
    overflow: hidden;
    border: 2px solid rgba(255,255,255,.2);
    box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    width: 100% !important;
    max-width: 100% !important;
}

/***** Footer *****/
.footer { 
    text-align: center; 
    opacity: .65; 
    font-size: .85rem; 
    margin-top: 2rem;
    padding: 1rem;
    background: rgba(255,255,255,0.05);
    border-radius: 15px;
    border: 1px solid rgba(255,255,255,0.1);
}

/***** Content panel styling *****/
.content-panel {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 15px;
    padding: 1rem;
    margin: 1rem 0;
}

/***** Landing page container *****/
.landing-container {
    text-align: center;
    padding: 1.5rem 1rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

/***** Landing page title *****/
.landing-title {
    font-size: 2rem;
    font-weight: bold;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1rem;
    text-align: center;
}

/***** Landing page subtitle *****/
.landing-subtitle {
    font-size: 1.1rem;
    opacity: 0.9;
    margin-bottom: 1.5rem;
    text-align: center;
}

/***** Source link styling *****/
.source-link {
    background: rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 1rem;
    margin: 1rem 0;
    border: 1px solid rgba(255,255,255,0.1);
    text-align: center;
    width: 100%;
}

.source-link a {
    color: #a3d9ff;
    text-decoration: none;
    font-size: 0.9rem;
    word-break: break-word;
    text-align: center;
}

.source-link a:hover {
    text-decoration: underline;
    color: #7ac6ff;
}

/***** Desktop-specific styles *****/
@media (min-width: 768px) {
    .zodiac-grid {
        grid-template-columns: repeat(4, 1fr);
        gap: 15px;
    }
    
    .mobile-nav {
        flex-direction: row;
        justify-content: center;
        gap: 20px;
    }
    
    .horoscope-image {
        width: 80% !important;
        max-width: 80% !important;
    }
    
    .landing-image {
        width: 70% !important;
        max-width: 70% !important;
    }
    
    .end-image {
        width: 70% !important;
        max-width: 70% !important;
    }
}

@media (min-width: 1024px) {
    .zodiac-grid {
        grid-template-columns: repeat(6, 1fr);
    }
    
    [data-testid="stAppViewContainer"] > div {
        padding: 1rem 2rem !important;
    }
}
</style>
"""

st.markdown(MOBILE_FRIENDLY_CSS, unsafe_allow_html=True)

# =============================
# ----- Utilities -----
# =============================

def discover_images(folder: str | os.PathLike) -> dict[str, Path]:
    """Return a dict mapping zodiac -> Image Path if found in folder.
    Supports JPG, JPEG, PNG, WEBP formats.
    """
    folder_path = Path(folder)
    found = {}
    if not folder_path.exists():
        return found
    
    # Support multiple image formats
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.webp']
    for ext in image_extensions:
        for p in folder_path.glob(ext):
            name = p.stem.lower().strip()
            if name in ZODIAC_ORDER:
                found[name] = p
    return found

def display_image(path: Path):
    """Display horoscope image with proper formatting and centering"""
    try:
        # Display the image with responsive sizing
        st.markdown('<div class="horoscope-image-container">', unsafe_allow_html=True)
        st.image(
            str(path),
            use_container_width=True,
            output_format="auto"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Add some decorative elements
        st.markdown("---")
        st.markdown(
            f'<div style="text-align: center; opacity: 0.8; font-style: italic;">'
            f'✨ The stars have spoken for {path.stem.title()}... ✨'
            f'</div>',
            unsafe_allow_html=True
        )
        
        # Display the source link for this zodiac sign
        zodiac_name = path.stem.lower().strip()
        if zodiac_name in ZODIAC_SOURCES:
            source_url = ZODIAC_SOURCES[zodiac_name]
            st.markdown(
                f'<div class="source-link">'
                f'<div style="font-size: 0.9rem; opacity: 0.8; margin-bottom: 0.5rem;">Learn more about sustainable procurement:</div>'
                f'<a href="{source_url}" target="_blank">{source_url}</a>'
                f'</div>',
                unsafe_allow_html=True
            )
        
    except Exception as e:
        st.error(f"Couldn't display image: {e}")
        st.info("Make sure your image file is a supported format (JPG, PNG, WEBP)")

# =============================
# ----- Mobile-Friendly Zodiac Selector -----
# =============================

def create_zodiac_selector():
    """Create a mobile-friendly zodiac selector with grid layout"""
    st.markdown("### 🌟 Select Your Zodiac Sign")
    
    # Create a grid of zodiac options
    st.markdown('<div class="zodiac-grid">', unsafe_allow_html=True)
    
    for zodiac in ZODIAC_ORDER:
        is_selected = st.session_state["picked_sign"] == zodiac
        selection_class = "selected" if is_selected else ""
        
        # Use columns to create a grid-like layout
        if st.button(
            f"{ZODIAC_EMOJI[zodiac]}\n{ZODIAC_DISPLAY_NAMES[zodiac]}",
            key=f"zodiac_{zodiac}",
            use_container_width=True
        ):
            st.session_state["picked_sign"] = zodiac
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Add navigation arrows for easier browsing
    current_idx = ZODIAC_ORDER.index(st.session_state["picked_sign"])
    
    st.markdown('<div class="mobile-nav">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("◀", key="prev", use_container_width=True):
            prev_idx = (current_idx - 1) % len(ZODIAC_ORDER)
            st.session_state["picked_sign"] = ZODIAC_ORDER[prev_idx]
            st.rerun()
    
    with col2:
        # Show current selection
        current_zodiac = st.session_state["picked_sign"]
        st.markdown(
            f'<div class="current-selection">'
            f'<div style="font-size: 2rem;">{ZODIAC_EMOJI[current_zodiac]}</div>'
            f'<div style="font-size: 1.3rem; font-weight: bold; color: white;">'
            f'{ZODIAC_DISPLAY_NAMES[current_zodiac]}'
            f'</div></div>',
            unsafe_allow_html=True
        )
    
    with col3:
        if st.button("▶", key="next", use_container_width=True):
            next_idx = (current_idx + 1) % len(ZODIAC_ORDER)
            st.session_state["picked_sign"] = ZODIAC_ORDER[next_idx]
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# =============================
# ----- End Image Page -----
# =============================

def show_end_image_page():
    """Display the end image on a separate page"""
    st.markdown("""
    <div class='landing-container'>
        <div class='landing-title'>✨ Sustainable Public Procurement Message ✨</div>
        <div class='landing-subtitle'>A special message from the stars</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display end image
    end_path = Path(DEFAULT_FOLDER) / "end.jpeg"
    if end_path.exists():
        st.markdown('<div class="end-image-container">', unsafe_allow_html=True)
        st.image(
            str(end_path),
            use_container_width=True,
            output_format="auto",
            caption="A special message for sustainable procurement 🌱"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("End image 'end.jpeg' not found in the folder.")
    
    # Add a button to return to the main game
    if st.button(
        "🔙 Return to Horoscope",
        key="return_button",
        use_container_width=True
    ):
        st.session_state["show_end_image"] = False
        st.rerun()

# =============================
# ----- Landing Page -----
# =============================

def show_landing_page():
    """Display the landing page with intro image and entry button"""
    st.markdown("""
    <div class='landing-container'>
        <div class='landing-title'>✨ Sustainable Public Procurement Horoscope ✨</div>
        <div class='landing-subtitle'>Discover what the stars have in store for you</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add the enter button
    if st.button(
        "🚀 Enter the Horoscope Realm",
        key="enter_button",
        use_container_width=True
    ):
        st.session_state["game_started"] = True
        st.session_state["show_end_image"] = False
        st.rerun()
    
    # Display intro image
    intro_path = Path(DEFAULT_FOLDER) / "intro.jpeg"
    if intro_path.exists():
        st.markdown('<div class="landing-image-container">', unsafe_allow_html=True)
        st.image(
            str(intro_path),
            use_container_width=True,
            output_format="auto",
            caption="Welcome to your sustainable journey 🌱"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("Intro image 'intro.jpeg' not found. Please add it for the best experience.")

# =============================
# ----- Main Game Page -----
# =============================

def show_main_game():
    """Display the main horoscope game"""
    # Main header
    st.markdown("""
    <div class='header-glass'>
      <div class='kicker'>Sustainable Public Procurement Horoscope</div>
      <h2>🔮 Your Zodiac Reading</h2>
      <div class='small'>Select your sign to discover your destiny</div>
    </div>
    """, unsafe_allow_html=True)

    # Date display
    now = datetime.now().strftime("%b %d, %Y")
    st.markdown(
        f"<div style='text-align: center; opacity: 0.8; margin-bottom: 1rem;'>Today: {now}</div>",
        unsafe_allow_html=True,
    )

    # SourcingHaus button
    if st.button(
        "📖 Learn more about SourcingHaus",
        key="learn_more_button",
        use_container_width=True
    ):
        st.session_state["show_end_image"] = True
        st.rerun()

    # Zodiac Selection
    create_zodiac_selector()

    # Content area
    st.markdown("<div class='content-panel'>", unsafe_allow_html=True)

    choice = st.session_state["picked_sign"]
    path = found.get(choice)

    if path and path.exists():
        display_image(path)
    else:
        st.markdown("### 🖼️ Your horoscope will appear here")
        st.caption("Add the image file and pick your sign to begin ✨")
        st.markdown('<div class="horoscope-image-container">', unsafe_allow_html=True)
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Zodiac_Clock_-_detail.jpg/640px-Zodiac_Clock_-_detail.jpg",
            use_container_width=True,
            caption="(Placeholder image loaded from Wikipedia)",
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display source link even if no image is found
        if choice in ZODIAC_SOURCES:
            source_url = ZODIAC_SOURCES[choice]
            st.markdown(
                f'<div class="source-link">'
                f'<div style="font-size: 0.9rem; opacity: 0.8; margin-bottom: 0.5rem;">Learn more about sustainable procurement:</div>'
                f'<a href="{source_url}" target="_blank">{source_url}</a>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.markdown("</div>", unsafe_allow_html=True)  # Close content-panel

    # Footer
    st.markdown('<div class="footer">', unsafe_allow_html=True)
    st.markdown("Discover your sustainable procurement destiny through the stars ✨")
    st.markdown('</div>', unsafe_allow_html=True)

    # Little end-of-page sparkle
    if random.random() < 0.08:
        st.snow()

# =============================
# ----- Main App -----
# =============================

# Initialize session state
if "game_started" not in st.session_state:
    st.session_state["game_started"] = False

if "picked_sign" not in st.session_state:
    st.session_state["picked_sign"] = "aries"

if "show_end_image" not in st.session_state:
    st.session_state["show_end_image"] = False

# Discover images in default folder
found = discover_images(DEFAULT_FOLDER)

# Show appropriate page based on game state
if not st.session_state["game_started"]:
    show_landing_page()
elif st.session_state["show_end_image"]:
    show_end_image_page()
else:
    show_main_game()
