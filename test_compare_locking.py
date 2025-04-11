import subprocess
import time

def run_test(label, script):
    print(f"\nRunning: {label}")
    start = time.time()
    result = subprocess.run(["python", script], capture_output=True, text=True)
    end = time.time()
    
    print(result.stdout)
    print(f"Time measured: {end - start:.2f}s")

# Ensure counter is reset before each test
def reset_counter():
    from hazelcast import HazelcastClient
    client = HazelcastClient()
    client.get_map("shared-counter").blocking().put("counter", 0)
    client.shutdown()
    print("Counter reset to 0")

if __name__ == "__main__":
    for script_name, label in [
        ("test_increment_no_lock.py", "NO LOCK (Race Condition)"),
        ("test_increment_pessimistic.py", "PESSIMISTIC LOCK"),
        ("test_increment_optimistic.py", "OPTIMISTIC (CAS)"),
    ]:
        reset_counter()
        run_test(label, script_name)
