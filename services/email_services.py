import os
import boto3
from dotenv import load_dotenv

load_dotenv()

ses_client = boto3.client(
    'ses',
    region_name=os.getenv("AWS_REGION")
)


def send_email_ses(recipient_email, subject, body_text, body_html=None):
    try:
        response = ses_client.send_email(
            Source='noreply@slingitdrinks.com',
            Destination={'ToAddresses': [recipient_email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {
                    'Text': {'Data': body_text}
                }
            }
        )
        return response
    except Exception as e:
        print(f"Error sending email: {e}")
        return None
