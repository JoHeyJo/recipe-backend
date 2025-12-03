import os
import boto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError

load_dotenv()

ses_client = boto3.client(
    'ses',
    region_name=os.getenv("AWS_REGION")
)

class EmailServices():
    """Backend email services"""
    @staticmethod
    def send_email_ses(recipient_email, subject, body_text, body_html=None):
        """Calls on AWS SES to automate sending emails"""
        try:
            response = ses_client.send_email(
                Source=os.environ["SES_FROM_EMAIL"],
                Destination={'ToAddresses': [recipient_email]},
                Message={
                    'Subject': {'Data': subject},
                    'Body': {
                        'Text': {'Data': body_text}
                    }
                }
            )
            return response
        except ClientError as e:
            raise RuntimeError(
                f"SES send failed: {e.response['Error']['Message']}")

    