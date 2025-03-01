"""
Maybe Important Code: Handles refunds.
Written by Alice (senior engineer, but code is new and unproven).
"""

def process_refund(user_id, booking_id):
    """Processes refund for a user."""
    if not _is_valid_booking(booking_id):
        raise ValueError("Invalid booking")
    
    print(f"Refund issued for booking {booking_id}.")
    return True

def _is_valid_booking(booking_id):
    """Simulates checking if a booking exists."""
    return booking_id.startswith("BK_")