from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient(
    "mongodb://localhost:27017",
    serverSelectionTimeoutMS=3000,
    connectTimeoutMS=3000,
)

# Database
db = client["travel_rag"]

# Collections
users_collection = db["users"]
embeddings_collection = db["travel_embeddings"]


def ensure_indexes():
    """Keep email unique without making MongoDB unavailable for a long time."""
    try:
        users_collection.create_index("email", unique=True)
        embeddings_collection.create_index(
            [("index_version", 1), ("chunk_id", 1)], unique=True
        )
    except Exception:
        # Authentication endpoints return a friendly error if MongoDB is down.
        # The chatbot itself remains usable.
        pass
