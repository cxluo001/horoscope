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

# Dictionary of zodiac sources
ZODIAC_SOURCES = {
    "virgo": "https://www.oecd.org/en/publications/government-at-a-glance-2025_0efd0bcd-en/full-report/green-public-procurement_5dbf73a9.html#indicator-d1e19503-94cb3dc3a1",
    "libra": "https://www.wto.org/english/news_e/news25_e/gpro_18jun25_e.htm?utm",
    "scorpio": "https://www.irena.org/Energy-Transition/Innovation/Offshore-Renewables",
    "sagittarius": "https://www.eib.org/en/press/all/2025-177-cities-across-europe-plan-to-bolster-climate-action-and-social-infrastructure-eib-survey-shows?utm",
    "capricorn": "https://decarbonization.unido.org/resources/harmonizing-reporting-for-green-public-procurement-and-green-building-programs-using-ecolabels-epds/",
    "aquarius": "https://www.adb.org/news/adb-gsa-sign-deal-open-green-data-center-thailand",
    "pisces": "https://environment.ec.europa.eu/news/commission-launches-consultation-upcoming-circular-economy-act-2025-08-01_en",
    "aries": "https://www.worldbank.org/en/news/press-release/2025/08/05/mobilizing-access-to-the-digital-economy-alliance-africa?utm",
    "taurus": "https://www.fao.org/americas/news/news-detail/programa-alimentacion-escolar/en?utm",
    "gemini": "https://www.unops.org/news-and-stories/news/unlocking-the-power-of-public-procurement?utm",
    "cancer": "https://www.who.int/news/item/26-07-2025-who-expands-guidance-on-sexually-transmitted-infections-and-reviews-country-progress-on-policy-implementation",
    "leo": "https://energy.ec.europa.eu/topics/energy-security/eu-energy-and-raw-materials-platform_en"
}

DEFAULT_FOLDER = "."

# Enhanced CSS with better centering and responsiveness
STARFIELD_CSS = """
<style>
/***** Hide sidebar completely *****/
[data-testid="stSidebar"] {
    display: none !important;
}

/***** Main content full width *****/
[data-testid="stAppViewContainer"] > div {
    padding-left: 1rem;
    padding-right: 1rem;
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
  box-shadow: 0 10px 30px rgba(0,0,0,0.25);
  border-radius: 20px;
  padding: 1.2rem 1.1rem;
  margin-bottom: 1rem;
}

h1, h2, h3 { color: #f6f7fb; }
.small { opacity: 0.8; font-size: 0.9rem; }
.kicker { letter-spacing: .2em; text-transform: uppercase; opacity: .7; font-size: .8rem; }

/***** Buttons *****/
.stButton>button {
  border-radius: 999px;
  padding: .6rem 1rem;
  border: 1px solid rgba(255,255,255,.15);
  background: linear-gradient(180deg, rgba(255,255,255,.08), rgba(255,255,255,.04));
}

/***** Landing page button styling *****/
.landing-button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border: none !important;
    font-size: 1.2rem !important;
    font-weight: bold !important;
    padding: 1rem 2rem !important;
    margin-top: 2rem;
}

/***** Footer button styling *****/
.footer-button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border: none !important;
    font-size: 1rem !important;
    padding: 0.5rem 1.5rem !important;
    margin-top: 1rem;
}

/***** SourcingHaus button styling *****/
.sourcinghaus-button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border: none !important;
    font-size: 1rem !important;
    padding: 0.5rem 1.5rem !important;
    margin: 1rem 0;
}

/***** Scroll Selector Styles - UPDATED FOR VERTICAL ALIGNMENT *****/
.scroll-selector {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    margin: 2rem 0;
}

.scroll-arrow {
    font-size: 24px;
    background: rgba(255,255,255,0.1);
    border: 2px solid rgba(255,255,255,0.2);
    border-radius: 50%;
    width: 50px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s ease;
}

.scroll-arrow:hover {
    background: rgba(255,255,255,0.2);
    transform: scale(1.1);
}

.current-zodiac {
    text-align: center;
    padding: 1.5rem;
    background: rgba(255,255,255,0.1);
    border-radius: 20px;
    border: 2px solid rgba(255,255,255,0.3);
    min-width: 150px;
    margin: 0 1rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

/***** Arrow container for vertical alignment *****/
.arrow-container {
    display: flex;
    align-items: center;
    height: 100%;
}

/***** Image styling - UPDATED FOR RESPONSIVE SIZING *****/
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
  /* Responsive width - 50% on desktop, 80% on mobile */
  width: 50% !important;
  max-width: 50% !important;
  margin: 0 auto;
}

@media (max-width: 767px) {
    .horoscope-image {
        width: 80% !important;
        max-width: 80% !important;
    }
}

/***** Landing page image styling - UPDATED FOR RESPONSIVE SIZING *****/
.landing-image-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  margin: 2rem 0;
}

.landing-image {
  border-radius: 20px;
  overflow: hidden;
  border: 2px solid rgba(255,255,255,.2);
  box-shadow: 0 15px 35px rgba(0,0,0,0.4);
  /* Responsive width - 50% on desktop, 80% on mobile */
  width: 50% !important;
  max-width: 50% !important;
  margin: 0 auto;
}

@media (max-width: 767px) {
    .landing-image {
        width: 80% !important;
        max-width: 80% !important;
    }
}

/***** End page image styling - UPDATED FOR RESPONSIVE SIZING *****/
.end-image-container {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    margin: 2rem 0;
}

.end-image {
    border-radius: 20px;
    overflow: hidden;
    border: 2px solid rgba(255,255,255,.2);
    box-shadow: 0 15px 35px rgba(0,0,0,0.4);
    /* Responsive width - 50% on desktop, 80% on mobile */
    width: 50% !important;
    max-width: 50% !important;
    margin: 0 auto;
}

@media (max-width: 767px) {
    .end-image {
        width: 80% !important;
        max-width: 80% !important;
    }
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
    border-radius: 20px;
    padding: 1.5rem;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
}

/***** Landing page container *****/
.landing-container {
    text-align: center;
    padding: 3rem 2rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

/***** Landing page title *****/
.landing-title {
    font-size: 2.5rem;
    font-weight: bold;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1rem;
    text-align: center;
}

@media (max-width: 767px) {
    .landing-title {
        font-size: 2rem;
    }
}

/***** Landing page subtitle *****/
.landing-subtitle {
    font-size: 1.2rem;
    opacity: 0.9;
    margin-bottom: 2rem;
    text-align: center;
}

@media (max-width: 767px) {
    .landing-subtitle {
        font-size: 1rem;
    }
}

/***** Center container for columns *****/
.center-container {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
}

/***** Source link styling - CENTERED *****/
.source-link {
    background: rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 1rem;
    margin: 1rem auto;
    border: 1px solid rgba(255,255,255,0.1);
    text-align: center;
    width: 80%;
    max-width: 600px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.source-link a {
    color: #a3d9ff;
    text-decoration: none;
    font-size: 0.9rem;
    word-break: break-all;
    text-align: center;
}

.source-link a:hover {
    text-decoration: underline;
    color: #7ac6ff;
}
</style>
"""

