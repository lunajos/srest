import pytest
import os
from unittest.mock import patch, MagicMock
from src.client.client import SlurmClient, SlurmError

@pytest.fixture
def mock_env():
    """Mock environment variables"""
    with patch.dict(os.environ, {
        'SLURM_REST_URL': 'http://slurm.test',
        'SLURM_REST_TOKEN': 'test-token'
    }):
        yield

@pytest.fixture
def client(mock_env):
    """Create test client"""
    return SlurmClient()

def test_client_initialization(mock_env):
    """Test client initialization"""
    client = SlurmClient()
    assert client.base_url == 'http://slurm.test'
    assert client.token == 'test-token'

def test_client_initialization_missing_url():
    """Test client initialization with missing URL"""
    with pytest.raises(ValueError, match="SLURM_REST_URL.*required"):
        SlurmClient()

def test_submit_job(client):
    """Test job submission"""
    with patch.object(client, '_make_request') as mock_request:
        mock_request.return_value = {'job_id': 12345}
        result = client.submit_job('echo test', {'partition': 'debug'})
        assert result['job_id'] == 12345
        mock_request.assert_called_once()

def test_submit_job_array(client):
    """Test job array submission"""
    with patch.object(client, '_make_request') as mock_request:
        mock_request.return_value = {'job_id': 12345}
        result = client.submit_job('echo test', {'array': '1-10:2'})
        assert result['job_id'] == 12345
        mock_request.assert_called_once()

def test_submit_job_invalid_array(client):
    """Test invalid job array submission"""
    with pytest.raises(ValueError, match="Invalid array specification"):
        client.submit_job('echo test', {'array': 'invalid'})

def test_submit_job_dependency(client):
    """Test job dependency submission"""
    with patch.object(client, '_make_request') as mock_request:
        mock_request.return_value = {'job_id': 12345}
        result = client.submit_job('echo test', {'dependency': '12344'})
        assert result['job_id'] == 12345
        mock_request.assert_called_once()

def test_list_jobs(client):
    """Test job listing"""
    with patch.object(client, '_make_request') as mock_request:
        mock_request.return_value = {'jobs': [{'job_id': 12345}]}
        result = client.list_jobs(user='testuser')
        assert len(result['jobs']) == 1
        mock_request.assert_called_once()

def test_cancel_job(client):
    """Test job cancellation"""
    with patch.object(client, '_make_request') as mock_request:
        mock_request.return_value = {}
        client.cancel_job('12345')
        mock_request.assert_called_once()

def test_list_nodes(client):
    """Test node listing"""
    with patch.object(client, '_make_request') as mock_request:
        mock_request.return_value = {'nodes': [{'name': 'node1'}]}
        result = client.list_nodes(state='idle')
        assert len(result['nodes']) == 1
        mock_request.assert_called_once()

def test_list_partitions(client):
    """Test partition listing"""
    with patch.object(client, '_make_request') as mock_request:
        mock_request.return_value = {'partitions': [{'name': 'debug'}]}
        result = client.list_partitions()
        assert len(result['partitions']) == 1
        mock_request.assert_called_once()

def test_list_reservations(client):
    """Test reservation listing"""
    with patch.object(client, '_make_request') as mock_request:
        mock_request.return_value = {'reservations': [{'name': 'test-res'}]}
        result = client.list_reservations()
        assert len(result['reservations']) == 1
        mock_request.assert_called_once()

def test_create_reservation(client):
    """Test reservation creation"""
    with patch.object(client, '_make_request') as mock_request:
        mock_request.return_value = {'name': 'test-res'}
        result = client.create_reservation({'name': 'test-res'})
        assert result['name'] == 'test-res'
        mock_request.assert_called_once()

def test_delete_reservation(client):
    """Test reservation deletion"""
    with patch.object(client, '_make_request') as mock_request:
        mock_request.return_value = {}
        client.delete_reservation('test-res')
        mock_request.assert_called_once()

def test_list_licenses(client):
    """Test license listing"""
    with patch.object(client, '_make_request') as mock_request:
        mock_request.return_value = {'licenses': [{'name': 'matlab'}]}
        result = client.list_licenses()
        assert len(result['licenses']) == 1
        mock_request.assert_called_once()

def test_get_diag(client):
    """Test diagnostics"""
    with patch.object(client, '_make_request') as mock_request:
        mock_request.return_value = {'statistics': {'server_thread_count': 4}}
        result = client.get_diag()
        assert result['statistics']['server_thread_count'] == 4
        mock_request.assert_called_once()

def test_error_handling(client):
    """Test error handling"""
    with patch.object(client.session, 'request') as mock_request:
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_request.return_value = mock_response
        
        with pytest.raises(SlurmError, match="API Error"):
            client.list_jobs()