import requests
import json
import time
# Add database support
import sqlite3
from sqlite3 import Error
from db import create_connection,update_reason






def decode(FEN):
    #https://app.decodechess.com/api/login?p=@Lara4cs&u=quake0day@gmail.com

    # Simulate login to decode chess
    URL = 'https://app.decodechess.com/api/login?p=@Lara4cs&u=quake0day@gmail.com'
    # payload = {
    #     'barcode': 'your user name/login',
    #     'telephone_primary': 'your password',
    #     'persistent': '1'  # remember me
    # }

    session = requests.session()
    r = session.get(URL)
    print(r.json()) # should be success


    # import new FEN
    #Request URL: https://app.decodechess.com/api/game
    import_URL = "https://app.decodechess.com/api/game"
    pgn = "[Event \"?\"]\n[Site \"?\"]\n[Date \"?\"]\n[Round \"?\"]\n[White \"?\"]\n[Black \"?\"]\n[Result \"*\"]\n[SetUp \"1\"]\n[FEN \"%s\"]\n[CSGameName \"Game\"]\n\n *" % FEN
    payload = {"key":"","pgn":pgn,"name":"Game","origin":"pasted_fen","positions":[],"reason":"changed","fen":None,"ss":None,"ssd":None,"moves":[],"scores":[],"depths":[],"bests":[]}

    r = session.post(import_URL, data=json.dumps(payload))
    game_key = r.json()['key'] # should contain
    print(game_key)
    import_URL = "https://app.decodechess.com/api/game"
    payload = {"key":game_key,"pgn":pgn,"name":"Game","origin":"pasted_fen","positions":[],"reason":"opened","fen":"","ss":None,"ssd":None,"moves":[],"scores":[],"depths":[],"bests":[]}
    r = session.post(import_URL, data=json.dumps(payload))
    game_key = r.json()['key'] # should contain
    print(game_key)

    # Read result
    status = "working"
    res = ""
    while status == "working":
        GAME_ID = game_key
        result_URL = 'https://app.decodechess.com/api/decode_game?a=0&b=fd957dd111ac4dd069a6272a6f8e38d0&g=%s&h=0&m=Game&p=0&r=0' % GAME_ID
        res = session.get(result_URL)
        final_result = res.json() # should be success
        #print(final_result['result'])
        status = res.json()['status']
        time.sleep(5)

    if status == "answered":
        return final_result['result']['0']
    return ""


# connect database
database = "./database.db"

# create a database connection
conn = create_connection(database)

with conn:
    cur = conn.cursor()
    sql = ''' SELECT * FROM positions WHERE reason IS NULL;'''
    cur.execute(sql)
    results = cur.fetchall()
    for result in results:
        uid = result[0]
        decode_result = decode(result[1])
        time.sleep(2)
        #decode_result = "h"
        if decode_result != "":
            #sql = ("UPDATE "main"."positions" SET "reason"='{}' WHERE "id"='{}'").format(decode_result, result[0])
            field = "main"
            field1 = "positions"
            row = "reasons"
            conditions = "id"
            uid = result[0]

            update_reason(conn, (decode_result, uid))