st.markdown(STARFIELD_CSS, unsafe_allow_html=True)

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
# ----- Simple Scroll Selector -----
# =============================

def create_scroll_selector():
    """Create a simple scroll-like selector"""
    st.markdown("### 🌟 Select Your Zodiac")
    
    # Current selection display
    current_idx = ZODIAC_ORDER.index(st.session_state["picked_sign"])
    
    # Show scroll selector with proper vertical alignment
    st.markdown('<div class="center-container">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    st.markdown('</div>', unsafe_allow_html=True)
    
    with col1:
        # Use a container to center the button vertically
        st.markdown('<div class="arrow-container">', unsafe_allow_html=True)
        if st.button("◀", key="prev", use_container_width=True):
            prev_idx = (current_idx - 1) % len(ZODIAC_ORDER)
            st.session_state["picked_sign"] = ZODIAC_ORDER[prev_idx]
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="current-zodiac">
            <div style="font-size: 2.5rem;">{ZODIAC_EMOJI[st.session_state['picked_sign']]}</div>
            <div style="font-size: 1.2rem; font-weight: bold; color: white;">
                {st.session_state['picked_sign'].title()}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Use a container to center the button vertically
        st.markdown('<div class="arrow-container">', unsafe_allow_html=True)
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
    st.markdown('<div class="center-container">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "🔙 Return to Horoscope",
            key="return_button",
            use_container_width=True
        ):
            st.session_state["show_end_image"] = False
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

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
    
    # Add the enter button above the image
    st.markdown('<div class="center-container">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "🚀 Enter the Horoscope Realm",
            key="enter_button",
            use_container_width=True
        ):
            st.session_state["game_started"] = True
            st.session_state["show_end_image"] = False
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display intro image with responsive sizing and centering
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
        st.warning("Intro image 'intro.jpeg' not found in the folder. Please add it for the best experience.")
        st.info("The intro image should be named 'intro.jpeg' and placed in the same folder as your zodiac images.")

# =============================
# ----- Main Game Page -----
# =============================

def show_main_game():
    """Display the main horoscope game"""
    # Main header
    col_title, col_info = st.columns([0.7, 0.3])
    with col_title:
        st.markdown("""
        <div class='header-glass'>
          <div class='kicker'>Sustainable Public Procurement Horoscope</div>
          <h1>🔮 Zodiac Wheel</h1>
          <div class='small'>Spin through the stars to discover your destiny</div>
        </div>
        """, unsafe_allow_html=True)

    with col_info:
        now = datetime.now().strftime("%b %d, %Y")
        st.markdown(
            f"<div class='header-glass'><div class='kicker'>Today</div><h3>{now}</h3><div class='small'>May the stars be ever in your favor ✨</div></div>",
            unsafe_allow_html=True,
        )

    # Add the SourcingHaus button at the top
    st.markdown('<div class="center-container">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "📖 Click here to learn more about SourcingHaus",
            key="learn_more_button",
            use_container_width=True
        ):
            st.session_state["show_end_image"] = True
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Zodiac Selection
    create_scroll_selector()

    # Content area - Simplified single column layout
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