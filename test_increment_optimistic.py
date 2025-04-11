from hazelcast import HazelcastClient
import time

client = HazelcastClient()
my_map = client.get_map("shared-counter").blocking()

start = time.time()
for _ in range(10_000):
    while True:
        old_value = my_map.get("counter")
        new_value = old_value + 1
        success = my_map.replace_if_same("counter", old_value, new_value)
        if success:
            break
end = time.time()

final = my_map.get("counter")
print(f"[Optimistic CAS] Finished in {end - start:.2f}s. Final counter: {final}")

client.shutdown()
