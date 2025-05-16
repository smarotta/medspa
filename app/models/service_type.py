from app.db.connection import get_connection

class ServiceType:
    def __init__(self, id=None, category_id=None, name=None):
        self.id = id
        self.category_id = category_id
        self.name = name

    def category(self, conn):
        """Get the category this type belongs to"""
        if not self.category_id:
            return None
        from app.models.service_category import ServiceCategory
        return ServiceCategory.get_by_id(self.category_id, conn)

    def products(self, conn):
        """Get all products of this type"""
        if not self.id:
            return []
        from app.models.service_product import ServiceProduct
        return ServiceProduct.get_by_type_id(self.id, conn)

    @staticmethod
    def from_db_row(row):
        if not row:
            return None
        return ServiceType(
            id=row['id'],
            category_id=row['category_id'],
            name=row['name']
        )

    def to_dict(self):
        return {
            'id': self.id,
            'category_id': self.category_id,
            'name': self.name
        }

    @classmethod
    def get_all(cls, conn):
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM service_types ORDER BY name")
            rows = cur.fetchall()
            return [cls.from_db_row(row) for row in rows]
        finally:
            cur.close()

    @classmethod
    def get_by_id(cls, type_id, conn):
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM service_types WHERE id = %s", (type_id,))
            row = cur.fetchone()
            return cls.from_db_row(row)
        finally:
            cur.close()

    @classmethod
    def get_by_category_id(cls, category_id, conn):
        """Get all types in a specific category"""
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM service_types WHERE category_id = %s ORDER BY name", (category_id,))
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
                    UPDATE service_types 
                    SET name = %s,
                        category_id = %s
                    WHERE id = %s RETURNING *
                    """,
                    (self.name, self.category_id, self.id)
                )
            else:
                if not self.name:
                    raise ValueError("Type name is required")
                if not self.category_id:
                    raise ValueError("Type must be associated with a category")
                    
                cur.execute(
                    """
                    INSERT INTO service_types (name, category_id)
                    VALUES (%s, %s) RETURNING *
                    """,
                    (self.name, self.category_id)
                )
            
            row = cur.fetchone()
            
            # Update instance with DB values
            self.id = row['id']
            self.name = row['name']
            self.category_id = row['category_id']
            return self
        finally:
            cur.close()

    def delete(self, conn):
        if not self.id:
            raise ValueError("Cannot delete unsaved ServiceType")
            
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM service_types WHERE id = %s RETURNING id", (self.id,))
            result = cur.fetchone()
            return result is not None
        finally:
            cur.close() 