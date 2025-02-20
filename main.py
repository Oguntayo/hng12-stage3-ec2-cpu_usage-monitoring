import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
import boto3
import httpx
import asyncio
import requests
from twilio.rest import Client

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Twilio Credentials

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
# TWILIO_ACCOUNT_SID = "AC973b9c10c57b2bb916a225292a2ca5ef"
# TWILIO_AUTH_TOKEN = "2e117115680854c9d1ad3ecbb3da4477"
# TWILIO_PHONE_NUMBER = "+12344234914"
#AWS CREDENTIALS
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Async function to send SMS alert
async def send_sms_alert(to_phone_number: str, message_body: str):
    loop = asyncio.get_event_loop()
    try:
        message = await loop.run_in_executor(
            None, 
            lambda: twilio_client.messages.create(
                body=message_body,
                from_=TWILIO_PHONE_NUMBER,
                to=to_phone_number
            )
        )
        return {"sid": message.sid, "status": message.status}
    except Exception as e:
        return {"error": str(e)}


# Function to assume AWS IAM role
def assume_role(account_id: str, role_name: str):
    try:
        sts_client = boto3.client(
            'sts',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"
        response = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName="CloudWatchAccessSession"
        )
        return response['Credentials']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error assuming role: {str(e)}")
@app.get("/integration.json")
def get_integration_json(request: Request):
    """
    Returns integration metadata for the check_cpu function.
    """
    base_url = str(request.base_url).rstrip("/")
    return {
        "data": {
            "descriptions": {
                "app_name": "AWS EC2 CPU Monitor",
                "app_description": "Monitors EC2 CPU usage and sends alerts",
                "app_url": base_url,
                "app_logo": "https://i.imgur.com/lZqvffp.png",#https://imgur.com/PN3pWJH
                "background_color": "#fff"
            },
            "integration_type": "interval",
            "settings": [
                {"label": "AWS Account ID", "type": "text", "required": True, "default": ""},
                {"label": "IAM Role Name", "type": "text", "required": True, "default": ""},
                {"label": "EC2 Instance ID", "type": "text", "required": True, "default": ""},
                {"label": "Alert Phone Number", "type": "text", "required": True, "default": ""},
                {"label": "Interval", "type": "text", "required": True, "default": "*/5 * * * *"}
            ],
            "tick_url": f"{base_url}/check_cpu/{{AWS_Account_ID}}/{{IAM_Role_Name}}/{{EC2_Instance_ID}}/{{Alert_Phone_Number}}"
        }
    }


class CPUMonitorPayload(BaseModel):
    account_id: str
    role_name: str
    instance_id: str
    phone_number: str
    return_url: str


async def get_cpu_usage(account_id: str, role_name: str, instance_id: str) -> float:
    credentials = assume_role(account_id, role_name)
    cloudwatch_client = boto3.client(
        "cloudwatch",
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
        region_name=AWS_REGION
    )
    
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=5)
    
    response = cloudwatch_client.get_metric_statistics(
        Period=300,
        StartTime=start_time.isoformat(),
        EndTime=end_time.isoformat(),
        MetricName="CPUUtilization",
        Namespace="AWS/EC2",
        Statistics=["Average"],
        Dimensions=[{"Name": "InstanceId", "Value": instance_id}]
    )
    
    if "Datapoints" in response and response["Datapoints"]:
        return response["Datapoints"][0]["Average"]
    return 0.0

async def send_sms_alert(to_phone_number: str, message_body: str):
    loop = asyncio.get_event_loop()
    try:
        message = await loop.run_in_executor(
            None, 
            lambda: twilio_client.messages.create(
                body=message_body,
                from_=TWILIO_PHONE_NUMBER,
                to=to_phone_number
            )
        )
        return {"sid": message.sid, "status": message.status}
    except Exception as e:
        return {"error": str(e)}

async def monitor_cpu_task(payload: CPUMonitorPayload):
    cpu_usage = await get_cpu_usage(payload.account_id, payload.role_name, payload.instance_id)
    alert_sent = False
    end_time = datetime.utcnow()
    end_time = datetime.utcnow()
    formatted_time = end_time.strftime("%H:%M:%S")
    message = f"CPU usage for instance {payload.instance_id} is {cpu_usage}% at {formatted_time}."

    
    if cpu_usage :#>= 85:
        alert_sent = True
        await send_sms_alert(payload.phone_number, message)
    
    data = {
        "event_name": "CPU Monitor",
        "message": message,
        "status": "success" if not alert_sent else "error",
        "username": payload.instance_id
    }
    
    response = requests.post(
        payload.return_url,
        json=data,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    )
    #print(response.json())

@app.post("/tick", status_code=202)
def monitor_cpu(payload: CPUMonitorPayload, background_tasks: BackgroundTasks):
    background_tasks.add_task(monitor_cpu_task, payload)
    return {"status": "accepted"}
