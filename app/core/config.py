import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Market Analyst Agent"

    # AWS Bedrock Configuration
    aws_region: str=os.getenv("aws_region", "us-east-1")
    aws_access_key: str=os.getenv("aws_access_key_id")
    aws_secret_key: str=os.getenv("aws_secret_access_key")

    #Database Configuration

    database_url: str=os.getenv("database_url","eg:postgresql://user:pass@localhost:5432/market_db")

    # Model ID (Defaulting to Claude 3 Sonnet on Bedrock)
    MODEL_ID: str = "anthropic.claude-3-sonnet-20240229-v1:0"

settings = Settings()