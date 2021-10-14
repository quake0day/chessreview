"""
PGN Scraper is a small program which downloads each of a user's archived games from chess.com and stores them in a pgn file.
When running the user is asked for the account name which shall be scraped and for game types.
The scraper only downloads games of the correct type.

Supported types are: bullet, rapid, blitz
                     rated, unrated
                     standard chess, other ruless (chess960, oddchess, etc.)
"""
from datetime import datetime
import json
import urllib.request
import os
import sys

def CheckFileName(file_name):
    """
    This function checks if a file with file_name already exists. If yes an error message is printed and the script aborted.
    """
    if os.path.isfile(os.getcwd()+f"/{file_name}"):
        print(f"Error: A file named '{file_name}' already exists.")
        print("Exiting...")
        quit()

def GameTypeTrue(game,game_type,rated,rules):
    """
    This function checks if the game is of the type defined in game_type (bullet, rapid or blitz) and returns either True or False.
    """
    # Check if game is of the correct type
    for type in game_type:
        for ra in rated:
            for ru in rules:
                if (game["time_class"] == type) and (game["rated"] == ra) and ( (game["rules"] == "chess") == ru):
                    return True

    # If not correct type return False
    return False


def initScrape():
    """
    This functions is used to set up the scraping parameters like account name and game type.
    """
    # Input account name
    #acc_name = input("Enter account name: ").strip()

    #Automatically get the user name that is passed in by the Flask server
    acc_name = sys.argv[1]

    # Check if acc_name is empty
    if bool(acc_name) == False:
        print("Error: Empty account name!")
        quit()

    # Input game type
    #game_type_code = input("Enter game type [1] All (default), [2] Rapid, [3] Blitz, [4] Bullet, [5] Rapid and Blitz: ").strip()

    # If game_type_code is empty set to 1
    #if bool(game_type_code) == False:
    game_type_code = "1"

    # Create dictionary for different game type options und apply input
    game_type_dict = {
        "1" : ["bullet", "blitz", "rapid"],
        "2" : ["rapid"],
        "3" : ["blitz"],
        "4" : ["bullet"],
        "5" : ["blitz", "rapid"]
    }


    game_type = game_type_dict["1"]

    # Input rated/unrated
    #rated_code = input("Consider [1] only rated games (default), [2] only unrated or [3] all games: ").strip()

    # If rated_code is empty set to 1
    #if bool(rated_code) == False:
    rated_code = "1"

    # Create dictionary for rated/unraked and apply input
    rated_dict = {
        "1" : [True],
        "2" : [False],
        "3" : [True, False]
    }

   # try:
    rated = rated_dict["3"]
   # except KeyError:
   #     print("Error: Invalid input!\nExiting...")
   #     quit()

    # Input rules ("chess"/other)
   # rules_code = input("Consider [1] only standard chess (default), [2] only other modes (oddchess, bughouse etc.) or [3] any type: ").strip()

    # If rules_code is empty set to 1
   # if bool(rules_code) == False:
    rules_code = "1"

    # Create dictionary for rules and apply input
    rules_dict = {
        "1" : [True],
        "2" : [False],
        "3" : [True, False]
    }

    #try:
    rules = rules_dict[rules_code]
   # except KeyError:
   #     print("Error: Invalid input!\nExiting...")
   #     quit()

    # Print warning if only rated and only other rules are selected
    if (rated_code == "1") and (rules_code == "2"):
        print("Warning: You selected only rated AND only other chess modes!")
        print("         Other chess modes are often unrated!")

    return [acc_name, game_type, rated, rules]

def beginScrape(params):
    """
    The downloading of the PGN archives happens here.
    The file is saved as "username_YYYY-MM-dd.pgn"
    """

    # Passing the predefined parameters
    acc_name = params[0]
    game_type = params[1]
    rated = params[2]
    rules = params[3]

    # Create name of pgn file
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    game_type_string = "_".join(game_type)
    file_name = f"{acc_name}_{date}_{game_type_string}.pgn"
    #file_name = "chessreview/" + file_name
    # Check if file already exists
    CheckFileName(file_name)

    # Run the request, check games for type and write correct ones to file
    with urllib.request.urlopen(f"https://api.chess.com/pub/player/{acc_name}/games/archives") as url:
        archives = list(dict(json.loads(url.read().decode()))["archives"])

        for archive in archives:
            with urllib.request.urlopen(archive) as url:
                games = list(dict(json.loads(url.read().decode()))["games"])
                for game in games:
                    if GameTypeTrue(game,game_type,rated,rules):
                        with open(file_name, "a") as text_file:
                            print(game["pgn"], file=text_file)
                            print("\n", file=text_file)
    return file_name

def main():
    """
    Scrape PGN files from chess.com .
    """
    params = initScrape()
    output = beginScrape(params)
    print(output)

if __name__ == '__main__':
    main()
