from passlib.context import CryptContext

# Create bcrypt context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Hash Password
def hash_password(password):
    return pwd_context.hash(password)


# Verify Password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)