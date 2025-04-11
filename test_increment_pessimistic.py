from hazelcast import HazelcastClient
import time

client = HazelcastClient()
my_map = client.get_map("shared-counter").blocking()

# 👉 Без put_if_absent — counter має бути створений заздалегідь = 0

start = time.time()
for _ in range(10_000):
    try:
        my_map.lock("counter")  # 🔒 Блокуємо ключ
        value = my_map.get("counter")
        value += 1
        my_map.put("counter", value)
    finally:
        my_map.unlock("counter")  # 🔓 Розблокування у будь-якому разі
end = time.time()

final_value = my_map.get("counter")
print(f"[Pessimistic] Finished in {end - start:.2f}s. Final counter: {final_value}")

client.shutdown()
