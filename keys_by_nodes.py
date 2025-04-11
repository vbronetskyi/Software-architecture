import hazelcast
from collections import defaultdict

client = hazelcast.HazelcastClient(
    cluster_members=[
        "127.0.0.1:5701",
        "127.0.0.1:5702",
        "127.0.0.1:5703"
    ]
)

my_map = client.get_map("capitals").blocking()
partition_service = client.partition_service

# UUID → Address
uuid_to_address = {
    member.uuid: member.address
    for member in client.cluster_service.get_members()
}

partition_owner_counts = defaultdict(int)

for i in range(1000):
    key = str(i)
    partition_id = partition_service.get_partition_id(key)
    owner_uuid = partition_service.get_partition_owner(partition_id)
    owner_address = uuid_to_address.get(owner_uuid, "Unknown")
    partition_owner_counts[owner_address] += 1

print("\nKeys by nodes:")
for address, count in partition_owner_counts.items():
    print(f"- {address} -> {count} keys")

client.shutdown()

