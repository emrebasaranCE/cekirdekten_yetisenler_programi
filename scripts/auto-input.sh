#!/usr/bin/env bash
#
# generate_pollution_data.sh
#
# Prompts for a number of records, then sends that many random pollution
# data points to the /api/v1/pollution/data endpoint.

API_URL="http://localhost:5001/api/v1/pollution/data"

read -p "How many random records would you like to generate? " COUNT
echo "Sending $COUNT records to $API_URL..."

for i in $(seq 1 "$COUNT"); do
  # Generate random latitude (40.000000–40.999999) and longitude (28.000000–28.999999)
  lat="40.$(printf "%06d" $((RANDOM % 1000000)))"
  lon="28.$(printf "%06d" $((RANDOM % 1000000)))"

  # Generate random pollutant values with two decimal places
  pm25="$(printf "%.2f" "$(awk -v r=$RANDOM 'BEGIN{srand(); print r/32767*200}')")"
  pm10="$(printf "%.2f" "$(awk -v r=$RANDOM 'BEGIN{srand(); print r/32767*300}')")"
  no2="$(printf "%.2f" "$(awk -v r=$RANDOM 'BEGIN{srand(); print r/32767*200}')")"
  so2="$(printf "%.2f" "$(awk -v r=$RANDOM 'BEGIN{srand(); print r/32767*150}')")"
  o3="$(printf "%.2f" "$(awk -v r=$RANDOM 'BEGIN{srand(); print r/32767*200}')")"

  # Build the JSON payload (timestamp will be added by the API if missing)
  payload=$(cat <<EOF
{
  "latitude": $lat,
  "longitude": $lon,
  "parameters": {
    "PM2.5": $pm25,
    "PM10": $pm10,
    "NO2": $no2,
    "SO2": $so2,
    "O3": $o3
  }
}
EOF
)

  # Send to the API
  resp=$(curl -s -w "\nHTTP_STATUS:%{http_code}\n" \
    -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d "$payload")

  # Split out the status and body
  body=$(echo "$resp" | sed -e 's/HTTP_STATUS\:.*//g')
  status=$(echo "$resp" | tr -d '\n' | sed -e 's/.*HTTP_STATUS://')

  echo "Record #$i → Status: $status"
  echo "Response: $body"
done

echo "Done."
