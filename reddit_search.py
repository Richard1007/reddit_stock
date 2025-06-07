#!/usr/bin/env python3
"""
Reddit API script to search for posts about "Google stock" from the past week.
Gets the top 2 posts sorted by relevance with all comments as JSON.
"""

import praw
import json
import os
from datetime import datetime, timedelta


def load_credentials():
    """Load Reddit API credentials directly."""
    return {
        'client_id': 'r30D7VvkUutFJtuQ4YNRsg',
        'client_secret': 'W4e7mRPBHTtPmkS7ui5P60HgFbVX_A',
        'user_agent': 'desktop:stocksentiment:v1.0.0',
        'username': 'Professional-Skin424',
        'password': 'Phh20001007!'
    }


def create_reddit_instance(credentials):
    """Create and return a Reddit instance."""
    return praw.Reddit(
        client_id=credentials['client_id'],
        client_secret=credentials['client_secret'],
        user_agent=credentials['user_agent'],
        username=credentials['username'],
        password=credentials['password']
    )


def extract_comments(comment_forest, max_depth=5, current_depth=0):
    """
    Recursively extract comments from a comment forest.
    
    Args:
        comment_forest: PRAW CommentForest or list of comments
        max_depth: Maximum recursion depth to prevent infinite loops
        current_depth: Current recursion depth
    
    Returns:
        List of comment dictionaries
    """
    if current_depth >= max_depth:
        return []
    
    comments_data = []
    
    # Replace MoreComments instances to get all comments
    if hasattr(comment_forest, 'replace_more'):
        try:
            comment_forest.replace_more(limit=32)  # Limit to prevent rate limiting
        except Exception as e:
            print(f"Warning: Could not load all comments: {e}")
    
    # Get all comments as a flat list
    if hasattr(comment_forest, 'list'):
        all_comments = comment_forest.list()
    else:
        all_comments = comment_forest
    
    for comment in all_comments:
        if hasattr(comment, 'body') and hasattr(comment, 'author'):
            try:
                comment_data = {
                    'id': comment.id,
                    'author': str(comment.author) if comment.author else '[deleted]',
                    'body': comment.body,
                    'score': comment.score,
                    'created_utc': datetime.fromtimestamp(comment.created_utc).isoformat(),
                    'permalink': f"https://reddit.com{comment.permalink}",
                    'is_submitter': comment.is_submitter,
                    'distinguished': comment.distinguished,
                    'edited': comment.edited if comment.edited else False
                }
                comments_data.append(comment_data)
            except Exception as e:
                print(f"Error processing comment {comment.id}: {e}")
                continue
    
    return comments_data


def search_reddit_posts(reddit, search_term="Google stock", limit=2, time_filter="week", sort="relevance"):
    """
    Search Reddit for posts matching the search term.
    
    Args:
        reddit: PRAW Reddit instance
        search_term: Search query
        limit: Number of posts to retrieve
        time_filter: Time filter (week, day, month, year, all)
        sort: Sort method (relevance, hot, top, new, comments)
    
    Returns:
        List of post dictionaries with comments
    """
    posts_data = []
    
    # Search across all of Reddit
    try:
        # Use reddit.subreddit("all") to search across all subreddits
        subreddit = reddit.subreddit("all")
        
        # Search for posts, sorted by relevance (default)
        search_results = subreddit.search(
            search_term, 
            sort=sort, 
            time_filter=time_filter, 
            limit=limit
        )
        
        for submission in search_results:
            try:
                print(f"Processing post: {submission.title[:50]}...")
                
                # Extract post data
                post_data = {
                    'id': submission.id,
                    'title': submission.title,
                    'author': str(submission.author) if submission.author else '[deleted]',
                    'subreddit': str(submission.subreddit),
                    'score': submission.score,
                    'upvote_ratio': submission.upvote_ratio,
                    'num_comments': submission.num_comments,
                    'created_utc': datetime.fromtimestamp(submission.created_utc).isoformat(),
                    'url': submission.url,
                    'permalink': f"https://reddit.com{submission.permalink}",
                    'selftext': submission.selftext,
                    'is_self': submission.is_self,
                    'over_18': submission.over_18,
                    'spoiler': submission.spoiler,
                    'locked': submission.locked,
                    'distinguished': submission.distinguished,
                    'stickied': submission.stickied
                }
                
                # Extract comments
                print(f"Extracting comments for post {submission.id}...")
                submission.comment_sort = "best"  # Sort comments by best
                comments = extract_comments(submission.comments)
                post_data['comments'] = comments
                post_data['comments_count'] = len(comments)
                
                posts_data.append(post_data)
                
            except Exception as e:
                print(f"Error processing submission {submission.id}: {e}")
                continue
    
    except Exception as e:
        print(f"Error during search: {e}")
        return []
    
    return posts_data


def save_to_json(data, filename="reddit_google_stock_search.json"):
    """Save data to JSON file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"Error saving to JSON: {e}")


def main():
    """Main function to run the Reddit search."""
    print("Reddit API - Google Stock Search")
    print("=" * 40)
    
    # Load credentials
    credentials = load_credentials()
    
    try:
        # Create Reddit instance
        print("Connecting to Reddit API...")
        reddit = create_reddit_instance(credentials)
        
        # Verify connection
        print(f"Connected as: {reddit.user.me()}")
        print(f"Read-only mode: {reddit.read_only}")
        
        # Search for posts
        print("\nSearching for 'Google stock' posts from the past week...")
        posts = search_reddit_posts(
            reddit, 
            search_term="Google stock", 
            limit=2, 
            time_filter="week",
            sort="relevance"
        )
        
        if not posts:
            print("No posts found matching the search criteria.")
            return
        
        # Create summary data
        summary = {
            'search_term': 'Google stock',
            'time_filter': 'past week',
            'sort_by': 'relevance',
            'posts_retrieved': len(posts),
            'search_timestamp': datetime.now().isoformat(),
            'posts': posts
        }
        
        # Save to JSON
        save_to_json(summary)
        
        # Print summary
        print(f"\nSummary:")
        print(f"Found {len(posts)} posts")
        for i, post in enumerate(posts, 1):
            print(f"{i}. '{post['title'][:60]}...' in r/{post['subreddit']}")
            print(f"   Score: {post['score']}, Comments: {post['comments_count']}")
        
        print(f"\nData saved to reddit_google_stock_search.json")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure your Reddit API credentials are correct.")


if __name__ == "__main__":
    main()