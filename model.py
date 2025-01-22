from pydantic import BaseModel
from datetime import datetime

   
class ClientData(BaseModel):
    client_name: str
    client_phone: str
    client_email: str
    client_message: str
    submitted_on: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
