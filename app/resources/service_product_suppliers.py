from app.models.service_product_supplier import ServiceProductSupplier
from app.db.connection import get_connection

def get_all():
    """Get all service product suppliers"""
    conn = get_connection()
    try:
        suppliers = ServiceProductSupplier.get_all(conn)
        return 200, [s.to_dict() for s in suppliers]
    except Exception as e:
        return 500, {"error": str(e)}
    finally:
        conn.close()

def create(data):
    """Create a new service product supplier"""
    conn = get_connection()
    try:
        supplier = ServiceProductSupplier(**data)
        supplier.save(conn)
        conn.commit()
        return 201, supplier.to_dict()
    except ValueError as e:
        conn.rollback()
        return 400, {"error": str(e)}
    except Exception as e:
        conn.rollback()
        return 500, {"error": str(e)}
    finally:
        conn.close() 