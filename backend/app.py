# SafeVault Backend API - Secure secrets management
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
import json
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import asyncio

# Load environment variables
load_dotenv()

from database import get_db, User, Secret, SecurityLog, create_tables
from auth import verify_password, get_password_hash, create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES
from metrics import (get_metrics, record_request, record_login_attempt, record_security_event, 
                    record_aws_operation, update_active_users, update_secrets_count)



app = FastAPI(title="SafeVault API")
security = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Metrics middleware
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    # Record metrics
    record_request(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code,
        duration=duration
    )
    
    return response

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    return get_metrics()

# Create tables on startup
create_tables()

# Background task to update business metrics
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(update_business_metrics())

async def update_business_metrics():
    """Update business metrics every 30 seconds"""
    while True:
        try:
            db = next(get_db())
            
            # Update active users count
            active_users_count = db.query(User).filter(User.is_active == True).count()
            update_active_users(active_users_count)
            
            # Update total secrets count
            secrets_count = db.query(Secret).count()
            update_secrets_count(secrets_count)
            
            db.close()
        except Exception as e:
            print(f"Error updating business metrics: {e}")
        
        await asyncio.sleep(30)  # Update every 30 seconds

# Email configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
FROM_EMAIL = os.getenv('FROM_EMAIL', 'noreply@safevault.com')

