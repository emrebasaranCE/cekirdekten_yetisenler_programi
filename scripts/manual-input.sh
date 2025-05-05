#!/usr/bin/env bash
#
# manual-input.sh
#
# Usage:
#   ./manual-input.sh <latitude> <longitude> <parameter> <value>
#
# Example:
#   ./manual-input.sh 40.123456 28.654321 PM2.5 42.7

API_URL="http://localhost:5001/api/v1/pollution/data"

if [ "$#" -ne 4 ]; then
  echo "Usage: $0 <latitude> <longitude> <parameter> <value>"
  echo "  parameter must be one of: PM2.5, PM10, NO2, SO2, O3"
  exit 1
fi

LAT="$1"
LON="$2"
PARAM="$3"
VALUE="$4"

# Validate pollutant key
case "$PARAM" in
  PM2.5|PM10|NO2|SO2|O3) ;;
  *)
    echo "Error: parameter must be one of PM2.5, PM10, NO2, SO2, O3"
    exit 1
    ;;
esac

# Build the JSON payload
PAYLOAD=$(cat <<EOF
{
  "latitude": $LAT,
  "longitude": $LON,
  "parameters": {
    "$PARAM": $VALUE
  }
}
EOF
)

echo "Sending payload to $API_URL:"
echo "$PAYLOAD"
echo

# Send it
curl -i \
     -X POST "$API_URL" \
     -H "Content-Type: application/json" \
     -d "$PAYLOAD"

echo
