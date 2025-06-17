# Reddit Search API

A Python script to search and extract posts and comments from Reddit using the PRAW (Python Reddit API Wrapper) library.

## Features

- Search Reddit posts with configurable parameters
- Extract posts and their comments
- Save results in JSON format
- Configurable search parameters (time filter, sort method, etc.)
- Rate limiting and error handling

## Prerequisites

- Python 3.6 or higher
- Reddit API credentials

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/reddit-search-api.git
cd reddit-search-api
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up your Reddit API credentials:
   - Go to https://www.reddit.com/prefs/apps
   - Create a new application
   - Copy `.env.example` to `.env`
   - Fill in your credentials in `.env`:
     ```
     REDDIT_CLIENT_ID=your_client_id_here
     REDDIT_CLIENT_SECRET=your_client_secret_here
     REDDIT_USER_AGENT=your_user_agent_here
     REDDIT_USERNAME=your_username_here
     REDDIT_PASSWORD=your_password_here
     ```

## Usage

Basic usage:
```bash
python reddit_search.py -s "search term" -l 5 -t week -o hot
```

### Parameters

- `-s, --search-term`: Search term to look for (default: "Google stock")
- `-l, --limit`: Number of posts to retrieve (default: 2)
- `-t, --time-filter`: Time filter for posts (day, week, month, year, all)
- `-o, --sort`: Sort method (relevance, hot, top, new, comments)

### Examples

```bash
# Search for Tesla stock posts
python reddit_search.py -s "Tesla stock" -l 5 -t day -o hot

# Search for daily discussion threads
python reddit_search.py -s "Daily Discussion Thread" -l 1 -t all -o new
```

## Output

Results are saved in JSON format in the `results` directory, organized by date.


## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 