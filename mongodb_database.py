"""
MongoDB Database Module
सभी user data, configurations, sessions और logs को MongoDB में store करता है
"""

from pymongo import MongoClient, ReturnDocument
from pymongo.errors import DuplicateKeyError, ConnectionFailure
import hashlib
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from pathlib import Path
import secrets
import os
import json
import uuid

# MongoDB Configuration
# Priority: Streamlit secrets > Environment variable > mongodb_config.py
try:
    import streamlit as st
    if hasattr(st, 'secrets') and 'MONGODB_URI' in st.secrets:
        MONGODB_URI = st.secrets['MONGODB_URI']
        print("🔐 Using MongoDB credentials from Streamlit Secrets")
    else:
        raise ImportError("Streamlit secrets not available")
except (ImportError, FileNotFoundError):
    try:
        from mongodb_config import MONGODB_URI
        print("🔐 Using MongoDB credentials from mongodb_config.py")
    except ImportError:
        MONGODB_URI = os.environ.get('MONGODB_URI', '')
        if MONGODB_URI:
            print("🔐 Using MongoDB credentials from Environment Variables")
        else:
            print("⚠️ MongoDB credentials not configured!")

# Encryption Key Management
ENCRYPTION_KEY_FILE = Path(__file__).parent / '.encryption_key'

def get_encryption_key():
    """
    Get encryption key for cookie storage
    Priority: Streamlit Secrets > Environment Variable > Local File
    """
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'ENCRYPTION_KEY' in st.secrets:
            key = st.secrets['ENCRYPTION_KEY']
            if isinstance(key, str):
                key = key.encode('utf-8')
            print("🔐 Using shared encryption key from Streamlit Secrets")
            return key
    except (ImportError, Exception):
        pass
    
    env_key = os.environ.get('ENCRYPTION_KEY')
    if env_key:
        if isinstance(env_key, str):
            env_key = env_key.encode('utf-8')
        print("🔐 Using shared encryption key from Environment Variable")
        return env_key
    
    if ENCRYPTION_KEY_FILE.exists():
        with open(ENCRYPTION_KEY_FILE, 'rb') as f:
            print("⚠️ Using local encryption key (development mode)")
            print("💡 For production: Set ENCRYPTION_KEY in Streamlit Secrets or Environment")
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(ENCRYPTION_KEY_FILE, 'wb') as f:
            f.write(key)
        print("🔑 Generated new encryption key (development mode)")
        print(f"📋 Key (base64): {key.decode('utf-8')}")
        print("💡 Copy this key to ENCRYPTION_KEY secret in all deployments!")
        return key

ENCRYPTION_KEY = get_encryption_key()
cipher_suite = Fernet(ENCRYPTION_KEY)

# MongoDB Client
_mongodb_client = None
_mongodb_db = None

def get_mongodb_client():
    """MongoDB client connection singleton"""
    global _mongodb_client, _mongodb_db
    if _mongodb_client is None:
        try:
            if not MONGODB_URI:
                print("❌ MongoDB URI not configured!")
                print("\n📋 Please set MONGODB_URI:")
                print("1. Create account at https://www.mongodb.com/cloud/atlas")
                print("2. Create new cluster")
                print("3. Get connection string from Connect button")
                print("4. Add to Replit Secrets or .streamlit/secrets.toml\n")
                return None, None
            
            _mongodb_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
            _mongodb_client.admin.command('ping')
            _mongodb_db = _mongodb_client.get_default_database()
            
            print("✅ MongoDB connected successfully!")
            print(f"💡 Using database: {_mongodb_db.name}")
            print("💡 All user data will be stored in MongoDB")
            
            init_db()
            
        except ConnectionFailure as e:
            print(f"❌ MongoDB connection error: {e}")
            print("💡 App will continue, but database features will be unavailable")
            return None, None
        except Exception as e:
            print(f"❌ MongoDB error: {e}")
            return None, None
    
    return _mongodb_client, _mongodb_db

