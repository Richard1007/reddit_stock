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
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT, REDDIT_USERNAME, REDDIT_PASSWORD
import time


def load_credentials():
    """Load Reddit API credentials from config."""
    return {
        'client_id': REDDIT_CLIENT_ID,
        'client_secret': REDDIT_CLIENT_SECRET,
        'user_agent': REDDIT_USER_AGENT,
        'username': REDDIT_USERNAME,
        'password': REDDIT_PASSWORD
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


def extract_comments(comment_forest, max_depth=5, current_depth=0, batch_size=200, delay_seconds=30):
    """
    Recursively extract comments from a comment forest in batches.
    
    Args:
        comment_forest: PRAW CommentForest or list of comments
        max_depth: Maximum recursion depth to prevent infinite loops
        current_depth: Current recursion depth
        batch_size: Number of comments to process before taking a break (default: 200)
        delay_seconds: Number of seconds to wait between batches (default: 30)
    
    Returns:
        List of comment dictionaries
    """
    if current_depth >= max_depth:
        return []
    
    comments_data = []
    total_comments_processed = 0
    total_comments_scraped = 0
    last_milestone = 0
    
    # Replace MoreComments instances to get all comments
    if hasattr(comment_forest, 'replace_more'):
        try:
            # Process comments in batches
            batch_count = 0
            max_retries = 3
            
            while True:
                try:
                    batch_count += 1
                    remaining = None
                    
                    for retry in range(max_retries):
                        try:
                            remaining = comment_forest.replace_more(limit=batch_size)
                            break
                        except Exception as e:
                            if retry < max_retries - 1:
                                time.sleep(delay_seconds)
                            break
                    
                    if remaining is None:
                        break
                        
                    if not remaining:
                        break
                    
                    total_comments_processed += batch_size
                    
                    if remaining:
                        time.sleep(delay_seconds)
                        
                except Exception as e:
                    break
                    
        except Exception as e:
            pass
    
    # Get all comments as a flat list
    try:
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
                        'edited': comment.edited if comment.edited else False,
                        'num_replies': len(comment.replies) if hasattr(comment, 'replies') else 0
                    }
                    comments_data.append(comment_data)
                    total_comments_scraped += 1
                    
                    # Show progress every 1000 comments
                    if total_comments_scraped >= last_milestone + 1000:
                        print(f"Total comments scraped: {total_comments_scraped}")
                        last_milestone = (total_comments_scraped // 1000) * 1000
                        
                except Exception as e:
                    continue
                    
    except Exception as e:
        pass
    
    print(f"\nFinal comment count: {total_comments_scraped} comments scraped")
    return comments_data


def search_reddit_posts(reddit, search_term="Daily Discussion Thread", limit=1, time_filter="all", sort="new"):
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
    
    # Search only in r/wallstreetbets
    try:
        # Use wallstreetbets subreddit instead of all
        subreddit = reddit.subreddit("wallstreetbets")
        
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
    """Save data to JSON file in date-organized folder structure."""
    try:
        # Create date-based folder (MM-DD-YYYY format)
        current_date = datetime.now()
        date_folder = current_date.strftime("%m-%d-%Y")
        results_folder = os.path.join("results", date_folder)
        
        # Create the directory if it doesn't exist
        os.makedirs(results_folder, exist_ok=True)
        
        # Create the full file path
        full_path = os.path.join(results_folder, filename)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Data saved to {full_path}")
        return full_path
    except Exception as e:
        print(f"Error saving to JSON: {e}")
        return None


def create_argument_parser():
    """Create and configure the argument parser with all available options."""
    parser = argparse.ArgumentParser(
        description='Search Reddit posts with configurable parameters',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
For detailed usage examples and parameter options, see the documentation at the end of this file.

Basic usage:
  python reddit_search.py -s "search term" -l 5 -t week -o hot

Use --help to see all available options.
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
                'search_scope': 'r/wallstreetbets',
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
        saved_path = save_to_json(summary, filename)
        
        # Update the results summary with actual saved path
        if saved_path:
            summary['results_summary']['saved_path'] = saved_path
        
        # Print summary
        print(f"\nSummary:")
        print(f"Search executed at: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Found {len(posts)} posts for '{args.search_term}'")
        print(f"Total comments extracted: {sum(post.get('comments_count', 0) for post in posts)}")
        for i, post in enumerate(posts, 1):
            print(f"{i}. '{post['title'][:60]}...' in r/{post['subreddit']}")
            print(f"   Score: {post['score']}, Comments: {post['comments_count']}")
        
        print(f"\nData saved to {saved_path if saved_path else filename}")
        print(f"JSON includes: metadata, search parameters, results summary, and all post data")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure your Reddit API credentials are correct.")


if __name__ == "__main__":
    main()


"""
=================================================================================
REDDIT SEARCH SCRIPT - COMPLETE USAGE GUIDE
=================================================================================

📋 Available Parameters:
┌─────────────┬──────┬─────────────────┬──────────────────────────────────┬─────────────┬─────────────────────────┐
│ Parameter   │ Short│ Long            │ Choices                          │ Default     │ Description             │
├─────────────┼──────┼─────────────────┼──────────────────────────────────┼─────────────┼─────────────────────────┤
│ Search Term │ -s   │ --search-term   │ Any text string                  │ Google stock│ What to search for      │
│ Limit       │ -l   │ --limit         │ Any positive integer             │ 2           │ Number of posts         │
│ Time Filter │ -t   │ --time-filter   │ day, week, month, year, all      │ week        │ Time period to search   │
│ Sort Method │ -o   │ --sort          │ relevance, hot, top, new, comments│ relevance   │ How to sort results     │
└─────────────┴──────┴─────────────────┴──────────────────────────────────┴─────────────┴─────────────────────────┘
                # Show help

 Examples:
#   python reddit_search.py -s "Tesla stock" -l 5 -t day -o hot


  python reddit_search.py -s "Daily Discussion Thread for June 13" -l 1 -o relevance
  python reddit_search.py -s "Daily Discussion Thread for June 12" -l 1 -o relevance
  python reddit_search.py -s "Daily Discussion Thread for June 11" -l 1 -o relevance
  python reddit_search.py -s "Daily Discussion Thread for June 10" -l 1 -o relevance
  python reddit_search.py -s "Daily Discussion Thread for June 09" -l 1 -o relevance
"""