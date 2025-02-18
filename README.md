# EC2 CPU Usage Monitoring API

## Overview

This API monitors the CPU usage of an AWS EC2 instance using CloudWatch and sends an SMS alert via Twilio if the usage exceeds a defined threshold (85%). It assumes an AWS IAM role to retrieve CloudWatch metrics and triggers alerts when necessary.

## Features

- **EC2 CPU Usage Monitoring**: Retrieves the average CPU utilization of an EC2 instance.
- **AWS IAM Role Assumption**: Uses STS to assume a role for accessing CloudWatch.
- **Twilio SMS Alerts**: Sends SMS notifications if CPU usage exceeds 85%.
- **CORS Handling**: Supports Cross-Origin Resource Sharing (CORS) to allow requests from any domain.

## Technology Stack

- **FastAPI**: Web framework for building the API.
- **AWS CloudWatch**: Fetches EC2 instance CPU metrics.
- **AWS STS**: Assumes IAM roles for cross-account access.
- **Twilio API**: Sends SMS alerts.
- **Python**: Primary programming language.

## API Endpoint

### **GET /check_cpu/{account_id}/{role_name}/{instance_id}/{phone_number}**

Retrieves the CPU usage of a specified EC2 instance and sends an SMS alert if the usage exceeds 85%.

#### **Path Parameters**

| Parameter      | Type   | Description                                |
|--------------|--------|--------------------------------------------|
| account_id   | string | AWS account ID where the EC2 instance resides. |
| role_name    | string | IAM role name with permissions to access CloudWatch. |
| instance_id  | string | The EC2 instance ID to monitor. |
| phone_number | string | The phone number to receive the SMS alert. |

#### **Response Format (200 OK)**

```json
{
  "cpu_usage": 72.5,
  "alert_sent": false
}
```

```json
{
  "cpu_usage": 87.9,
  "alert_sent": true
}
```

#### **Response Format (500 Internal Server Error)**

```json
{
  "detail": "Error retrieving CPU usage: <error message>"
}
```

## Setup Instructions

### **Requirements**
- Python 3.7 or higher
- AWS account with CloudWatch permissions
- Twilio account for SMS notifications

### **Install Dependencies**

Clone the repository:

```bash
git clone https://github.com/Oguntayo/hng12-stage3-ec2-cpu_usage-monitoring.git
cd hng12-stage3-ec2-cpu_usage-monitoring
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### **Run Locally**

To start the API locally, use Uvicorn:

```bash
uvicorn main:app --reload
```

The API will be running on **http://127.0.0.1:8000**.

Example request:

```bash
curl "http://127.0.0.1:8000/check_cpu/123456789012/MyRole/i-0abcd1234ef567890/+1234567890"
```

### **Deployment**

To deploy the API, you can use AWS EC2, AWS Lambda, or a hosting service like Render or Heroku.

---

## Notes
- Ensure the AWS IAM role has permissions to read CloudWatch metrics.
- The API handles errors and returns appropriate HTTP status codes.
- The CPU alert threshold is set at 85% but can be modified in the source code.
- Twilio credentials must be set correctly to send SMS alerts.

