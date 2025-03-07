"""Reservation management client"""
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass
from .base import BaseClient
from .models import SlurmMeta

@dataclass
class ReservationInfo:
    """Reservation information"""
    accounts: Optional[List[str]] = None
    burst_buffer: Optional[str] = None
    core_count: Optional[int] = None
    end_time: Optional[int] = None
    features: Optional[str] = None
    flags: Optional[List[str]] = None
    licenses: Optional[Dict[str, int]] = None
    name: Optional[str] = None
    node_count: Optional[int] = None
    node_list: Optional[str] = None
    partition: Optional[str] = None
    start_time: Optional[int] = None
    users: Optional[List[str]] = None
    state: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values"""
        return {k: v for k, v in self.__dict__.items() if v is not None}

    def get(self, key: str, default: Any = None) -> Any:
        """Get value by key with default"""
        return getattr(self, key, default)

@dataclass
class ReservationResponse:
    """Response for reservation queries"""
    meta: Optional[SlurmMeta] = None
    reservations: Optional[List[ReservationInfo]] = None
    errors: Optional[List[Dict[str, Any]]] = None
    warnings: Optional[List[Dict[str, Any]]] = None

    def __post_init__(self):
        """Post-initialization processing"""
        if self.reservations is None:
            self.reservations = []
        else:
            self.reservations = [ReservationInfo(**r) if isinstance(r, dict) else r for r in self.reservations]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'meta': self.meta.to_dict() if self.meta else {},
            'reservations': [r.to_dict() for r in self.reservations] if self.reservations else [],
            'errors': self.errors if self.errors else [],
            'warnings': self.warnings if self.warnings else []
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get value by key with default"""
        return getattr(self, key, default)

@dataclass
class ReservationCreateRequest:
    """Request to create a reservation"""
    name: str
    start_time: str  # Format: YYYY-MM-DD[THH:MM[:SS]]
    duration: str    # Format: Minutes or HH:MM:SS
    nodes: Optional[str] = None
    node_cnt: Optional[int] = None
    users: Optional[List[str]] = None
    accounts: Optional[List[str]] = None
    licenses: Optional[Dict[str, int]] = None
    features: Optional[str] = None
    flags: Optional[List[str]] = None
    partition: Optional[str] = None
    core_cnt: Optional[int] = None
    burst_buffer: Optional[str] = None
    tres_per_node: Optional[str] = None
    watts: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values"""
        return {k: v for k, v in self.__dict__.items() if v is not None}

class ReservationClient(BaseClient):
    """Client for reservation-related operations"""
    
    def get_reservations(self, return_curl: bool = False) -> Union[ReservationResponse, str]:
        """Get list of reservations"""
        return self._make_request(
            method='GET',
            endpoint='reservations',  # Endpoint paths are now relative to base API URL
            response_type=ReservationResponse,
            return_curl=return_curl
        )
    
    def get_reservation(self, name: str, return_curl: bool = False) -> Union[ReservationResponse, str]:
        """Get information about a specific reservation"""
        return self._make_request(
            method='GET',
            endpoint=f'reservation/{name}',  # Endpoint paths are now relative to base API URL
            response_type=ReservationResponse,
            return_curl=return_curl
        )
    
    def create_reservation(self, reservation: ReservationCreateRequest, return_curl: bool = False) -> Union[ReservationResponse, str]:
        """Create a new reservation"""
        return self._make_request(
            method='POST',
            endpoint='reservation',  # Endpoint paths are now relative to base API URL
            json=reservation.to_dict(),
            response_type=ReservationResponse,
            return_curl=return_curl
        )
    
    def delete_reservation(self, name: str, return_curl: bool = False) -> Union[ReservationResponse, str]:
        """Delete a reservation"""
        return self._make_request(
            method='DELETE',
            endpoint=f'reservation/{name}',  # Endpoint paths are now relative to base API URL
            response_type=ReservationResponse,
            return_curl=return_curl
        )