def init_db():
    """Initialize MongoDB collections and indexes"""
    try:
        _, db = get_mongodb_client()
        if db is None:
            return False
        
        db.users.create_index("username", unique=True)
        db.user_sessions.create_index("token_hash", unique=True)
        db.user_sessions.create_index("expires_at")
        db.user_configs.create_index("user_id", unique=True)
        db.automation_logs.create_index("user_id")
        db.automation_locks.create_index("user_id", unique=True)
        db.automation_instances.create_index("instance_id")
        db.app_uptime.create_index("id", unique=True)
        
        print("✅ MongoDB indexes created")
        return True
    except Exception as e:
        print(f"⚠️ MongoDB initialization: {e}")
        return False

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def hash_token(token):
    """Hash session token using SHA-256"""
    return hashlib.sha256(token.encode()).hexdigest()

def create_user(username, password):
    """Create new user"""
    try:
        _, db = get_mongodb_client()
        if db is None:
            return False, "MongoDB not connected. Please configure credentials."
        
        password_hash = hash_password(password)
        
        user_id = str(uuid.uuid4())
        
        try:
            db.users.insert_one({
                "_id": user_id,
                "username": username,
                "password_hash": password_hash,
                "created_at": datetime.utcnow()
            })
        except DuplicateKeyError:
            return False, "Username already exists!"
        
        db.user_configs.insert_one({
            "user_id": user_id,
            "chat_id": "",
            "name_prefix": "",
            "delay": 30,
            "cookies_encrypted": "",
            "messages": "",
            "automation_running": 0,
            "fb_profile_id": "",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        
        print(f"✅ User created: {username}")
        return True, "Account created successfully!"
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return False, f"Error: {str(e)}"

def verify_user(username, password):
    """Verify user credentials and return user_id"""
    try:
        _, db = get_mongodb_client()
        if db is None:
            return None
        
        password_hash = hash_password(password)
        
        user = db.users.find_one({
            "username": username,
            "password_hash": password_hash
        })
        
        if user:
            return str(user['_id'])
        return None
    except Exception as e:
        print(f"❌ Error verifying user: {e}")
        return None

def get_user_id(username):
    """Get user ID from username"""
    try:
        _, db = get_mongodb_client()
        if db is None:
            return None
        user = db.users.find_one({"username": username})
        return str(user['_id']) if user else None
    except Exception as e:
        print(f"❌ Error getting user ID: {e}")
        return None

def create_session(username):
    """Create session token for user"""
    try:
        _, db = get_mongodb_client()
        if db is None:
            return None
        user_id = get_user_id(username)
        if not user_id:
            return None
        
        token = secrets.token_urlsafe(32)
        token_hash = hash_token(token)
        
        expires_at = datetime.utcnow() + timedelta(days=7)
        
        db.user_sessions.insert_one({
            "token_hash": token_hash,
            "user_id": user_id,
            "issued_at": datetime.utcnow(),
            "expires_at": expires_at,
            "revoked": 0
        })
        
        print(f"✅ Session created for user: {username}")
        return token
    except Exception as e:
        print(f"❌ Error creating session: {e}")
        return None

def verify_session(token):
    """Verify session token and return user data dict with user_id and username"""
    try:
        _, db = get_mongodb_client()
        if db is None:
            return None
        token_hash = hash_token(token)
        
        session = db.user_sessions.find_one({
            "token_hash": token_hash,
            "revoked": 0,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if not session:
            return None
        
        user_id = session['user_id']
        user = db.users.find_one({"_id": user_id})
        
        if user:
            return {
                'user_id': user_id,
                'username': user['username']
            }
        return None
    except Exception as e:
        print(f"❌ Error verifying session: {e}")
        return None

def revoke_session(token):
    """Revoke session token"""
    try:
        _, db = get_mongodb_client()
        if db is None:
            return False
        token_hash = hash_token(token)
        db.user_sessions.update_one(
            {"token_hash": token_hash},
            {"$set": {"revoked": 1}}
        )
        return True
    except Exception as e:
        print(f"❌ Error revoking session: {e}")
        return False

def revoke_session_token(token):
    """Alias for revoke_session"""
    return revoke_session(token)

def save_user_config(username, chat_id, name_prefix, delay, cookies_json, messages, fb_profile_id=""):
    """Save user configuration"""
    try:
        _, db = get_mongodb_client()
        if db is None:
            return False
        
        user_id = get_user_id(username)
        if not user_id:
            return False
        
        cookies_encrypted = cipher_suite.encrypt(cookies_json.encode()).decode()
        
        db.user_configs.update_one(
            {"user_id": user_id},
            {"$set": {
                "chat_id": chat_id,
                "name_prefix": name_prefix,
                "delay": delay,
                "cookies_encrypted": cookies_encrypted,
                "messages": messages,
                "fb_profile_id": fb_profile_id,
                "updated_at": datetime.utcnow()
            }},
            upsert=True
        )
        
        print(f"✅ Config saved for user: {username}")
        return True
    except Exception as e:
        print(f"❌ Error saving config: {e}")
        return False

def get_user_config(user_id_or_username):
    """Get user configuration"""
    try:
        _, db = get_mongodb_client()
        if db is None:
            return None
        
        if not user_id_or_username.isdigit() and '-' not in str(user_id_or_username):
            user_id = get_user_id(user_id_or_username)
        else:
            user_id = user_id_or_username
        
        if not user_id:
            return None
        
        config = db.user_configs.find_one({"user_id": user_id})
        
        if not config:
            return None
        
        try:
            if config.get('cookies_encrypted'):
                cookies_json = cipher_suite.decrypt(config['cookies_encrypted'].encode()).decode()
            else:
                cookies_json = ""
        except:
            cookies_json = ""
        
        return {
            'chat_id': config.get('chat_id', ''),
            'name_prefix': config.get('name_prefix', ''),
            'delay': config.get('delay', 30),
            'cookies': cookies_json,
            'messages': config.get('messages', ''),
            'automation_running': config.get('automation_running', 0),
            'fb_profile_id': config.get('fb_profile_id', '')
        }
    except Exception as e:
        print(f"❌ Error getting config: {e}")
        return None

def set_automation_status(username, status):
    """Set automation running status"""
    return set_automation_running(get_user_id(username), status)

def set_automation_running(user_id, status):
    """Set automation running status, creates row if it doesn't exist"""
    try:
        _, db = get_mongodb_client()
        if db is None:
            print(f"❌ [set_automation_running] MongoDB client is None for user {user_id}")
            return False
        
        status_int = 1 if status else 0
        user_id_str = str(user_id)
        
        print(f"🔍 [set_automation_running] Attempting to update user {user_id} to status {status_int}")
        
        result = db.user_configs.update_one(
            {"user_id": user_id_str},
            {"$set": {
                "automation_running": status_int,
                "updated_at": datetime.utcnow()
            }},
            upsert=True
        )
        
        print(f"🔍 [set_automation_running] Update result for user {user_id}: matched={result.matched_count}, modified={result.modified_count}")
        
        verify = db.user_configs.find_one({"user_id": user_id_str})
        actual_status = verify.get('automation_running', None) if verify else None
        print(f"✅ [set_automation_running] User {user_id} status set to {status_int}, verified as: {actual_status}")
        
        if actual_status != status_int:
            print(f"⚠️ [set_automation_running] WARNING: Status mismatch! Set {status_int} but got {actual_status}")
        
        return True
    except Exception as e:
        print(f"❌ [set_automation_running] Error for user {user_id}: {e}")
        import traceback
        print(f"❌ [set_automation_running] Traceback: {traceback.format_exc()}")
        return False

def get_automation_running(user_id):
    """
    Get automation running status
    Returns:
        1/True: Automation is running
        0/False: Automation is explicitly stopped
        None: Status unknown (no connection, missing row, or error)
    """
    try:
        _, db = get_mongodb_client()
        if db is None:
            print(f"⚠️ [get_automation_running] MongoDB client is None for user {user_id}")
            return None
        
        user_id_str = str(user_id)
        
        config = db.user_configs.find_one({"user_id": user_id_str})
        
        if not config:
            print(f"⚠️ [get_automation_running] No user_configs row found for user {user_id} - returning None")
            return None
        
        status = config.get('automation_running', 0)
        print(f"✅ [get_automation_running] User {user_id} status: {status}")
        return status
    except Exception as e:
        print(f"❌ [get_automation_running] Error for user {user_id}: {e}")
        return None

def deduplicate_user_config(user_id):
    """MongoDB uses unique index on user_id, so no duplicates possible"""
    print(f"✅ [deduplicate_user_config] MongoDB prevents duplicates via unique index")
    return True

def get_username(user_id):
    """Get username from user ID"""
    try:
        _, db = get_mongodb_client()
        if db is None:
            return None
        user = db.users.find_one({"_id": user_id})
        return user['username'] if user else None
    except Exception as e:
        print(f"❌ Error getting username: {e}")
        return None

def get_all_running_users():
    """Get all users with automation running"""
    try:
        _, db = get_mongodb_client()
        if db is None:
            return []
        
        configs = db.user_configs.find({"automation_running": 1})
        
        running_users = []
        for config in configs:
            user_id = config['user_id']
            chat_id = config.get('chat_id', '')
            username = get_username(user_id)
            if username:
                running_users.append({
                    'user_id': user_id,
                    'username': username,
                    'chat_id': chat_id
                })
        
        return running_users
    except Exception as e:
        print(f"❌ Error getting running users: {e}")
        return []

def validate_session_token(token):
    """Alias for verify_session"""
    return verify_session(token)

def cleanup_expired_sessions():
    """Clean up expired sessions"""
    try:
        _, db = get_mongodb_client()
        if db is None:
            return 0
        
        result = db.user_sessions.delete_many({
            "expires_at": {"$lt": datetime.utcnow()}
        })
        return result.deleted_count
    except Exception as e:
        print(f"❌ Error cleaning up sessions: {e}")
        return 0

def get_automation_logs(user_id):
    """Get automation logs for user"""
    try:
        _, db = get_mongodb_client()
        if db is None:
            return []
        
        log_doc = db.automation_logs.find_one(
            {"user_id": user_id},
            sort=[("timestamp", -1)]
        )
        
        if log_doc:
            return log_doc.get('logs', '').split('\n') if log_doc.get('logs') else []
        return []
    except Exception as e:
        print(f"❌ Error getting logs: {e}")
        return []

def save_automation_logs(user_id, logs):
    """Save automation logs for user"""
    try:
        _, db = get_mongodb_client()
        if db is None:
            return False
        
        logs_text = '\n'.join(logs) if isinstance(logs, list) else logs
        
        db.automation_logs.update_one(
            {"user_id": user_id},
            {"$set": {
                "logs": logs_text,
                "timestamp": datetime.utcnow()
            }},
            upsert=True
        )
        
        return True
    except Exception as e:
        print(f"❌ Error saving logs: {e}")
        return False

def clear_automation_logs(user_id):
    """Clear automation logs for user"""
    try:
        _, db = get_mongodb_client()
        if db is None:
            return False
        
        db.automation_logs.delete_many({"user_id": user_id})
        return True
    except Exception as e:
        print(f"❌ Error clearing logs: {e}")
        return False

def get_instance_id():
    """Get or generate unique instance ID"""
    instance_file = Path(__file__).parent / '.instance_id'
    if instance_file.exists():
        with open(instance_file, 'r') as f:
            return f.read().strip()
    else:
        instance_id = str(uuid.uuid4())
        with open(instance_file, 'w') as f:
            f.write(instance_id)
        return instance_id

def acquire_automation_lock(user_id, instance_id=None, ttl_seconds=20):
    """Acquire automation lock for distributed system (atomic operation with unique index)"""
    try:
        _, db = get_mongodb_client()
        if db is None:
            return False
        
        if instance_id is None:
            instance_id = get_instance_id()
        
        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=ttl_seconds)
        
        try:
            result = db.automation_locks.find_one_and_update(
                {
                    "user_id": user_id,
                    "expires_at": {"$lt": now}
                },
                {"$set": {
                    "instance_id": instance_id,
                    "acquired_at": now,
                    "heartbeat_at": now,
                    "expires_at": expires_at
                }},
                upsert=False,
                return_document=ReturnDocument.AFTER
            )
            
            if result:
                return True
            
            result = db.automation_locks.insert_one({
                "user_id": user_id,
                "instance_id": instance_id,
                "acquired_at": now,
                "heartbeat_at": now,
                "expires_at": expires_at
            })
            return result.inserted_id is not None
            
        except DuplicateKeyError:
            return False
            
    except Exception as e:
        print(f"❌ Error acquiring lock: {e}")
        return False

def release_automation_lock(user_id, instance_id=None):
    """Release automation lock"""
    try:
        _, db = get_mongodb_client()
        if db is None:
            return False
        
        db.automation_locks.delete_many({"user_id": user_id})
        return True
    except Exception as e:
        print(f"❌ Error releasing lock: {e}")
        return False

def cleanup_expired_locks():
    """Clean up expired automation locks"""
    try:
        _, db = get_mongodb_client()
        if db is None:
            return 0
        
        result = db.automation_locks.delete_many({
            "expires_at": {"$lt": datetime.utcnow()}
        })
        return result.deleted_count
    except Exception as e:
        print(f"❌ Error cleaning up locks: {e}")
        return 0

def update_lock_heartbeat(user_id, instance_id=None, ttl_seconds=20):
    """Update lock heartbeat (atomic operation)"""
    try:
        _, db = get_mongodb_client()
        if db is None:
            return False
        
        if instance_id is None:
            instance_id = get_instance_id()
        
        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=ttl_seconds)
        
        result = db.automation_locks.update_one(
            {
                "user_id": user_id,
                "instance_id": instance_id
            },
            {"$set": {
                "heartbeat_at": now,
                "expires_at": expires_at
            }}
        )
        
        return result.matched_count > 0
    except Exception as e:
        print(f"❌ Error updating heartbeat: {e}")
        return False

def register_automation_instance(user_id, instance_id=None):
    """Register automation instance"""
    try:
        _, db = get_mongodb_client()
        if db is None:
            return False
        
        if instance_id is None:
            instance_id = get_instance_id()
        
        db.automation_instances.update_one(
            {"user_id": user_id, "instance_id": instance_id},
            {"$set": {
                "started_at": datetime.utcnow(),
                "heartbeat_at": datetime.utcnow(),
                "status": "active"
            }},
            upsert=True
        )
        
        return True
    except Exception as e:
        print(f"❌ Error registering instance: {e}")
        return False

def update_instance_heartbeat(user_id, instance_id=None, ttl_seconds=60):
    """Update instance heartbeat to keep it alive"""
    try:
        _, db = get_mongodb_client()
        if db is None:
            return False
        
        if instance_id is None:
            instance_id = get_instance_id()
        
        result = db.automation_instances.update_one(
            {"user_id": user_id, "instance_id": instance_id},
            {"$set": {
                "heartbeat_at": datetime.utcnow(),
                "status": "active"
            }}
        )
        
        return result.matched_count > 0
    except Exception as e:
        print(f"❌ Error updating instance heartbeat: {e}")
        return False

def remove_automation_instance(user_id, instance_id=None):
    """Remove automation instance registration"""
    try:
        _, db = get_mongodb_client()
        if db is None:
            return False
        
        if instance_id is None:
            instance_id = get_instance_id()
        
        db.automation_instances.delete_many({"user_id": user_id, "instance_id": instance_id})
        return True
    except Exception as e:
        print(f"❌ Error removing instance: {e}")
        return False

def get_or_create_app_uptime():
    """Get or create app uptime singleton record"""
    try:
        _, db = get_mongodb_client()
        if db is None:
            return datetime.utcnow()
        
        result = db.app_uptime.find_one({"id": 1})
        
        if result:
            start_time_str = result['started_at']
            if isinstance(start_time_str, datetime):
                return start_time_str
            return datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
        
        start_time = datetime.utcnow()
        try:
            db.app_uptime.insert_one({
                "id": 1,
                "started_at": start_time,
                "last_restart_at": start_time
            })
            print("🚀 New app uptime tracking started!")
        except DuplicateKeyError:
            result = db.app_uptime.find_one({"id": 1})
            if result:
                start_time_str = result['started_at']
                if isinstance(start_time_str, datetime):
                    return start_time_str
                return datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
        
        return start_time
    except Exception as e:
        print(f"⚠️ Uptime tracking error: {e}")
        return datetime.utcnow()

def get_app_uptime_string():
    """Get formatted uptime string"""
    try:
        start_time = get_or_create_app_uptime()
        current_time = datetime.utcnow()
        
        uptime_delta = current_time - start_time
        
        days = uptime_delta.days
        hours, remainder = divmod(uptime_delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        
        if not parts:
            parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
        
        return ", ".join(parts)
    except Exception as e:
        print(f"⚠️ Error calculating uptime: {e}")
        return "Unable to calculate"

def update_app_restart_time():
    """Update last restart time"""
    try:
        _, db = get_mongodb_client()
        if db is None:
            return False
        
        restart_time = datetime.utcnow()
        
        db.app_uptime.update_one(
            {"id": 1},
            {"$set": {"last_restart_at": restart_time}},
            upsert=True
        )
        print("🔄 App restart time updated!")
        
        return True
    except Exception as e:
        print(f"⚠️ Error updating restart time: {e}")
        return False

def get_lock_owner(user_id):
    """Get the instance ID that owns the automation lock for this user"""
    try:
        _, db = get_mongodb_client()
        if db is None:
            return None
        
        lock = db.automation_locks.find_one({"user_id": str(user_id)})
        
        if lock:
            expires_at = lock['expires_at']
            if datetime.utcnow() < expires_at:
                return lock['instance_id']
        
        return None
    except Exception as e:
        print(f"❌ Error getting lock owner: {e}")
        return None

def register_global_instance_heartbeat(instance_id, role='secondary', ttl_seconds=20):
    """Register global instance heartbeat with role"""
    try:
        _, db = get_mongodb_client()
        if db is None:
            return False
        
        heartbeat_time = datetime.utcnow()
        
        db.automation_instances.update_one(
            {"instance_id": instance_id},
            {"$set": {
                "user_id": "global",
                "heartbeat_at": heartbeat_time,
                "status": role
            },
            "$setOnInsert": {
                "started_at": heartbeat_time
            }},
            upsert=True
        )
        
        return True
    except Exception as e:
        print(f"❌ Error registering global heartbeat: {e}")
        return False

def check_primary_instance_alive(heartbeat_timeout=15):
    """Check if primary instance is still alive"""
    try:
        _, db = get_mongodb_client()
        if db is None:
            return False
        
        instances = db.automation_instances.find({"status": "primary"})
        
        current_time = datetime.utcnow()
        for instance in instances:
            heartbeat_time = instance.get('heartbeat_at')
            if not heartbeat_time:
                continue
                
            # Handle different types
            if isinstance(heartbeat_time, str):
                heartbeat_time = datetime.fromisoformat(heartbeat_time.replace('Z', '+00:00'))
            elif isinstance(heartbeat_time, (int, float)):
                heartbeat_time = datetime.fromtimestamp(heartbeat_time)
            elif not isinstance(heartbeat_time, datetime):
                continue
            
            time_since_heartbeat = (current_time - heartbeat_time).total_seconds()
            
            if time_since_heartbeat < heartbeat_timeout:
                return True
        
        return False
    except Exception as e:
        print(f"❌ Error checking primary instance: {e}")
        return False

def deactivate_global_instance(instance_id):
    """Deactivate global instance"""
    try:
        _, db = get_mongodb_client()
        if db is None:
            return False
        
        db.automation_instances.update_one(
            {"instance_id": instance_id},
            {"$set": {"status": "inactive"}}
        )
        
        return True
    except Exception as e:
        print(f"❌ Error deactivating global instance: {e}")
        return False

def clear_all_database_data():
    """
    DANGER: Clear all data from all MongoDB collections
    This action is IRREVERSIBLE!
    """
    try:
        _, db = get_mongodb_client()
        if db is None:
            return False, "MongoDB not connected", {}
        
        stats = {}
        
        collections = [
            'automation_locks',
            'automation_logs',
            'automation_instances',
            'user_message_index',
            'user_sessions',
            'user_configs',
            'users'
        ]
        
        for collection in collections:
            try:
                count = db[collection].count_documents({})
                db[collection].delete_many({})
                stats[collection] = count
                print(f"✅ Cleared {count} records from {collection}")
            except Exception as e:
                print(f"⚠️ Error clearing {collection}: {e}")
                stats[collection] = 0
        
        message = f"🗑️ Database cleared! Total records removed: {sum(stats.values())}"
        return True, message, stats
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        return False, f"Error: {str(e)}", {}

print("📦 MongoDB Database Module loaded!")
print("💡 Using MongoDB for data storage")
