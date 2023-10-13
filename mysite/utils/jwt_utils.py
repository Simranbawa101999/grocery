
from datetime import datetime, timedelta
from rest_framework_jwt.utils import jwt_decode_handler
from rest_framework_jwt.utils import jwt_encode_handler

'''SECRET_KEY = '123'
def generate_jwt_token(user_id):
    try:
        # Create a payload (claims) for the token
        payload = {'user_id': user_id}

        # Encode the payload and create the token
        token = jwt_encode_handler(payload)

        return (True, token)

    except Exception as e:
        return (False, f"Token generation failed: {e}")'''

def verify_jwt_token(token):
    try:
        # Decode the JWT token to get the claims
        claims = jwt_decode_handler(token) #extracted decoded payload 

        # Extract the user_id from the claims
        user_id = claims.get('user_id') #extracted user id from payload 

        # Ensure user_id is an integer
        if isinstance(user_id, int):
            return (True, user_id)
        else:
            return (False, "Invalid user ID in the token.")

    except Exception as e:
        return (False, f"Token verification failed: {e}")