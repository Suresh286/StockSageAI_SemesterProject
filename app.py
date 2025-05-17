import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from scipy import stats
from plotly.subplots import make_subplots
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (mean_squared_error, r2_score, accuracy_score, 
                           mean_absolute_error, confusion_matrix, 
                           precision_score, recall_score, f1_score,
                           silhouette_score)
import plotly.express as px
import io
import requests
import time
import logging
import base64
from typing import Optional, Dict, Any

# Configure yfinance logging
logging.getLogger('yfinance').setLevel(logging.ERROR)

# Theme configurations
THEMES = {
    'zombie': {
        'name': 'Zombie Theme',
        'colors': {
            'primary': '#4CAF50',      # Sickly Green
            'secondary': '#8B0000',    # Dark Red
            'accent': '#FF4500',       # Blood Orange
            'background': '#1A1A1A',   # Dark Background
            'surface': '#2D2D2D',      # Slightly Lighter Dark
            'card': '#3D3D3D',         # Card Background
            'text': '#E0E0E0',         # Light Text
            'text_secondary': '#A0A0A0', # Secondary Text
            'error': '#FF0000',        # Blood Red
            'success': '#00FF00',      # Toxic Green
            'warning': '#FFA500'       # Warning Orange
        },
        'font': 'Creepster',
        'animation': 'zombie_walk.gif'  # Placeholder for GIF
    },
    'futuristic': {
        'name': 'Futuristic Theme',
        'colors': {
            'primary': '#00FFFF',      # Cyan
            'secondary': '#FF00FF',    # Magenta
            'accent': '#00FF00',       # Neon Green
            'background': '#000033',   # Deep Space Blue
            'surface': '#000066',      # Space Blue
            'card': '#000099',         # Card Blue
            'text': '#FFFFFF',         # White
            'text_secondary': '#CCCCFF', # Light Blue Text
            'error': '#FF0000',        # Red
            'success': '#00FF00',      # Green
            'warning': '#FFFF00'       # Yellow
        },
        'font': 'Orbitron',
        'animation': 'space_animation.gif'  # Placeholder for GIF
    },
    'got': {
        'name': 'Game of Thrones Theme',
        'colors': {
            'primary': '#8B0000',      # Stark Red
            'secondary': '#000080',    # Lannister Gold
            'accent': '#006400',       # Forest Green
            'background': '#2F4F4F',   # Dark Slate
            'surface': '#3F5F5F',      # Lighter Slate
            'card': '#4F6F6F',         # Card Slate
            'text': '#F5F5DC',         # Beige
            'text_secondary': '#D2B48C', # Tan
            'error': '#8B0000',        # Dark Red
            'success': '#006400',      # Dark Green
            'warning': '#DAA520'       # Goldenrod
        },
        'font': 'MedievalSharp',
        'animation': 'fire_and_ice.gif'  # Placeholder for GIF
    },
    'gaming': {
        'name': 'Gaming Theme',
        'colors': {
            'primary': '#FF00FF',      # Hot Pink
            'secondary': '#00FFFF',    # Cyan
            'accent': '#FFFF00',       # Yellow
            'background': '#000000',   # Black
            'surface': '#1A1A1A',      # Dark Gray
            'card': '#2D2D2D',         # Card Gray
            'text': '#FFFFFF',         # White
            'text_secondary': '#FF00FF', # Pink Text
            'error': '#FF0000',        # Red
            'success': '#00FF00',      # Green
            'warning': '#FFA500'       # Orange
        },
        'font': 'Press Start 2P',
        'animation': 'pixel_art.gif'  # Placeholder for GIF
    }
}

# Initialize session state for theme if not exists
if 'current_theme' not in st.session_state:
    st.session_state['current_theme'] = 'futuristic'  # Default theme

def get_current_theme():
    """Get the current theme configuration"""
    return THEMES[st.session_state['current_theme']]

