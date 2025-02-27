"""Mock Slurm REST API server for testing"""
import json
import random
import threading
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, List
from pathlib import Path

class MockData:
    """Mock data generator"""
    
    def __init__(self):
        self.jobs: Dict[str, Dict] = {}
        self.job_id_counter = 1000
        self.nodes = self._generate_nodes()
        self.partitions = self._generate_partitions()
        self.accounts = self._generate_accounts()
        self.associations = self._generate_associations()
        self.mcs_labels = self._generate_mcs_labels()
        
    def _generate_nodes(self) -> List[Dict]:
        """Generate mock nodes"""
        nodes = []
        for i in range(1, 5):
            nodes.append({
                'name': f'node{i}',
                'state': random.choice(['IDLE', 'ALLOCATED', 'MIXED']),
                'cpus': 32,
                'alloc_cpus': random.randint(0, 32),
                'real_memory': 128000,
                'alloc_memory': random.randint(0, 128000),
                'features': ['gpu', 'nvlink'] if i <= 2 else ['cpu']
            })
        return nodes
    
    def _generate_partitions(self) -> List[Dict]:
        """Generate mock partitions"""
        return [
            {
                'name': 'debug',
                'nodes': 'node[1-2]',
                'max_time': 60,
                'default': True
            },
            {
                'name': 'gpu',
                'nodes': 'node[1-2]',
                'max_time': 1440,
                'default': False
            },
            {
                'name': 'cpu',
                'nodes': 'node[3-4]',
                'max_time': 4320,
                'default': False
            }
        ]
    
    def _generate_accounts(self) -> List[Dict]:
        """Generate mock accounts"""
        return [
            {
                'name': 'research',
                'description': 'Research group account',
                'organization': 'Research Dept',
                'users': ['mockuser', 'researcher1', 'researcher2'],
                'qos': ['normal', 'high'],
                'fairshare': 1000
            },
            {
                'name': 'engineering',
                'description': 'Engineering group account',
                'organization': 'Engineering Dept',
                'users': ['mockuser', 'engineer1', 'engineer2'],
                'qos': ['normal', 'urgent'],
                'fairshare': 2000
            },
            {
                'name': 'test',
                'description': 'Test account',
                'organization': 'IT Dept',
                'users': ['mockuser'],
                'qos': ['normal'],
                'fairshare': 100
            }
        ]
    
    def _generate_associations(self) -> List[Dict]:
        """Generate mock user-account associations"""
        associations = []
        for account in self.accounts:
            for user in account['users']:
                associations.append({
                    'user': user,
                    'account': account['name'],
                    'partition': '*',
                    'max_jobs': 1000,
                    'max_nodes': 100,
                    'max_cpus': 1000,
                    'qos': account['qos'],
                    'default_qos': account['qos'][0]
                })
        return associations
    
    def _generate_mcs_labels(self) -> List[Dict]:
        """Generate mock MCS labels"""
        return [
            {
                'name': 'secure1',
                'type': 'security',
                'priority': 1,
                'allowed_accounts': ['research'],
                'allowed_users': ['mockuser', 'researcher1']
            },
            {
                'name': 'secure2',
                'type': 'security',
                'priority': 2,
                'allowed_accounts': ['engineering'],
                'allowed_users': ['mockuser', 'engineer1']
            },
            {
                'name': 'classified',
                'type': 'security',
                'priority': 3,
                'allowed_accounts': ['research', 'engineering'],
                'allowed_users': ['mockuser']
            }
        ]

    def submit_job(self, script: str, params: Dict) -> Dict:
        """Submit a mock job"""
        job_id = str(self.job_id_counter)
        self.job_id_counter += 1
        
        # Validate account
        account = params.get('account')
        if account and not any(a['name'] == account for a in self.accounts):
            raise ValueError(f"Account not found: {account}")
            
        # Validate MCS label
        mcs_label = params.get('mcs_label')
        if mcs_label:
            label = next((l for l in self.mcs_labels if l['name'] == mcs_label), None)
            if not label:
                raise ValueError(f"MCS label not found: {mcs_label}")
            if account and account not in label['allowed_accounts']:
                raise ValueError(f"Account {account} not allowed for MCS label {mcs_label}")
        
        job = {
            'job_id': job_id,
            'name': params.get('job_name', 'mock_job'),
            'state': 'PENDING',
            'user_id': 1000,
            'user_name': 'mockuser',
            'account': account or self.accounts[0]['name'],  # Default to first account
            'mcs_label': mcs_label,
            'nodes': [],
            'submit_time': int(datetime.now().timestamp()),
            'start_time': 0,
            'end_time': 0
        }
        
        self.jobs[job_id] = job
        
        # Simulate job progression in background
        def run_job():
            import time
            time.sleep(2)  # Pending for 2 seconds
            job['state'] = 'RUNNING'
            job['start_time'] = int(datetime.now().timestamp())
            time.sleep(5)  # Run for 5 seconds
            job['state'] = 'COMPLETED'
            job['end_time'] = int(datetime.now().timestamp())
            
        threading.Thread(target=run_job).start()
        return {'job_id': job_id}

