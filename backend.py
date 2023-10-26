from flask import Flask, request, jsonify
import db_connection
import random
import string
import jwt
import datetime
import smtplib
from email.mime.text import MIMEText
from flask_swagger_ui import get_swaggerui_blueprint
app = Flask(__name__)

SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/static/swagger.json'  # Our API url (can of course be a local resource)

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "Test application"
    },
    # oauth_config={  # OAuth config. See https://github.com/swagger-api/swagger-ui#oauth2-configuration .
    #    'clientId': "your-client-id",
    #    'clientSecret': "your-client-secret-if-required",
    #    'realm': "your-realms",
    #    'appName': "your-app-name",
    #    'scopeSeparator': " ",
    #    'additionalQueryStringParams': {'test': "hello"}
    # }
)

app.register_blueprint(swaggerui_blueprint)

# Replace with a strong secret key for JWT token generation
app.config['SECRET_KEY'] = 'your-secret-key'

# Replace with your SMTP email settings
SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = 'cheeraganesh1995@gmail.com'
SMTP_PASS = 'arrg begf poyg alvn'

# Database connection
def get_db_connection():
    return db_connection.data_connection()

# Generate a random password
def generate_random_password(length):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

# Signup route
@app.route('/signup', methods=['POST'])
def signup():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        data = request.json
        firstname = data.get('firstname')
        middlename = data.get('middlename')
        lastname = data.get('lastname')
        email = data.get('email')
        phonenumber = data.get('phonenumber')
        gender = data.get('gender')
        relationship = data.get('relationship')
        dateofbirth = data.get('dateofbirth')
        password = data.get('password')

        # For security, store the password securely, e.g., hashed with bcrypt

        args = (firstname, middlename, lastname, email, phonenumber, gender, relationship, dateofbirth, password)
        db_query = "INSERT INTO user (firstname, middlename, lastname, email, phonenumber, gender, relationship, dateofbirth, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(db_query, args)
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({"message": "Registered Successfully"},data), 200
    except Exception as er:
        return jsonify({"err": str(er)}), 500

# Generate a JWT token
def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

# Login route
@app.route('/login', methods=['POST'])
def login():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        data = request.json
        email = data.get('email')
        password = data.get('password')  # Assuming you have a password field in the request

        # Verify user credentials - Replace this with your actual authentication logic
        db_query = "SELECT user_id, password FROM user WHERE email = %s"
        cursor.execute(db_query, (email,))
        user = cursor.fetchone()

        if user and password == user[1]:  # Access the second element of the tuple
            user_id = user[0]  # Access the first element of the tuple
            # Generate a token
            token = generate_token(user_id)
            return jsonify({"token": token}), 200
        else:
            return jsonify({"message": "Invalid credentials"}), 401

    except Exception as er:
        return jsonify({"err": str(er)}), 500

# Protected route example
@app.route('/protected', methods=['GET'])
def protected_route():
    # Check if the request has a valid token
    token = request.headers.get('Authorization')
    if token:
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
            # Implement your logic for the protected route here
            return jsonify({"message": "Access granted to protected route for user ID: " + user_id}), 200
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401

    return jsonify({"message": "Token is missing or invalid"}), 401

# Generate a random OTP
def generate_random_otp(length):
    otp = ''.join(random.choice(string.digits) for _ in range(length))
    return otp

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        data = request.json
        email = data.get('email')

        # Check if the email exists in the database
        db_query = "SELECT user_id, firstname FROM user WHERE email = %s"
        cursor.execute(db_query, (email,))
        user = cursor.fetchone()

        if user:
            # Generate a unique OTP
            reset_otp = generate_random_otp(6)

            # Store the OTP in the database and associate it with the user
            db_query = "UPDATE user SET reset_otp = %s WHERE user_id = %s"
            cursor.execute(db_query, (reset_otp, user[0]))
            connection.commit()

            # Send an email with the OTP
            send_reset_otp_email(user[1], email, reset_otp)

            return jsonify({"message": "Password reset OTP sent"}), 200
        else:
            return jsonify({"message": "No user with this email found"}), 404

    except Exception as er:
        return jsonify({"err": str(er)}), 500

# Send an email with the OTP
def send_reset_otp_email(user_name, user_email, reset_otp):
    msg = MIMEText(f"Hello {user_name},\n\nTo reset your password, use the following OTP: {reset_otp}\n\nIf you didn't request this, please ignore this email.")
    msg['Subject'] = 'Password Reset OTP'
    msg['From'] = 'your-email@example.com'
    msg['To'] = user_email

    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USER, SMTP_PASS)
    server.sendmail('your-email@example.com', [user_email], msg.as_string())
    server.quit()

# Route to reset the password with the OTP
@app.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        data = request.json
        email = data.get('email')
        reset_otp = data.get('reset_otp')
        new_password = data.get('new_password')

        # Verify the OTP
        db_query = "SELECT user_id FROM user WHERE reset_otp = %s AND email = %s"
        cursor.execute(db_query, (reset_otp, email))
        user = cursor.fetchone()

        if user:
            # Reset the password
            db_query = "UPDATE user SET password = %s, reset_otp = NULL WHERE email = %s"
            cursor.execute(db_query, (new_password, email))
            connection.commit()

            return jsonify({"message": "Password reset successfully"}), 200
        else:
            return jsonify({"message": "Invalid or expired OTP"}), 401

    except Exception as er:
        return jsonify({"err": str(er)}), 500

def get_user_profile(token):
    try:
        # Verify the token and decode the payload
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']

        # Retrieve the user's profile details from the database
        connection = get_db_connection()
        cursor = connection.cursor()

        # Replace 'your_user_table' with the actual table name where user profiles are stored
        db_query = "SELECT firstname, middlename, lastname, email, phonenumber, gender, relationship, dateofbirth FROM user WHERE user_id = %s"
        cursor.execute(db_query, (user_id,))
        user_profile = cursor.fetchone()

        cursor.close()
        connection.close()

        if user_profile:
            # Format the user profile data as a dictionary
            profile_data = {
                'firstname': user_profile[0],
                'middlename': user_profile[1],
                'lastname': user_profile[2],
                'email': user_profile[3],
                'phonenumber': user_profile[4],
                'gender': user_profile[5],
                'relationship': user_profile[6],
                'dateofbirth': user_profile[7]
            }

            return profile_data
        else:
            return None  # User not found

    except jwt.ExpiredSignatureError:
        return None  # Token has expired
    except jwt.InvalidTokenError:
        return None  # Invalid token
    except Exception as e:
        return None  # Other errors

# API endpoint to get the user's profile by token
@app.route('/profile', methods=['GET'])
def get_profile():
    token = request.headers.get('Authorization'
                                '')

    if token:
        profile_data = get_user_profile(token)
        if profile_data:
            return jsonify(profile_data), 200
        else:
            return jsonify({"message": "Unauthorized"}), 401
    else:
        return jsonify({"message": "Token is missing or invalid"}), 401


#admin

# @app.route('/enrollcls',methods=['POST'])
# def enroll_cls():
#     try:
#         admin_connection=get_db_connection()
#         cursor=admin_connection.cursor()
#         data=request.json


if __name__ == "__main__":
    app.run(debug=True)
