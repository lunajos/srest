"""Mock server entry point"""
import click
import threading
from .server import start_mock_server
from .auth import start_mock_auth_server

@click.command()
@click.option('--slurm-port', default=8082, help='Port for mock Slurm REST API')
@click.option('--auth-port', default=8081, help='Port for mock Keycloak server')
def main(slurm_port: int, auth_port: int):
    """Start mock servers"""
    # Start servers in threads
    slurm_thread = threading.Thread(target=start_mock_server, args=(slurm_port,))
    auth_thread = threading.Thread(target=start_mock_auth_server, args=(auth_port,))
    
    slurm_thread.daemon = True
    auth_thread.daemon = True
    
    slurm_thread.start()
    auth_thread.start()
    
    print("\nMock Environment Setup:")
    print("----------------------")
    print(f"Mock Slurm REST API: http://localhost:{slurm_port}")
    print(f"Mock Keycloak Server: http://localhost:{auth_port}")
    print("\nTo use with srest, configure:")
    print("srest config set slurm.url http://localhost:8082")
    print("srest config set auth.server_url http://localhost:8081")
    print("\nDefault mock credentials:")
    print("Username: mockuser")
    print("Password: any password will work")
    print("\nPress Ctrl+C to stop servers")
    
    try:
        # Keep main thread alive
        slurm_thread.join()
    except KeyboardInterrupt:
        print("\nStopping mock servers...")

if __name__ == '__main__':
    main()
