# 🚀 PRINCE E2EE - Facebook Automation Tool

A powerful Streamlit-based Facebook automation tool with E2EE messaging support.

Created by **Prince Malhotra**

## 🌟 Features

- 🔐 **Secure Authentication** - Supabase-based user management with session tokens
- 💬 **E2EE Messaging** - End-to-end encrypted Facebook messaging
- 🤖 **Automated Messages** - Send messages automatically with custom delays
- 📊 **Real-time Logs** - Live monitoring of automation status
- 🔄 **Auto-Resume** - Automatically resumes automation after app restarts
- 💾 **Persistent Storage** - Supabase PostgreSQL for reliable data storage
- 🛡️ **Health Monitoring** - Auto-restart on crashes (Replit only)
- 📱 **Telegram Notifications** - Get notified about automation events

## 🚀 Streamlit Cloud Deployment

### Prerequisites

1. Supabase account with a project setup
2. Telegram Bot Token (optional, for notifications)
3. Facebook account cookies

### Environment Variables

Add these secrets in Streamlit Cloud dashboard:

```
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_ADMIN_ID=your_telegram_chat_id
```

### Deployment Steps

1. **Fork or Clone** this repository
2. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Deploy to Streamlit Cloud"
   git push origin main
   ```
3. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your repository
   - Main file: `streamlit_app.py`
   - Add secrets in "Advanced settings"
   - Click "Deploy"

### Supabase Setup

1. Create a free account on [Supabase](https://supabase.com)
2. Create a new project
3. Run the SQL table creation scripts in SQL Editor
4. Get your Project URL and anon/public key from Settings > API
5. Add credentials to Streamlit secrets

## 📦 Requirements

All dependencies are listed in `requirements.txt`:
- streamlit
- selenium
- supabase
- requests
- bcrypt
- pytz
- And more...

## 🔧 Local Development

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py --server.port 5000
```

## 📱 Usage

1. **Sign Up** - Create your account
2. **Configure** - Add Chat ID, Cookies, Messages
3. **Start E2EE** - Begin automation
4. **Monitor** - Watch real-time logs
5. **Stop** - Stop automation anytime

## 🛡️ Security

- Passwords are hashed with bcrypt
- Session tokens with expiry
- Supabase PostgreSQL with encryption at rest
- Secure cookie handling

## 📞 Support

Created by **Prince Malhotra**

[Contact Developer on Facebook](https://www.facebook.com/profile.php?id=61567810846706)

## ⚠️ Disclaimer

This tool is for educational purposes. Use responsibly and in accordance with Facebook's Terms of Service.

## 📝 License

Private - All rights reserved
