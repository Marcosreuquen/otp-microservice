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

# Structure of the project

The project is structured in the following way:
```
.
├── app
│   ├── lib # all the third-party libraries
│   ├── routes # endpoints
│   ├── schemas # custom types and schemas
│   ├── controllers # the logic of the endpoints
│   ├── models # the database models
│   ├── utils # utils functions
│   ├── main.py # the file that runs the project
├── config # loads the environment variables into the project
├── requirements.txt # a list of the dependencies of the project
└── .env # the environment variables

```

# Installation

Clone this repository: 

```bash
git clone https://github.com/marcosreuquen/otp-microservice.git
cd otp-microservice
```

Install the dependencies: 
```bash 
pip install -r requirements.txt
```

Create a virtual environment:
```bash 
python3 -m venv .venv
```

Activate the virtual environment: 
```bash
source .venv/bin/activate # for linux and mac
source .venv/Scripts/activate # for windows
```

Prepare the environment variables:

```bash
cp .env.example .env
```

Update the environment variables in the `.env` file with the values in the `.env.example` file.

You will need a database to run the server, or it will fail. If you don't have a database, you can use a local Postgres instance or run a Docker container.
```bash 
docker run -p 5432:5432 -e POSTGRES_PASSWORD=your_password postgres
```

Run the server: 
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
``` 

or 

```bash
fastapi run app/main.py
```

Then you can use **Swagger UI** at http://localhost:8000/docs to access the API documentation.


## Usage with Docker

To run the application and the database using Docker, run the following command:

```bash 
docker-compose up --build
```

This will start both the application and the database, and the network to connect them. 
The API will be available at http://localhost:8000/docs.


# Contribution

If you want to contribute to this project, please create a fork and send a pull request.

# Me

- You can find me here: [marcosreuquen](https://marcosdiaz.dev)