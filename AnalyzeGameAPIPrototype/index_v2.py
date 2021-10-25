from flask import Flask, request
import json
import subprocess
from flask_cors import CORS, cross_origin
import sqlite3
from sqlite3 import Error

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/', methods=['POST'])
@cross_origin()
def result():
   
   json_string = request.json
   try:
      username = json_string["username"]
   except:
      username = None
   output = ""
   
   if not username is None:
      #Add code to have subprocess print the output of scraper.py to an output_file variable

      scraper_output = subprocess.check_output(['python', 'scraper.py', username])
      output = scraper_output

   return output
   

@app.route('/analyze', methods=['POST'])
def analyze():

   database = "analyzed_game_users.db"
   con = sqlite3.connect(database)
   cur = con.cursor()

   json_string = request.json
   
   try:
      pgn_file = json_string["pgnFile"]
      username = pgn_file.split("_")[0]
   except:
      pgn_file = None
   output = ""
   
   if not pgn_file is None:      
          pgn_file = pgn_file.split("\n")[0]
          cur.execute("REPLACE INTO users (user, isProcessing) VALUES (?, 'true')", (username,))
          con.commit()
          try:
            analysis_output = subprocess.check_output(['python', 'main.py', pgn_file])
            cur.execute("REPLACE INTO users (user, isProcessing) VALUES (?, 'false')", (username,))
            con.commit()
            con.close()
            return "Analysis complete"

          except subprocess.CalledProcessError as e:
            cur.execute("REPLACE INTO users (user, isProcessing) VALUES (?, 'false')", (username,))
            con.commit()
            con.close()
            return "Analysis failed"



if __name__ == "__main__":
  app.run()
