from app.models.service_type import ServiceType
from app.db.connection import get_connection

def get_all():
    """Get all service types"""
    conn = get_connection()
    try:
        types = ServiceType.get_all(conn)
        return 200, [t.to_dict() for t in types]
    except Exception as e:
        return 500, {"error": str(e)}
    finally:
        conn.close()

def create(data):
    """Create a new service type"""
    conn = get_connection()
    try:
        service_type = ServiceType(**data)
        service_type.save(conn)
        conn.commit()
        return 201, service_type.to_dict()
    except ValueError as e:
        conn.rollback()
        return 400, {"error": str(e)}
    except Exception as e:
        conn.rollback()
        return 500, {"error": str(e)}
    finally:
        conn.close() 