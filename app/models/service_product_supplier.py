from app.db.connection import get_connection

class ServiceProductSupplier:
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name

    def products(self, conn):
        """Get all products supplied by this supplier"""
        if not self.id:
            return []
        from app.models.service_product import ServiceProduct
        return ServiceProduct.get_by_supplier_id(self.id, conn)

    @staticmethod
    def from_db_row(row):
        if not row:
            return None
        return ServiceProductSupplier(
            id=row['id'],
            name=row['name']
        )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

    @classmethod
    def get_all(cls, conn):
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM service_product_suppliers ORDER BY name")
            rows = cur.fetchall()
            return [cls.from_db_row(row) for row in rows]
        finally:
            cur.close()

    @classmethod
    def get_by_id(cls, supplier_id, conn):
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM service_product_suppliers WHERE id = %s", (supplier_id,))
            row = cur.fetchone()
            return cls.from_db_row(row)
        finally:
            cur.close()

    def save(self, conn):
        cur = conn.cursor()
        try:
            if self.id:
                cur.execute(
                    """
                    UPDATE service_product_suppliers 
                    SET name = %s
                    WHERE id = %s RETURNING *
                    """,
                    (self.name, self.id)
                )
            else:
                if not self.name:
                    raise ValueError("Supplier name is required")
                    
                cur.execute(
                    """
                    INSERT INTO service_product_suppliers (name)
                    VALUES (%s) RETURNING *
                    """,
                    (self.name,)
                )
            
            row = cur.fetchone()
            
            # Update instance with DB values
            self.id = row['id']
            self.name = row['name']
            return self
        finally:
            cur.close()

    def delete(self, conn):
        if not self.id:
            raise ValueError("Cannot delete unsaved ServiceProductSupplier")
            
        cur = conn.cursor()
        try:
            # First check if there are any products using this supplier
            cur.execute("SELECT COUNT(*) FROM service_products WHERE supplier_id = %s", (self.id,))
            count = cur.fetchone()['count']
            if count > 0:
                raise ValueError(f"Cannot delete supplier: {count} products are associated with this supplier")

            cur.execute("DELETE FROM service_product_suppliers WHERE id = %s RETURNING id", (self.id,))
            result = cur.fetchone()
            return result is not None
        finally:
            cur.close() 