from app.db.connection import get_connection

class ServiceProduct:
    def __init__(self, id=None, type_id=None, supplier_id=None, name=None):
        self.id = id
        self.type_id = type_id
        self.supplier_id = supplier_id
        self.name = name

    def type(self, conn):
        """Get the type this product belongs to"""
        if not self.type_id:
            return None
        from app.models.service_type import ServiceType
        return ServiceType.get_by_id(self.type_id, conn)

    def supplier(self, conn):
        """Get the supplier of this product"""
        if not self.supplier_id:
            return None
        from app.models.service_product_supplier import ServiceProductSupplier
        return ServiceProductSupplier.get_by_id(self.supplier_id, conn)

    @staticmethod
    def from_db_row(row):
        if not row:
            return None
        return ServiceProduct(
            id=row['id'],
            type_id=row['type_id'],
            supplier_id=row['supplier_id'],
            name=row['name']
        )

    def to_dict(self):
        return {
            'id': self.id,
            'type_id': self.type_id,
            'supplier_id': self.supplier_id,
            'name': self.name
        }

    @classmethod
    def get_all(cls, conn):
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM service_products ORDER BY name")
            rows = cur.fetchall()
            return [cls.from_db_row(row) for row in rows]
        finally:
            cur.close()

    @classmethod
    def get_by_id(cls, product_id, conn):
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM service_products WHERE id = %s", (product_id,))
            row = cur.fetchone()
            return cls.from_db_row(row)
        finally:
            cur.close()

    @classmethod
    def get_by_type_id(cls, type_id, conn):
        """Get all products of a specific type"""
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM service_products WHERE type_id = %s ORDER BY name", (type_id,))
            rows = cur.fetchall()
            return [cls.from_db_row(row) for row in rows]
        finally:
            cur.close()

    @classmethod
    def get_by_supplier_id(cls, supplier_id, conn):
        """Get all products from a specific supplier"""
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM service_products WHERE supplier_id = %s ORDER BY name", (supplier_id,))
            rows = cur.fetchall()
            return [cls.from_db_row(row) for row in rows]
        finally:
            cur.close()

    def save(self, conn):
        cur = conn.cursor()
        try:
            if self.id:
                cur.execute(
                    """
                    UPDATE service_products 
                    SET name = %s,
                        type_id = %s,
                        supplier_id = %s
                    WHERE id = %s RETURNING *
                    """,
                    (self.name, self.type_id, self.supplier_id, self.id)
                )
            else:
                if not self.name:
                    raise ValueError("Product name is required")
                if not self.type_id:
                    raise ValueError("Product must be associated with a type")
                if not self.supplier_id:
                    raise ValueError("Product must be associated with a supplier")
                    
                cur.execute(
                    """
                    INSERT INTO service_products (name, type_id, supplier_id)
                    VALUES (%s, %s, %s) RETURNING *
                    """,
                    (self.name, self.type_id, self.supplier_id)
                )
            
            row = cur.fetchone()
            
            # Update instance with DB values
            self.id = row['id']
            self.name = row['name']
            self.type_id = row['type_id']
            self.supplier_id = row['supplier_id']
            return self
        finally:
            cur.close()

    def delete(self, conn):
        if not self.id:
            raise ValueError("Cannot delete unsaved ServiceProduct")
            
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM service_products WHERE id = %s RETURNING id", (self.id,))
            result = cur.fetchone()
            return result is not None
        finally:
            cur.close() 