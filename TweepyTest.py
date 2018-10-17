import tweepy


class TwitterAPI:
    def __init__(self):
        consumer_key = "kE2qKHbUyIP7eFZwpiQFcDS18"
        consumer_secret = "2C5QP9QtJxprydZjw2VjTDL2O2Jc1SExNqrpm5XeUWaSeAmfqS"
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        access_token = "843786300188704768-2zFNwekrzOWHNOAoxYphVdQEKo0Nh6Q"
        access_token_secret = "Mq3Cz5s0l3UhDaBcptzUBw8CCJm6i7oqM6IQCmqWV8GPK"
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)

    def get_last_tweet(self):
        tweet = self.api.home_timeline(id = self.api, count = 1)[0]
        print(tweet.text)

if __name__ == "__main__":
    twitter = TwitterAPI()
    twitter.get_last_tweet()
