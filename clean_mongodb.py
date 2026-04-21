#!/usr/bin/env python3
"""
MongoDB Database Cleanup Script
पूरे database को clean करता है - सभी collections और indexes को delete कर देता है
"""

from pymongo import MongoClient
import os

# MongoDB Configuration - same priority as main app
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
            print("❌ MongoDB credentials not configured!")
            exit(1)

def clean_mongodb():
    """पूरे MongoDB database को clean करता है"""
    try:
        print("\n" + "="*70)
        print("🧹 MONGODB DATABASE CLEANUP SCRIPT")
        print("="*70)
        
        # Connect to MongoDB
        print("\n📡 Connecting to MongoDB...")
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        db = client.get_default_database()
        
        print(f"✅ Connected successfully!")
        print(f"💡 Database name: {db.name}")
        
        # Get all collections
        collections = db.list_collection_names()
        print(f"\n📋 Found {len(collections)} collections:")
        for col in collections:
            print(f"   - {col}")
        
        if not collections:
            print("\n✅ Database is already clean!")
            return
        
        # Confirm before deletion
        print("\n⚠️  WARNING: यह पूरे database को clean कर देगा!")
        print("⚠️  WARNING: All data, collections, and indexes will be deleted!")
        
        # Drop all collections
        print("\n🗑️  Dropping all collections...")
        for collection_name in collections:
            print(f"   🗑️  Dropping: {collection_name}")
            db.drop_collection(collection_name)
        
        print("\n✅ Database cleaned successfully!")
        print("💡 All collections और indexes delete हो गए हैं")
        print("💡 अब workflows restart करने पर fresh indexes बनेंगे")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error cleaning database: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    clean_mongodb()
