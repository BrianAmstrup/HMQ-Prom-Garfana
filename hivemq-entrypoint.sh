#!/bin/sh

# Remove DISABLED flagfile
echo "🔧 Removing DISABLED flagfile..."
rm -rf /opt/hivemq/extensions/hivemq-enterprise-security-extension/DISABLED
echo "✅ Security extention is enabled!"


# Remove DISABLED flagfile
echo "🔧 Removing DISABLED flagfile..."
rm -rf /opt/hivemq/extensions/hivemq-postgresql-extension/DISABLED
echo "✅ Postgres extension is enabled!"

# create DISABLED flagfile
echo "🔧 Adding DISABLED flagfile..."
touch /opt/hivemq/extensions/hivemq-allow-all-extension/DISABLED
echo "✅ Allow all is disabled !"


# Start HiveMQ
echo "🚀 Starting HiveMQ..."
/opt/hivemq/bin/run.sh &


echo "\r\r 🚀Probing Hive healthprobe .... \r"
# wait until API is ready
until curl -s --fail localhost:8889/api/v1/health/; do
  sleep 2
done

echo "\r\r Hive healthprobe is now OK 🚀 Enabling Datahub\r\r"
curl -X POST localhost:8888/api/v1/data-hub/management/start-trial

echo "\r🚀  Datahub enabled for 5 hrs\r"

echo "\r🚀 end of hivemq-entrypoint, Now waiting...."
wait


