import sqlite3

# TODO: make those functions async


def db_init():
    conn = sqlite3.connect('users.db')
    conn.execute("DROP TABLE Users;")

    conn.execute("CREATE TABLE Users \
                    (   username    TEXT    NOT NULL PRIMARY KEY UNIQUE, \
                        password    TEXT    NOT NULL);")
    conn.commit()
    conn.close()


def db_create_new_user(name, pwd):
    conn = sqlite3.connect('users.db')
    conn.execute(f"INSERT INTO Users VALUES ('{name}', '{pwd}' );")
    conn.commit()
    conn.close()


def db_delete_user(name):
    conn = sqlite3.connect('users.db')
    conn.execute(f" DELETE \
                    FROM Users \
                    WHERE username = '{name}';")
    conn.commit()
    conn.close()


def db_authenticate_user(name, pwd):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute(f"SELECT password, COUNT(password) \
                    FROM Users \
                    WHERE username = '{name}';")

    db_pwd = cur.fetchall()[0][0]
    if db_pwd != pwd or db_pwd is None:
        ret = False
    else:
        ret = True
    conn.close()
    return ret

def db_get_all_users():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute(f"SELECT * \
                    FROM Users;")

    print([i for i in cur.fetchall()[0]])
    conn.close()
