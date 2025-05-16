from app.models.service import Service
from app.db.connection import get_connection

def create(data):
    """Create a new service"""
    conn = get_connection()
    try:
        service = Service(**data)
        service.save(conn)
        conn.commit()
        return 201, service.to_dict()
    except ValueError as e:
        conn.rollback()
        return 400, {"error": str(e)}
    except Exception as e:
        conn.rollback()
        return 500, {"error": str(e)}
    finally:
        conn.close()

def update(data, service_id):
    """Update a service"""
    conn = get_connection()
    try:
        service = Service.get_by_id(service_id, conn)
        if not service:
            return 404, {"error": "Service not found"}
        
        # Update fields
        for field, value in data.items():
            setattr(service, field, value)
        
        service.save(conn)
        conn.commit()
        return 200, service.to_dict()
    except ValueError as e:
        conn.rollback()
        return 400, {"error": str(e)}
    except Exception as e:
        conn.rollback()
        return 500, {"error": str(e)}
    finally:
        conn.close()

def get_by_id(service_id):
    """Get a service by ID"""
    conn = get_connection()
    try:
        service = Service.get_by_id(service_id, conn)
        if service:
            return 200, service.to_dict()
        return 404, {"error": "Service not found"}
    except Exception as e:
        return 500, {"error": str(e)}
    finally:
        conn.close()

def get_all_by_medspa(medspa_id):
    """Get all services for a medspa"""
    conn = get_connection()
    try:
        services = Service.get_by_medspa_id(medspa_id, conn)
        return 200, [s.to_dict() for s in services]
    except Exception as e:
        return 500, {"error": str(e)}
    finally:
        conn.close() 