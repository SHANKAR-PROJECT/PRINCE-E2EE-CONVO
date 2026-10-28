"""Vercel entrypoint for the Streamlit application.

The main application is hosted by Streamlit, while this lightweight Flask
handler keeps the Vercel deployment healthy and directs visitors to it.
"""

from flask import Flask, redirect

app = Flask(__name__)

STREAMLIT_APP_URL = "https://prince-insta-convo-lp6tm6jqownopvxqhp98kd.streamlit.app/"


@app.get("/")
def home():
    """Send visitors directly to the working Streamlit dashboard."""
    return redirect(STREAMLIT_APP_URL, code=302)


@app.get("/health")
def health():
    return {"status": "ok", "service": "prince-e2ee-convo"}
