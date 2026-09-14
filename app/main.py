from sqlalchemy import text

from config.database import engine

try :
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        print("Connected successfully!")
        print(result.fetchone())
        
except Exception as e:
    print(e)