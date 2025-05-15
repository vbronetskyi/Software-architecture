#!/usr/bin/env bash
# populate-kv.sh — заповнює Consul KV для Kafka

# Якщо потрібно, можна переоприділити через ENV:
CONSUL_ADDR="${CONSUL_ADDR:-http://consul:8500}"
BOOTSTRAP="${BOOTSTRAP:-kafka1:9092,kafka2:9092,kafka3:9092}"
TOPIC="${TOPIC:-messages}"

echo "Waiting for Consul at ${CONSUL_ADDR}…"
until curl --silent "${CONSUL_ADDR}/v1/status/leader" | grep -q ":"; do
  sleep 1
done

echo "Setting config/kafka/bootstrap_servers → ${BOOTSTRAP}"
curl -sSL -X PUT --data "${BOOTSTRAP}" \
     "${CONSUL_ADDR}/v1/kv/config/kafka/bootstrap_servers" && echo " OK"

echo "Setting config/kafka/topic → ${TOPIC}"
curl -sSL -X PUT --data "${TOPIC}" \
     "${CONSUL_ADDR}/v1/kv/config/kafka/topic" && echo " OK"

echo "Done populating KV."
