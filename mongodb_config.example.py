# MongoDB Configuration Example
# यह file example है - इसे copy करके mongodb_config.py बनाएं और अपने credentials भरें

# MongoDB Atlas Connection String
# Format: mongodb+srv://username:password@cluster.mongodb.net/database_name
MONGODB_URI = "mongodb+srv://your_username:your_password@your_cluster.mongodb.net/your_database?retryWrites=true&w=majority"

# 📋 Setup Instructions:
# 1. MongoDB Atlas पे account बनाएं: https://www.mongodb.com/cloud/atlas
# 2. Free cluster create करें (M0)
# 3. Database user बनाएं (username/password)
# 4. Network Access में अपना IP add करें (या 0.0.0.0/0 for all)
# 5. Connect button click करें और connection string copy करें
# 6. इस file को mongodb_config.py के नाम से save करें
# 7. MONGODB_URI में अपनी connection string paste करें
# 8. <username>, <password>, और database name replace करें

# 💡 Production Deployment:
# Replit Secrets में MONGODB_URI add करें (safer!)
# या .streamlit/secrets.toml में:
# MONGODB_URI = "your_connection_string_here"
