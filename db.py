import psycopg2, os

class DB:
    def __init__(self):
        self.conn = psycopg2.connect(os.environ["DATABASE_URL"])
        self.cur = self.conn.cursor()

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE,
            password TEXT
        )
        """)

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS messages(
            id SERIAL PRIMARY KEY,
            sender TEXT,
            receiver TEXT,
            room TEXT,
            msg TEXT,
            time TEXT
        )
        """)

        self.conn.commit()

    def register(self, name, password):
        try:
            self.cur.execute(
                "INSERT INTO users(name,password) VALUES(%s,%s)",
                (name, password)
            )
            self.conn.commit()
            return True
        except:
            self.conn.rollback()
            return False

    def login(self, name, password):
        self.cur.execute(
            "SELECT * FROM users WHERE name=%s AND password=%s",
            (name, password)
        )
        return self.cur.fetchone() is not None

    def save_msg(self, s, r, room, msg, time):
        self.cur.execute(
            "INSERT INTO messages(sender,receiver,room,msg,time) VALUES(%s,%s,%s,%s,%s)",
            (s, r, room, msg, time)
        )
        self.conn.commit()
