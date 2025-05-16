from app.models.service_product import ServiceProduct
from app.db.connection import get_connection

def get_all():
    """Get all service products"""
    conn = get_connection()
    try:
        products = ServiceProduct.get_all(conn)
        return 200, [p.to_dict() for p in products]
    except Exception as e:
        return 500, {"error": str(e)}
    finally:
        conn.close()

def create(data):
    """Create a new service product"""
    conn = get_connection()
    try:
        product = ServiceProduct(**data)
        product.save(conn)
        conn.commit()
        return 201, product.to_dict()
    except ValueError as e:
        conn.rollback()
        return 400, {"error": str(e)}
    except Exception as e:
        conn.rollback()
        return 500, {"error": str(e)}
    finally:
        conn.close() 