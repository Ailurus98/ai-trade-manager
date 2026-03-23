from textblob import TextBlob


def get_sentiment(news_list):
    if not news_list:
        return "Neutral"

    scores = []

    for news in news_list:
        if news is None:
            continue

        try:
            text = str(news).strip()
            if not text:
                continue
            score = TextBlob(text).sentiment.polarity
            scores.append(score)
        except Exception:
            continue

    if not scores:
        return "Neutral"

    avg = sum(scores) / len(scores)

    if avg > 0:
        return "Positive"
    elif avg < 0:
        return "Negative"
    else:
        return "Neutral"
