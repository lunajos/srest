from .jobs import jobs_group
from .nodes import nodes_group
from .partitions import partitions_group
from .reservations import reservations_group
from .licenses import licenses_group
from .diag import diag_group
from .accounts import accounts_group
from .mcs import mcs_group
from .config import config_group
from .auth import auth_group

__all__ = [
    'jobs_group',
    'nodes_group',
    'partitions_group',
    'reservations_group',
    'licenses_group',
    'diag_group',
    'accounts_group',
    'mcs_group',
    'config_group',
    'auth_group'
]