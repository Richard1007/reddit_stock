#!/usr/bin/env python3
"""
Simple test script with hardcoded credentials from env_example.txt
"""

import praw


def test_connection():
    """Test Reddit API connection with direct credentials."""
    
    # Direct credentials from env_example.txt
    credentials = {
        'client_id': 'r30D7VvkUutFJtuQ4YNRsg',
        'client_secret': 'W4e7mRPBHTtPmkS7ui5P60HgFbVX_A',
        'user_agent': 'desktop:stocksentiment:v1.0.0',
        'username': 'Professional-Skin424',
        'password': 'Phh20001007!'
    }
    
    try:
        # Create Reddit instance
        print("🔗 Connecting to Reddit API...")
        reddit = praw.Reddit(
            client_id=credentials['client_id'],
            client_secret=credentials['client_secret'],
            user_agent=credentials['user_agent'],
            username=credentials['username'],
            password=credentials['password']
        )
        
        # Test connection
        user = reddit.user.me()
        print(f"✅ Successfully connected as: {user}")
        print(f"📖 Read-only mode: {reddit.read_only}")
        
        # Test basic search (just 1 result to verify)
        print("🔍 Testing search functionality...")
        subreddit = reddit.subreddit("all")
        search_results = list(subreddit.search("Google stock", limit=1))
        
        if search_results:
            print("✅ Search functionality working!")
            print(f"Sample result: {search_results[0].title[:50]}...")
            print(f"From subreddit: r/{search_results[0].subreddit}")
        else:
            print("⚠️  No results found for 'Google stock'")
        
        print("\n🎉 Connection test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False


if __name__ == "__main__":
    print("Reddit API Simple Connection Test")
    print("=" * 35)
    test_connection()