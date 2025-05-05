#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import logging
from datetime import datetime, timedelta
import math

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# WHO guideline thresholds for pollutants (µg/m³)
WHO_THRESHOLDS = {
    'PM2.5': 15.0,  # 24-hour mean
    'PM10': 45.0,   # 24-hour mean
    'NO2': 25.0,    # 24-hour mean
    'SO2': 40.0,    # 24-hour mean
    'O3': 100.0     # 8-hour mean
}

# Dangerous thresholds defined as twice the WHO values
DANGEROUS_THRESHOLDS = {
    pollutant: threshold * 2
    for pollutant, threshold in WHO_THRESHOLDS.items()
}

def is_who_threshold_exceeded(data):
    """
    Check which pollutant parameters exceed WHO guideline or dangerous thresholds.

    Args:
        data (dict): A single pollution reading, containing a 'parameters' dict.

    Returns:
        list of dict: A list of threshold-exceeded anomaly records.
    """
    anomalies = []
    params = data.get('parameters', {})

    for pollutant, raw_value in params.items():
        if pollutant not in WHO_THRESHOLDS:
            continue

        try:
            value = float(raw_value)
        except (TypeError, ValueError):
            continue

        # Check against WHO guideline
        if value > WHO_THRESHOLDS[pollutant]:
            severity = "warning"
            message = (
                f"{pollutant} exceeded WHO threshold "
                f"({value:.2f} > {WHO_THRESHOLDS[pollutant]:.2f})"
            )

            # Check against dangerous threshold
            if value > DANGEROUS_THRESHOLDS[pollutant]:
                severity = "danger"
                message = (
                    f"{pollutant} exceeded dangerous threshold "
                    f"({value:.2f} > {DANGEROUS_THRESHOLDS[pollutant]:.2f})"
                )

            anomalies.append({
                'type': 'threshold_exceeded',
                'parameter': pollutant,
                'value': value,
                'threshold': WHO_THRESHOLDS[pollutant],
                'dangerous_threshold': DANGEROUS_THRESHOLDS[pollutant],
                'severity': severity,
                'message': message
            })

    return anomalies

def calculate_z_score(value, series):
    """
    Compute the Z-score of a value within a series.

    Args:
        value (float): The point to test.
        series (list of float): Reference values.

    Returns:
        float: The Z-score, or 0 if not enough data or zero std dev.
    """
    if len(series) < 2:
        return 0.0

    mean = np.mean(series)
    std = np.std(series)
    if std == 0:
        return 0.0

    return (value - mean) / std

