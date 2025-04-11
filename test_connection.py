from hazelcast import HazelcastClient

client = HazelcastClient()

print("\nConnected to Hazelcast cluster:")
connections = client._connection_manager.active_connections.copy()
if not connections:
    print("No active connections found.")
else:
    for conn in connections.values():
        addr = conn.remote_address
        print(f"- Address(host={addr.host}, port={addr.port})")

client.shutdown()
