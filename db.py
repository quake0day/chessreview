# Add database support
import sqlite3
from sqlite3 import Error

DATABASE = "./database.db"

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

def store_positions(conn, positions):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    # """
    # INSERT
    # INTO
    # "main".
    # "positions"("id", "fen", "bestmove", "bestmove_san", "site", "date", "white_name", "black_name", "final_fen")
    # VALUES(NULL, '', '', NULL, NULL, NULL, NULL, NULL);

    sql = ''' INSERT INTO positions("fen", "bestmove", "bestmove_san", "site", "date", "white_name", "black_name", "final_fen", "tester")
              VALUES(?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, positions)
    conn.commit()
    return cur.lastrowid

def update_reason(conn, reason):
    """
    update priority, begin_date, and end date of a task
    :param conn:
    :param task:
    :return: project id
    """
    sql = ''' UPDATE positions
              SET reason = ? 
              WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, reason)
    conn.commit()

def update_best_move(conn, id, move, move_san):
    """
    update priority, begin_date, and end date of a task
    :param conn:
    :param task:
    :return: project id
    """
    sql = ''' UPDATE positions
              SET bestmove = ? 
              WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, (move,id))
    conn.commit()
    sql = ''' UPDATE positions
              SET bestmove_san = ? 
              WHERE id = ?'''
    cur.execute(sql, (move_san,id))
    conn.commit()

def store_hash(conn, hash_val):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    # """
    # INSERT
    # INTO
    # "main".
    # "positions"("id", "fen", "bestmove", "bestmove_san", "site", "date", "white_name", "black_name", "final_fen")
    # VALUES(NULL, '', '', NULL, NULL, NULL, NULL, NULL);
    sql = ''' INSERT INTO game_hash("hash_val")
              VALUES(?) '''
    cur = conn.cursor()
    cur.execute(sql, (hash_val,))
    conn.commit()
    return cur.lastrowid

# True --> exist
# False --> not exist
def is_hash_exist(conn, hash_val):
    cur = conn.cursor()
    sql = '''SELECT * from game_hash where hash_val = ?'''
    cur.execute(sql, (hash_val,))
    results = cur.fetchall()
    return len(results) >= 1