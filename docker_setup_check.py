import subprocess
import sys

def check_docker():
    print("Checking Docker connectivity...")
    try:
        # Run 'docker info' to verify connection to the daemon
        result = subprocess.run(['docker', 'info'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ SUCCCESS: Docker is running and accessible!")
            # Print a few key details
            for line in result.stdout.splitlines():
                if "Server Version" in line or "OSType" in line or "Kernel Version" in line:
                    print(f"   {line.strip()}")
            return True
        else:
            print("❌ FAILURE: Docker command ran but returned an error.")
            print(f"Error output:\n{result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ FAILURE: 'docker' command not found. Is it installed and in your PATH?")
        return False
    except Exception as e:
        print(f"❌ FAILURE: An unexpected error occurred: {e}")
        return False

if __name__ == "__main__":
    if check_docker():
        sys.exit(0)
    else:
        sys.exit(1)
