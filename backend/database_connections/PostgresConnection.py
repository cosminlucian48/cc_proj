import psycopg2
import psycopg2.pool
from fastapi import HTTPException

from db_helper.db_credentials_helper import get_postgres_creds


class PostgresConnection:
    def __init__(self):
        try:
            config = get_postgres_creds()
            if config:
                self.connection_pool = psycopg2.pool.SimpleConnectionPool(1, 1,
                                                                          host=config['host'],
                                                                          user=config['user'],
                                                                          password=config['password'],
                                                                          database=config['database'])
        except psycopg2.OperationalError as e:
            print("Error connecting to database:", e)
        except AttributeError:
            raise HTTPException(status_code=400, detail="Could not retrieve database credentials.")

    def query(self, query):
        result = None
        try:
            conn = self.connection_pool.getconn()
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
        except psycopg2.ProgrammingError as e:
            print(e)
            raise HTTPException(status_code=500, detail="Error when executing SQL statement in class.")
        except psycopg2.pool.PoolError:
            raise HTTPException(status_code=500, detail="Could not create new postgres connection.")
        except AttributeError as e:
            raise HTTPException(status_code=500, detail="Error on the connection pool.")
        except psycopg2.OperationalError as e:
            raise HTTPException(status_code=500, detail="Database connection could not be established.")
        except psycopg2.IntegrityError as e:
            raise HTTPException(status_code=400, detail="User already exists.")
        except psycopg2.DataError as e:
            raise HTTPException(status_code=500, detail="Query data is invalid.")
        except psycopg2.InternalError as e:
            raise HTTPException(status_code=500, detail="Database server error.")
        finally:
            self.connection_pool.putconn(conn)
        return result

    def insert(self, query):
        try:
            conn = self.connection_pool.getconn()
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
            cursor.close()
        except psycopg2.ProgrammingError as e:
            print(e)
            raise HTTPException(status_code=500, detail="Error when executing SQL statement in class.")
        except psycopg2.pool.PoolError:
            raise HTTPException(status_code=500, detail="Could not create new postgres connection.")
        except AttributeError as e:
            raise HTTPException(status_code=500, detail="Error on the connection pool.")
        except psycopg2.OperationalError as e:
            raise HTTPException(status_code=500, detail="Database connection could not be established.")
        except psycopg2.IntegrityError as e:
            raise HTTPException(status_code=400, detail="User already exists.")
        except psycopg2.DataError as e:
            raise HTTPException(status_code=500, detail="Query data is invalid.")
        except psycopg2.InternalError as e:
            raise HTTPException(status_code=500, detail="Database server error.")
        finally:
            self.connection_pool.putconn(conn)

    def update_facial_encodings(self, query):
        try:
            conn = self.connection_pool.getconn()
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
            cursor.close()
        except psycopg2.ProgrammingError as e:
            print(e)
            raise HTTPException(status_code=500, detail="Error when executing SQL statement in class.")
        except psycopg2.pool.PoolError:
            raise HTTPException(status_code=500, detail="Could not create new postgres connection.")
        except AttributeError as e:
            raise HTTPException(status_code=500, detail="Error on the connection pool.")
        except psycopg2.OperationalError as e:
            raise HTTPException(status_code=500, detail="Database connection could not be established.")
        except psycopg2.IntegrityError as e:
            raise HTTPException(status_code=400, detail="User already exists.")
        except psycopg2.DataError as e:
            raise HTTPException(status_code=500, detail="Query data is invalid.")
        except psycopg2.InternalError as e:
            raise HTTPException(status_code=500, detail="Database server error.")
        finally:
            self.connection_pool.putconn(conn)
        