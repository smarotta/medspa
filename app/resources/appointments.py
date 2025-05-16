import json
from app.db.connection import get_connection
from app.models.appointment import Appointment
from app.models.medspa import Medspa
from app.models.service import Service
from datetime import datetime

def create(data):
    """Create a new appointment"""
    conn = get_connection()
    try:
        # Verify medspa exists
        if 'medspa_id' not in data:
            return 400, {"error": "medspa_id is required"}
            
        medspa = Medspa.get_by_id(data['medspa_id'], conn=conn)
        if not medspa:
            return 404, {"error": "Medspa not found"}
        
        # Extract service_ids before creating appointment
        service_ids = data.pop('service_ids', [])
        
        # Force status to be 'scheduled'
        data['status'] = 'scheduled'
        
        # Create appointment
        appointment = Appointment(**data)
        appointment.save(conn=conn)
        
        # Add services if provided
        for service_id in service_ids:
            service = Service.get_by_id(service_id, conn=conn)
            if not service:
                conn.rollback()
                return 404, {"error": f"Service {service_id} not found"}
            try:
                appointment.add_service(service, conn=conn)
            except ValueError as e:
                conn.rollback()
                return 400, {"error": str(e)}
        
        # Get response with totals
        result = appointment.to_dict()
        result['total_duration'] = appointment.total_duration(conn)
        result['total_price'] = appointment.total_price(conn)
        
        conn.commit()
        return 201, result
    except ValueError as e:
        conn.rollback()
        return 400, {"error": str(e)}
    except Exception as e:
        conn.rollback()
        return 500, {"error": str(e)}
    finally:
        conn.close()

def get_by_id(appointment_id):
    """Get an appointment by ID"""
    conn = get_connection()
    try:
        appointment = Appointment.get_by_id(appointment_id, conn=conn)
        if not appointment:
            return 404, {"error": "Appointment not found"}
            
        result = appointment.to_dict()
        result['total_duration'] = appointment.total_duration(conn)
        result['total_price'] = appointment.total_price(conn)
        
        return 200, result
    except Exception as e:
        return 500, {"error": str(e)}
    finally:
        conn.close()

def get_all(query_params=None):
    """Get all appointments, optionally filtered by status or date"""
    conn = get_connection()
    try:
        status = None
        start_date = None
        
        if query_params:
            status = query_params.get('status')
            if 'start_date' in query_params:
                try:
                    start_date = datetime.strptime(query_params['start_date'], '%Y-%m-%d').date()
                except ValueError:
                    return 400, {"error": "Invalid date format. Use YYYY-MM-DD"}
        
        appointments = Appointment.get_all(status=status, start_date=start_date, conn=conn)
                
        # Add total duration and price to each appointment
        results = []
        for appointment in appointments:
            result = appointment.to_dict()
            result['total_duration'] = appointment.total_duration(conn)
            result['total_price'] = appointment.total_price(conn)
            results.append(result)
            
        return 200, results
    except Exception as e:
        return 500, {"error": str(e)}
    finally:
        conn.close()

def update(data, appointment_id):
    """Update an appointment"""
    conn = get_connection()
    try:
        appointment = Appointment.get_by_id(appointment_id, conn=conn)
        if not appointment:
            return 404, {"error": "Appointment not found"}
        
        # Handle status update with transition rules
        if 'status' in data:
            new_status = data['status']
            if new_status not in ['completed', 'canceled']:
                return 400, {"error": "Status must be 'completed' or 'canceled'"}
            appointment.status = new_status
        
        # Update other fields
        if 'start_time' in data:
            appointment.start_time = data['start_time']
        
        # Handle services if provided
        if 'service_ids' in data:
            # Remove all current services
            for service in appointment.services(conn=conn):
                appointment.remove_service(service, conn=conn)
            
            # Add new services
            for service_id in data['service_ids']:
                service = Service.get_by_id(service_id, conn=conn)
                if not service:
                    conn.rollback()
                    return 404, {"error": f"Service {service_id} not found"}
                try:
                    appointment.add_service(service, conn=conn)
                except ValueError as e:
                    conn.rollback()
                    return 400, {"error": str(e)}
        
        appointment.save(conn=conn)
        
        # Get response with totals
        result = appointment.to_dict()
        result['total_duration'] = appointment.total_duration(conn)
        result['total_price'] = appointment.total_price(conn)
        
        conn.commit()
        return 200, result
    except ValueError as e:
        conn.rollback()
        return 400, {"error": str(e)}
    except Exception as e:
        conn.rollback()
        return 500, {"error": str(e)}
    finally:
        conn.close() 