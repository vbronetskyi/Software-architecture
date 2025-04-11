from hazelcast import HazelcastClient
import time

client = HazelcastClient()
map = client.get_map("shared-counter").blocking()

map.put_if_absent("counter", 0)

start = time.time()
for _ in range(10_000):
    value = map.get("counter")
    value += 1
    map.put("counter", value)
end = time.time()

print(f"Client done in {end - start:.2f}s")
final = map.get("counter")
print(f"Final value (might be incorrect): {final}")

client.shutdown()
