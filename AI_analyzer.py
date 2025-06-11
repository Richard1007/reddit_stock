import json
import sys
from collections import Counter
from datetime import datetime

def analyze_stock_sentiment(json_file):
    """Analyze Reddit sentiment and generate stock perception report."""
    
    # Load the data
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    print("=" * 80)
    print("📊 GOOGLE/ALPHABET STOCK - REDDIT PUBLIC PERCEPTION REPORT")
    print("=" * 80)
    
    # Extract search info
    search_term = data.get('search_parameters', {}).get('search_term', 'Unknown')
    search_date = data.get('metadata', {}).get('search_executed_at_readable', 'Unknown')
    
    print(f"\n🔍 Search Query: {search_term}")
    print(f"📅 Analysis Date: {search_date}")
    print(f"📈 Posts Analyzed: {len(data.get('posts', []))}")
    
    # Collect all comments with sentiment data
    all_comments = []
    google_related_posts = 0
    
    for post in data.get('posts', []):
        # Check if post is actually about Google/Alphabet stock
        title = post.get('title', '').lower()
        selftext = post.get('selftext', '').lower()
        
        is_google_related = any(keyword in title + ' ' + selftext for keyword in 
                               ['google', 'alphabet', 'googl', 'goog', 'gemini'])
        
        if is_google_related:
            google_related_posts += 1
        
        # Collect comments
        for comment in post.get('comments', []):
            if comment.get('sentiment') and comment.get('stock_action'):
                comment_data = {
                    'sentiment': comment.get('sentiment'),
                    'stock_action': comment.get('stock_action'),
                    'score': comment.get('score', 0),
                    'summary': comment.get('summary', ''),
                    'post_title': post.get('title', ''),
                    'is_google_related': is_google_related
                }
                all_comments.append(comment_data)
    
    print(f"🎯 Google-Related Posts: {google_related_posts}")
    print(f"💬 Total Comments Analyzed: {len(all_comments)}")
    
    if not all_comments:
        print("\n❌ No sentiment data found in comments!")
        return
    
    # Sentiment Analysis
    print("\n" + "="*50)
    print("📈 SENTIMENT ANALYSIS")
    print("="*50)
    
    sentiments = [c['sentiment'] for c in all_comments]
    sentiment_counts = Counter(sentiments)
    
    total_comments = len(all_comments)
    for sentiment, count in sentiment_counts.most_common():
        percentage = (count / total_comments) * 100
        print(f"{sentiment.upper():>10}: {count:>3} comments ({percentage:>5.1f}%)")
    
    # Stock Action Analysis
    print("\n" + "="*50)
    print("📊 STOCK ACTION INDICATORS")
    print("="*50)
    
    actions = [c['stock_action'] for c in all_comments]
    action_counts = Counter(actions)
    
    for action, count in action_counts.most_common():
        percentage = (count / total_comments) * 100
        action_display = action.upper() if action != 'na' else 'NO ACTION'
        print(f"{action_display:>10}: {count:>3} comments ({percentage:>5.1f}%)")
    
    # Weighted Sentiment (by comment score)
    print("\n" + "="*50)
    print("⚖️  WEIGHTED SENTIMENT (by upvotes)")
    print("="*50)
    
    weighted_sentiment = {'positive': 0, 'neutral': 0, 'negative': 0}
    total_weight = 0
    
    for comment in all_comments:
        score = max(comment['score'], 1)  # Minimum weight of 1
        weighted_sentiment[comment['sentiment']] += score
        total_weight += score
    
    for sentiment, weight in weighted_sentiment.items():
        percentage = (weight / total_weight) * 100 if total_weight > 0 else 0
        print(f"{sentiment.upper():>10}: {percentage:>5.1f}% (weighted by upvotes)")
    
    # Overall Assessment
    print("\n" + "="*50)
    print("🎯 OVERALL MARKET SENTIMENT ASSESSMENT")
    print("="*50)
    
    positive_pct = (sentiment_counts.get('positive', 0) / total_comments) * 100
    negative_pct = (sentiment_counts.get('negative', 0) / total_comments) * 100
    neutral_pct = (sentiment_counts.get('neutral', 0) / total_comments) * 100
    
    buy_pct = (action_counts.get('buy', 0) / total_comments) * 100
    sell_pct = (action_counts.get('sell', 0) / total_comments) * 100
    hold_pct = (action_counts.get('hold', 0) / total_comments) * 100
    
    print(f"\n📊 Sentiment Breakdown:")
    print(f"   • Positive: {positive_pct:.1f}%")
    print(f"   • Neutral:  {neutral_pct:.1f}%") 
    print(f"   • Negative: {negative_pct:.1f}%")
    
    print(f"\n💰 Investment Intent:")
    print(f"   • Buy signals:  {buy_pct:.1f}%")
    print(f"   • Hold signals: {hold_pct:.1f}%")
    print(f"   • Sell signals: {sell_pct:.1f}%")
    
    # Market Mood Assessment
    print(f"\n🔮 MARKET MOOD:")
    if positive_pct > negative_pct + 20:
        mood = "🚀 BULLISH - Strong positive sentiment toward Google/Alphabet stock"
    elif negative_pct > positive_pct + 20:
        mood = "🐻 BEARISH - Negative sentiment prevails"
    elif positive_pct > negative_pct:
        mood = "📈 CAUTIOUSLY OPTIMISTIC - Slight positive bias"
    elif negative_pct > positive_pct:
        mood = "📉 CAUTIOUS - Slight negative bias"
    else:
        mood = "😐 NEUTRAL - Mixed opinions, no clear direction"
    
    print(f"   {mood}")
    
    # Key Insights
    print(f"\n💡 KEY INSIGHTS:")
    
    if google_related_posts == 0:
        print("   • ⚠️  No posts directly discussing Google/Alphabet stock performance")
        print("   • 📝 Comments mostly relate to Google products/services rather than investment")
    else:
        print(f"   • 🎯 {google_related_posts} out of {len(data.get('posts', []))} posts directly mention Google/Alphabet")
    
    if buy_pct > sell_pct:
        print(f"   • 💚 More buy signals ({buy_pct:.1f}%) than sell signals ({sell_pct:.1f}%)")
    elif sell_pct > buy_pct:
        print(f"   • 🔴 More sell signals ({sell_pct:.1f}%) than buy signals ({buy_pct:.1f}%)")
    
    if neutral_pct > 60:
        print("   • 😐 Majority of comments are neutral - limited strong opinions")
    
    # Most upvoted comments
    print(f"\n🔥 TOP UPVOTED COMMENTS:")
    top_comments = sorted(all_comments, key=lambda x: x['score'], reverse=True)[:3]
    
    for i, comment in enumerate(top_comments, 1):
        print(f"\n   {i}. Score: {comment['score']} | {comment['sentiment'].upper()} | {comment['stock_action'].upper()}")
        print(f"      Post: {comment['post_title'][:60]}...")
        print(f"      Summary: {comment['summary'][:80]}...")
    
    print("\n" + "="*80)
    print("📋 DISCLAIMER: This analysis is based on a small sample of Reddit comments")
    print("and should not be used as the sole basis for investment decisions.")
    print("="*80)

# Main execution
if __name__ == "__main__":
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        json_file = "results/google stock/reddit_google_stock_day_hot_summarized.json"
    
    try:
        analyze_stock_sentiment(json_file)
    except FileNotFoundError:
        print(f"❌ File not found: {json_file}")
    except Exception as e:
        print(f"❌ Error: {e}")
