import asyncio
import chess
import chess.engine
import chess.pgn
import io
import numpy as np
from stockfish import Stockfish
from db import create_connection, store_positions, is_hash_exist, store_hash
import hashlib
import sys

# Add database support
import sqlite3
from sqlite3 import Error

#USERNAME= ""
DATABASE = "database.db"
STOCK_FISH = "/usr/bin/stockfish"
THREADS = 128
#PGNNAME = "quake0day_2021-09-21_bullet_blitz_rapid.pgn"
#PGNNAME = "EricHe1222_2021-09-14_bullet_blitz_rapid.pgn"
PGNNAME = str(sys.argv[1])
USERNAME = PGNNAME.split("_")[0]




#Go to the end of the game and create a chess.Board() from it:
#game = game.end()
#board = game.board()

#So if you want, here's also your PGN to FEN conversion:
#print('FEN of the last position of the game: %s ', board.fen())

#or if you want to loop over all game nodes:
def find_blunder(game, sentitive = 500, username="quake0day"):
    score_white = []
    score_black = []
    fen = []
    white = game.headers["White"]
    black = game.headers["Black"]
    print(white)
    print(black)
    while not game.is_end():
        node = game.variations[0]
        board = game.board() #print the board if you want, to make sure
        print(board.fen())
        fen.append(board.fen())

        info = engine.analyse(board, chess.engine.Limit(depth=20))
        #print("Score:", info["score"])
        score = info.get("score")


        if board.turn:
            print(score.pov("white"))
            score_white.append(score.pov("white").score())
        else:
            print(score.pov(("black")))
            score_black.append(score.pov("black").score())
        game = node

    score_white = np.array(score_white)
    score_white = score_white[score_white != np.array(None)]
    diff_white = np.diff(score_white)

    score_black = np.array(score_black)
    score_black = score_black[score_black != np.array(None)] # remove NoneType
    diff_black = np.diff(score_black)
    blunder_positions = []

    if white == username:
        for i in range(len(diff_white)):
            if diff_white[i] > sentitive:
                print("Find Blunder! White move: %s" % str(i + 1))
                print(fen[2 * i])
                blunder_positions.append(fen[2 * i])
    elif black == username:
        for i in range(len(diff_black)):
            if diff_black[i] > sentitive:
                print("Find Blunder! Black move: %s" % str(i + 1))
                print(fen[2 * i + 1])
                blunder_positions.append(fen[2 * i + 1])

    return blunder_positions






if __name__ == "__main__":
    #Let's try our code with the starting position of chess:
    # create a database connection
    conn = create_connection(DATABASE)

    pgnfilename = PGNNAME
    engine = chess.engine.SimpleEngine.popen_uci(STOCK_FISH)
    stockfish = Stockfish(STOCK_FISH, parameters={"Threads": THREADS})
    # Set options
    engine.configure({"Threads": THREADS})
    stockfish.set_depth(18)
    #limit = chess.engine.Limit(time=movesec_lim, nodes=node_lim)

    f = open(pgnfilename)

    #Read pgn file (may contains multiple games)
    game_list = []

    while True:
        singlegame = chess.pgn.read_game(f)
        if singlegame is None:
            break  # end of file
        game_list.append(singlegame)


    print(game_list)
    for game in game_list:
        m = hashlib.md5()
        old_stdout = sys.stdout

        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        print(USERNAME)
        print(game)

        output = new_stdout.getvalue()
        m.update(output.encode("UTF-8"))
        sys.stdout = old_stdout
        game_hash = m.hexdigest()
        print(game_hash)
        if(is_hash_exist(conn, game_hash) != True): # if this is a new game record
            store_hash(conn, game_hash)
            blunders = find_blunder(game, 200, USERNAME)
            for blunder in blunders:

                stockfish.set_fen_position(blunder)
                print(blunder)
                best_move = stockfish.get_best_move()
                board = chess.Board(blunder)
                move = chess.Move.from_uci(best_move)
                san = board.san(chess.Move.from_uci(best_move))
                #print(san)
                print("best move: %s" % best_move)

                print("best move: %s" % san)

                board.push(move)
                print(board.fen())
                final_fen = board.fen()



                site = game.headers["Site"]
                date = game.headers["Date"]
                white = game.headers["White"]
                black = game.headers["Black"]
                tester = USERNAME
                try:  #not update dub record
                    with conn:
                        positions = (blunder, best_move, san, site, date, white, black,final_fen,tester)
                        project_id = store_positions(conn, positions)
                        print(project_id)
                except:
                    pass


    engine.quit()


