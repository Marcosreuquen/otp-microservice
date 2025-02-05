# One time password with FastAPI

This project is a microservice authentication using FastAPI, designed to provide an additional security layer to your applications.

# Features

- MFA (multiple factor authentication) supports as Whatsapp, SMS and email
- Application registration, modification and deletion
- User registration, login and logout
- Code generation and verification
- Status of OTP

# Endpoints

These are the available groups of endpoints, you will need to run the project and go to `/docs` to get the detailed endpoints under the groups:
### /api/code: 
Generation and verification of TOTP codes
### /api/otp:
Registration and verification of OTP
### /api/auth:
Users authentication
### /api/app:
registration, modification and deletion of applications

# Tech Stack

- FastAPI (Backend Framework)
- Pydantic (Schema)
- SQLModel (Postgres ORM)
- Passlib (Password hashing)
- pyotp (OTP generator)
- segno (QR code generator)
- Resend (Email sender)
- Twilio (SMS/whatsapp sender)
- SwaggerUI (API Documentation)

# Installation

Clone this repository: `git clone https://github.com/marcosreuquen/otp-microservice.git`

Install the dependencies: `pip install -r requirements.txt`

Create a virtual environment:
`python3 -m venv .venv`

Activate the virtual environment: `source .venv/bin/activate`

Update the environment variables in the `.env` file with the values in the `.env.example` file.

You will need a database to run the server, or it will fail. If you don't have a database, you can use a local Postgres instance or run a Docker container.
`docker run -p 5432:5432 -e POSTGRES_PASSWORD=your_password postgres`

Run the server: `uvicorn main:app --host 0.0.0.0 --port 8000` or `fastapi run app/main.py`

Then you can use Swagger UI at http://localhost:8000/docs to access the API documentation.


## Usage with Docker

To run the application and the database using Docker, follow these steps:

1. Build the Docker images:
`docker-compose build`

2. Start the containers:
`docker-compose up`

This will start both the application and the database. The API will be available at http://localhost:8000/docs.


# Contribution

If you want to contribute to this project, please create a fork and send a pull request.
