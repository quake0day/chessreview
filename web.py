from flask import Flask
import sqlite3
from flask import g
from flask import render_template, request
from flask_cors import CORS, cross_origin
from sqlite3 import Error
import json
import subprocess
import requests

#DATABASE = './chessreview/database.db'
DATABASE = './database.db'
processingCheckDb = './analyzed_game_users.db'

#DATABASE = '/var/www/chess/chessChen/database.db'

app = Flask(__name__)

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

@app.route('/getIsProcessing/<username>')
def query_is_processing_status(username):
    con = sqlite3.connect(processingCheckDb)
    cur = con.cursor()
    cur.execute("SELECT isProcessing from users WHERE user=?", (username,))
    db_result = cur.fetchone()
    if not db_result is None:
        return db_result[0]
    else:
        return "User not found"

@app.route('/analyze/<username>')
def analyze_games(username):
    scraper_output = subprocess.check_output(['python3', 'scraper.py', username])
    scraper_output = scraper_output.decode("utf-8")
    if not "Error" in scraper_output:
        con = sqlite3.connect(processingCheckDb)
        cur = con.cursor()
        pgn_file = str(scraper_output.split(".pgn")[0] + ".pgn")
        print(pgn_file)
        cur.execute("REPLACE INTO users (user, isProcessing) VALUES (?, 'true')", (username,))
        con.commit();
        try:
           # analysis_process = subprocess.Popen(['python3', 'main.py', pgn_file])
            analysis_output = subprocess.check_output(['python3', 'main.py', pgn_file]) 
            cur.execute("REPLACE INTO users (user, isProcessing) VALUES (?, 'false')", (username,))
            con.commit()
            con.close()
            return "Analysis Successful"
        except subprocess.CalledProcessError as e:
           cur.execute("REPLACE INTO users (user, isProcessing) VALUES (?, 'false')", (username,))
           con.commit()
           con.close()
           return "Analysis failed: " + str(e)
    else:
      return (scraper_output)

@app.route('/<name>')
@app.route('/<name>/<id>')
def hello(name="quake0day", id=1):
    fen=""
    best_move = ""
    san = ""
    site = ""
    date = ""
    white_player = ""
    black_player = ""
    final_fen = ""
    orientation = "white"
    reasons = ""
   # username = str(request.path).split("/")[1]
    username = name
#    print(username) 

    request_response = requests.get("http://localhost:5000/getIsProcessing/" + name).text
    if not "User not found" in request_response:
        isProcessingStatusForUser = request_response
    else:
        return render_template('user-not-found.html')
    tester = (name,)
    sql = ''' SELECT * FROM positions WHERE tester = ? ORDER by date DESC
    
               '''

    # create a database connection

    conn = create_connection(DATABASE)
    cur = conn.cursor()
    cur.execute(sql, tester)
    results = cur.fetchall()
    total = len(results)

    if "true" in isProcessingStatusForUser:
        isProcessingStatusForUser = True
    else:
        isProcessingStatusForUser = False
 

    try:
        iid = int(id)
    except ValueError:
        print("Error")
        pass
    if iid <= 0 or iid > total:
        iid = 1
    try:
        positions = results[iid-1]
        fen = positions[1]
        best_move = positions[2]
        san = positions[3]
        site = positions[4]
        date = positions[5]
        white_player = positions[6]
        black_player = positions[7]
        final_fen = positions[8]
        reasons = positions[9]
        best_move = best_move[:2] + "-" + best_move[2:]
        print(fen)
        next_move = fen.split(" ")[-5] # check sides
        print(next_move)
        print(best_move)
        orientation  = "white"
        if next_move == "b":
            orientation = "black"
    except:
        pass
    print(isProcessingStatusForUser)
    return render_template('index.html', isProcessing = isProcessingStatusForUser, id = iid, fen=fen, best_move=best_move, orientation=orientation, san = san, site = site, date = date, white_player = white_player, black_player = black_player, reasons= reasons, final_fen=final_fen, total=total)


def hello_world():
    return 'Hello, World!'

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

