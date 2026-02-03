from app.database import SessionLocal
from app.models.event import Event
from datetime import datetime, timedelta

db = SessionLocal()
try:
    e = Event(
        title="Test Event",
        start_time=datetime.utcnow(),
        end_time=datetime.utcnow() + timedelta(hours=1),
        created_by=1
    )
    db.add(e)
    db.commit()
    print("Success!")
except Exception as ex:
    print(f"Failed: {ex}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