def apply_theme():
    """Apply the current theme to the app"""
    theme = get_current_theme()
    
    # For zombie theme, add background image using base64 encoding
    if theme['name'] == 'Zombie Theme':
        try:
            # Use the root directory GIF as background
            encoded_image = get_base64_of_bin_file("zombie_header.gif")
            # Add background image
            st.markdown(f"""
                <style>
                .stApp {{
                    background-image: url('data:image/gif;base64,{encoded_image}');
                    background-size: cover;
                    background-position: center;
                    background-attachment: fixed;
                }}
                </style>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error loading background image: {str(e)}")
    
    # Apply custom CSS
    st.markdown(f"""
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family={theme["font"].replace(" ", "+")}&display=swap');
        /* Main app styling */
        .stApp {{
            background-color: {theme['colors']['background']};
            color: {theme['colors']['text']};
            font-family: '{theme["font"]}', sans-serif;
            {f'background-image: url("assets/gifs/zombie_header.gif"); background-size: cover; background-attachment: fixed; background-position: center;' if theme['name'] == 'Zombie Theme' else ''}
        }}
        /* Add overlay for zombie theme to ensure text readability */
        {f'''
        .stApp::before {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.7);
            z-index: -1;
            pointer-events: none;
        }}
        ''' if theme['name'] == 'Zombie Theme' else ''}
        
        /* Ensure content is above the background */
        .main .block-container {{
            position: relative;
            z-index: 1;
            {f'background-color: rgba(26, 26, 26, 0.8);' if theme['name'] == 'Zombie Theme' else ''}
        }}
        
        /* Sidebar styling */
        .css-1d391kg {{
            background-color: {theme['colors']['surface']};
            border-right: 1px solid {theme['colors']['primary']}33;
            {f'background-color: rgba(45, 45, 45, 0.9);' if theme['name'] == 'Zombie Theme' else ''}
            position: relative;
            z-index: 2;
        }}
        
        /* All buttons styling */
        .stButton>button, button {{
            width: 100%;
            padding: 0.75rem 1.5rem;
            margin-bottom: 0.75rem;
            border: none;
            border-radius: 8px;
            background: linear-gradient(45deg, {theme['colors']['primary']}, {theme['colors']['primary']}dd);
            color: {theme['colors']['text']};
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            font-family: '{theme["font"]}', sans-serif;
            {f'background: linear-gradient(45deg, #4CAF50, #8B0000);' if theme['name'] == 'Zombie Theme' else ''}
        }}
        
        .stButton>button:hover, button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            background: linear-gradient(45deg, {theme['colors']['primary']}, {theme['colors']['accent']});
            {f'background: linear-gradient(45deg, #8B0000, #4CAF50);' if theme['name'] == 'Zombie Theme' else ''}
        }}
        
        /* Pipeline buttons specific styling */
        .pipeline-button {{
            background: linear-gradient(45deg, {theme['colors']['primary']}, {theme['colors']['accent']});
            color: {theme['colors']['text']};
            border: 2px solid {theme['colors']['primary']};
            border-radius: 12px;
            padding: 1.2rem;
            margin: 0.8rem 0;
            transition: all 0.3s ease;
            font-size: 1.1rem;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
            {f'background: linear-gradient(45deg, #4CAF50, #8B0000); border-color: #FF4500;' if theme['name'] == 'Zombie Theme' else ''}
        }}
        
        .pipeline-button:hover {{
            background: linear-gradient(45deg, {theme['colors']['accent']}, {theme['colors']['primary']});
            transform: translateY(-3px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.3);
            {f'background: linear-gradient(45deg, #8B0000, #4CAF50); box-shadow: 0 6px 12px rgba(255, 69, 0, 0.3);' if theme['name'] == 'Zombie Theme' else ''}
        }}
        
        /* Card styling */
        .metric-card {{
            background-color: {theme['colors']['card']};
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
            margin-bottom: 1rem;
            border: 1px solid {theme['colors']['primary']}33;
            {f'background-color: rgba(61, 61, 61, 0.9); border-color: #FF4500;' if theme['name'] == 'Zombie Theme' else ''}
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.2);
            {f'box-shadow: 0 6px 12px rgba(255, 69, 0, 0.2);' if theme['name'] == 'Zombie Theme' else ''}
        }}
        
        /* Headers styling */
        h1, h2, h3 {{
            color: {theme['colors']['text']};
            font-family: '{theme["font"]}', sans-serif;
            border-bottom: 2px solid {theme['colors']['primary']}33;
            padding-bottom: 0.5rem;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            {f'text-shadow: 2px 2px 4px rgba(255, 69, 0, 0.3);' if theme['name'] == 'Zombie Theme' else ''}
        }}
        
        /* Links styling */
        a {{
            color: {theme['colors']['primary']};
            text-decoration: none;
            transition: color 0.3s ease;
            {f'color: #FF4500;' if theme['name'] == 'Zombie Theme' else ''}
        }}
        
        a:hover {{
            color: {theme['colors']['accent']};
            {f'color: #4CAF50;' if theme['name'] == 'Zombie Theme' else ''}
        }}
        
        /* Status boxes styling */
        .success-box {{
            background-color: {theme['colors']['success']}22;
            border: 1px solid {theme['colors']['success']};
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            {f'background-color: rgba(0, 255, 0, 0.1);' if theme['name'] == 'Zombie Theme' else ''}
        }}
        
        .warning-box {{
            background-color: {theme['colors']['warning']}22;
            border: 1px solid {theme['colors']['warning']};
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            {f'background-color: rgba(255, 165, 0, 0.1);' if theme['name'] == 'Zombie Theme' else ''}
        }}
        
        .error-box {{
            background-color: {theme['colors']['error']}22;
            border: 1px solid {theme['colors']['error']};
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            {f'background-color: rgba(255, 0, 0, 0.1);' if theme['name'] == 'Zombie Theme' else ''}
        }}
        
        /* Selectbox styling */
        .stSelectbox > div > div {{
            background-color: {theme['colors']['surface']};
            border: 1px solid {theme['colors']['primary']};
            border-radius: 8px;
            color: {theme['colors']['text']};
            font-family: '{theme["font"]}', sans-serif;
            {f'background-color: rgba(45, 45, 45, 0.9);' if theme['name'] == 'Zombie Theme' else ''}
        }}
        
        /* Slider styling */
        .stSlider > div > div > div {{
            background-color: {theme['colors']['primary']};
            {f'background-color: #FF4500;' if theme['name'] == 'Zombie Theme' else ''}
        }}
        
        /* Radio button styling */
        .stRadio > div {{
            color: {theme['colors']['text']};
            font-family: '{theme["font"]}', sans-serif;
        }}
        
        /* Text input styling */
        .stTextInput > div > div > input {{
            background-color: {theme['colors']['surface']};
            color: {theme['colors']['text']};
            border: 1px solid {theme['colors']['primary']};
            border-radius: 8px;
            font-family: '{theme["font"]}', sans-serif;
            {f'background-color: rgba(45, 45, 45, 0.9);' if theme['name'] == 'Zombie Theme' else ''}
        }}
        
        /* Date input styling */
        .stDateInput > div > div > input {{
            background-color: {theme['colors']['surface']};
            color: {theme['colors']['text']};
            border: 1px solid {theme['colors']['primary']};
            border-radius: 8px;
            font-family: '{theme["font"]}', sans-serif;
            {f'background-color: rgba(45, 45, 45, 0.9);' if theme['name'] == 'Zombie Theme' else ''}
        }}
        
        /* Expander styling */
        .streamlit-expanderHeader {{
            background-color: {theme['colors']['surface']};
            color: {theme['colors']['text']};
            border: 1px solid {theme['colors']['primary']}33;
            border-radius: 8px;
            font-family: '{theme["font"]}', sans-serif;
            {f'background-color: rgba(45, 45, 45, 0.9);' if theme['name'] == 'Zombie Theme' else ''}
        }}
        
        /* Progress bar styling */
        .stProgress > div > div {{
            background-color: {theme['colors']['primary']};
            {f'background-color: #FF4500;' if theme['name'] == 'Zombie Theme' else ''}
        }}
        
        /* Dataframe styling */
        .dataframe {{
            background-color: {theme['colors']['surface']};
            color: {theme['colors']['text']};
            border: 1px solid {theme['colors']['primary']}33;
            border-radius: 8px;
            padding: 1rem;
            {f'background-color: rgba(45, 45, 45, 0.9);' if theme['name'] == 'Zombie Theme' else ''}
        }}
        
        /* Theme-specific button animations */
        {f'''
        @keyframes zombie-pulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
            100% {{ transform: scale(1); }}
        }}
        ''' if theme['name'] == 'Zombie Theme' else ''}
        
        {f'''
        @keyframes futuristic-glow {{
            0% {{ box-shadow: 0 0 5px {theme['colors']['primary']}; }}
            50% {{ box-shadow: 0 0 20px {theme['colors']['accent']}; }}
            100% {{ box-shadow: 0 0 5px {theme['colors']['primary']}; }}
        }}
        ''' if theme['name'] == 'Futuristic Theme' else ''}
        
        {f'''
        @keyframes got-flame {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
        ''' if theme['name'] == 'Game of Thrones Theme' else ''}
        
        {f'''
        @keyframes gaming-pixel {{
            0% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-2px); }}
            100% {{ transform: translateY(0); }}
        }}
        ''' if theme['name'] == 'Gaming Theme' else ''}
        
        /* Apply theme-specific animations to buttons */
        .stButton>button {{
            {f'animation: zombie-pulse 2s infinite;' if theme['name'] == 'Zombie Theme' else ''}
            {f'animation: futuristic-glow 2s infinite;' if theme['name'] == 'Futuristic Theme' else ''}
            {f'animation: got-flame 3s infinite;' if theme['name'] == 'Game of Thrones Theme' else ''}
            {f'animation: gaming-pixel 0.5s infinite;' if theme['name'] == 'Gaming Theme' else ''}
        }}
        </style>
    """, unsafe_allow_html=True)

# Define color scheme
COLOR_SCHEME = {
    'primary': '#2962ff',      # Vibrant Blue
    'secondary': '#00c853',    # Fresh Green
    'accent': '#ff6d00',       # Warm Orange
    'background': '#1a1a2e',   # Deep Navy
    'surface': '#16213e',      # Lighter Navy
    'card': '#0f3460',         # Medium Navy
    'text': '#ffffff',         # White
    'text_secondary': '#b0bec5', # Light Gray
    'error': '#ff5252',        # Red
    'success': '#69f0ae',      # Light Green
    'warning': '#ffd740'       # Amber
}

# Set page configuration
st.set_page_config(
    page_title="StockSage AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to set background color and styling
st.markdown(f"""
    <style>
    /* Main app styling */
    .stApp {{
        background-color: {COLOR_SCHEME['background']};
        color: {COLOR_SCHEME['text']};
    }}
    
    /* Sidebar styling */
    .css-1d391kg {{
        background-color: {COLOR_SCHEME['surface']};
    }}
    
    /* Buttons styling */
    .stButton>button {{
        width: 100%;
        padding: 0.75rem 1.5rem;
        margin-bottom: 0.75rem;
        border: none;
        border-radius: 8px;
        background: linear-gradient(45deg, {COLOR_SCHEME['primary']}, {COLOR_SCHEME['primary']}dd);
        color: {COLOR_SCHEME['text']};
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }}
    
    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        background: linear-gradient(45deg, {COLOR_SCHEME['primary']}, {COLOR_SCHEME['accent']});
    }}
    
    .stButton>button:active {{
        transform: translateY(0);
    }}
    
    /* Card styling */
    .metric-card {{
        background-color: {COLOR_SCHEME['card']};
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
        margin-bottom: 1rem;
        border: 1px solid rgba(255,255,255,0.1);
    }}
    
    .metric-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
    }}
    
    .metric-card h3 {{
        color: {COLOR_SCHEME['text']};
        margin-bottom: 0.75rem;
        font-size: 1.25rem;
    }}
    
    .metric-card p {{
        color: {COLOR_SCHEME['text_secondary']};
        font-size: 0.95rem;
        line-height: 1.5;
    }}
    
    /* Status boxes styling */
    .success-box {{
        padding: 1rem;
        border-radius: 8px;
        background-color: {COLOR_SCHEME['success']}22;
        border: 1px solid {COLOR_SCHEME['success']};
        margin: 1rem 0;
    }}
    
    .warning-box {{
        padding: 1rem;
        border-radius: 8px;
        background-color: {COLOR_SCHEME['warning']}22;
        border: 1px solid {COLOR_SCHEME['warning']};
        margin: 1rem 0;
    }}
    
    .error-box {{
        padding: 1rem;
        border-radius: 8px;
        background-color: {COLOR_SCHEME['error']}22;
        border: 1px solid {COLOR_SCHEME['error']};
        margin: 1rem 0;
    }}
    
    /* Progress bar styling */
    .stProgress > div > div {{
        background-color: {COLOR_SCHEME['primary']};
    }}
    
    /* Selectbox styling */
    .stSelectbox > div > div {{
        background-color: {COLOR_SCHEME['surface']};
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px;
    }}
    
    /* Slider styling */
    .stSlider > div > div > div {{
        background-color: {COLOR_SCHEME['primary']};
    }}
    
    /* DataFrame styling */
    .dataframe {{
        background-color: {COLOR_SCHEME['surface']};
        border-radius: 8px;
        padding: 1rem;
    }}
    
    /* Welcome animation container */
    .welcome-animation {{
        background-color: {COLOR_SCHEME['surface']};
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }}
    
    /* Headers styling */
    h1, h2, h3 {{
        color: {COLOR_SCHEME['text']};
        font-weight: 600;
        margin-bottom: 1rem;
    }}
    
    /* Links styling */
    a {{
        color: {COLOR_SCHEME['primary']};
        text-decoration: none;
        transition: color 0.3s ease;
    }}
    
    a:hover {{
        color: {COLOR_SCHEME['accent']};
    }}
    </style>
