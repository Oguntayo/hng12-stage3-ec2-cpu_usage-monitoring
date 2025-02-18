from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import boto3
from twilio.rest import Client
from datetime import datetime, timedelta
import asyncio
import os
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
TWILIO_ACCOUNT_SID = "AC973b9c10c57b2bb916a225292a2ca5ef"
TWILIO_AUTH_TOKEN = "2e117115680854c9d1ad3ecbb3da4477"
TWILIO_PHONE_NUMBER = "+12344234914"
#ALERT_PHONE_NUMBER = '+2348149650354'

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


AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")



# Function to assume AWS IAM role
def assume_role(account_id: str, role_name: str):
    try:
        #sts_client = boto3.client('sts')
        sts_client = boto3.client(
    'sts',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)
        role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"
        response = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName="CloudWatchAccessSession"
        )
        return response['Credentials']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error assuming role: {str(e)}")

@app.get("/check_cpu/{account_id}/{role_name}/{instance_id}/{phone_number}")
async def check_cpu(account_id: str, role_name: str, instance_id: str,phone_number:str):
    """
    Get CPU usage for the given EC2 instance and send an SMS alert if usage exceeds 85%.
    """
    try:
        credentials = assume_role(account_id, role_name)
        cloudwatch_client = boto3.client(
            'cloudwatch',
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken']
        )

        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=5)

        response = cloudwatch_client.get_metric_statistics(
            Period=300,
            StartTime=start_time.isoformat(),
            EndTime=end_time.isoformat(),
            MetricName='CPUUtilization',
            Namespace='AWS/EC2',
            Statistics=['Average'],
            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}]
        )

        if 'Datapoints' in response and response['Datapoints']:
            cpu_usage = response['Datapoints'][0]['Average']
            alert_sent = False
            
            if cpu_usage >= 85:
                message_body = f"ALERT: CPU usage for instance {instance_id} is {cpu_usage}%."
                await send_sms_alert(phone_number, message_body)
                alert_sent = True

            return {"cpu_usage": cpu_usage, "alert_sent": alert_sent}
        else:
            return {"cpu_usage": 0, "alert_sent": False}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving CPU usage: {str(e)}")
