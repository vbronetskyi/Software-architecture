from hazelcast import HazelcastClient

client = HazelcastClient()
my_map = client.get_map("distributed-map").blocking()

print("Writing 1000 entries...")
for i in range(1000):
    my_map.put(f"key-{i}", f"value-{i}")

print("Done. Now check Management Center for key distribution.")

client.shutdown()