""", unsafe_allow_html=True)

# Alpha Vantage API configuration
ALPHA_VANTAGE_API_KEY = ""  # Will be set by user input

def fetch_alpha_vantage_data(ticker_symbol: str, start_date: pd.Timestamp, end_date: pd.Timestamp) -> Optional[pd.DataFrame]:
    """
    Fetch stock data from Alpha Vantage API
    
    Parameters:
    -----------
    ticker_symbol : str
        The stock ticker symbol
    start_date : pd.Timestamp
        Start date for data fetching
    end_date : pd.Timestamp
        End date for data fetching
        
    Returns:
    --------
    Optional[pd.DataFrame]
        DataFrame containing the stock data or None if fetch fails
    """
    if not ALPHA_VANTAGE_API_KEY:
        st.error("Please enter an Alpha Vantage API key in the sidebar.")
        st.info("You can get a free API key at https://www.alphavantage.co/support/#api-key")
        return None
        
    try:
        # Base URL for Alpha Vantage API
        base_url = "https://www.alphavantage.co/query"
        
        # Parameters for the API request
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": ticker_symbol,
            "apikey": ALPHA_VANTAGE_API_KEY,
            "outputsize": "full"
        }
        
        with st.spinner(f'Fetching data for {ticker_symbol} from Alpha Vantage...'):
            # Make the API request
            response = requests.get(base_url, params=params)
            
            if response.status_code != 200:
                st.error(f"Failed to fetch data: HTTP {response.status_code}")
                return None
                
            data = response.json()
            
            # Check for API errors
            if "Error Message" in data:
                st.error(f"API Error: {data['Error Message']}")
                return None
                
            if "Time Series (Daily)" not in data:
                st.error("No daily time series data found in the response")
                return None
                
            # Convert the data to a DataFrame
            time_series_data = data["Time Series (Daily)"]
            
            # Create lists to store the data
            dates = []
            opens = []
            highs = []
            lows = []
            closes = []
            volumes = []
            
            # Parse the time series data
            for date, values in time_series_data.items():
                dates.append(date)
                opens.append(float(values['1. open']))
                highs.append(float(values['2. high']))
                lows.append(float(values['3. low']))
                closes.append(float(values['4. close']))
                volumes.append(float(values['5. volume']))
            
            # Create DataFrame
            df = pd.DataFrame({
                'open': opens,
                'high': highs,
                'low': lows,
                'close': closes,
                'volume': volumes
            }, index=pd.to_datetime(dates))
            
            # Sort index in ascending order
            df.sort_index(inplace=True)
            
            # Filter the date range
            df = df.loc[start_date:end_date]
            
            if len(df) == 0:
                st.error(f"No data available for {ticker_symbol} in the specified date range.")
                return None
                
            # Add ticker symbol as a column
            df['symbol'] = ticker_symbol
            
            st.success(f"Successfully fetched {len(df)} days of data for {ticker_symbol}")
            return df
            
    except Exception as e:
        st.error(f"Error fetching data from Alpha Vantage: {str(e)}")
        return None

def fetch_stock_data(ticker_symbol: str, start_date: Any, end_date: Any, max_retries: int = 3, retry_delay: int = 2) -> Optional[pd.DataFrame]:
    """
    Fetch stock data with fallback between different data sources
    """
    # Convert dates to pandas Timestamp if they aren't already
    if not isinstance(start_date, pd.Timestamp):
        start_date = pd.Timestamp(start_date)
    if not isinstance(end_date, pd.Timestamp):
        end_date = pd.Timestamp(end_date)
        
    # Ensure end_date is not in the future
    today = pd.Timestamp.now()
    if end_date > today:
        end_date = today
        
    # Add 1 day buffer to end_date to include the last day
    end_date = end_date + pd.Timedelta(days=1)
        
    # Validate ticker symbol
    ticker_symbol = ticker_symbol.strip().upper()
    
    # First try Alpha Vantage
    if ALPHA_VANTAGE_API_KEY:
        df = fetch_alpha_vantage_data(ticker_symbol, start_date, end_date)
        if df is not None:
            return df
        st.warning("Alpha Vantage API failed, falling back to Yahoo Finance...")
    
    # Fallback to Yahoo Finance
    try:
        with st.spinner(f'Fetching data for {ticker_symbol} from Yahoo Finance...'):
            # Set up custom headers to avoid rate limiting
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            stock_data = None
            last_error = None
            
            # Try to fetch data with retries
            for attempt in range(max_retries):
                try:
                    ticker = yf.Ticker(ticker_symbol)
                    ticker.session.headers.update(headers)
                    
                    stock_data = ticker.history(
                        start=start_date,
                        end=end_date,
                        interval="1d",
                        auto_adjust=True
                    )
                    
                    if not stock_data.empty:
                        break
                        
                except Exception as e:
                    last_error = str(e)
                    st.warning(f"Attempt {attempt + 1}/{max_retries} failed. Retrying...")
                    time.sleep(retry_delay * (attempt + 1))
                    continue
            
            if stock_data is None or stock_data.empty:
                if last_error:
                    st.error(f"Failed to fetch data after {max_retries} attempts. Last error: {last_error}")
                else:
                    st.error(f"No data found for {ticker_symbol}. Please verify the ticker symbol and try again.")
                return None
            
            # Standardize column names
            stock_data.columns = stock_data.columns.str.lower()
            
            # Add ticker symbol as a column
            stock_data['symbol'] = ticker_symbol
            
            st.success(f"Successfully fetched {len(stock_data)} days of data for {ticker_symbol}")
            return stock_data
            
    except Exception as e:
        st.error(f"Error fetching stock data: {str(e)}")
        return None

def display_stock_data(df, title="Stock Data Overview"):
    """Display stock data with interactive components"""
    st.subheader(title)
    
    # Display basic statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Latest Close", f"${df['close'].iloc[-1]:.2f}", 
                 f"{((df['close'].iloc[-1] - df['close'].iloc[-2])/df['close'].iloc[-2]*100):.2f}%")
    with col2:
        st.metric("Highest Price", f"${df['high'].max():.2f}")
    with col3:
        st.metric("Lowest Price", f"${df['low'].min():.2f}")
    
    # Create interactive price chart
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index if isinstance(df.index, pd.DatetimeIndex) else df['date'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='OHLC'
    ))
    fig.update_layout(
        title='Stock Price Chart',
        yaxis_title='Price',
        template='plotly_dark',
        xaxis_rangeslider_visible=False
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Display the raw data with expandable details
    with st.expander("View Raw Data"):
        st.dataframe(df)
        
        # Display summary statistics
        st.subheader("Summary Statistics")
        st.dataframe(df.describe())

def preprocess_stock_data(df):
    """
    Preprocess stock data by handling missing values and outliers.
    Returns the preprocessed dataframe and a summary of changes made.
    """
    if df is None or df.empty:
        return None, "No data to preprocess"
    
    # Create a copy to avoid modifying original data
    processed_df = df.copy()
    summary = []
    
    # Store initial shape
    initial_rows = len(processed_df)
    
    # Check and report missing values
    missing_values = processed_df.isnull().sum()
    if missing_values.sum() > 0:
        summary.append("Missing values found:")
        for column in missing_values[missing_values > 0].index:
            summary.append(f"- {column}: {missing_values[column]} missing values")
        
        # Forward fill missing values (use previous day's values)
        processed_df.fillna(method='ffill', inplace=True)
        # Backward fill any remaining missing values at the start
        processed_df.fillna(method='bfill', inplace=True)
        
        summary.append("→ Filled missing values using forward and backward fill")
    
    # Handle outliers using Z-score method
    numeric_columns = ['open', 'high', 'low', 'close', 'volume']
    outliers_summary = {}
    
    for column in numeric_columns:
        # Calculate Z-scores
        z_scores = np.abs(stats.zscore(processed_df[column]))
        # Identify outliers (|z| > 3)
        outliers = z_scores > 3
        outliers_count = outliers.sum()
        
        if outliers_count > 0:
            outliers_summary[column] = outliers_count
            # Replace outliers with column mean
            column_mean = processed_df[column][~outliers].mean()
            processed_df.loc[outliers, column] = column_mean
    
    if outliers_summary:
        summary.append("\nOutliers detected and handled:")
        for column, count in outliers_summary.items():
            summary.append(f"- {column}: {count} outliers replaced with mean")
    
    # Calculate basic statistics for the processed data
    stats_summary = processed_df.describe()
    
    # Return processed dataframe and summary
    return processed_df, "\n".join(summary), stats_summary

def display_preprocessing_results(original_df, processed_df, summary, stats_summary):
    """Display the results of preprocessing in a user-friendly format"""
    
    # Display summary of changes
    st.subheader("Preprocessing Summary")
    st.text(summary)
    
    # Display statistics before and after
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Before Preprocessing")
        st.dataframe(original_df.describe())
    
    with col2:
        st.subheader("After Preprocessing")
        st.dataframe(stats_summary)
    
    # Display comparison plots
    st.subheader("Data Visualization")
    
    # Create comparison plot for closing prices
    fig = go.Figure()
    
    # Add original close price
    fig.add_trace(go.Scatter(
        x=original_df.index if isinstance(original_df.index, pd.DatetimeIndex) else original_df['date'],
        y=original_df['close'],
        name='Original Close Price',
        line=dict(color='blue', width=1)
    ))
    
    # Add processed close price
    fig.add_trace(go.Scatter(
        x=processed_df.index if isinstance(processed_df.index, pd.DatetimeIndex) else processed_df['date'],
        y=processed_df['close'],
        name='Processed Close Price',
        line=dict(color='green', width=1)
    ))
    
    # Update layout
    fig.update_layout(
        title='Comparison of Close Prices Before and After Preprocessing',
        yaxis_title='Price',
        template='plotly_dark',
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)

def calculate_technical_indicators(df):
    """Calculate various technical indicators for stock data"""
    df = df.copy()
    
    # Moving Averages
    df['SMA_20'] = df['close'].rolling(window=20).mean()
    df['SMA_50'] = df['close'].rolling(window=50).mean()
    df['EMA_20'] = df['close'].ewm(span=20, adjust=False).mean()
    
    # Bollinger Bands
    df['BB_middle'] = df['close'].rolling(window=20).mean()
    df['BB_upper'] = df['BB_middle'] + 2 * df['close'].rolling(window=20).std()
    df['BB_lower'] = df['BB_middle'] - 2 * df['close'].rolling(window=20).std()
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    # Calculate daily returns
    df['Daily_Return'] = df['close'].pct_change()
    
    # Calculate correlations with daily returns
    correlations = {}
    technical_indicators = ['SMA_20', 'SMA_50', 'EMA_20', 'RSI', 'MACD']
    for indicator in technical_indicators:
        correlations[indicator] = df['Daily_Return'].corr(df[indicator].fillna(0))
    
    return df, correlations

def display_technical_indicators(df, correlations):
    """Display technical indicators with interactive plots"""
    
    # Create subplots
    fig = make_subplots(rows=3, cols=1, 
                        shared_xaxes=True,
                        vertical_spacing=0.05,
                        row_heights=[0.5, 0.25, 0.25],
                        subplot_titles=('Price and Moving Averages', 'RSI', 'MACD'))
    
    # Plot 1: Price and Moving Averages
    fig.add_trace(go.Candlestick(
        x=df.index if isinstance(df.index, pd.DatetimeIndex) else df['date'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='OHLC'
    ), row=1, col=1)
    
    # Add Moving Averages
    fig.add_trace(go.Scatter(
        x=df.index if isinstance(df.index, pd.DatetimeIndex) else df['date'],
        y=df['SMA_20'],
        name='SMA 20',
        line=dict(color='orange')
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=df.index if isinstance(df.index, pd.DatetimeIndex) else df['date'],
        y=df['SMA_50'],
        name='SMA 50',
        line=dict(color='blue')
    ), row=1, col=1)
    
    # Add Bollinger Bands
    fig.add_trace(go.Scatter(
        x=df.index if isinstance(df.index, pd.DatetimeIndex) else df['date'],
        y=df['BB_upper'],
        name='BB Upper',
        line=dict(color='gray', dash='dash')
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=df.index if isinstance(df.index, pd.DatetimeIndex) else df['date'],
        y=df['BB_lower'],
        name='BB Lower',
        line=dict(color='gray', dash='dash'),
        fill='tonexty'
    ), row=1, col=1)
    
    # Plot 2: RSI
    fig.add_trace(go.Scatter(
        x=df.index if isinstance(df.index, pd.DatetimeIndex) else df['date'],
        y=df['RSI'],
        name='RSI',
        line=dict(color='purple')
    ), row=2, col=1)
    
    # Add RSI levels
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
    
    # Plot 3: MACD
    fig.add_trace(go.Scatter(
        x=df.index if isinstance(df.index, pd.DatetimeIndex) else df['date'],
        y=df['MACD'],
        name='MACD',
        line=dict(color='blue')
    ), row=3, col=1)
    
    fig.add_trace(go.Scatter(
        x=df.index if isinstance(df.index, pd.DatetimeIndex) else df['date'],
        y=df['Signal_Line'],
        name='Signal Line',
        line=dict(color='orange')
    ), row=3, col=1)
    
    # Update layout
    fig.update_layout(
        height=800,
        title='Technical Analysis Dashboard',
        template='plotly_dark',
        showlegend=True,
        xaxis_rangeslider_visible=False
    )
    
    # Display the plot
    st.plotly_chart(fig, use_container_width=True)
    
    # Display correlations
    st.subheader("Correlation with Daily Returns")
    correlation_df = pd.DataFrame.from_dict(correlations, orient='index', columns=['Correlation'])
    correlation_df = correlation_df.sort_values('Correlation', ascending=False)
    
    # Create a bar chart for correlations
    fig_corr = go.Figure()
    fig_corr.add_trace(go.Bar(
        x=correlation_df.index,
        y=correlation_df['Correlation'],
        marker_color=['green' if x > 0 else 'red' for x in correlation_df['Correlation']]
    ))
    fig_corr.update_layout(
        title='Correlation of Technical Indicators with Daily Returns',
        template='plotly_dark',
        showlegend=False,
        yaxis_title='Correlation Coefficient'
    )
    st.plotly_chart(fig_corr, use_container_width=True)
    
    # Display the technical indicators data
    with st.expander("View Technical Indicators Data"):
        st.dataframe(df.tail(50))

def split_and_visualize_data(df, test_size=0.2, random_state=42):
    """
    Split the dataset into training and testing sets and visualize the split.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The input dataset
    test_size : float
        The proportion of the dataset to include in the test split
    random_state : int
        Random state for reproducibility
    
    Returns:
    --------
    tuple : (X_train, X_test, y_train, y_test)
        The split datasets
    """
    
    # Prepare features and target
    # Use all available technical indicators as features
    feature_columns = ['open', 'high', 'low', 'close', 'volume']
    
    # Add technical indicators if they exist
    technical_indicators = ['SMA_20', 'SMA_50', 'EMA_20', 'RSI', 'MACD']
    for indicator in technical_indicators:
        if indicator in df.columns:
            feature_columns.append(indicator)
    
    # Remove any NaN values that might have been created by technical indicators
    df_clean = df.dropna()
    
    # Prepare features (X) and target (y)
    X = df_clean[feature_columns]
    # Use next day's closing price as target
    y = df_clean['close'].shift(-1)[:-1]
    X = X[:-1]  # Remove the last row as we don't have tomorrow's price for it
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, shuffle=False
    )
    
    # Create split visualization
    split_data = {
        'Dataset': ['Training Set', 'Testing Set'],
        'Size': [len(X_train), len(X_test)]
    }
    
    # Calculate percentages for the pie chart
    total = len(X_train) + len(X_test)
    train_pct = (len(X_train) / total) * 100
    test_pct = (len(X_test) / total) * 100
    
    # Create pie chart
    fig = px.pie(
        split_data,
        values='Size',
        names='Dataset',
        title='Dataset Split Distribution',
        color='Dataset',
        color_discrete_map={'Training Set': 'rgb(46, 204, 113)', 'Testing Set': 'rgb(52, 152, 219)'}
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        texttemplate="%{label}<br>%{percent:.1%}<br>(%{value:,} samples)"
    )
    
    fig.update_layout(
        template='plotly_dark',
        showlegend=True,
        height=400
    )
    
    # Display the split information
    st.subheader("Dataset Split Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Split Details")
        st.write(f"Total samples: {total:,}")
        st.write(f"Training set: {len(X_train):,} samples ({train_pct:.1f}%)")
        st.write(f"Testing set: {len(X_test):,} samples ({test_pct:.1f}%)")
        
        st.markdown("### Features Used")
        st.write("Base features:")
        st.write(", ".join(feature_columns[:5]))  # Original features
        if len(feature_columns) > 5:
            st.write("\nTechnical indicators:")
            st.write(", ".join(feature_columns[5:]))  # Technical indicators
    
    # Display sample data
    with st.expander("View Sample Data"):
        st.subheader("Training Set Sample")
        st.dataframe(X_train.head())
        st.subheader("Testing Set Sample")
        st.dataframe(X_test.head())
    
    return X_train, X_test, y_train, y_test

def train_and_evaluate_model(X_train, X_test, y_train, y_test, model_type, n_clusters=None):
    """
    Train and evaluate the selected model.
    
    Parameters:
    -----------
    X_train, X_test : pd.DataFrame
        Training and testing feature sets
    y_train, y_test : pd.Series
        Training and testing target variables
    model_type : str
        Type of model to train ('linear', 'logistic', or 'kmeans')
    n_clusters : int, optional
        Number of clusters for K-means clustering
    
    Returns:
    --------
    tuple : (trained_model, metrics, predictions)
    """
    
    # Scale the features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    metrics = {}
    predictions = None
    
    if model_type == 'linear':
        # Linear Regression
        model = LinearRegression()
        model.fit(X_train_scaled, y_train)
        
        # Make predictions
        train_pred = model.predict(X_train_scaled)
        test_pred = model.predict(X_test_scaled)
        
        # Calculate metrics
        metrics = {
            'R² Score (Train)': r2_score(y_train, train_pred),
            'R² Score (Test)': r2_score(y_test, test_pred),
            'RMSE (Train)': np.sqrt(mean_squared_error(y_train, train_pred)),
            'RMSE (Test)': np.sqrt(mean_squared_error(y_test, test_pred))
        }
        
        predictions = test_pred
        
    elif model_type == 'logistic':
        # Convert the problem to classification (price up/down)
        y_train_class = (y_train > y_train.shift(1)).astype(int)
        y_test_class = (y_test > y_test.shift(1)).astype(int)
        
        # Remove NaN values
        valid_train_idx = ~y_train_class.isna()
        valid_test_idx = ~y_test_class.isna()
        
        model = LogisticRegression(random_state=42)
        model.fit(X_train_scaled[valid_train_idx], y_train_class[valid_train_idx])
        
        # Make predictions
        train_pred = model.predict(X_train_scaled[valid_train_idx])
        test_pred = model.predict(X_test_scaled[valid_test_idx])
        
        # Calculate metrics
        metrics = {
            'Accuracy (Train)': accuracy_score(y_train_class[valid_train_idx], train_pred),
            'Accuracy (Test)': accuracy_score(y_test_class[valid_test_idx], test_pred)
        }
        
        predictions = test_pred
        
    elif model_type == 'kmeans':
        # K-means clustering
        model = KMeans(n_clusters=n_clusters, random_state=42)
        model.fit(X_train_scaled)
        
        # Make predictions
        train_clusters = model.predict(X_train_scaled)
        test_clusters = model.predict(X_test_scaled)
        
        # Calculate metrics (silhouette score or inertia)
        metrics = {
            'Inertia': model.inertia_,
            'Number of Clusters': n_clusters
        }
        
        predictions = test_clusters
    
    return model, metrics, predictions

def plot_model_results(X_test, y_test, predictions, model_type):
    """Plot the results of model training"""
    
    if model_type == 'linear':
        # Create scatter plot of actual vs predicted values
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=y_test,
            y=predictions,
            mode='markers',
            name='Predictions',
            marker=dict(color='blue', size=8)
        ))
        
        # Add perfect prediction line
        min_val = min(min(y_test), min(predictions))
        max_val = max(max(y_test), max(predictions))
        fig.add_trace(go.Scatter(
            x=[min_val, max_val],
            y=[min_val, max_val],
            mode='lines',
            name='Perfect Prediction',
            line=dict(color='red', dash='dash')
        ))
        
        fig.update_layout(
            title='Actual vs Predicted Values',
            xaxis_title='Actual Price',
            yaxis_title='Predicted Price',
            template='plotly_dark'
        )
        
    elif model_type == 'logistic':
        # Create confusion matrix visualization
        confusion_matrix = pd.crosstab(y_test, predictions)
        fig = px.imshow(confusion_matrix,
                       labels=dict(x="Predicted", y="Actual"),
                       x=['Down', 'Up'],
                       y=['Down', 'Up'],
                       color_continuous_scale='RdBu',
                       title='Confusion Matrix')
        
        fig.update_layout(template='plotly_dark')
        
    else:  # kmeans
        # Create scatter plot of clusters
        fig = px.scatter(
            x=X_test[:, 0],
            y=X_test[:, 1],
            color=predictions,
            title='K-means Clustering Results',
            labels={'x': 'Feature 1', 'y': 'Feature 2'}
        )
        
        fig.update_layout(template='plotly_dark')
    
    st.plotly_chart(fig, use_container_width=True)

def evaluate_regression_model(y_true, y_pred, title_prefix=""):
    """
    Evaluate regression model performance with multiple metrics and visualizations.
    """
    # Calculate metrics
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    
    # Calculate residuals
    residuals = y_true - y_pred
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Predicted vs Actual Values',
            'Residuals Plot',
            'Residuals Distribution',
            'Error Metrics'
        )
    )
    
    # 1. Predicted vs Actual Values
    fig.add_trace(
        go.Scatter(
            x=y_true,
            y=y_pred,
            mode='markers',
            name='Predictions',
            marker=dict(color='blue')
        ),
        row=1, col=1
    )
    
    # Add perfect prediction line
    min_val = min(min(y_true), min(y_pred))
    max_val = max(max(y_true), max(y_pred))
    fig.add_trace(
        go.Scatter(
            x=[min_val, max_val],
            y=[min_val, max_val],
            mode='lines',
            name='Perfect Prediction',
            line=dict(color='red', dash='dash')
        ),
        row=1, col=1
    )
    
    # 2. Residuals Plot
    fig.add_trace(
        go.Scatter(
            x=y_pred,
            y=residuals,
            mode='markers',
            name='Residuals',
            marker=dict(color='green')
        ),
        row=1, col=2
    )
    
    # Add horizontal line at y=0
    fig.add_hline(y=0, line_dash="dash", line_color="red", row=1, col=2)
    
    # 3. Residuals Distribution
    fig.add_trace(
        go.Histogram(
            x=residuals,
            name='Residuals Distribution',
            nbinsx=30,
            marker_color='purple'
        ),
        row=2, col=1
    )
    
    # 4. Error Metrics Bar Chart
    metrics = {
        'R²': r2,
        'RMSE': rmse,
        'MAE': mae
    }
    
    fig.add_trace(
        go.Bar(
            x=list(metrics.keys()),
            y=list(metrics.values()),
            name='Error Metrics',
            marker_color=['blue', 'red', 'green']
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=800,
        title_text=f"{title_prefix} Model Evaluation",
        showlegend=True,
        template='plotly_dark'
    )
    
    # Update axes labels
    fig.update_xaxes(title_text="Actual Values", row=1, col=1)
    fig.update_yaxes(title_text="Predicted Values", row=1, col=1)
    fig.update_xaxes(title_text="Predicted Values", row=1, col=2)
    fig.update_yaxes(title_text="Residuals", row=1, col=2)
    fig.update_xaxes(title_text="Residual Value", row=2, col=1)
    fig.update_yaxes(title_text="Frequency", row=2, col=1)
    fig.update_xaxes(title_text="Metric", row=2, col=2)
    fig.update_yaxes(title_text="Value", row=2, col=2)
    
    return fig, {
        'R-squared': r2,
        'Mean Squared Error': mse,
        'Root Mean Squared Error': rmse,
        'Mean Absolute Error': mae
    }

def evaluate_classification_model(y_true, y_pred, title_prefix=""):
    """
    Evaluate classification model performance with multiple metrics and visualizations.
    """
    # Calculate metrics
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred)
    rec = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    conf_matrix = confusion_matrix(y_true, y_pred)
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Confusion Matrix',
            'Performance Metrics',
            'Precision-Recall Trade-off',
            'Classification Distribution'
        ),
        specs=[[{"type": "heatmap"}, {"type": "bar"}],
               [{"type": "scatter"}, {"type": "pie"}]]
    )
    
    # 1. Confusion Matrix
    fig.add_trace(
        go.Heatmap(
            z=conf_matrix,
            x=['Predicted Down', 'Predicted Up'],
            y=['Actual Down', 'Actual Up'],
            colorscale='RdBu',
            showscale=True
        ),
        row=1, col=1
    )
    
    # 2. Performance Metrics Bar Chart
    metrics = {
        'Accuracy': acc,
        'Precision': prec,
        'Recall': rec,
        'F1 Score': f1
    }
    
    fig.add_trace(
        go.Bar(
            x=list(metrics.keys()),
            y=list(metrics.values()),
            marker_color='lightblue'
        ),
        row=1, col=2
    )
    
    # 3. Class Distribution Pie Chart
    class_dist = pd.Series(y_true).value_counts()
    fig.add_trace(
        go.Pie(
            labels=['Down', 'Up'],
            values=class_dist.values,
            hole=0.3
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=800,
        title_text=f"{title_prefix} Model Evaluation",
        showlegend=True,
        template='plotly_dark'
    )
    
    return fig, metrics

def evaluate_clustering_model(X, labels, n_clusters, title_prefix=""):
    """
    Evaluate clustering model performance with multiple metrics and visualizations.
    """
    # Calculate metrics
    silhouette_avg = silhouette_score(X, labels)
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Cluster Distribution',
            'Feature Space Visualization',
            'Silhouette Score',
            'Cluster Sizes'
        )
    )
    
    # 1. Cluster Distribution
    cluster_sizes = pd.Series(labels).value_counts().sort_index()
    fig.add_trace(
        go.Bar(
            x=[f'Cluster {i}' for i in range(n_clusters)],
            y=cluster_sizes.values,
            marker_color=px.colors.qualitative.Set3[:n_clusters]
        ),
        row=1, col=1
    )
    
    # 2. Feature Space Visualization (first two features)
    for i in range(n_clusters):
        mask = labels == i
        fig.add_trace(
            go.Scatter(
                x=X[mask, 0],
                y=X[mask, 1],
                mode='markers',
                name=f'Cluster {i}',
                marker=dict(size=8)
            ),
            row=1, col=2
        )
    
    # 3. Silhouette Score Gauge
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=silhouette_avg,
            title={'text': "Silhouette Score"},
            gauge={'axis': {'range': [-1, 1]},
                  'steps': [
                      {'range': [-1, 0], 'color': "red"},
                      {'range': [0, 0.5], 'color': "yellow"},
                      {'range': [0.5, 1], 'color': "green"}
                  ],
                  'bar': {'color': "darkblue"}}
        ),
        row=2, col=1
    )
    
    # Update layout
    fig.update_layout(
        height=800,
        title_text=f"{title_prefix} Clustering Evaluation",
        showlegend=True,
        template='plotly_dark'
    )
    
    metrics = {
        'Silhouette Score': silhouette_avg,
        'Number of Clusters': n_clusters,
        'Largest Cluster Size': cluster_sizes.max(),
        'Smallest Cluster Size': cluster_sizes.min()
    }
    
    return fig, metrics

def create_download_dataframe(df, y_test, predictions, future_predictions=None, model_type='linear'):
    """
    Create a formatted DataFrame for downloading predictions and actual values.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Original dataset with dates
    y_test : array-like
        Actual test values
    predictions : array-like
        Model predictions
    future_predictions : array-like, optional
        Future price predictions
    model_type : str
        Type of model ('linear', 'logistic', or 'kmeans')
    
    Returns:
    --------
    pandas.DataFrame : Formatted results for download
    """
    # Get dates for test set
    dates = df.index[-len(y_test):] if isinstance(df.index, pd.DatetimeIndex) else df['date'].iloc[-len(y_test):]
    
    if model_type == 'linear':
        # Create DataFrame with actual and predicted values
        results_df = pd.DataFrame({
            'Date': dates,
            'Actual_Price': y_test,
            'Predicted_Price': predictions,
            'Prediction_Error': y_test - predictions,
            'Prediction_Error_Pct': ((y_test - predictions) / y_test) * 100,
            'Within_5Pct': np.abs((y_test - predictions) / y_test) <= 0.05
        })
        
        # Add confidence intervals
        error_std = np.std(y_test - predictions)
        results_df['Upper_Bound'] = predictions + 2 * error_std
        results_df['Lower_Bound'] = predictions - 2 * error_std
        
        # Add future predictions if available
        if future_predictions is not None:
            future_dates = pd.date_range(
                start=dates[-1] + pd.Timedelta(days=1),
                periods=len(future_predictions)
            )
            
            future_df = pd.DataFrame({
                'Date': future_dates,
                'Actual_Price': np.nan,
                'Predicted_Price': future_predictions,
                'Prediction_Type': 'Future'
            })
            
            # Add confidence intervals for future predictions
            future_df['Upper_Bound'] = future_predictions + 2 * error_std
            future_df['Lower_Bound'] = future_predictions - 2 * error_std
            
            # Combine historical and future predictions
            results_df['Prediction_Type'] = 'Historical'
            results_df = pd.concat([results_df, future_df], axis=0)
    
    elif model_type == 'logistic':
        # Create DataFrame with actual and predicted directions
        actual_direction = (y_test > y_test.shift(1)).astype(int)
        
        results_df = pd.DataFrame({
            'Date': dates,
            'Actual_Price': y_test,
            'Price_Change': y_test - y_test.shift(1),
            'Actual_Direction': ['Up' if x == 1 else 'Down' for x in actual_direction],
            'Predicted_Direction': ['Up' if x == 1 else 'Down' for x in predictions],
            'Prediction_Correct': actual_direction == predictions
        })
    
    else:  # kmeans
        results_df = pd.DataFrame({
            'Date': dates,
            'Actual_Price': y_test,
            'Cluster_Label': predictions
        })
    
    return results_df

def visualize_predictions(df, y_test, predictions, future_predictions=None, model_type='linear'):
    """
    Create interactive visualizations for model predictions.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Original dataset with dates
    y_test : array-like
        Actual test values
    predictions : array-like
        Model predictions
    future_predictions : array-like, optional
        Predictions for future dates
    model_type : str
        Type of model ('linear', 'logistic', or 'kmeans')
    """
    
    if model_type == 'linear':
        # Create figure with secondary y-axis
        fig = make_subplots(rows=2, cols=1, 
                           shared_xaxes=True,
                           vertical_spacing=0.1,
                           subplot_titles=('Stock Price Prediction', 'Prediction Error'),
                           row_heights=[0.7, 0.3])
        
        # Get dates for test set
        dates = df.index[-len(y_test):] if isinstance(df.index, pd.DatetimeIndex) else df['date'].iloc[-len(y_test):]
        
        # Plot actual prices
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=y_test,
                name='Actual Price',
                line=dict(color='blue'),
                mode='lines'
            ),
            row=1, col=1
        )
        
        # Plot predicted prices
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=predictions,
                name='Predicted Price',
                line=dict(color='red', dash='dash'),
                mode='lines'
            ),
            row=1, col=1
        )
        
        # Add confidence interval (±2 std of prediction error)
        error = y_test - predictions
        std_error = np.std(error)
        
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=predictions + 2*std_error,
                name='Upper Bound',
                line=dict(color='rgba(200, 200, 200, 0.3)'),
                mode='lines'
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=predictions - 2*std_error,
                name='Lower Bound',
                line=dict(color='rgba(200, 200, 200, 0.3)'),
                fill='tonexty',
                mode='lines'
            ),
            row=1, col=1
        )
        
        # Plot future predictions if available
        if future_predictions is not None:
            # Generate future dates
            last_date = dates[-1]
            if isinstance(last_date, pd.Timestamp):
                future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), 
                                          periods=len(future_predictions))
            else:
                future_dates = pd.date_range(start=pd.Timestamp(last_date) + pd.Timedelta(days=1), 
                                          periods=len(future_predictions))
            
            fig.add_trace(
                go.Scatter(
                    x=future_dates,
                    y=future_predictions,
                    name='Future Predictions',
                    line=dict(color='green', dash='dot'),
                    mode='lines+markers'
                ),
                row=1, col=1
            )
        
        # Add prediction error plot
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=error,
                name='Prediction Error',
                line=dict(color='orange'),
                mode='lines'
            ),
            row=2, col=1
        )
        
        # Add zero line for error plot
        fig.add_hline(y=0, line_dash="dash", line_color="red", row=2, col=1)
        
        # Update layout
        fig.update_layout(
            title='Stock Price Predictions with Confidence Intervals',
            template='plotly_dark',
            height=800,
            showlegend=True,
            xaxis2_title='Date',
            yaxis_title='Price',
            yaxis2_title='Error'
        )
        
        # Calculate prediction statistics
        stats = {
            'Mean Prediction Error': np.mean(error),
            'Error Standard Deviation': std_error,
            'Maximum Overprediction': np.max(error),
            'Maximum Underprediction': np.min(error),
            'Prediction Accuracy (within ±5%)': np.mean(np.abs(error/y_test) <= 0.05) * 100
        }
        
        return fig, stats
    
    elif model_type == 'logistic':
        # Create figure for directional prediction
        fig = go.Figure()
        
        # Get dates for test set
        dates = df.index[-len(y_test):] if isinstance(df.index, pd.DatetimeIndex) else df['date'].iloc[-len(y_test):]
        
        # Plot actual price
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=y_test,
                name='Actual Price',
                line=dict(color='blue'),
                mode='lines'
            )
        )
        
        # Color regions based on predicted direction
        for i in range(len(predictions)-1):
            color = 'rgba(0, 255, 0, 0.1)' if predictions[i] == 1 else 'rgba(255, 0, 0, 0.1)'
            fig.add_vrect(
                x0=dates[i],
                x1=dates[i+1],
                fillcolor=color,
                layer="below",
                line_width=0,
                annotation_text="Up" if predictions[i] == 1 else "Down",
                annotation_position="top left"
            )
        
        fig.update_layout(
            title='Price Movement Direction Predictions',
            template='plotly_dark',
            height=600,
            showlegend=True,
            xaxis_title='Date',
            yaxis_title='Price'
        )
        
        # Calculate prediction statistics
        correct_predictions = np.sum(predictions == (y_test > y_test.shift(1)).astype(int)[1:])
        total_predictions = len(predictions)
        
        stats = {
            'Directional Accuracy': correct_predictions / total_predictions * 100,
            'Total Predictions': total_predictions,
            'Correct Predictions': correct_predictions,
            'Up Predictions': np.sum(predictions == 1),
            'Down Predictions': np.sum(predictions == 0)
        }
        
        return fig, stats

def predict_future_prices(model, scaler, last_window, n_steps=30):
    """
    Predict future stock prices using the trained model.
    
    Parameters:
    -----------
    model : sklearn model
        Trained model
    scaler : StandardScaler
        Fitted scaler
    last_window : array-like
        Last window of data used for prediction
    n_steps : int
        Number of future steps to predict
    
    Returns:
    --------
    array-like : Predicted future prices
    """
    future_predictions = []
    current_window = last_window.copy()
    
    # Calculate technical indicators for the initial window
    def calculate_window_indicators(window_df):
        # Calculate SMA
        window_df['SMA_20'] = window_df['close'].rolling(window=20, min_periods=1).mean()
        window_df['SMA_50'] = window_df['close'].rolling(window=50, min_periods=1).mean()
        
        # Calculate EMA
        window_df['EMA_20'] = window_df['close'].ewm(span=20, adjust=False, min_periods=1).mean()
        
        # Calculate RSI
        delta = window_df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
        rs = gain / loss
        window_df['RSI'] = 100 - (100 / (1 + rs))
        
        # Calculate MACD
        exp1 = window_df['close'].ewm(span=12, adjust=False, min_periods=1).mean()
        exp2 = window_df['close'].ewm(span=26, adjust=False, min_periods=1).mean()
        window_df['MACD'] = exp1 - exp2
        
        return window_df
    
    # Ensure current_window is a DataFrame with datetime index
    if not isinstance(current_window, pd.DataFrame):
        current_window = pd.DataFrame(current_window)
    
    for _ in range(n_steps):
        # Calculate technical indicators for current window
        window_with_indicators = calculate_window_indicators(current_window)
        
        # Get the last row with all features
        last_row = window_with_indicators.iloc[-1:]
        
        # Ensure all required features are present
        required_features = ['open', 'high', 'low', 'close', 'volume', 
                           'SMA_20', 'SMA_50', 'EMA_20', 'RSI', 'MACD']
        
        # Scale the features
        scaled_features = scaler.transform(last_row[required_features])
        
        # Make prediction
        prediction = model.predict(scaled_features)
        future_predictions.append(prediction[0])
        
        # Create new row with predicted close price
        new_row = pd.DataFrame({
            'open': [prediction[0]],  # Use prediction as next open
            'high': [prediction[0]],  # Initialize with prediction
            'low': [prediction[0]],   # Initialize with prediction
            'close': [prediction[0]], # Use prediction as close
            'volume': [current_window['volume'].mean()]  # Use mean volume
        }, index=[current_window.index[-1] + pd.Timedelta(days=1)])
        
        # Update the window by removing oldest row and adding new row
        current_window = pd.concat([current_window[1:], new_row])
    
    return np.array(future_predictions)

def display_model_selection():
    """Display model selection options in the sidebar"""
    st.sidebar.markdown("### Model Configuration")
    
    model_type = st.sidebar.selectbox(
        "Select Model Type",
        ["Linear Regression", "Logistic Regression", "K-Means Clustering"],
        help="Choose the type of machine learning model to train"
    )
    
    # Model-specific parameters
    params = {}
    
    if model_type == "Linear Regression":
        params['fit_intercept'] = st.sidebar.checkbox(
            "Fit Intercept",
            value=True,
            help="Whether to calculate the intercept for this model"
        )
        
    elif model_type == "Logistic Regression":
        params['C'] = st.sidebar.slider(
            "Regularization (C)",
            0.01, 10.0, 1.0,
            help="Inverse of regularization strength"
        )
        params['max_iter'] = st.sidebar.slider(
            "Maximum Iterations",
            100, 1000, 200,
            help="Maximum number of iterations for solver"
        )
        
    else:  # K-Means Clustering
        params['n_clusters'] = st.sidebar.slider(
            "Number of Clusters",
            2, 10, 5,
            help="Number of clusters to form"
        )
        params['n_init'] = st.sidebar.slider(
            "Number of Initializations",
            5, 20, 10,
            help="Number of times to run k-means with different centroid seeds"
        )
    
    return model_type, params

def create_model(model_type, params):
    """Create and configure the selected model with given parameters"""
    if model_type == "Linear Regression":
        return LinearRegression(fit_intercept=params['fit_intercept'])
    
    elif model_type == "Logistic Regression":
        return LogisticRegression(
            C=params['C'],
            max_iter=params['max_iter'],
            random_state=42
        )
    
    else:  # K-Means Clustering
        return KMeans(
            n_clusters=params['n_clusters'],
            n_init=params['n_init'],
            random_state=42
        )

def prepare_data_for_model(df, model_type):
    """Prepare features and target based on model type"""
    # Common feature columns
    feature_columns = ['open', 'high', 'low', 'close', 'volume']
    
    # Add technical indicators if they exist
    technical_indicators = ['SMA_20', 'SMA_50', 'EMA_20', 'RSI', 'MACD']
    for indicator in technical_indicators:
        if indicator in df.columns:
            feature_columns.append(indicator)
    
    # Remove any NaN values
    df_clean = df.dropna()
    
    if model_type == "Linear Regression":
        # Predict next day's closing price
        y = df_clean['close'].shift(-1)  # Next day's price
        X = df_clean[feature_columns]
        # Remove the last row since we don't have next day's price for it
        X = X[:-1]
        y = y[:-1]  # Remove the last NaN value from target
        
    elif model_type == "Logistic Regression":
        # Predict price direction (up/down)
        y = (df_clean['close'].shift(-1) > df_clean['close'])  # Next day's direction
        X = df_clean[feature_columns]
        # Remove the last row since we don't have next day's direction for it
        X = X[:-1]
        y = y[:-1].astype(int)  # Remove the last NaN value and convert to int
        
    else:  # K-Means Clustering
        # No target needed for clustering
        X = df_clean[feature_columns]
        y = None
    
    return X, y

def train_model_pipeline():
    """Main model training pipeline with dynamic model selection"""
    # Get data from session state
    if 'data' not in st.session_state:
        st.error("Please load and preprocess data first!")
        return
    
    df = st.session_state['data']
    
    # Display model selection sidebar
    model_type, params = display_model_selection()
    
    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Prepare data
        status_text.text("Preparing data...")
        X, y = prepare_data_for_model(df, model_type)
        progress_bar.progress(20)
        
        # Step 2: Split data
        status_text.text("Splitting data...")
        if model_type != "K-Means Clustering":
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, shuffle=False
            )
        else:
            X_train = X
            X_test = X
            y_train = None
            y_test = None
        progress_bar.progress(40)
        
        # Step 3: Scale features
        status_text.text("Scaling features...")
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        progress_bar.progress(60)
        
        # Step 4: Create and train model
        status_text.text("Training model...")
        model = create_model(model_type, params)
        
        if model_type != "K-Means Clustering":
            model.fit(X_train_scaled, y_train)
            train_pred = model.predict(X_train_scaled)
            test_pred = model.predict(X_test_scaled)
        else:
            train_pred = model.fit_predict(X_train_scaled)
            test_pred = model.predict(X_test_scaled)
        progress_bar.progress(80)
        
        # Step 5: Evaluate model
        status_text.text("Evaluating model...")
        if model_type == "Linear Regression":
            fig, metrics = evaluate_regression_model(y_test, test_pred)
        elif model_type == "Logistic Regression":
            fig, metrics = evaluate_classification_model(y_test, test_pred)
        else:
            fig, metrics = evaluate_clustering_model(X_test_scaled, test_pred, params['n_clusters'])
        progress_bar.progress(100)
        
        # Store results in session state
        st.session_state['model'] = model
        st.session_state['model_type'] = model_type
        st.session_state['scaler'] = scaler
        st.session_state['predictions'] = test_pred
        st.session_state['metrics'] = metrics
        
        # Display results
        status_text.text("Training complete!")
        st.success(f"Successfully trained {model_type} model!")
        
        # Display metrics
        st.subheader("Model Performance Metrics")
        metrics_df = pd.DataFrame.from_dict(metrics, orient='index', columns=['Value'])
        st.dataframe(metrics_df)
        
        # Display visualization
        st.subheader("Model Performance Visualization")
        st.plotly_chart(fig, use_container_width=True)
        
        # Add download button for predictions
        if model_type != "K-Means Clustering":
            results_df = create_download_dataframe(df, y_test, test_pred, model_type=model_type.lower().replace(" ", "_"))
            csv = results_df.to_csv(index=False)
            st.download_button(
                label="Download Predictions",
                data=csv,
                file_name="model_predictions.csv",
                mime="text/csv"
            )
    
    except Exception as e:
        st.error(f"Error during model training: {str(e)}")
        progress_bar.empty()
        status_text.empty()

def main():
    # Show welcome splash only once per session
    if 'show_welcome_splash' not in st.session_state:
        st.session_state['show_welcome_splash'] = True

    if st.session_state['show_welcome_splash']:
        st.markdown('''
            <style>
            .welcome-splash-overlay {
                position: fixed;
                top: 0; left: 0; right: 0; bottom: 0;
                width: 100vw; height: 100vh;
                background: #111;
                z-index: 99999;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }
            .welcome-splash-title {
                color: #fff;
                font-size: 3rem;
                font-weight: bold;
                margin-bottom: 2rem;
                text-shadow: 2px 2px 8px #000;
            }
            </style>
            <div class="welcome-splash-overlay">
                <div class="welcome-splash-title">Welcome to StockSage AI</div>
                <img src="https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExdWE2aWpjOXVpZnVwbGltaHpxMHJsaXdyOGl3bzY5bnJ0N3J5aWhobSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/eGmQlEGrVNuJYXvoXp/giphy.gif" alt="Balloons" style="width:300px;"/>
            </div>
        ''', unsafe_allow_html=True)
        time.sleep(4)
        st.session_state['show_welcome_splash'] = False
        st.rerun()
        st.stop()

    # --- Theme transition animation logic ---
    if st.session_state.get('show_theme_transition', False):
        theme_id = st.session_state.get('pending_theme', st.session_state['current_theme'])
        theme_gif_map = {
            'zombie': 'zombie_header.gif',
            'futuristic': 'https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExOHhjdGQ1aWlqYmFidm5yeTlpcm94bnVhY3FkeWJxMTVqdm4yNzRpNiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/lbcLMX9B6sTsGjUmS3/giphy.gif',  # New public futuristic GIF
            'got': 'got_header.gif',
            'gaming': 'https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExN3dzejY5cDB0N2VsMXRwdnF4eW4xNjh0ZGxrZzg1Zm84bXA0bTVqcSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ul3DvfCRQixLa/giphy.gif',  # Public gaming GIF
        }
        if theme_id in theme_gif_map:
            gif_path = theme_gif_map[theme_id]
            if gif_path.startswith('http'):
                img_tag = f'<img src="{gif_path}" alt="Theme Transition GIF">'
            else:
                encoded_gif = get_base64_of_bin_file(gif_path)
                img_tag = f'<img src="data:image/gif;base64,{encoded_gif}" alt="Theme Transition GIF">'
            st.markdown(f'''
                <style>
                body {{
                    overflow: hidden !important;
                }}
                .theme-transition-overlay {{
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    width: 100vw;
                    height: 100vh;
                    background: black;
                    z-index: 99999;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    overflow: hidden;
                }}
                .theme-transition-overlay img {{
                    width: 100vw;
                    height: 100vh;
                    object-fit: cover;
                }}
                .theme-transition-message {{
                    color: white;
                    font-size: 2.5rem;
                    font-weight: bold;
                    margin-top: 2rem;
                    text-shadow: 2px 2px 8px #000;
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, 100px);
                    width: 100vw;
                    text-align: center;
                }}
                </style>
                <div class="theme-transition-overlay">
                    {img_tag}
                    <div class="theme-transition-message">Switching theme...</div>
                </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown("<h2 style='text-align:center;'>Switching theme...</h2>", unsafe_allow_html=True)
        time.sleep(3)
        st.session_state['current_theme'] = theme_id
        st.session_state['show_theme_transition'] = False
        st.rerun()
        st.stop()

    # Initialize session state for completed steps
    if 'completed_steps' not in st.session_state:
        st.session_state['completed_steps'] = set()

    # Sidebar navigation
    st.sidebar.title("Navigation")

    # Add theme selector back to the sidebar
    st.sidebar.markdown("### Theme Selection")
    theme_options = {theme['name']: theme_id for theme_id, theme in THEMES.items()}
    selected_theme = st.sidebar.selectbox(
        "Choose Theme",
        options=list(theme_options.keys()),
        index=list(theme_options.keys()).index(THEMES[st.session_state['current_theme']]['name']),
        help="Select your preferred theme"
    )
    # Theme transition trigger
    if theme_options[selected_theme] != st.session_state['current_theme']:
        st.session_state['pending_theme'] = theme_options[selected_theme]
        st.session_state['show_theme_transition'] = True
        st.rerun()
    # Apply the selected theme
    apply_theme()
    
    # Add Alpha Vantage API key input
    global ALPHA_VANTAGE_API_KEY
    ALPHA_VANTAGE_API_KEY = st.sidebar.text_input(
        "Alpha Vantage API Key",
        type="password",
        help="Enter your Alpha Vantage API key. Get one for free at https://www.alphavantage.co/support/#api-key"
    )
    if ALPHA_VANTAGE_API_KEY:
        st.sidebar.success("✅ API Key set")
    else:
        st.sidebar.info("ℹ️ Enter API key for more reliable data fetching")
    
    # Create pipeline step buttons
    pipeline_buttons = {
        "Data Loading": st.sidebar.button(
            "📥 Load Data",
            help="Upload CSV or fetch stock data"
        ),
        "Preprocessing": st.sidebar.button(
            "🔄 Preprocess Data",
            help="Clean and prepare the data"
        ),
        "Feature Engineering": st.sidebar.button(
            "⚙️ Engineer Features",
            help="Create technical indicators"
        ),
        "Model Selection": st.sidebar.button(
            "🎯 Select Model",
            help="Choose and configure ML model"
        ),
        "Model Training": st.sidebar.button(
            "🚀 Train Model",
            help="Train the selected model"
        ),
        "Evaluation": st.sidebar.button(
            "📊 Evaluate Model",
            help="View model performance"
        ),
        "Predictions": st.sidebar.button(
            "🔮 Make Predictions",
            help="Generate stock predictions"
        )
    }
    
    # Handle button clicks
    for step, clicked in pipeline_buttons.items():
        if clicked:
            if step == "Data Loading" or 'data' in st.session_state:
                st.session_state['current_step'] = step
                if step not in st.session_state['completed_steps']:
                    st.session_state['completed_steps'].add(step)
            else:
                st.warning("Please load data first!")
    
    # Main content area
    if 'current_step' not in st.session_state:
        theme = get_current_theme()
        # (No header GIF/banner)
        st.markdown(f"""
            <style>
            .welcome-content {{
                position: relative;
                z-index: 1;
                text-align: center;
                padding: 2rem;
            }}
            </style>
            <div class="welcome-content">
                <h1 style="color: {theme['colors']['text']}; font-size: 2.5rem; margin-bottom: 1rem; font-family: '{theme['font']}', sans-serif;">
                    📈 StockSage AI
                </h1>
                <p style="color: {theme['colors']['text_secondary']}; font-size: 1.2rem; margin-bottom: 2rem;">
                    Your AI-powered stock analysis and prediction platform!
                </p>
                <h2 style='color: {theme['colors']['primary']}; margin-bottom: 0.5rem; font-family: '{theme['font']}', sans-serif;'>What can you do here?</h2>
                <ul style='color: {theme['colors']['text_secondary']}; text-align: left; max-width: 600px; margin: 0 auto 2rem auto; font-size: 1.1rem;'>
                    <li>Fetch or upload stock data for any ticker</li>
                    <li>Clean, preprocess, and engineer features automatically</li>
                    <li>Train and evaluate ML models (regression, classification, clustering)</li>
                    <li>Visualize results and download predictions</li>
                </ul>
                <h3 style='color: {theme['colors']['accent']}; margin-bottom: 0.5rem; font-family: '{theme['font']}', sans-serif;'>How to get started?</h3>
                <ol style='color: {theme['colors']['text_secondary']}; text-align: left; max-width: 600px; margin: 0 auto 2rem auto; font-size: 1.05rem;'>
                    <li>Use the sidebar to navigate through the pipeline steps</li>
                    <li>Load your data (CSV upload or Yahoo Finance fetch)</li>
                    <li>Follow the steps: Preprocessing → Feature Engineering → Model Selection → Training → Evaluation → Predictions</li>
                </ol>
                <p style='color: {theme['colors']['text_secondary']}; margin-top: 2rem;'>
                    <b>Tip:</b> You can always return to this home page by refreshing the app.
                </p>
            </div>
        """, unsafe_allow_html=True)
        # Display feature cards with enhanced styling
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
                <div class="metric-card">
                    <h3 style="color: {theme['colors']['primary']}; font-family: '{theme['font']}', sans-serif;">📊 Smart Analysis</h3>
                    <p style="color: {theme['colors']['text_secondary']};">Upload your own dataset or fetch real-time stock data using Yahoo Finance API</p>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
                <div class="metric-card">
                    <h3 style="color: {theme['colors']['primary']}; font-family: '{theme['font']}', sans-serif;">🤖 AI Pipeline</h3>
                    <p style="color: {theme['colors']['text_secondary']};">Advanced machine learning pipeline with automated preprocessing, feature engineering, and model selection</p>
                </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
                <div class="metric-card">
                    <h3 style="color: {theme['colors']['primary']}; font-family: '{theme['font']}', sans-serif;">🔮 Smart Predictions</h3>
                    <p style="color: {theme['colors']['text_secondary']};">Get AI-powered stock price predictions with interactive visualizations and downloadable reports</p>
                </div>
            """, unsafe_allow_html=True)
    else:
        # Display current step title with emoji
        step_emojis = {
            "Data Loading": "📥",
            "Preprocessing": "🔄",
            "Feature Engineering": "⚙️",
            "Model Selection": "🎯",
            "Model Training": "🚀",
            "Evaluation": "📊",
            "Predictions": "🔮"
        }
        current_step = st.session_state['current_step']
        # (No header GIF/banner)
        st.title(f"{step_emojis.get(current_step, '')} {current_step}")
        
        # Handle different pipeline steps
        if current_step == "Data Loading":
            theme = get_current_theme()
            st.markdown(f"""
                <style>
                .data-loading-text {{
                    color: {theme['colors']['text']};
                    font-family: '{theme["font"]}', sans-serif;
                }}
                .data-loading-subtext {{
                    color: {theme['colors']['text_secondary']};
                    font-family: '{theme["font"]}', sans-serif;
                }}
                </style>
                <div class="data-loading-text">
                    <h2>Choose how you want to load your stock data:</h2>
                </div>
            """, unsafe_allow_html=True)
            
            data_source = st.radio(
                "Data Source",
                ["Upload CSV", "Fetch from Yahoo Finance"],
                help="Select whether to upload your own CSV file or fetch data from Yahoo Finance"
            )
            
            if data_source == "Upload CSV":
                st.markdown(f"""
                    <div class="data-loading-subtext">
                        <p>Upload your stock data in CSV format. The file should contain the following columns:</p>
                        <ul>
                            <li>Date (YYYY-MM-DD format)</li>
                            <li>Open (Opening price)</li>
                            <li>High (Highest price)</li>
                            <li>Low (Lowest price)</li>
                            <li>Close (Closing price)</li>
                            <li>Volume (Trading volume)</li>
                        </ul>
                    </div>
                """, unsafe_allow_html=True)
                
                uploaded_file = st.file_uploader(
                    "Upload your stock data CSV file",
                    type=["csv"],
                    help="Upload a CSV file with columns: Date, Open, High, Low, Close, Volume"
                )
                
                if uploaded_file is not None:
                    df = load_csv_data(uploaded_file)
                    if df is not None:
                        st.session_state['data'] = df
                        st.success("Data loaded successfully!")
                        display_stock_data(df)
                    
            else:  # Fetch from Yahoo Finance
                st.markdown(f"""
                    <div class="data-loading-subtext">
                        <p>Enter the stock ticker symbol and date range to fetch historical data from Yahoo Finance.</p>
                        <p>Example ticker symbols: AAPL (Apple), GOOGL (Google), MSFT (Microsoft)</p>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([2, 1.5, 1.5])
                
                with col1:
                    ticker = st.text_input(
                        "Stock Ticker Symbol",
                        help="Enter the stock ticker symbol (e.g., AAPL for Apple)"
                    ).upper()
                
                with col2:
                    start_date = st.date_input(
                        "Start Date",
                        help="Select the start date for historical data"
                    )
                
                with col3:
                    end_date = st.date_input(
                        "End Date",
                        help="Select the end date for historical data"
                    )
                
                if st.button("Fetch Data"):
                    if ticker and start_date and end_date:
                        with st.spinner(f"Fetching data for {ticker}..."):
                            df = fetch_stock_data(ticker, start_date, end_date)
                            if df is not None:
                                st.session_state['data'] = df
                                st.success(f"Successfully fetched data for {ticker}!")
                                display_stock_data(df)
                    else:
                        st.warning("Please fill in all the required fields.")
        elif current_step == "Preprocessing":
            if 'data' in st.session_state:
                df = st.session_state['data']
                processed_df, summary, stats_summary = preprocess_stock_data(df)
                if processed_df is not None:
                    st.session_state['data'] = processed_df
                    display_preprocessing_results(df, processed_df, summary, stats_summary)
            else:
                st.error("No data available. Please load data first!")
        elif current_step == "Feature Engineering":
            if 'data' in st.session_state:
                df = st.session_state['data']
                df_with_features, correlations = calculate_technical_indicators(df)
                st.session_state['data'] = df_with_features
                display_technical_indicators(df_with_features, correlations)
            else:
                st.error("No data available. Please load data first!")
        elif current_step == "Model Selection":
            if 'data' in st.session_state:
                st.write("Configure your model parameters below:")
                
                model_type = st.selectbox(
                    "Select Model Type",
                    ["Linear Regression", "Logistic Regression", "K-Means Clustering"],
                    help="Choose the type of machine learning model to train"
                )
                
                # Model-specific parameters
                params = {}
                
                if model_type == "Linear Regression":
                    params['fit_intercept'] = st.checkbox(
                        "Fit Intercept",
                        value=True,
                        help="Whether to calculate the intercept for this model"
                    )
                    
                elif model_type == "Logistic Regression":
                    params['C'] = st.slider(
                        "Regularization (C)",
                        0.01, 10.0, 1.0,
                        help="Inverse of regularization strength"
                    )
                    params['max_iter'] = st.slider(
                        "Maximum Iterations",
                        100, 1000, 200,
                        help="Maximum number of iterations for solver"
                    )
                    
                else:  # K-Means Clustering
                    params['n_clusters'] = st.slider(
                        "Number of Clusters",
                        2, 10, 5,
                        help="Number of clusters to form"
                    )
                    params['n_init'] = st.slider(
                        "Number of Initializations",
                        5, 20, 10,
                        help="Number of times to run k-means with different centroid seeds"
                    )
                
                # Save model configuration
                if st.button("Save Model Configuration"):
                    st.session_state['model_config'] = {
                        'type': model_type,
                        'params': params
                    }
                    st.success(f"Model configuration saved! Selected model: {model_type}")
                    
                    # Display current configuration
                    st.subheader("Current Model Configuration")
                    st.write("Model Type:", model_type)
                    st.write("Parameters:")
                    for param, value in params.items():
                        st.write(f"- {param}: {value}")
            else:
                st.error("No data available. Please load and preprocess data first!")
        elif current_step == "Model Training":
            train_model_pipeline()
        elif current_step == "Evaluation":
            if all(key in st.session_state for key in ['model', 'data', 'predictions', 'metrics']):
                st.subheader("Model Performance Metrics")
                metrics_df = pd.DataFrame.from_dict(st.session_state['metrics'], 
                                                 orient='index', 
                                                 columns=['Value'])
                st.dataframe(metrics_df)
                
                if 'evaluation_plot' in st.session_state:
                    st.plotly_chart(st.session_state['evaluation_plot'])
            else:
                st.error("No model evaluation results available. Please train a model first!")
        elif current_step == "Predictions":
            if all(key in st.session_state for key in ['model', 'data', 'scaler']):
                st.subheader("Future Price Predictions")
                n_days = st.slider("Number of days to predict", 5, 30, 7)
                
                if st.button("Generate Predictions"):
                    try:
                        with st.spinner("Generating predictions..."):
                            df = st.session_state['data']
                            model = st.session_state['model']
                            scaler = st.session_state['scaler']
                            
                            # Get the last window of data with all required features
                            required_features = ['open', 'high', 'low', 'close', 'volume']
                            last_window = df.tail(50)[required_features].copy()  # Get more data for technical indicators
                            
                            # Generate predictions
                            future_predictions = predict_future_prices(
                                model, 
                                scaler, 
                                last_window, 
                                n_steps=n_days
                            )
                            
                            # Create dates for future predictions
                            last_date = df.index[-1]
                            future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=n_days)
                            
                            # Create DataFrame with predictions
                            predictions_df = pd.DataFrame({
                                'Predicted_Price': future_predictions
                            }, index=future_dates)
                            
                            # Display predictions
                            st.subheader("Predicted Prices")
                            st.dataframe(predictions_df)
                            
                            # Plot predictions
                            fig = go.Figure()
                            
                            # Plot historical data
                            fig.add_trace(go.Scatter(
                                x=df.index[-30:],  # Last 30 days
                                y=df['close'][-30:],
                                name='Historical Price',
                                line=dict(color='blue')
                            ))
                            
                            # Plot predictions
                            fig.add_trace(go.Scatter(
                                x=future_dates,
                                y=future_predictions,
                                name='Predicted Price',
                                line=dict(color='red', dash='dash')
                            ))
                            
                            fig.update_layout(
                                title='Stock Price Predictions',
                                xaxis_title='Date',
                                yaxis_title='Price',
                                template='plotly_dark',
                                showlegend=True
                            )
                            
                            st.plotly_chart(fig)
                            
                    except Exception as e:
                        st.error(f"Error in prediction: {str(e)}")
            else:
                missing_keys = [key for key in ['model', 'data', 'scaler'] if key not in st.session_state]
                st.error(f"Missing required components: {', '.join(missing_keys)}. Please train a model first!")

    # --- Footer ---
    st.markdown(f"""
        <style>
        .footer {{
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100vw;
            background: {COLOR_SCHEME['surface']};
            color: {COLOR_SCHEME['text_secondary']};
            text-align: center;
            padding: 0.7rem 0 0.5rem 0;
            font-size: 1rem;
            z-index: 100;
            border-top: 1px solid #222;
        }}
        </style>
        
    """, unsafe_allow_html=True)

def load_csv_data(uploaded_file):
    """
    Load a CSV file uploaded by the user and return a pandas DataFrame.
    Ensures all column names are lowercase and checks for required columns.
    """
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = [col.lower() for col in df.columns]
        # Optionally, parse dates if a 'date' column exists
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
        # Check for required columns
        required_cols = {'open', 'high', 'low', 'close', 'volume'}
        missing = required_cols - set(df.columns)
        if missing:
            st.error(f"Missing required columns in uploaded CSV: {', '.join(missing)}. Please upload a file with columns: {', '.join(required_cols)}.")
            return None
        return df
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return None

def get_base64_of_bin_file(bin_file):
    """Convert binary file to base64 string"""
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

if __name__ == "__main__":
    main() 
