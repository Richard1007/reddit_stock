import json
from openai import OpenAI
import time
import sys
import os
from config import OPENAI_API_KEY

# 🔑 Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# 🧠 1. Summarize the post content
def summarize_post(title, selftext):
    prompt = f"""
You are a financial summarizer. Given the title and selftext of a Reddit post, summarize its core message in 1-3 sentences.

### TITLE:
{title}

### SELF TEXT:
{selftext}

Respond with just the summary text.
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=150
    )
    return response.choices[0].message.content.strip()

# 🧠 2. Analyze comment with post summary
def analyze_comment(comment_body, post_summary):
    prompt = f"""
You are a financial assistant. Given a Reddit comment and the post summary it is replying to, analyze it and respond with exactly 3 lines:

SUMMARY: [1-sentence summary of the comment]
SENTIMENT: [positive/neutral/negative]
ACTION: [buy/sell/hold/NA]

### POST SUMMARY:
{post_summary}

### COMMENT:
{comment_body}

Remember: Respond with exactly 3 lines starting with SUMMARY:, SENTIMENT:, and ACTION:
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=200
    )
    
    raw_content = response.choices[0].message.content.strip()
    print(f"    📝 Raw response: {raw_content}")
    
    # Parse the 3 lines
    lines = raw_content.split('\n')
    result = {}
    
    for line in lines:
        line = line.strip()
        if line.startswith('SUMMARY:'):
            result['summary'] = line[8:].strip()
        elif line.startswith('SENTIMENT:'):
            result['sentiment'] = line[10:].strip().lower()
        elif line.startswith('ACTION:'):
            result['stock_action'] = line[7:].strip().lower()
    
    # Set defaults if missing
    result['summary'] = result.get('summary', 'No summary available')
    result['sentiment'] = result.get('sentiment', 'neutral')
    result['stock_action'] = result.get('stock_action', 'na')
    
    return result

# Get input file from command line or use default
if len(sys.argv) > 1:
    input_file = sys.argv[1]
else:
    input_file = "results/google stock/reddit_google_stock_day_hot.json"

print(f"🔄 Processing: {input_file}")

# Load Reddit data
with open(input_file, "r") as f:
    reddit_data = json.load(f)

# Process each post
for post in reddit_data["posts"]:
    try:
        post_summary = summarize_post(post["title"], post.get("selftext", ""))
        post["post_summary"] = post_summary
        print(f"\nPOST: {post['title'][:80]}...")
        print(f"SUMMARY: {post_summary}")
        
        for comment in post.get("comments", [])[:10]:  # Max 10 comments
            try:
                print(f"  🔄 Processing comment: {comment['body'][:50]}...")
                result = analyze_comment(comment["body"], post_summary)
                comment["summary"] = result["summary"]
                comment["sentiment"] = result["sentiment"]
                comment["stock_action"] = result["stock_action"]
                print(f"  ✓ {result['sentiment']}/{result['stock_action']}")
            except json.JSONDecodeError as e:
                comment["summary"] = ""
                comment["sentiment"] = "json_error"
                comment["stock_action"] = "NA"
                comment["error"] = f"JSON parsing error: {str(e)}"
                print(f"  ✗ JSON Error: {str(e)}")
                print(f"  Raw response might not be valid JSON")
            except Exception as e:
                comment["summary"] = ""
                comment["sentiment"] = "error"
                comment["stock_action"] = "NA"
                comment["error"] = str(e)
                print(f"  ✗ Comment error: {str(e)}")
                print(f"  Comment length: {len(comment['body'])} chars")
            time.sleep(0.5)
    except Exception as e:
        post["post_summary"] = ""
        post["error"] = str(e)
        print(f"  ✗ Post error")
        continue

# Save to same folder as input
input_dir = os.path.dirname(input_file)
input_name = os.path.splitext(os.path.basename(input_file))[0]
output_file = os.path.join(input_dir, f"{input_name}_summarized.json")

with open(output_file, "w") as f:
    json.dump(reddit_data, f, indent=2)

print(f"\n✅ Saved: {output_file}")
