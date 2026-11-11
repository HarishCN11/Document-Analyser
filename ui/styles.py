"""
UI Styles Module
Contains all CSS styling for the Streamlit app
"""

MAIN_STYLES = """
    <style>
    /* Page background - Light Blue */
    .stApp {
        background-color: #e3f2fd;
    }
    
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #333;
    }
    
    /* Simple card styling */
    .card {
        background: white;
        border-radius: 8px;
        padding: 20px;
        border: 1px solid #bbdefb;
        margin-bottom: 15px;
    }
    
    .card-success {
        border-left: 4px solid #4caf50;
    }
    
    .card-warning {
        border-left: 4px solid #ff9800;
    }
    
    /* Header styling - Simple */
    .header-main {
        text-align: center;
        padding: 30px 20px;
        background-color: #1e88e5;
        border-radius: 8px;
        color: white;
        margin-bottom: 30px;
    }
    
    .header-main h1 {
        font-size: 2em;
        margin: 0;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    .header-main p {
        font-size: 1em;
        margin: 10px 0 0 0;
        opacity: 0.95;
    }
    
    /* Feature box - Simple grid */
    .feature-box {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
        margin: 20px 0;
    }
    
    .feature-item {
        background: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-top: 3px solid #1e88e5;
    }
    
    .feature-item h3 {
        color: #1e88e5;
        margin-top: 10px;
    }
    
    /* Status badges */
    .badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 600;
        margin-right: 10px;
    }
    
    .badge-success {
        background: #d1fae5;
        color: #065f46;
    }
    
    .badge-warning {
        background: #fef3c7;
        color: #92400e;
    }
    
    .badge-info {
        background: #dbeafe;
        color: #0c2d6b;
    }
    
    /* Upload section */
    .upload-section {
        background: white;
        border-radius: 8px;
        padding: 30px;
        text-align: center;
        border: 2px dashed #1e88e5;
        margin: 20px 0;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #e3f2fd;
        border-radius: 8px;
        padding: 5px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1e88e5 !important;
        color: white !important;
    }
    
    /* Button styling - Simple */
    .stButton > button {
        background-color: #1e88e5;
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 500;
        padding: 10px 24px;
    }
    
    .stButton > button:hover {
        background-color: #1565c0;
    }
    </style>
"""


def apply_styles():
    """Apply main styles to the Streamlit app"""
    import streamlit as st

    st.markdown(MAIN_STYLES, unsafe_allow_html=True)
