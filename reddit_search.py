#!/usr/bin/env python3
"""
Reddit API script to search for posts with configurable parameters.
Gets posts with all comments as JSON.
"""

import praw
import json
import os
import argparse
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


def create_argument_parser():
    """Create and configure the argument parser with all available options."""
    parser = argparse.ArgumentParser(
        description='Search Reddit posts with configurable parameters',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
REDDIT SEARCH SCRIPT - COMPLETE USAGE GUIDE
==========================================

📋 Available Parameters:
┌─────────────┬──────┬─────────────────┬──────────────────────────────────┬─────────────┬─────────────────────────┐
│ Parameter   │ Short│ Long            │ Choices                          │ Default     │ Description             │
├─────────────┼──────┼─────────────────┼──────────────────────────────────┼─────────────┼─────────────────────────┤
│ Search Term │ -s   │ --search-term   │ Any text string                  │ Google stock│ What to search for      │
│ Limit       │ -l   │ --limit         │ Any positive integer             │ 2           │ Number of posts         │
│ Time Filter │ -t   │ --time-filter   │ day, week, month, year, all      │ week        │ Time period to search   │
│ Sort Method │ -o   │ --sort          │ relevance, hot, top, new, comments│ relevance   │ How to sort results     │
└─────────────┴──────┴─────────────────┴──────────────────────────────────┴─────────────┴─────────────────────────┘


🚀 Real-World Examples:
  # Find trending Tesla discussions from today
  python reddit_search.py -s "Tesla" -l 5 -t day -o hot
  
  # Search for recent Bitcoin news
  python reddit_search.py -s "Bitcoin BTC news" -l 15 -t day -o new
  
        """
    )
    
    parser.add_argument(
        '-s', '--search-term',
        type=str,
        default='Google stock',
        help='Search term to look for (default: "Google stock")'
    )
    
    parser.add_argument(
        '-l', '--limit',
        type=int,
        default=2,
        help='Number of posts to retrieve (default: 2, recommended: 1-25)'
    )
    
    parser.add_argument(
        '-t', '--time-filter',
        type=str,
        default='week',
        choices=['day', 'week', 'month', 'year', 'all'],
        help='Time filter for posts (default: week) # Options: day, week, month, year, all'
    )
    
    parser.add_argument(
        '-o', '--sort',
        type=str,
        default='relevance',
        choices=['relevance', 'hot', 'top', 'new', 'comments'],
        help='Sort method for posts (default: relevance) # Options: relevance, hot, top, new, comments'
    )
    
    return parser


def main():
    """Main function to run the Reddit search."""
    # Parse command line arguments
    parser = create_argument_parser()
    args = parser.parse_args()
    
    print("Reddit API - Configurable Search")
    print("=" * 40)
    print(f"Search term: '{args.search_term}'")
    print(f"Number of posts: {args.limit}")
    print(f"Time filter: {args.time_filter}")
    print(f"Sort by: {args.sort}")
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
        
        # Search for posts using provided parameters
        print(f"\nSearching for '{args.search_term}' posts...")
        posts = search_reddit_posts(
            reddit, 
            search_term=args.search_term, 
            limit=args.limit, 
            time_filter=args.time_filter,
            sort=args.sort
        )
        
        if not posts:
            print("No posts found matching the search criteria.")
            return
        
        # Generate filename based on search parameters
        safe_search_term = "".join(c for c in args.search_term if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_search_term = safe_search_term.replace(' ', '_').lower()
        filename = f"reddit_{safe_search_term}_{args.time_filter}_{args.sort}.json"
        
        # Create summary data
        current_time = datetime.now()
        summary = {
            'metadata': {
                'search_executed_at': current_time.isoformat(),
                'search_executed_at_readable': current_time.strftime('%Y-%m-%d %H:%M:%S %Z'),
                'timezone': str(current_time.astimezone().tzinfo),
                'script_version': 'reddit_search.py v2.0',
                'reddit_api_version': 'PRAW',
                'execution_duration_note': 'Time taken depends on number of posts and comments'
            },
            'search_parameters': {
                'search_term': args.search_term,
                'limit_requested': args.limit,
                'time_filter': args.time_filter,
                'sort_method': args.sort,
                'search_scope': 'all_subreddits',
                'include_comments': True,
                'comment_sort': 'best'
            },
            'results_summary': {
                'posts_found': len(posts),
                'posts_requested': args.limit,
                'search_successful': len(posts) > 0,
                'total_comments_extracted': sum(post.get('comments_count', 0) for post in posts),
                'filename': filename
            },
            'posts': posts
        }
        
        # Save to JSON
        save_to_json(summary, filename)
        
        # Print summary
        print(f"\nSummary:")
        print(f"Search executed at: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Found {len(posts)} posts for '{args.search_term}'")
        print(f"Total comments extracted: {sum(post.get('comments_count', 0) for post in posts)}")
        for i, post in enumerate(posts, 1):
            print(f"{i}. '{post['title'][:60]}...' in r/{post['subreddit']}")
            print(f"   Score: {post['score']}, Comments: {post['comments_count']}")
        
        print(f"\nData saved to {filename}")
        print(f"JSON includes: metadata, search parameters, results summary, and all post data")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure your Reddit API credentials are correct.")


if __name__ == "__main__":
    main()