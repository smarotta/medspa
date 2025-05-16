from app.models.service_category import ServiceCategory
from app.db.connection import get_connection

def get_all():
    """Get all service categories"""
    conn = get_connection()
    try:
        categories = ServiceCategory.get_all(conn)
        return 200, [c.to_dict() for c in categories]
    except Exception as e:
        return 500, {"error": str(e)}
    finally:
        conn.close()

def create(data):
    """Create a new service category"""
    conn = get_connection()
    try:
        category = ServiceCategory(**data)
        category.save(conn)
        conn.commit()
        return 201, category.to_dict()
    except ValueError as e:
        conn.rollback()
        return 400, {"error": str(e)}
    except Exception as e:
        conn.rollback()
        return 500, {"error": str(e)}
    finally:
        conn.close() 