"""Mock server for testing"""
import json
import logging
import os
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from ..parsers.submit import SlurmDirectiveParser

# Set up logging
log_dir = os.path.expanduser("~/develop/srest/logs")
os.makedirs(log_dir, exist_ok=True)

# Get the root logger and set up file handler
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(os.path.join(log_dir, 'mock_server.log'))
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Mock data
MOCK_JOBS = {
    "1000": {
        "job_id": "1000",
        "name": "large_simulation",
        "user_name": "mockuser",
        "account": "research",
        "partition": "gpu",
        "qos": "high",
        "job_state": "RUNNING",
        "nodes": 4,
        "cpus_per_task": 8,
        "memory_per_node": "32G",
        "time_limit_minutes": 1440,  # 24 hours
        "work_dir": "/home/mockuser/simulations",
        "command": "python3 simulation.py",
        "submit_time": (datetime.now() - timedelta(hours=2)).isoformat(),
        "start_time": (datetime.now() - timedelta(hours=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(hours=23)).isoformat(),
        "stderr_path": "/home/mockuser/simulations/slurm-1000.err",
        "stdout_path": "/home/mockuser/simulations/slurm-1000.out",
        "array_job_id": None,
        "array_task_id": None,
        "dependencies": None,
        "mcs_label": "confidential",
        "mail_type": None,
        "mail_user": None,
        "constraint": None,
        "nodelist": None,
        "exclude": None
    },
    "1001": {
        "job_id": "1001",
        "name": "data_analysis_array",
        "user_name": "mockuser",
        "account": "research",
        "partition": "cpu",
        "qos": "normal",
        "job_state": "PENDING",
        "nodes": 1,
        "cpus_per_task": 4,
        "memory_per_node": "16G",
        "time_limit_minutes": 120,
        "work_dir": "/home/mockuser/analysis",
        "command": "python3 analyze.py",
        "submit_time": (datetime.now() - timedelta(minutes=30)).isoformat(),
        "start_time": None,
        "end_time": None,
        "stderr_path": "/home/mockuser/analysis/slurm-1001_%A_%a.err",
        "stdout_path": "/home/mockuser/analysis/slurm-1001_%A_%a.out",
        "array_job_id": "1001",
        "array_task_id": "[1-100]",
        "dependencies": None,
        "mcs_label": None,
        "queue_info": {
            "position": 2,
            "estimated_start_time": (datetime.now() + timedelta(minutes=45)).isoformat(),
            "reason": "Resources"
        }
    }
}

MOCK_ACCOUNTS = {
    "research": {
        "name": "research",
        "description": "Research group account",
        "organization": "Research Dept",
        "qos": ["normal", "high"],
        "fairshare": 1000
    },
    "engineering": {
        "name": "engineering",
        "description": "Engineering group account",
        "organization": "Engineering Dept",
        "qos": ["normal", "urgent"],
        "fairshare": 2000
    },
    "test": {
        "name": "test",
        "description": "Test account",
        "organization": "IT Dept",
        "qos": ["normal"],
        "fairshare": 100
    }
}

MOCK_LICENSES = {
    "matlab": {
        "name": "matlab",
        "total": 50,
        "used": 25,
        "remote": False
    },
    "ansys": {
        "name": "ansys",
        "total": 100,
        "used": 75,
        "remote": True
    },
    "cuda": {
        "name": "cuda",
        "total": 200,
        "used": 150,
        "remote": False
    }
}

MOCK_MCS_LABELS = {
    "confidential": {
        "name": "confidential",
        "type": "security",
        "priority": 100,
        "allowed_accounts": ["research", "engineering"]
    },
    "test": {
        "name": "test",
        "type": "testing",
        "priority": 50,
        "allowed_accounts": ["test"]
    },
    "public": {
        "name": "public",
        "type": "security",
        "priority": 0,
        "allowed_accounts": ["*"]
    }
}

MOCK_JOB_ID = 1004

class MockSlurmHandler(BaseHTTPRequestHandler):
    """Handler for mock Slurm REST API"""
    
    def do_GET(self):
        """Handle GET requests"""
        logger.info(f"Received GET request: {self.path}")
        if self.path.startswith('/slurm/v0.0.38/job/'):
            job_id = self.path.split('/')[-1]
            if job_id in MOCK_JOBS:
                response = MOCK_JOBS[job_id].copy()
                # Add queue info for pending jobs
                if response['job_state'] == 'PENDING' and 'queue_info' not in response:
                    response['queue_info'] = {
                        "position": len([j for j in MOCK_JOBS.values() if j['job_state'] == 'PENDING']),
                        "estimated_start_time": (datetime.now() + timedelta(minutes=30)).isoformat(),
                        "reason": "Resources"
                    }
                logger.debug(f"Returning job details for job {job_id}: {json.dumps(response, indent=2)}")
                self._send_json(response)
            else:
                logger.warning(f"Job not found: {job_id}")
                self._send_error("Job not found")
        elif self.path == '/slurm/v0.0.38/jobs':
            logger.debug("Returning list of all jobs")
            self._send_json({"jobs": list(MOCK_JOBS.values())})
        elif self.path == '/slurm/v0.0.38/licenses':
            logger.debug("Returning list of all licenses")
            self._send_json({"licenses": list(MOCK_LICENSES.values())})
        elif self.path.startswith('/slurm/v0.0.38/license/'):
            license_name = self.path.split('/')[-1]
            if license_name in MOCK_LICENSES:
                logger.debug(f"Returning license details for {license_name}")
                self._send_json(MOCK_LICENSES[license_name])
            else:
                logger.warning(f"License not found: {license_name}")
                self._send_error("License not found")
        elif self.path == '/slurm/v0.0.38/mcs/labels':
            type_filter = self.path.split('?type=')[-1] if '?type=' in self.path else None
            labels = list(MOCK_MCS_LABELS.values())
            if type_filter:
                labels = [l for l in labels if l['type'] == type_filter]
            logger.debug(f"Returning MCS labels with type filter: {type_filter}")
            self._send_json({"labels": labels})
        elif self.path.startswith('/slurm/v0.0.38/mcs/'):
            label_name = self.path.split('/')[-1]
            if label_name in MOCK_MCS_LABELS:
                logger.debug(f"Returning MCS label details for {label_name}")
                self._send_json(MOCK_MCS_LABELS[label_name])
            else:
                logger.warning(f"MCS label not found: {label_name}")
                self._send_error("MCS label not found")
        elif self.path == '/slurm/v0.0.38/accounts':
            logger.debug("Returning list of all accounts")
            self._send_json({"accounts": list(MOCK_ACCOUNTS.values())})
        elif self.path.startswith('/slurm/v0.0.38/account/'):
            account_name = self.path.split('/')[-1]
            if account_name in MOCK_ACCOUNTS:
                logger.debug(f"Returning account details for {account_name}")
                self._send_json(MOCK_ACCOUNTS[account_name])
            else:
                logger.warning(f"Account not found: {account_name}")
                self._send_error("Account not found")
        else:
            logger.warning(f"Invalid endpoint: {self.path}")
            self._send_error("Not found")
    
    def do_POST(self):
        """Handle POST requests"""
        logger.info(f"Received POST request: {self.path}")
        if self.path == '/slurm/v0.0.38/job/submit':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            job_data = json.loads(post_data)
            
            # Log the raw submission data
            logger.debug(f"Raw job submission data: {json.dumps(job_data, indent=2)}")
            
            # Parse script directives
            script_content = job_data.get("script", "")
            logger.info("=== Original Script Content ===")
            logger.info(script_content)
            logger.info("==============================")
            
            try:
                script_content, directives = SlurmDirectiveParser.parse_script(script_content)
                logger.info("=== Parsed Script Content (after directive removal) ===")
                logger.info(script_content)
                logger.info("=================================================")
                logger.info(f"Parsed SBATCH directives: {json.dumps(directives, indent=2)}")
            except Exception as e:
                logger.error(f"Error parsing script directives: {e}")
                self._send_error(f"Failed to parse script: {str(e)}")
                return
            
            # Command line args override directives
            params = {
                **directives,
                **job_data.get("job", {})
            }
            logger.debug(f"Final job parameters after merging: {json.dumps(params, indent=2)}")
            
            global MOCK_JOB_ID
            job_id = str(MOCK_JOB_ID)
            MOCK_JOB_ID += 1
            
            # Create mock job with all parsed directives
            try:
                new_job = {
                    "job_id": job_id,
                    "name": params.get("name", f"job_{job_id}"),
                    "user_name": "mockuser",
                    "account": params.get("account", "research"),
                    "partition": params.get("partition", "debug"),
                    "qos": params.get("qos", "normal"),
                    "job_state": "PENDING",
                    "nodes": int(params.get("nodes", 1)),
                    "cpus_per_task": int(params.get("cpus_per_task", 1)),
                    "memory_per_node": params.get("mem", "4G"),
                    "time_limit_minutes": int(params.get("time", 60)),
                    "work_dir": "/home/mockuser/jobs",
                    "command": script_content,  # This will be the actual script content without directives
                    "submit_time": datetime.now().isoformat(),
                    "start_time": None,
                    "end_time": None,
                    "stderr_path": f"/home/mockuser/jobs/slurm-{job_id}.err",
                    "stdout_path": f"/home/mockuser/jobs/slurm-{job_id}.out",
                    "array_job_id": job_id if params.get("array") else None,
                    "array_task_id": params.get("array"),
                    "dependencies": params.get("dependency"),
                    "mcs_label": params.get("mcs_label"),
                    "mail_type": params.get("mail_type"),
                    "mail_user": params.get("mail_user"),
                    "constraint": params.get("constraint"),
                    "nodelist": params.get("nodelist"),
                    "exclude": params.get("exclude"),
                    "queue_info": {
                        "position": len([j for j in MOCK_JOBS.values() if j['job_state'] == 'PENDING']) + 1,
                        "estimated_start_time": (datetime.now() + timedelta(minutes=30)).isoformat(),
                        "reason": "Resources"
                    }
                }
                
                # Log the final job details with special focus on the script
                logger.info("=== Final Job Details ===")
                logger.info(f"Job ID: {job_id}")
                logger.info("Script that will be executed:")
                logger.info(new_job["command"])
                logger.info("=======================")
                
                MOCK_JOBS[job_id] = new_job
                self._send_json({"job_id": job_id})
            except Exception as e:
                logger.error(f"Error creating job: {e}")
                self._send_error(f"Failed to create job: {str(e)}")
                return
        elif self.path.startswith('/slurm/v0.0.38/job/') and self.path.endswith('/cancel'):
            job_id = self.path.split('/')[-2]
            if job_id in MOCK_JOBS:
                MOCK_JOBS[job_id]['job_state'] = 'CANCELLED'
                MOCK_JOBS[job_id]['end_time'] = datetime.now().isoformat()
                logger.info(f"Cancelled job {job_id}")
                self._send_json({"message": f"Job {job_id} cancelled"})
            else:
                logger.warning(f"Job not found: {job_id}")
                self._send_error("Job not found")
        else:
            logger.warning(f"Invalid endpoint: {self.path}")
            self._send_error("Not found")
    
    def _send_json(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _send_error(self, message):
        """Send error response"""
        self.send_response(404)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode())

def run_mock_server():
    """Run mock Slurm REST API server"""
    server = HTTPServer(('localhost', 8082), MockSlurmHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    logger.info("Mock Slurm REST API server running on http://localhost:8082")

if __name__ == '__main__':
    run_mock_server()
    input("Press Enter to quit...")
