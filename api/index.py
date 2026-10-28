"""Vercel entrypoint for the Streamlit application.

The main application is hosted by Streamlit, while this lightweight Flask
handler keeps the Vercel deployment healthy and directs visitors to it.
"""

from flask import Flask, render_template_string

app = Flask(__name__)

STREAMLIT_APP_URL = "https://prince-insta-convo-lp6tm6jqownopvxqhp98kd.streamlit.app/"


@app.get("/")
def home():
    return render_template_string(
        """
        <!doctype html>
        <html lang="en">
          <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <title>Prince E2EE Convo</title>
            <style>
              :root { color-scheme: dark; }
              * { box-sizing: border-box; }
              body { margin: 0; min-height: 100vh; display: grid; place-items: center; padding: 24px; background: #02070c; color: #f5fbff; font-family: Inter, system-ui, sans-serif; }
              main { width: min(720px, 100%); padding: clamp(28px, 7vw, 64px); border: 1px solid #00d9ff66; border-radius: 24px; text-align: center; background: linear-gradient(145deg, #071a25, #03090f); box-shadow: 0 0 60px #00d9ff18; }
              .mark { display: inline-grid; place-items: center; width: 72px; height: 72px; border: 2px solid #00d9ff; border-radius: 50%; color: #00d9ff; font-size: 30px; font-weight: 800; box-shadow: 0 0 24px #00d9ff66; }
              h1 { margin: 24px 0 12px; color: #00d9ff; font-size: clamp(2rem, 7vw, 4rem); letter-spacing: .08em; text-transform: uppercase; }
              p { margin: 0 auto 28px; max-width: 520px; color: #b8d4df; font-size: 1.05rem; line-height: 1.7; }
              a { display: inline-block; padding: 14px 24px; border: 1px solid #00d9ff; border-radius: 10px; background: #00d9ff1c; color: #fff; font-weight: 700; text-decoration: none; }
              a:hover { background: #00d9ff36; }
              small { display: block; margin-top: 24px; color: #70909c; }
            </style>
          </head>
          <body>
            <main>
              <div class="mark" aria-hidden="true">P</div>
              <h1>Prince E2EE Convo</h1>
              <p>The deployment is live. Open the Streamlit workspace to use the complete encrypted conversation automation interface.</p>
              <a href="{{ streamlit_url }}" target="_blank" rel="noopener noreferrer">Open Web Interface</a>
              <small>Service status: online</small>
            </main>
          </body>
        </html>
        """,
        streamlit_url=STREAMLIT_APP_URL,
    )


@app.get("/health")
def health():
    return {"status": "ok", "service": "prince-e2ee-convo"}
