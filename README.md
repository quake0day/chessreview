# chess_review
a chess review system to help you review your blunders



# How to run this program locally.
1. export FLASK_APP=web
2. flask run
3. Type localhost:5000/<username> into the address bar of your browser

# How the program works
The first thing the program does is check to see if the specified username has their games currently being analyzed.
If they do, then a message is displayed indicating this. This message will not appear on subsequent loads of the page if game analysis is not currently occurring for the specified username.

When a board has loaded, the user can step through the specified user's games, and see the chess engine's recommended moves for that game.

If the specified username in the URL has never had any games analyzed, it will show a prompt allowing you to analyze the games for that user.

