# Healing Agent Sandbox Manager
import docker
import tarfile
import io
import os
import time

class DockerSandbox:
    def __init__(self, image_name="healing-agent-sandbox"):
        self.client = docker.from_env()
        self.image_name = image_name
        self.container = None

    def start_container(self, mount_dir=None):
        """
        Starts a detached container.
        Args:
            mount_dir (str): Absolute path to mount to /app (optional).
        """
        try:
            volumes = {}
            if mount_dir:
                volumes = {mount_dir: {'bind': '/app', 'mode': 'rw'}}
            
            print(f"Starting container from image: {self.image_name}")
            self.container = self.client.containers.run(
                self.image_name,
                command="tail -f /dev/null",  # Keep running
                detach=True,
                volumes=volumes,
                working_dir="/app",
                # Add resource limits if needed (e.g., mem_limit='512m')
            )
            print(f"Container started: {self.container.short_id}")
            return self.container.short_id
        except Exception as e:
            print(f"Error starting container: {e}")
            raise

    def stop_container(self):
        """Stops and removes the container."""
        if self.container:
            try:
                print(f"Stopping container: {self.container.short_id}")
                self.container.stop()
                self.container.remove()
                self.container = None
            except Exception as e:
                print(f"Error stopping container: {e}")

    def execute_command(self, cmd):
        """
        Executes a command inside the container.
        Returns: (exit_code, output)
        """
        if not self.container:
            raise RuntimeError("Container not running. Call start_container() first.")

        print(f"Executing: {cmd}")
        try:
            exit_code, output = self.container.exec_run(
                cmd,
                workdir="/app"
            )
            return exit_code, output.decode('utf-8')
        except Exception as e:
            print(f"Error executing command: {e}")
            return -1, str(e)

    def inject_file(self, file_path, content):
        """
        Injects a file with content into the container.
        Args:
            file_path (str): Relative path inside /app (e.g., 'src/fix.py')
            content (str): The content string to write.
        """
        if not self.container:
            raise RuntimeError("Container not running.")

        # Create a tar archive in memory
        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode='w') as tar:
            file_data = content.encode('utf-8')
            tar_info = tarfile.TarInfo(name=file_path)
            tar_info.size = len(file_data)
            tar_info.mtime = time.time()
            tar.addfile(tar_info, io.BytesIO(file_data))
        
        tar_stream.seek(0)
        
        # Put the archive into the container
        # Note: put_archive expects the parent directory to exist.
        # Ideally we ensure parent dirs exist first.
        # For simplicity, we assume root or existing dirs, or we can run mkdir.
        parent_dir = os.path.dirname(file_path)
        if parent_dir:
            self.execute_command(f"mkdir -p {parent_dir}")

        try:
            self.container.put_archive(
                path="/app",  # Extract relative to workdir
                data=tar_stream
            )
            print(f"Injected file: {file_path}")
            return True
        except Exception as e:
            print(f"Error injecting file: {e}")
            return False

if __name__ == "__main__":
    # Simple test
    sandbox = DockerSandbox()
    try:
        sandbox.start_container()
        
        # Test 1: Command
        code, out = sandbox.execute_command("python --version")
        print(f"Python Version: {out.strip()}")
        
        # Test 2: File Injection
        sandbox.inject_file("test_inject.py", "print('Hello from inside container')")
        code, out = sandbox.execute_command("python test_inject.py")
        print(f"Injection Output: {out.strip()}")
        
    finally:
        sandbox.stop_container()
