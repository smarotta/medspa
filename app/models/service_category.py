from app.db.connection import get_connection

class ServiceCategory:
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name

    def types(self, conn):
        """Get all service types in this category"""
        if not self.id:
            return []
        from app.models.service_type import ServiceType
        return ServiceType.get_by_category_id(self.id, conn)

    @staticmethod
    def from_db_row(row):
        if not row:
            return None
        return ServiceCategory(
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
            cur.execute("SELECT * FROM service_categories ORDER BY name")
            rows = cur.fetchall()
            return [cls.from_db_row(row) for row in rows]
        finally:
            cur.close()

    @classmethod
    def get_by_id(cls, category_id, conn):
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM service_categories WHERE id = %s", (category_id,))
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
                    UPDATE service_categories 
                    SET name = %s
                    WHERE id = %s RETURNING *
                    """,
                    (self.name, self.id)
                )
            else:
                if not self.name:
                    raise ValueError("Category name is required")
                    
                cur.execute(
                    """
                    INSERT INTO service_categories (name)
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
            raise ValueError("Cannot delete unsaved ServiceCategory")
            
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM service_categories WHERE id = %s RETURNING id", (self.id,))
            result = cur.fetchone()
            return result is not None
        finally:
            cur.close() 