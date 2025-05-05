# Data Ingestion Scripts

This folder contains two helper Bash scripts for feeding pollution readings into the Data Collector service:

1. **auto-input.sh** — auto-generates a given number of random data points  
2. **manual-input.sh** — allows you to manually submit a single reading

---

## 1. auto-input.sh

### Description

Randomly generates latitude/longitude within a preset range, and random pollutant values, then POSTs them to the collector’s `/api/v1/pollution/data` endpoint.

### Usage

1. Change your directory to `scripts/`
    ```bash
    cd scripts/

2. Give needed permissions to the bash script
    ```bash
    chmod +x auto-input.sh 

3. Run the script
    ```bash 
    ./auto-input.sh

4. After running, the script will ask for number of records to input. 
    ```
    How many random records would you like to generate?
    ```

    Enter any integer, e.g. `50`, and the script will send that many readings.

---

## 2. manual-input.sh

### Description

Submits a single pollution record with the exact coordinates and pollutant/value you specify.

### Usage

1. Change your directory to `scripts/`
    ```bash
    cd scripts/

2. Give needed permissions to the bash script
    ```bash
    chmod +x manual-input.sh

3. Run the script with 4 parameter
    ```bash 
    ./manual-input.sh <latitude> <longitude> <parameter> <value>
    ```

    - **latitude**, **longitude**: decimal degrees  
    - **parameter**: one of `PM2.5`, `PM10`, `NO2`, `SO2`, `O3`  
    - **value**: numeric concentration  

    #### Examples

    ```bash
    # Valid call
    ./manual-input.sh 40.123456 28.654321 PM2.5 42.7

    # Invalid parameter
    ./manual-input.sh 40.1 28.6 O2 10
    # → Error: parameter must be one of PM2.5, PM10, NO2, SO2, O3
    ```

---

## Configuration

Both scripts target the local Data Collector at:

```
http://localhost:5001/api/v1/pollution/data
```

If your collector lives elsewhere, update the `API_URL` variable at the top of each script.