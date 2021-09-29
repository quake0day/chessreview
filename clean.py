from db import create_connection, update_best_move
from bs4 import BeautifulSoup

# connect database
database = "./database.db"

# create a database connection
conn = create_connection(database)

with conn:
    cur = conn.cursor()
    sql = ''' SELECT * FROM positions WHERE reason IS NOT NULL;'''
    cur.execute(sql)
    results = cur.fetchall()
    i = 0
    for result in results:
        #print(result[2])
        id = result[0]
        print(result[-2])
        soup = BeautifulSoup(result[-2],'html.parser')
        best_move = soup.find("span").attrs['data-em']
        print(best_move)
        if soup.find("span", {"class":"move b"}) != None:
            best_move_san = soup.find("span", {"class":"move b"}).text
        elif soup.find("span", {"class":"move w"}) != None:
            best_move_san = soup.find("span", {"class":"move w"}).text
        else:
            best_move_san = None
        print(best_move_san)
        update_best_move(conn, id, best_move, best_move_san)
        #board.parse_san('')
        # if best_move != result[2]:
        #     i+=1
    # print(i)
