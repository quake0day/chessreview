from flask import Flask, request
import json
import subprocess
from flask_cors import CORS, cross_origin

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
     # scraper_output = str(scraper_output, 'utf-8').split("/")[1]
#      output = pgn_file_output   
      if not "Error" in str(scraper_output):
          scraper_output = str(scraper_output, 'utf-8').split("\n")[0]
          analysis_output = subprocess.check_output(['python', 'main.py', scraper_output])
          output = analysis_output
      else:
          output = scraper_output
   return output
   
if __name__ == "__main__":
  app.run()
