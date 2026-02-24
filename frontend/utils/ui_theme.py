import streamlit as st
from html import escape


def apply_theme(page_title: str, subtitle: str = "") -> None:
    safe_title = escape(page_title)
    safe_subtitle = escape(subtitle)
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
        }

        .stApp {
            background: radial-gradient(circle at 0% 0%, #fff3dd 0%, #f8fafc 52%, #eef7ff 100%);
            color: #1f2937;
        }

        p, li, div, label, span, small {
            color: #1f2937;
        }

        .main .block-container {
            padding-top: 1.1rem;
            padding-bottom: 1.8rem;
            max-width: 1180px;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(255,255,255,0.94), rgba(248,250,252,0.94));
            border-right: 1px solid #e5e7eb;
        }

        section[data-testid="stSidebar"] * {
            color: #0f172a !important;
        }

        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
            color: #1e293b;
            font-weight: 600;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.35rem;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 10px;
            padding: 0.4rem 0.8rem;
        }

        .stTabs [aria-selected="true"] {
            background: #dbeafe;
            border-radius: 10px;
        }

        .stTextInput input,
        .stTextArea textarea,
        .stNumberInput input,
        .stDateInput input,
        .stTimeInput input {
            background: #ffffff !important;
            color: #0f172a !important;
            border: 1px solid #cbd5e1 !important;
        }

        div[data-baseweb="select"] > div {
            background: #ffffff !important;
            color: #0f172a !important;
            border: 1px solid #cbd5e1 !important;
        }

        .stTextInput label, .stTextArea label, .stNumberInput label, .stDateInput label, .stTimeInput label {
            font-weight: 600;
            color: #334155 !important;
        }

        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.95);
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 12px 14px;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
        }

        div[data-testid="stForm"] {
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 14px;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
        }

        div[data-testid="stExpander"] {
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.9);
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            overflow: hidden;
        }

        .stButton > button {
            border-radius: 10px;
            border: 1px solid #1d4ed8;
            background: #1d4ed8;
            color: #ffffff;
            font-weight: 600;
            min-height: 2.5rem;
            padding: 0.35rem 0.9rem;
        }

        .stButton > button:disabled {
            background: #ffffff !important;
            color: #64748b !important;
            border: 1px solid #cbd5e1 !important;
            opacity: 1 !important;
        }

        .ux-hero {
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid #e5e7eb;
            border-radius: 16px;
            padding: 16px 18px;
            margin-bottom: 14px;
            box-shadow: 0 10px 28px rgba(15, 23, 42, 0.07);
        }

        .ux-hero h1 {
            margin: 0;
            font-size: 1.55rem;
            color: #0f172a;
        }

        .ux-hero p {
            margin: 4px 0 0;
            color: #475569;
            font-size: 0.95rem;
        }

        div[data-testid="stAlert"] {
            border-radius: 12px;
            border: 1px solid #e5e7eb;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='ux-hero'><h1>{safe_title}</h1><p>{safe_subtitle}</p></div>",
        unsafe_allow_html=True,
    )
