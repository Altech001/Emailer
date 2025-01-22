from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
import os
from dotenv import load_dotenv
from pathlib import Path
from model import ClientData
import jinja2

load_dotenv()

# Create templates directory if it doesn't exist
TEMPLATES_DIR = Path("templates")
TEMPLATES_DIR.mkdir(exist_ok=True)

# Setup Jinja2 template environment
template_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader('templates')
)

config = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT")),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER=str(TEMPLATES_DIR)
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def render_template(template_name: str, **kwargs) -> str:
    template = template_env.get_template(template_name)
    return template.render(**kwargs)

async def contact_us(email: str, message: str, subject: str = "Thanks For Contacting Us"):
    html_content = render_template(
        "client_response.html",
        message=message
    )
    
    message = MessageSchema(
        subject=subject,
        recipients=[email],
        body=html_content,
        subtype=MessageType.html,
        attachments=[
            {
                "file": "assets/attach.jpg",
                "headers": {"Content-ID": "<company_logo>"},
                "mime_type": "image/jpg",
                "mime_subtype": "jpg",
            }
        ]
    )
    
    fm = FastMail(config)
    await fm.send_message(message)

async def feedback(email: str, message: str, client_email: str,client_name: str,client_phone: str,submitted_on: str, subject: str = "New Client Feedback Received"):
    html_content = render_template(
        "feedback_notification.html",
        message=message,
        client_email=client_email,
        client_name=client_name,
        client_phone=client_phone,
        submitted_on=submitted_on,
    )
    
    message = MessageSchema(
        subject=subject,
        recipients=[email],
        body=html_content,
        subtype=MessageType.html,
        attachments=[
            {
                "file": "assets/attach.jpg",
                "headers": {"Content-ID": "assets/attach.jpg"},
                "mime_type": "image/jpg",
                "mime_subtype": "jpg",
            }
        ]
    )
    
    fm = FastMail(config)
    await fm.send_message(message)

@app.post("/root")
async def root(client_data: ClientData):
    try:
        await contact_us(client_data.client_email, client_data.client_message)
        await feedback(os.getenv("ADMIN_EMAIL"), client_data.client_message, client_data.client_email,client_data.client_name,client_data.client_phone,client_data.submitted_on)
        return {"message": "Email has been sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
