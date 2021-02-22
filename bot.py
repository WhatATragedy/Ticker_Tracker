import praw
import pandas as pd
import re
from yahooquery import Ticker
from tqdm import tqdm

def extract_possible_tickers(body):
    matches = re.findall("[A-Z]{2,5}", body)
    return matches

def filter_reddit_data(subreddit, thread="Daily Discussion", limit=100):
    tickers = []
    posts = [post for post in reddit.subreddit(subreddit).hot(limit=limit)]
    for submission in posts:
        flair = submission.link_flair_text if submission.link_flair_text is not None else ""
        title = submission.title if submission.title is not None else ""
        if thread in flair or thread in title:
            print(f" {submission} is the daily discussion..")
            submission.comments.replace_more(limit=0)
            for top_level_comment in submission.comments:
                body = top_level_comment.body
                score = top_level_comment.score
                for ticker in extract_possible_tickers(body):
                    tickers.append([ticker, score, subreddit])
    return tickers

def check_ticker(ticker):
    result = Ticker(ticker)
    if 'Quote not found for ticker symbol' in result.price[ticker]:
        return None
    else:
        return result.history(period='1mo')

    

reddit = praw.Reddit(client_id ='Kq-sVZLnsAx65Q', 
                     client_secret ='6PVw44uoK1epL4qHiRJejp_zP-oRkA', 
                     user_agent ='Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405')

subreddits = [
    ('wallstreetbets', "Daily Discussion"),
    ("pennystocks", "Daily Plays")
]

comments = []
for subreddit in subreddits:
    print(f"Enumerating {subreddit[0]} for the thread {subreddit[1]}...")
    comments.extend(filter_reddit_data(subreddit[0], thread=subreddit[1], limit=10))

submissions = pd.DataFrame(comments, columns=["Ticker", "Score", "Subreddit"])
tickers = submissions.groupby(['Ticker', 'Subreddit'])['Score'].agg(['sum','count']).reset_index()

tqdm.pandas()

tickers['yahoo'] = tickers['Ticker'].progress_apply(check_ticker)
tickers.dropna(inplace=True)
print(len(tickers.index))
tickers = tickers.sort_values(by=['sum'], ascending=False)
print(tickers.head())









