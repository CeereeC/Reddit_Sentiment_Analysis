import praw
import heapq
import squarify
import pandas as pd
from data import *
import matplotlib.pyplot as plt
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Uncomment this for preloaded results
# from contextlib import redirect_stdout
# from out import *

reddit = praw.Reddit(
    user_agent="Comment Extraction",
    client_id="",
    client_secret="",
)

PICKS_NUMBER = 10;
subs = ['superstonk', 'wallstreetbets', 'stocks', 'investing']
flairs = ['Company Analysis','Gain','Discussion', 'Daily Discussion', 'Weekend Discussion', 'DD', 'Fundamentals/DD', "Technical Analysis", "YOLO", "Industry Discussion"]
post_min_upvotes = 20
comment_min_upvote = 3
count = {}
ticker_mentions, ticker_comments = {} , {}


for sub in subs:
    subreddit = reddit.subreddit(sub)
    hot_sub = subreddit.hot()
    for submission in hot_sub:
        flair = submission.link_flair_text
        id = submission.id
        if flair in flairs and submission.ups > post_min_upvotes:
            submission.comment_sort = 'new'
            comments = submission.comments
            submission.comments.replace_more(limit=10)
            for comment in comments:
                if comment.score > comment_min_upvote:
                    body = comment.body
                    words = body.split()
                    for word in words:
                        if word in tickers and word not in skip and word.isupper():
                            if word in ticker_mentions:
                                ticker_mentions[word] += 1
                                ticker_comments[word].append(comment.body)
                            else:                               
                                ticker_mentions[word] = 1
                                ticker_comments[word] = [comment.body]

# with open('out.py', 'w') as f:
#     with redirect_stdout(f):
#         print(ticker_comments)
#         print(ticker_mentions)                                

top_picks = heapq.nlargest(PICKS_NUMBER, ticker_mentions, key=ticker_mentions.get)
print(top_picks)

scores = {}
count = {ticker:0 for ticker in top_picks}

vader = SentimentIntensityAnalyzer()
vader.lexicon.update(words_to_update)

for stock in top_picks:
    for comment in ticker_comments[stock]:
        score = vader.polarity_scores(comment)
        count[stock] += 1    
        if stock in scores:
            for key in score.keys():
                scores[stock][key] += score[key]
        else:
            scores[stock] = score
    for key in score:
        scores[stock][key] = scores[stock][key] / count[stock]
        scores[stock][key]  = "{pol:.3f}".format(pol=scores[stock][key])

df = pd.DataFrame(scores)
df.index = ['Bearish', 'Neutral', 'Bullish', 'Compound']
df = df.T
print(df)

squarify.plot(sizes=[ticker_mentions[i] for i in top_picks], label=[t for t in top_picks], alpha=.7 )
plt.axis('off')
plt.title(f"{PICKS_NUMBER} most mentioned picks")
plt.show()
