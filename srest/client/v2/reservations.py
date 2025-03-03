"""Reservation management client"""
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass
from .base import BaseClient
from .models import SlurmMeta

@dataclass
class ReservationInfo:
    """Reservation information"""
    name: str
    accounts: Optional[List[str]] = None
    burst_buffer: Optional[str] = None
    core_count: Optional[int] = None
    end_time: Optional[int] = None
    features: Optional[str] = None
    flags: Optional[List[str]] = None
    licenses: Optional[Dict[str, int]] = None
    node_count: Optional[int] = None
    node_list: Optional[str] = None
    partition: Optional[str] = None
    start_time: Optional[int] = None
    users: Optional[List[str]] = None
    state: Optional[str] = None

@dataclass
class ReservationResponse:
    """Response for reservation queries"""
    meta: SlurmMeta
    reservations: List[ReservationInfo]
    errors: Optional[List[Dict[str, Any]]] = None
    warnings: Optional[List[Dict[str, Any]]] = None

@dataclass
class ReservationCreateRequest:
    """Request to create a reservation"""
    name: str
    start_time: str  # Format: YYYY-MM-DD[THH:MM[:SS]]
    duration: str    # Format: Minutes or HH:MM:SS
    nodes: Optional[str] = None
    node_count: Optional[int] = None
    users: Optional[List[str]] = None
    accounts: Optional[List[str]] = None
    licenses: Optional[Dict[str, int]] = None
    features: Optional[str] = None
    flags: Optional[List[str]] = None
    partition: Optional[str] = None

class ReservationClient(BaseClient):
    """Client for reservation-related operations"""
    
    def get_reservations(self, return_curl: bool = False) -> Union[ReservationResponse, str]:
        """Get list of reservations"""
        return self._make_request(
            method='GET',
            endpoint='/reservations',
            response_type=ReservationResponse,
            return_curl=return_curl
        )
    
    def get_reservation(self, name: str, return_curl: bool = False) -> Union[ReservationResponse, str]:
        """Get information about a specific reservation"""
        return self._make_request(
            method='GET',
            endpoint=f'/reservation/{name}',
            response_type=ReservationResponse,
            return_curl=return_curl
        )
    
    def create_reservation(self, reservation: ReservationCreateRequest, return_curl: bool = False) -> Union[ReservationResponse, str]:
        """Create a new reservation"""
        return self._make_request(
            method='POST',
            endpoint='/reservations',
            json=reservation.__dict__,
            response_type=ReservationResponse,
            return_curl=return_curl
        )
    
    def delete_reservation(self, name: str, return_curl: bool = False) -> Union[ReservationResponse, str]:
        """Delete a reservation"""
        return self._make_request(
            method='DELETE',
            endpoint=f'/reservation/{name}',
            response_type=ReservationResponse,
            return_curl=return_curl
        )
