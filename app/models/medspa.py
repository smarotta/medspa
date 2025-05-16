from app.db.connection import get_connection
from app.models.appointment import Appointment
from app.models.service import Service

class Medspa:
    def __init__(self, id=None, name=None, address=None, phone_number=None, email_address=None, created_at=None, updated_at=None):
        self.id = id
        self.name = name
        self.address = address
        self.phone_number = phone_number
        self.email_address = email_address
        self.created_at = created_at
        self.updated_at = updated_at

    def appointments(self, conn):
        """Get all appointments for this medspa"""
        if not self.id:
            return []
        return Appointment.get_by_medspa_id(self.id, conn)

    def services(self, conn):
        """Get all services for this medspa"""
        if not self.id:
            return []
        return Service.get_by_medspa_id(self.id, conn)

    def add_service(self, service, conn):
        """Add a service to this medspa"""
        if not self.id:
            raise ValueError("Cannot add services to unsaved Medspa")
        service.medspa_id = self.id
        return service.save(conn)

    @staticmethod
    def from_db_row(row):
        if not row:
            return None
        return Medspa(
            id=row['id'],
            name=row['name'],
            address=row['address'],
            phone_number=row['phone_number'],
            email_address=row['email_address'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'phone_number': self.phone_number,
            'email_address': self.email_address,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def get_all(cls, conn):
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM medspas")
            rows = cur.fetchall()
            return [cls.from_db_row(row) for row in rows]
        finally:
            cur.close()

    @classmethod
    def get_by_id(cls, medspa_id, conn):
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM medspas WHERE id = %s", (medspa_id,))
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
                    UPDATE medspas 
                    SET name = %s,
                        address = %s,
                        phone_number = %s,
                        email_address = %s
                    WHERE id = %s RETURNING *
                    """,
                    (self.name, self.address, self.phone_number, self.email_address, self.id)
                )
            else:
                if not all([self.name, self.address, self.phone_number, self.email_address]):
                    raise ValueError("All fields are required")
                    
                cur.execute(
                    """
                    INSERT INTO medspas (name, address, phone_number, email_address)
                    VALUES (%s, %s, %s, %s) RETURNING *
                    """,
                    (self.name, self.address, self.phone_number, self.email_address)
                )
            
            row = cur.fetchone()
            
            # Update instance with DB values
            self.id = row['id']
            self.name = row['name']
            self.address = row['address']
            self.phone_number = row['phone_number']
            self.email_address = row['email_address']
            self.created_at = row['created_at']
            self.updated_at = row['updated_at']
            return self
        finally:
            cur.close()

    def delete(self, conn):
        if not self.id:
            raise ValueError("Cannot delete unsaved Medspa")
            
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM medspas WHERE id = %s RETURNING id", (self.id,))
            result = cur.fetchone()
            return result is not None
        finally:
            cur.close() 