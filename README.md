# EC2 CPU Usage Monitoring API

## Overview

This API monitors the CPU usage of an AWS EC2 instance and provides real-time metrics. It helps in tracking resource utilization and detecting anomalies that might indicate performance issues. The API collects CPU usage statistics and can be integrated into monitoring dashboards or alerting systems.

## Features

- **Real-time CPU Monitoring**: Fetches the current CPU usage of an EC2 instance.
- **Historical Data Retrieval**: Allows users to retrieve CPU usage trends over a period.
- **Threshold-Based Alerts**: Sends alerts if CPU usage exceeds a predefined threshold.
- **CORS Handling**: Supports Cross-Origin Resource Sharing (CORS) for accessibility from different domains.

## Technology Stack

- **FastAPI**: Web framework for building APIs.
- **Python**: Programming language.
- **Boto3**: AWS SDK for Python to interact with EC2 CloudWatch metrics.
- **Uvicorn**: ASGI server for running the API.

## API Endpoints

### **1. Get Current CPU Usage**
**GET /api/cpu-usage**

#### Response Format (200 OK)
```json
{
  "instance_id": "i-0abcd1234efgh5678",
  "cpu_usage": 42.5,
  "timestamp": "2025-02-18T12:30:00Z"
}
```

#### Response Format (400 Bad Request)
```json
{
  "error": "Invalid request parameters"
}
```

### **2. Get CPU Usage History**
**GET /api/cpu-usage-history?start_time=YYYY-MM-DDTHH:MM:SSZ&end_time=YYYY-MM-DDTHH:MM:SSZ**

#### Response Format (200 OK)
```json
{
  "instance_id": "i-0abcd1234efgh5678",
  "cpu_usage_history": [
    { "timestamp": "2025-02-18T12:00:00Z", "cpu_usage": 35.2 },
    { "timestamp": "2025-02-18T12:10:00Z", "cpu_usage": 38.6 }
  ]
}
```

## Setup Instructions

### **Requirements**
- Python 3.7 or higher
- AWS credentials configured for accessing EC2 metrics
- pip for installing Python dependencies

### **Install Dependencies**
Clone the repository:
```sh
git clone https://github.com/Oguntayo/hng12-stage3-ec2-cpu_usage-monitoring.git
cd hng12-stage3-ec2-cpu_usage-monitoring
```
Install the required Python dependencies:
```sh
pip install -r requirements.txt
```

### **Run Locally**
To run the API locally, use Uvicorn:
```sh
uvicorn main:app --reload
```
The API will be running on http://127.0.0.1:8000.

You can access it by visiting the following URL:
```sh
http://127.0.0.1:8000/api/cpu-usage
```

### **Test the API Locally**
You can test the API using any HTTP client like Postman or cURL:
```sh
curl "http://127.0.0.1:8000/api/cpu-usage"
```

### **Access the Endpoint Online**
The API is deployed and accessible via the following public URL:
```
https://hng12-stage3-ec2-cpu-usage-monitoring.onrender.com/
```

### **Example Request**
To get CPU usage, make a GET request to:
```
https://hng12-stage3-ec2-cpu-usage-monitoring.onrender.com/api/cpu-usage
```

### **Example Response**
```json
{
  "instance_id": "i-0abcd1234efgh5678",
  "cpu_usage": 42.5,
  "timestamp": "2025-02-18T12:30:00Z"
}
```

## Notes
- The API retrieves CPU usage data from AWS CloudWatch.
- Ensure your AWS credentials are correctly configured to access EC2 metrics.
- The API returns a 400 Bad Request response if invalid parameters are provided.
- This API is useful for cloud monitoring and automated alerting systems.

