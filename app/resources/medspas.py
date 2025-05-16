from app.models.medspa import Medspa
from app.db.connection import get_connection

def get_all():
    """Get all medspas"""
    conn = get_connection()
    try:
        medspas = Medspa.get_all(conn)
        return 200, [m.to_dict() for m in medspas]
    except Exception as e:
        return 500, {"error": str(e)}
    finally:
        conn.close()

def get_by_id(medspa_id):
    """Get a medspa by ID"""
    conn = get_connection()
    try:
        medspa = Medspa.get_by_id(medspa_id, conn)
        if medspa:
            return 200, medspa.to_dict()
        return 404, {"error": "Medspa not found"}
    except Exception as e:
        return 500, {"error": str(e)}
    finally:
        conn.close()

def create(data):
    """Create a new medspa"""
    conn = get_connection()
    try:
        medspa = Medspa(**data)
        medspa.save(conn)
        conn.commit()
        return 201, medspa.to_dict()
    except Exception as e:
        conn.rollback()
        return 400, {"error": str(e)}
    finally:
        conn.close()

def update(data, medspa_id):
    """Update a medspa"""
    conn = get_connection()
    try:
        medspa = Medspa.get_by_id(medspa_id, conn)
        if not medspa:
            return 404, {"error": "Medspa not found"}
            
        # Update with whatever fields were provided
        for field, value in data.items():
            setattr(medspa, field, value)
        
        medspa.save(conn)
        conn.commit()
        return 200, medspa.to_dict()
    except Exception as e:
        conn.rollback()
        return 400, {"error": str(e)}
    finally:
        conn.close()

def delete(medspa_id):
    """Delete a medspa"""
    conn = get_connection()
    try:
        medspa = Medspa.get_by_id(medspa_id, conn)
        if not medspa:
            return 404, {"error": "Medspa not found"}
            
        medspa.delete(conn)
        conn.commit()
        return 200, {"message": f"Medspa {medspa_id} deleted"}
    except Exception as e:
        conn.rollback()
        return 400, {"error": str(e)}
    finally:
        conn.close() 