def detect_anomalies(current_data, historical_data):
    """
    Compare current reading against historical data to find statistical anomalies.

    Triggers if:
      - |Z-score| > 3
      - Percent change > 50%

    Also delegates to regional anomaly detection.

    Args:
        current_data (dict): The latest pollution reading.
        historical_data (list of dict): Past readings.

    Returns:
        list of dict: Statistical and regional anomalies detected.
    """
    anomalies = []

    # Need at least 5 past points
    if len(historical_data) < 5:
        return anomalies

    curr_params = current_data.get('parameters', {})

    # Collect history per pollutant
    history_by_param = {p: [] for p in WHO_THRESHOLDS}
    for record in historical_data:
        rec_params = record.get('parameters', {})
        for pollutant in history_by_param:
            if pollutant in rec_params:
                try:
                    history_by_param[pollutant].append(float(rec_params[pollutant]))
                except (TypeError, ValueError):
                    pass

    # Compute 24h mean historical values
    historical_means = {
        p: np.mean(vals)
        for p, vals in history_by_param.items() if vals
    }

    # Check each current pollutant
    for pollutant, raw_value in curr_params.items():
        try:
            curr_value = float(raw_value)
        except (TypeError, ValueError):
            logger.warning(f"Non-numeric value for {pollutant}")
            continue

        if pollutant in historical_means:
            mean = historical_means[pollutant]
            z = calculate_z_score(curr_value, history_by_param[pollutant])
            pct_change = ((curr_value - mean) / mean * 100) if mean > 0 else 0

            # Flag if stats conditions met
            if abs(z) > 3 or abs(pct_change) > 50:
                sev = "warning"
                msg = ""
                if abs(z) > 3:
                    sev = "danger" if abs(z) > 5 else "warning"
                    msg = f"{pollutant} abnormal change (Z-score: {z:.2f})"
                if abs(pct_change) > 50:
                    direction = "increase" if pct_change > 0 else "decrease"
                    sev = "danger" if abs(pct_change) > 100 else sev
                    msg = f"{pollutant} {abs(pct_change):.1f}% {direction}"

                anomalies.append({
                    'type': 'statistical_anomaly',
                    'parameter': pollutant,
                    'value': curr_value,
                    'average': mean,
                    'z_score': z,
                    'percent_change': pct_change,
                    'severity': sev,
                    'message': msg
                })

    # Append any regional anomalies
    detect_regional_anomalies(current_data, historical_data, anomalies)
    return anomalies

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Compute the great-circle distance between two points on Earth.

    Args:
        lat1, lon1, lat2, lon2 (float): Coordinates in decimal degrees.

    Returns:
        float: Distance in kilometers.
    """
    R = 6371.0  # Earth radius in km
    φ1, φ2 = math.radians(lat1), math.radians(lat2)
    Δφ = math.radians(lat2 - lat1)
    Δλ = math.radians(lon2 - lon1)

    a = math.sin(Δφ/2)**2 + math.cos(φ1) * math.cos(φ2) * math.sin(Δλ/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def detect_regional_anomalies(current_data, historical_data, anomalies):
    """
    Identify anomalies when a reading drastically differs from nearby stations.

    Looks at readings within a 25km radius in the past 6 hours.

    Args:
        current_data (dict): The latest reading.
        historical_data (list of dict): Past readings.
        anomalies (list): List to append any regional anomalies to.
    """
    try:
        lat = float(current_data.get('latitude', 0))
        lon = float(current_data.get('longitude', 0))
        timestamp = datetime.fromisoformat(current_data['timestamp'].replace('Z', ''))
        window_start = timestamp - timedelta(hours=6)

        # Gather nearby records in time window
        nearby = []
        for rec in historical_data:
            try:
                rec_time = datetime.fromisoformat(rec['timestamp'].replace('Z', ''))
                if window_start <= rec_time <= timestamp:
                    rec_lat = float(rec.get('latitude', 0))
                    rec_lon = float(rec.get('longitude', 0))
                    if haversine_distance(lat, lon, rec_lat, rec_lon) <= 25.0:
                        nearby.append(rec)
            except Exception:
                continue

        if not nearby:
            return

        # Compute regional means
        region_means = {}
        curr_params = current_data.get('parameters', {})
        for pollutant in curr_params:
            values = []
            for rec in nearby:
                try:
                    values.append(float(rec['parameters'][pollutant]))
                except Exception:
                    pass
            if values:
                region_means[pollutant] = np.mean(values)

        # Compare current against region
        for pollutant, raw_val in curr_params.items():
            try:
                curr_val = float(raw_val)
            except Exception:
                continue

            if pollutant in region_means:
                reg_mean = region_means[pollutant]
                pct_diff = ((curr_val - reg_mean) / reg_mean * 100) if reg_mean > 0 else 0
                if abs(pct_diff) > 75:
                    direction = "higher" if pct_diff > 0 else "lower"
                    sev = "danger" if abs(pct_diff) > 150 else "warning"
                    # Avoid duplicating if already flagged
                    if not any(a['parameter'] == pollutant and a['type'] in ['statistical_anomaly', 'regional_anomaly'] for a in anomalies):
                        anomalies.append({
                            'type': 'regional_anomaly',
                            'parameter': pollutant,
                            'value': curr_val,
                            'regional_avg': reg_mean,
                            'percent_diff': pct_diff,
                            'severity': sev,
                            'message': f"{pollutant} is {abs(pct_diff):.1f}% {direction} than regional average"
                        })

    except Exception as e:
        logger.error(f"Error detecting regional anomalies: {e}")
