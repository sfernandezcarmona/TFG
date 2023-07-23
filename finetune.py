import praw

reddit = praw.Reddit(
    client_id="4sn_H1XsYXdsaBCu08CbrA",
    client_secret="_ZVU_3dfw9qefABWeqKJ2FKMtfkuIg",
    password="etsisi123",
    username="bp0330UPM",
    user_agent="TFGBP0330",
)

sub = reddit.submission("1343wgp")
print(sub.title)