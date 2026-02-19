import time
from sandbox_manager import DockerSandbox

def main():
    print("🚀 Starting Sandbox Verification Flow...")
    sandbox = DockerSandbox()
    
    try:
        # 1. Start Sandbox
        print("\n[1/6] Spinning up Docker Sandbox...")
        container_id = sandbox.start_container()
        print(f"✅ Sandbox Active: {container_id}")

        # 2. Inject Buggy Code
        print("\n[2/6] Injecting 'Buggy' Code...")
        buggy_code = """
def add(a, b):
    return a - b  # BUG: Subtraction instead of addition
"""
        test_code = """
import unittest
from calculator import add

class TestAdd(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)

if __name__ == '__main__':
    unittest.main()
"""
        sandbox.inject_file("calculator.py", buggy_code)
        sandbox.inject_file("test_calc.py", test_code)
        print("✅ Code Injected.")

        # 3. Run Test (Expect Failure)
        print("\n[3/6] Running Test (Expecting Failure)...")
        exit_code, output = sandbox.execute_command("python test_calc.py")
        if exit_code != 0:
            print("✅ Test Failed as expected.")
        else:
            print("❌ UNEXPECTED: Test Passed on buggy code!")
            print(output)
            return

        # 4. Inject Fix
        print("\n[4/6] Injecting 'Fixed' Code (Healing)...")
        fixed_code = """
def add(a, b):
    return a + b  # FIXED: Addition
"""
        sandbox.inject_file("calculator.py", fixed_code)
        print("✅ Fix Applied.")

        # 5. Run Test (Expect Success)
        print("\n[5/6] Running Test (Expecting Success)...")
        exit_code, output = sandbox.execute_command("python test_calc.py")
        if exit_code == 0:
            print("✅ Test PASSED! System Healed.")
        else:
            print("❌ FAILURE: Test failed on fixed code.")
            print(output)
            return

        print("\n✨ VERIFICATION SUCCESSFUL! The Sandbox logic is solid.")

    except Exception as e:
        print(f"\n❌ Error during verification: {e}")
    finally:
        # 6. Cleanup
        print("\n[6/6] Cleaning up...")
        sandbox.stop_container()
        print("✅ Sandbox Destroyed.")

if __name__ == "__main__":
    main()