class MockHandler(BaseHTTPRequestHandler):
    """Mock REST API handler"""
    
    def __init__(self, *args, **kwargs):
        self.mock_data = MockData()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            if self.path.startswith('/slurm/v0.0.38/jobs'):
                response = {'jobs': list(self.mock_data.jobs.values())}
            elif self.path.startswith('/slurm/v0.0.38/nodes'):
                response = {'nodes': self.mock_data.nodes}
            elif self.path.startswith('/slurm/v0.0.38/partitions'):
                response = {'partitions': self.mock_data.partitions}
            elif self.path.startswith('/slurm/v0.0.38/accounts'):
                response = {'accounts': self.mock_data.accounts}
            elif self.path.startswith('/slurm/v0.0.38/associations'):
                response = {'associations': self.mock_data.associations}
            elif self.path.startswith('/slurm/v0.0.38/mcs'):
                response = {'labels': self.mock_data.mcs_labels}
            elif self.path.startswith('/slurm/v0.0.38/diag'):
                response = {
                    'statistics': {
                        'server_thread_count': 4,
                        'agent_queue_size': 0,
                        'jobs_submitted': len(self.mock_data.jobs),
                        'jobs_started': sum(1 for j in self.mock_data.jobs.values() if j['state'] in ['RUNNING', 'COMPLETED']),
                        'jobs_completed': sum(1 for j in self.mock_data.jobs.values() if j['state'] == 'COMPLETED'),
                    }
                }
            elif self.path.startswith('/slurm/v0.0.38/ping'):
                response = {
                    'ping': 'pong',
                    'version': 'v0.0.38',
                    'slurm_version': '23.02.0'
                }
            else:
                self.send_error(404)
                return
                
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_error(500, str(e))
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            if self.path.startswith('/slurm/v0.0.38/jobs'):
                content_length = int(self.headers['Content-Length'])
                body = self.rfile.read(content_length)
                data = json.loads(body)
                
                response = self.mock_data.submit_job(data['script'], data)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_error(404)
                
        except Exception as e:
            self.send_error(500, str(e))
    
    def do_DELETE(self):
        """Handle DELETE requests"""
        try:
            if self.path.startswith('/slurm/v0.0.38/jobs/'):
                job_id = self.path.split('/')[-1]
                if job_id in self.mock_data.jobs:
                    self.mock_data.jobs[job_id]['state'] = 'CANCELLED'
                    
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({}).encode())
            else:
                self.send_error(404)
                
        except Exception as e:
            self.send_error(500, str(e))

def start_mock_server(port: int = 8082):
    """Start mock server"""
    server = HTTPServer(('localhost', port), MockHandler)
    print(f"Mock Slurm REST API server running on http://localhost:{port}")
    server.serve_forever()
