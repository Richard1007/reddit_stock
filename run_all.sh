#!/bin/bash
# Extract comments from Reddit posts from past week
python reddit_search.py -s "Daily Discussion Thread for June 12" -l 1 -o relevance
python reddit_search.py -s "Daily Discussion Thread for June 11" -l 1 -o relevance
python reddit_search.py -s "Daily Discussion Thread for June 10" -l 1 -o relevance
python reddit_search.py -s "Daily Discussion Thread for June 09" -l 1 -o relevance