def send_security_alert(to_email: str, subject: str, message: str):
    """Send security alert email"""
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print(f"📧 Email not configured - Alert: {subject}")
        return
    
    try:
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(message, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"📧 Security alert sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

def log_security_event(db: Session, event_type: str, username: str, ip_address: str, user_agent: str, details: str, user_email: str = None):
    """Log security event and send alerts if needed"""
    # Record security event metric
    record_security_event(event_type)
    
    # Create security log
    security_log = SecurityLog(
        event_type=event_type,
        username=username,
        ip_address=ip_address,
        user_agent=user_agent,
        details=details
    )
    db.add(security_log)
    db.commit()
    
    # Check for suspicious activity
    if event_type == "login_failed":
        # Count failed attempts in last 15 minutes (including this one)
        recent_failures = db.query(SecurityLog).filter(
            SecurityLog.event_type == "login_failed",
            SecurityLog.username == username,
            SecurityLog.created_at > datetime.utcnow() - timedelta(minutes=15)
        ).count()
        
        # Send alert on multiples of 3 (3rd, 6th, 9th, 12th, etc.)
        if recent_failures % 3 == 0 and recent_failures >= 3 and user_email:
            print(f"🚨 TRIGGERING EMAIL ALERT for {username}")
            subject = "🚨 SafeVault Security Alert - Multiple Failed Login Attempts"
            message = f"""
Security Alert for your SafeVault account!

Multiple failed login attempts detected:
- Username: {username}
- IP Address: {ip_address}
- Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
- Failed attempts in last 15 minutes: {recent_failures}

If this wasn't you, please:
1. Change your password immediately
2. Check your account for unauthorized access
3. Contact support if needed

Stay secure!
SafeVault Security Team
            """
            send_security_alert(user_email, subject, message)
    
    elif event_type == "password_changed" and user_email:
        subject = "🔐 SafeVault - Password Changed Successfully"
        message = f"""
Your SafeVault password has been changed successfully.

Details:
- Username: {username}
- IP Address: {ip_address}
- Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

If you didn't make this change, please contact support immediately.

SafeVault Security Team
        """
        send_security_alert(user_email, subject, message)

# Local storage for development
SECRETS_FILE = "secrets.json"

def load_secrets():
    if os.path.exists(SECRETS_FILE):
        with open(SECRETS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_secrets(secrets):
    with open(SECRETS_FILE, 'w') as f:
        json.dump(secrets, f)

# AWS Secrets Manager setup
print(f"AWS_ACCESS_KEY_ID: {os.getenv('AWS_ACCESS_KEY_ID')[:10]}..." if os.getenv('AWS_ACCESS_KEY_ID') else "AWS_ACCESS_KEY_ID: Not set")
print(f"AWS_REGION: {os.getenv('AWS_REGION')}")

try:
    import boto3
    from botocore.config import Config
    
    # Configure with short timeouts to fail fast
    config = Config(
        connect_timeout=2,
        read_timeout=3,
        retries={'max_attempts': 1}
    )
    
    secrets_client = boto3.client(
        'secretsmanager', 
        region_name=os.getenv('AWS_REGION', 'eu-west-1'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        config=config
    )
    
    # Skip connection test - will attempt AWS on each operation
    USE_AWS = True
    print(f"✅ AWS client configured for {os.getenv('AWS_REGION')} (will test on operations)")
except Exception as e:
    USE_AWS = False
    print(f"❌ AWS client initialization failed: {str(e)}")

class SecretRequest(BaseModel):
    name: str
    value: str
    description: str = ""
    category: str = "general"

class SecretResponse(BaseModel):
    name: str
    description: str
    category: str
    created_date: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "user"

class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    payload = verify_token(token)
    username = payload.get("sub")
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.post("/signup")
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"message": "User created successfully", "user_id": db_user.id}

@app.post("/login")
async def login(login_data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_data.username).first()
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        # Record failed login metric
        record_login_attempt(success=False, username=login_data.username)
        
        # Log failed login attempt
        user_email = user.email if user else None
        log_security_event(
            db, "login_failed", login_data.username, client_ip, user_agent,
            f"Invalid credentials for user: {login_data.username}", user_email
        )
        print(f"⚠️ SECURITY ALERT: Failed login attempt for {login_data.username} from {client_ip}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_active:
        # Log disabled account access attempt
        log_security_event(
            db, "login_failed", login_data.username, client_ip, user_agent,
            "Account disabled", user.email
        )
        print(f"⚠️ SECURITY ALERT: Disabled account access attempt for {login_data.username} from {client_ip}")
        raise HTTPException(status_code=401, detail="User account is disabled")
    
    # Record successful login metric
    record_login_attempt(success=True)
    
    # Log successful login
    log_security_event(
        db, "login_success", user.username, client_ip, user_agent,
        "Successful login", user.email
    )
    print(f"✅ LOGIN SUCCESS: {user.username} from {client_ip}")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    }

@app.get("/secrets", response_model=List[SecretResponse])
async def list_secrets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Get user's secrets from database
    print(f"Fetching secrets for user: {current_user.username} (ID: {current_user.id})")
    user_secrets = db.query(Secret).filter(Secret.user_id == current_user.id).all()
    print(f"Found {len(user_secrets)} secrets in database")
    
    # Sync with AWS - add missing secrets and remove deleted ones
    if USE_AWS:
        try:
            # Get all AWS secrets for this user
            aws_response = secrets_client.list_secrets(MaxResults=100)
            aws_secrets = {}
            aws_sync_successful = True
            
            for aws_secret in aws_response.get('SecretList', []):
                aws_name = aws_secret['Name']
                if aws_name.startswith(f"{current_user.username}-"):
                    # Extract the sanitized secret name (remove username prefix)
                    sanitized_secret_name = aws_name.replace(f"{current_user.username}-", "", 1)
                    aws_secrets[sanitized_secret_name] = aws_secret
            
            # Get current database secret names
            db_secret_names = {secret.name for secret in user_secrets}
            
            # Add secrets from AWS that are missing in database
            # Match by sanitized names
            for sanitized_name, aws_secret in aws_secrets.items():
                # Find matching local secret by sanitizing local names
                matching_local = None
                for local_secret in user_secrets:
                    local_sanitized = local_secret.name.replace(' ', '-').replace('_', '-').lower()
                    if local_sanitized == sanitized_name:
                        matching_local = local_secret
                        break
                
                if not matching_local:
                    print(f"➕ Adding {sanitized_name} from AWS to database")
                    new_secret = Secret(
                        name=sanitized_name.replace('-', ' ').title(),  # Convert back to readable name
                        value="[Stored in AWS]",  # Placeholder value
                        description=aws_secret.get('Description', ''),
                        category='general',  # Default category
                        user_id=current_user.id,
                        created_at=aws_secret.get('CreatedDate', datetime.utcnow())
                    )
                    db.add(new_secret)
                    user_secrets.append(new_secret)
            
            # Remove AWS-synced secrets that no longer exist in AWS
            # Match by sanitized names to handle spaces and special characters
            secrets_to_remove = []
            for secret in user_secrets:
                if secret.value == "[Stored in AWS]":  # Only AWS-synced secrets
                    local_sanitized = secret.name.replace(' ', '-').replace('_', '-').lower()
                    if local_sanitized not in aws_secrets:
                        secrets_to_remove.append(secret)
                        print(f"🗑️ Removing {secret.name} - deleted from AWS")
            
            # Delete from database
            for secret in secrets_to_remove:
                db.delete(secret)
                user_secrets.remove(secret)
            
            # Commit all changes
            if aws_secrets or secrets_to_remove:
                db.commit()
                # Count actual additions by checking new secrets
                added_count = len([s for s in user_secrets if s.value == "[Stored in AWS]"])
                removed_count = len(secrets_to_remove)
                if added_count > 0 or removed_count > 0:
                    print(f"✅ AWS Sync: +{added_count} added, -{removed_count} removed")
                else:
                    print(f"✅ AWS Sync: No changes needed")
                
        except Exception as e:
            print(f"⚠️ AWS sync failed: {type(e).__name__} - keeping all local secrets")
            # Don't remove any secrets if AWS sync fails - all secrets are preserved
    
    result = [
        SecretResponse(
            name=secret.name,
            description=secret.description,
            category=getattr(secret, 'category', 'general') or 'general',  # Handle missing category
            created_date=secret.created_at.isoformat()
        )
        for secret in user_secrets
    ]
    print(f"Returning {len(result)} secrets to frontend")
    return result

@app.post("/secrets")
async def create_secret(secret: SecretRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Store in AWS with user prefix and sanitized name
    # AWS secret names can only contain alphanumeric characters, hyphens, and underscores
    sanitized_name = secret.name.replace(' ', '-').replace('_', '-').lower()
    aws_secret_name = f"{current_user.username}-{sanitized_name}"
    aws_stored = False
    print(f"🔄 Attempting to store in AWS as: {aws_secret_name}")
    
    # Try AWS with timeout, fallback to local
    if USE_AWS:
        try:
            import asyncio
            import concurrent.futures
            
            def create_aws_secret():
                return secrets_client.create_secret(
                    Name=aws_secret_name,
                    SecretString=secret.value,
                    Description=f"User: {current_user.username} - {secret.description}"
                )
            
            # Try AWS with 3 second timeout
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(create_aws_secret)
                try:
                    response = future.result(timeout=3)
                    aws_stored = True
                    record_aws_operation("create_secret", True)
                    print(f"✅ AWS Secret created: {aws_secret_name}")
                except concurrent.futures.TimeoutError:
                    record_aws_operation("create_secret", False)
                    print(f"⚠️ AWS timeout - storing locally: {aws_secret_name}")
                    
        except Exception as e:
            error_name = type(e).__name__
            error_msg = str(e)
            print(f"❌ AWS Error Details: {error_name} - {error_msg}")
            
            if 'ResourceExistsException' in error_msg:
                print(f"⚠️ AWS Secret already exists: {aws_secret_name} - updating instead")
                try:
                    # Update existing secret
                    print(f"🔄 Updating existing AWS secret: {aws_secret_name}")
                    secrets_client.update_secret(
                        SecretId=aws_secret_name,
                        SecretString=secret.value,
                        Description=f"User: {current_user.username} - {secret.description}"
                    )
                    aws_stored = True
                    record_aws_operation("update_secret", True)
                    print(f"✅ AWS Secret updated: {aws_secret_name}")
                except Exception as update_error:
                    record_aws_operation("update_secret", False)
                    print(f"❌ AWS update failed: {type(update_error).__name__} - {str(update_error)}")
            else:
                record_aws_operation("create_secret", False)
                print(f"❌ AWS unavailable - storing locally: {error_name}")
                if 'InvalidSignatureException' in error_msg or 'AccessDenied' in error_msg:
                    print("💡 Check AWS credentials and permissions")
    
    # Also store metadata in database
    print(f"Creating secret with category: {secret.category}")
    db_secret = Secret(
        name=secret.name,
        value=secret.value,
        description=secret.description,
        category=secret.category or 'general',
        user_id=current_user.id
    )
    db.add(db_secret)
    db.commit()
    print(f"Secret saved with category: {db_secret.category}")
    
    if aws_stored:
        return {"message": f"Secret stored in AWS eu-west-1 and database"}
    else:
        return {"message": "Secret created in secure local database"}

@app.get("/secrets/{secret_name}")
async def get_secret(secret_name: str, request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Try to get from AWS first
    sanitized_name = secret_name.replace(' ', '-').replace('_', '-').lower()
    aws_secret_name = f"{current_user.username}-{sanitized_name}"
    
    if USE_AWS:
        try:
            response = secrets_client.get_secret_value(SecretId=aws_secret_name)
            record_aws_operation("get_secret", True)
            print(f"✅ Retrieved from AWS eu-west-1: {aws_secret_name}")
            return {"name": secret_name, "value": response['SecretString']}
        except Exception as e:
            record_aws_operation("get_secret", False)
            print(f"❌ AWS Retrieve Error: {str(e)}")
            print(f"Error type: {type(e).__name__}")
    
    # Fallback to database
    secret = db.query(Secret).filter(Secret.name == secret_name, Secret.user_id == current_user.id).first()
    if not secret:
        raise HTTPException(status_code=404, detail="Secret not found")
    print(f"✅ Retrieved from database: {secret_name}")
    
    # Log secret access
    log_security_event(
        db, "secret_accessed", current_user.username, request.client.host,
        request.headers.get("user-agent", ""), f"Accessed secret: {secret_name}"
    )
    
    return {"name": secret.name, "value": secret.value}

@app.delete("/secrets/{secret_name}")
async def delete_secret(secret_name: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Delete from AWS first
    sanitized_name = secret_name.replace(' ', '-').replace('_', '-').lower()
    aws_secret_name = f"{current_user.username}-{sanitized_name}"
    aws_deleted = False
    
    if USE_AWS:
        try:
            secrets_client.delete_secret(SecretId=aws_secret_name, ForceDeleteWithoutRecovery=True)
            aws_deleted = True
            record_aws_operation("delete_secret", True)
            print(f"✅ Deleted from AWS eu-west-1: {aws_secret_name}")
        except Exception as e:
            record_aws_operation("delete_secret", False)
            print(f"❌ AWS Delete Error: {str(e)}")
            print(f"Error type: {type(e).__name__}")
    
    # Delete from database
    secret = db.query(Secret).filter(Secret.name == secret_name, Secret.user_id == current_user.id).first()
    if not secret:
        raise HTTPException(status_code=404, detail="Secret not found")
    
    db.delete(secret)
    db.commit()
    
    if aws_deleted:
        return {"message": "Secret deleted from AWS eu-west-1 and database"}
    else:
        return {"message": "Secret deleted from database (AWS unavailable)"}

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

@app.put("/change-password")
async def change_password(password_data: PasswordChangeRequest, request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Update password in database
    db.query(User).filter(User.id == current_user.id).update({
        "hashed_password": get_password_hash(password_data.new_password)
    })
    db.commit()
    
    # Log password change
    log_security_event(
        db, "password_changed", current_user.username, request.client.host,
        request.headers.get("user-agent", ""), "Password successfully changed", current_user.email
    )
    print(f"✅ PASSWORD CHANGED: {current_user.username} from {request.client.host}")
    
    return {"message": "Password updated successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)