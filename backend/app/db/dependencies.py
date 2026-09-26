from app.db.database import SessionLocal
def get_db(): 
    # fastapi talking to the postgres db needs a session 
    # and instead of doing this manually in every api endpoint we can do this->
    db = SessionLocal()
    try:
        yield db
    finally: # this block makes sure that the session is closed even if the request throws an error
        db.close()