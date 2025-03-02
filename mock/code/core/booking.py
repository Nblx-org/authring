"""
Extremely Important Code: Handles flight reservations.
Written by Alice (senior engineer, domain expert, long tenure).
"""

import asyncio

async def book_flight(user_id, flight_id):
    """Handles flight booking logic."""
    # Simulated database interaction
    await asyncio.sleep(0.1)  # Simulate async database interaction
    if flight_id not in FLIGHT_SCHEDULE:
        raise ValueError("Invalid flight ID")
    if FLIGHT_SCHEDULE[flight_id]['seats'] == 0:
        raise ValueError("Flight is full")
    
    FLIGHT_SCHEDULE[flight_id]['seats'] -= 1
    print(f"Flight {flight_id} booked for user {user_id}.")
    return True

FLIGHT_SCHEDULE = {
    "AA123": {"seats": 5},
    "BB456": {"seats": 0}  # Full flight
}