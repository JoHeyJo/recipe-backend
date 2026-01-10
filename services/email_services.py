import os
import boto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from urllib.parse import urlencode

load_dotenv()

ses_client = boto3.client(
    'ses',
    region_name=os.getenv("AWS_REGION")
)

class EmailServices():
    """Backend email services"""
    @staticmethod
    def send_email_ses(recipient_email, subject, body_html):
        """Calls on AWS SES to automate sending emails"""
        try:
            response = ses_client.send_email(
                Source=os.environ["SES_FROM_EMAIL"],
                Destination={'ToAddresses': [recipient_email]},
                Message={
                    'Subject': {'Data': subject},
                    'Body': {
                        'Html': {'Data': body_html}
                    }
                }
            )
            return response
        except ClientError as e:
            raise RuntimeError(
                f"SES send failed: {e.response['Error']['Message']}")

    @staticmethod
    def create_password_reset_email(token, recipient_email):
        """Compose password reset email requested by client"""
        # link = f"http://localhost:3000/reset?{urlencode({'token': token})}"
        link = f"{os.environ['FRONTEND_RESET_URL']}?{urlencode({'token': token})}"
        subject = "Password rest"
        body_html = f"""
        <p>We received a request to reset your password.</p>
        <p><a href="{link}">Click here to reset your password</a></p>
        <p>If you didn't request this, ignore this email.</p>
        """
        return EmailServices.send_email_ses(recipient_email=recipient_email,subject=subject, body_html=body_html)
