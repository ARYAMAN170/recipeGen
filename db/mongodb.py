# stir-backend/app/db/mongodb.py

import motor.motor_asyncio
from core.config import settings

# The MongoDB client is created once and shared
client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)

# Get a specific database
db = client["recipe_db"]
