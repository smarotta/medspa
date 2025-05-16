from app.db.connection import get_connection
from datetime import datetime, timedelta

class Appointment:
    # Valid status values
    SCHEDULED = 'scheduled'
    COMPLETED = 'completed'
    CANCELED = 'canceled'

    def __init__(self, id=None, medspa_id=None, start_time=None, status='scheduled', created_at=None, updated_at=None):
        self.id = id
        self.medspa_id = medspa_id
        self.start_time = start_time
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at

    @property
    def services(self, conn):
        """Get all services for this appointment"""
        if not self.id:
            return []
            
        # Import here to avoid circular imports
        from app.models.service import Service
        
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT service_id FROM appointment_services
                WHERE appointment_id = %s
            """, (self.id,))
            service_ids = [row['service_id'] for row in cur.fetchall()]
            return [Service.get_by_id(sid, conn) for sid in service_ids]
        finally:
            cur.close()

    def add_service(self, service, conn):
        """Add a service to this appointment"""
        if not self.id:
            raise ValueError("Cannot add services to unsaved Appointment")
        if not service.id:
            raise ValueError("Cannot add unsaved Service")
        if service.medspa_id != self.medspa_id:
            raise ValueError("Service must belong to the same medspa as the appointment")
            
        return service.add_to_appointment(self.id, conn)

    def remove_service(self, service, conn):
        """Remove a service from this appointment"""
        if not self.id or not service.id:
            return False
        return service.remove_from_appointment(self.id, conn)

    def total_duration(self, conn):
        """Calculate total duration of all services using SQL"""
        if not self.id:
            return 0
            
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT COALESCE(SUM(s.duration), 0) as total_duration
                FROM services s
                JOIN appointment_services aps ON s.id = aps.service_id
                WHERE aps.appointment_id = %s
            """, (self.id,))
            return cur.fetchone()['total_duration']
        finally:
            cur.close()

    def total_price(self, conn):
        """Calculate total price of all services using SQL"""
        if not self.id:
            return 0
            
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT COALESCE(SUM(s.price), 0) as total_price
                FROM services s
                JOIN appointment_services aps ON s.id = aps.service_id
                WHERE aps.appointment_id = %s
            """, (self.id,))
            return cur.fetchone()['total_price']
        finally:
            cur.close()

    @staticmethod
    def from_db_row(row):
        if not row:
            return None
        return Appointment(
            id=row['id'],
            medspa_id=row['medspa_id'],
            start_time=row['start_time'],
            status=row['status'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

    def to_dict(self):
        return {
            'id': self.id,
            'medspa_id': self.medspa_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def get_all(cls, conn, status=None, start_date=None):
        """Get all appointments with optional filters"""
        cur = conn.cursor()
        
        query = "SELECT * FROM appointments WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = %s"
            params.append(status)
            
        if start_date:
            query += " AND DATE(start_time) = %s"
            params.append(start_date)
            
        query += " ORDER BY start_time"
        
        try:
            if params:
                cur.execute(query, tuple(params))
            else:
                cur.execute(query)
            rows = cur.fetchall()
            return [cls.from_db_row(row) for row in rows]
        finally:
            cur.close()

    @classmethod
    def get_by_id(cls, appointment_id, conn):
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM appointments WHERE id = %s", (appointment_id,))
            row = cur.fetchone()
            return cls.from_db_row(row)
        finally:
            cur.close()

    @classmethod
    def get_by_medspa_id(cls, medspa_id, conn):
        """Get all appointments for a specific medspa"""
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM appointments WHERE medspa_id = %s ORDER BY start_time", (medspa_id,))
            rows = cur.fetchall()
            return [cls.from_db_row(row) for row in rows]
        finally:
            cur.close()

    def save(self, conn):
        if not all([self.medspa_id, self.start_time]):
            raise ValueError("Medspa ID and start time are required")

        cur = conn.cursor()
        try:
            if self.id:
                cur.execute(
                    """
                    UPDATE appointments 
                    SET medspa_id = %s,
                        start_time = %s,
                        status = %s
                    WHERE id = %s RETURNING *
                    """,
                    (self.medspa_id, self.start_time, self.status, self.id)
                )
            else:
                cur.execute(
                    """
                    INSERT INTO appointments (medspa_id, start_time, status)
                    VALUES (%s, %s, %s) RETURNING *
                    """,
                    (self.medspa_id, self.start_time, self.status)
                )
            
            row = cur.fetchone()
            
            # Update instance with DB values
            self.id = row['id']
            self.medspa_id = row['medspa_id']
            self.start_time = row['start_time']
            self.status = row['status']
            self.created_at = row['created_at']
            self.updated_at = row['updated_at']
            return self
        finally:
            cur.close()

    def delete(self, conn):
        if not self.id:
            raise ValueError("Cannot delete unsaved Appointment")
            
        cur = conn.cursor()
        try:
            # First delete any service associations
            cur.execute("DELETE FROM appointment_services WHERE appointment_id = %s", (self.id,))
            # Then delete the appointment
            cur.execute("DELETE FROM appointments WHERE id = %s RETURNING id", (self.id,))
            result = cur.fetchone()
            return result is not None
        finally:
            cur.close() 