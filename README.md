# Reddit API - Google Stock Search

This Python script uses the official Reddit API (via PRAW) to search for posts about "Google stock" from the past week, retrieving the top 2 posts sorted by relevance along with all their comments as JSON data.

## Features

- Searches Reddit for "Google stock" posts from the past week
- Retrieves top 2 posts sorted by relevance
- Extracts all comments from each post
- Saves data as structured JSON
- Handles deleted users, comments, and API rate limits

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Reddit API Credentials

You need to create a Reddit application to get API credentials:

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Choose "script" as the application type
4. Fill in the required fields:
   - **Name**: Your app name (e.g., "Google Stock Search")
   - **Description**: Brief description
   - **About URL**: Can be left blank
   - **Redirect URI**: Use `http://localhost:8080` for script apps

5. After creating the app, note down:
   - **Client ID**: Found under the app name (short string)
   - **Client Secret**: The longer string labeled "secret"

### 3. Environment Configuration

The credentials are currently hardcoded in the scripts. You can modify them in:
- `reddit_search.py` 
- `simple_test.py`

Or use the format in `env_example.txt` to set up environment variables.

## Usage

### Quick Test

Run the connection test:

```bash
python simple_test.py
```

### Main Search

Run the main script:

```bash
python reddit_search.py
```

The script will:
1. Connect to Reddit API
2. Search for "Google stock" posts from the past week
3. Retrieve the top 2 posts sorted by relevance
4. Extract all comments from each post
5. Save everything to `reddit_google_stock_search.json`

## Output Format

The JSON output contains:

```json
{
  "search_term": "Google stock",
  "time_filter": "past week",
  "sort_by": "relevance",
  "posts_retrieved": 2,
  "search_timestamp": "2024-01-XX...",
  "posts": [
    {
      "id": "post_id",
      "title": "Post Title",
      "author": "username",
      "subreddit": "subreddit_name",
      "score": 100,
      "upvote_ratio": 0.95,
      "num_comments": 25,
      "created_utc": "2024-01-XX...",
      "url": "https://...",
      "permalink": "https://reddit.com/r/...",
      "selftext": "Post content...",
      "comments": [
        {
          "id": "comment_id",
          "author": "commenter",
          "body": "Comment text...",
          "score": 10,
          "created_utc": "2024-01-XX...",
          "permalink": "https://reddit.com/...",
          "is_submitter": false,
          "distinguished": null,
          "edited": false
        }
      ],
      "comments_count": 25
    }
  ]
}
```

## Configuration Options

You can modify the search parameters in the `main()` function:

- **search_term**: Change from "Google stock" to any search query
- **limit**: Change from 2 to get more/fewer posts
- **time_filter**: Options are "hour", "day", "week", "month", "year", "all"
- **sort**: Options are "relevance", "hot", "top", "new", "comments"

## Rate Limiting

The script includes built-in rate limiting protection:
- Limits comment expansion to prevent excessive API calls
- Handles API errors gracefully
- Uses PRAW's built-in rate limiting

## Troubleshooting

### Common Issues

1. **Authentication Error**: Verify your credentials in the `.env` file
2. **No Posts Found**: Try different search terms or time filters
3. **Rate Limited**: Wait a few minutes and try again
4. **Missing Comments**: Some comments may be deleted or load slowly

### Debug Mode

To see more detailed output, you can add print statements or check the console output for processing status.

## Requirements

- Python 3.7+
- PRAW (Python Reddit API Wrapper) 7.7.1
- python-dotenv 1.0.0
- Valid Reddit account and API credentials

## License

This project is for educational and research purposes. Please respect Reddit's API terms of service and rate limits. 