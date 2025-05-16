from app.db.connection import get_connection
from app.models.service_category import ServiceCategory
from app.models.service_type import ServiceType
from app.models.service_product import ServiceProduct
from datetime import datetime

class Service:
    def __init__(self, id=None, medspa_id=None, category_id=None, type_id=None, product_id=None,
                 name=None, description=None, price=None, duration=None, created_at=None, updated_at=None):
        self.id = id
        self.medspa_id = medspa_id
        self.category_id = category_id
        self.type_id = type_id
        self.product_id = product_id
        self.name = name
        self.description = description
        self.price = price
        self.duration = duration
        self.created_at = created_at
        self.updated_at = updated_at

    def category(self, conn):
        """Get the category of this service"""
        if not self.category_id:
            return None
        return ServiceCategory.get_by_id(self.category_id, conn)

    def type(self, conn):
        """Get the type of this service"""
        if not self.type_id:
            return None
        return ServiceType.get_by_id(self.type_id, conn)

    def product(self, conn):
        """Get the product used in this service"""
        if not self.product_id:
            return None
        return ServiceProduct.get_by_id(self.product_id, conn)

    def validate_hierarchy(self, conn):
        """Validate that category/type/product follow the correct hierarchy"""
        type_obj = ServiceType.get_by_id(self.type_id, conn)
        if type_obj.category_id != self.category_id:
            raise ValueError("Type must belong to the specified category")

        product_obj = ServiceProduct.get_by_id(self.product_id, conn)
        if product_obj.type_id != self.type_id:
            raise ValueError("Product must belong to the specified type")

    def appointments(self, conn):
        """Get all appointments that include this service"""
        if not self.id:
            return []
        # Import here to avoid circular imports
        from app.models.appointment import Appointment
        
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT appointment_id FROM appointment_services
                WHERE service_id = %s
            """, (self.id,))
            appointment_ids = [row['appointment_id'] for row in cur.fetchall()]
            return [Appointment.get_by_id(aid, conn) for aid in appointment_ids]
        finally:
            cur.close()

    def add_to_appointment(self, appointment_id, conn):
        """Add this service to an appointment"""
        if not self.id:
            raise ValueError("Cannot add unsaved service to appointment")
            
        # Import here to avoid circular imports
        from app.models.appointment import Appointment
        
        # First verify the appointment exists and belongs to the same medspa
        appointment = Appointment.get_by_id(appointment_id, conn)
        if not appointment:
            raise ValueError("Appointment not found")
        if appointment.medspa_id != self.medspa_id:
            raise ValueError("Service must belong to the same medspa as the appointment")

        # Add the service to the appointment
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO appointment_services (appointment_id, service_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
                RETURNING appointment_id
            """, (appointment_id, self.id))
            result = cur.fetchone()
            return result is not None
        finally:
            cur.close()

    def remove_from_appointment(self, appointment_id, conn):
        """Remove this service from an appointment"""
        if not self.id:
            return False
            
        cur = conn.cursor()
        try:
            cur.execute("""
                DELETE FROM appointment_services 
                WHERE appointment_id = %s AND service_id = %s
                RETURNING appointment_id
            """, (appointment_id, self.id))
            result = cur.fetchone()
            return result is not None
        finally:
            cur.close()

    def get_upcoming_appointments(self, conn):
        """Get all future appointments that include this service"""
        if not self.id:
            return []
        
        appointments = self.appointments(conn)
        now = datetime.now()
        return [
            a for a in appointments 
            if a.start_time > now and a.status == 'scheduled'
        ]

    @staticmethod
    def from_db_row(row):
        if not row:
            return None
        return Service(
            id=row['id'],
            medspa_id=row['medspa_id'],
            category_id=row['category_id'],
            type_id=row['type_id'],
            product_id=row['product_id'],
            name=row['name'],
            description=row['description'],
            price=row['price'],
            duration=row['duration'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

    def to_dict(self):
        return {
            'id': self.id,
            'medspa_id': self.medspa_id,
            'category_id': self.category_id,
            'type_id': self.type_id,
            'product_id': self.product_id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'duration': self.duration,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def get_all(cls, conn):
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM services ORDER BY name")
            rows = cur.fetchall()
            return [cls.from_db_row(row) for row in rows]
        finally:
            cur.close()

    @classmethod
    def get_by_id(cls, service_id, conn):
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM services WHERE id = %s", (service_id,))
            row = cur.fetchone()
            return cls.from_db_row(row)
        finally:
            cur.close()

    @classmethod
    def get_by_medspa_id(cls, medspa_id, conn):
        """Get all services for a specific medspa"""
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM services WHERE medspa_id = %s ORDER BY name", (medspa_id,))
            rows = cur.fetchall()
            return [cls.from_db_row(row) for row in rows]
        finally:
            cur.close()

    def save(self, conn):
        cur = conn.cursor()
        try:
            if self.id:
                # UPDATE: Get existing record to merge with updates
                cur.execute("SELECT * FROM services WHERE id = %s", (self.id,))
                existing = cur.fetchone()
                if not existing:
                    raise ValueError("Service not found")

                # Merge existing values with updates
                category_id = self.category_id if self.category_id is not None else existing['category_id']
                type_id = self.type_id if self.type_id is not None else existing['type_id']
                product_id = self.product_id if self.product_id is not None else existing['product_id']
                
                # If we have all three, validate the hierarchy
                if all([category_id, type_id, product_id]):
                    self.category_id = category_id
                    self.type_id = type_id
                    self.product_id = product_id
                    self.validate_hierarchy(conn)

                cur.execute(
                    """
                    UPDATE services 
                    SET medspa_id = COALESCE(%s, medspa_id),
                        category_id = COALESCE(%s, category_id),
                        type_id = COALESCE(%s, type_id),
                        product_id = COALESCE(%s, product_id),
                        name = COALESCE(%s, name),
                        description = COALESCE(%s, description),
                        price = COALESCE(%s, price),
                        duration = COALESCE(%s, duration)
                    WHERE id = %s RETURNING *
                    """,
                    (self.medspa_id, self.category_id, self.type_id, self.product_id,
                     self.name, self.description, self.price, self.duration, self.id)
                )
            else:
                # CREATE: All required fields must be present
                if not all([self.medspa_id, self.name, self.price, self.duration,
                          self.category_id, self.type_id, self.product_id]):
                    raise ValueError("Missing required fields")
                    
                # Validate hierarchy before saving
                self.validate_hierarchy(conn)
                
                cur.execute(
                    """
                    INSERT INTO services (
                        medspa_id, category_id, type_id, product_id,
                        name, description, price, duration
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING *
                    """,
                    (self.medspa_id, self.category_id, self.type_id, self.product_id,
                     self.name, self.description, self.price, self.duration)
                )
            
            row = cur.fetchone()
            
            # Update instance with DB values
            self.id = row['id']
            self.created_at = row['created_at']
            self.updated_at = row['updated_at']
            return self
        finally:
            cur.close()

    def delete(self, conn):
        if not self.id:
            raise ValueError("Cannot delete unsaved Service")
            
        cur = conn.cursor()
        try:
            # First delete any appointment associations
            cur.execute("DELETE FROM appointment_services WHERE service_id = %s", (self.id,))
            # Then delete the service
            cur.execute("DELETE FROM services WHERE id = %s RETURNING id", (self.id,))
            result = cur.fetchone()
            return result is not None
        finally:
            cur.close() 