# FastAPI User and Post Management Application

This is a FastAPI-based web application for user authentication and managing posts. The application allows users to sign up, log in, create, retrieve, and delete posts. It uses JWT tokens for authentication and integrates with a MySQL database via SQLAlchemy ORM.

## Features
- **Signup**: Users can sign up with an email and password, and receive a JWT token for authentication.
- **Login**: Users can log in with email and password and get a JWT token.
- **Create Post**: Authenticated users can create posts (with text up to 1 MB in size).
- **Get Posts**: Authenticated users can retrieve their posts, with in-memory caching for up to 5 minutes.
- **Delete Post**: Users can delete their posts.

## Requirements
- Python 3.8+
- FastAPI
- SQLAlchemy
- MySQL (or any compatible database)
- JWT for authentication
- `cachetools` for in-memory caching
- `bcrypt` for password hashing
- `python-dotenv` for environment variable management

## Setup Instructions

### Step 1: Clone the Repository and Setup the Project

1. **Clone the Repository**:
   - First, clone the repository to your local machine:
     ```bash
     git clone https://github.com/yourusername/your-repo-name.git
     cd your-repo-name
     ```

2. **Create a Virtual Environment** (optional but recommended):
   - You can create a virtual environment to keep your dependencies isolated.
     ```bash
     python -m venv venv
     ```

3. **Activate the Virtual Environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install Dependencies**:
   - Install the required dependencies by running:
     ```bash
     pip install -r requirements.txt
     ```

5. **Set Up Environment Variables**:
   - Create a `.env` file in the root of the project and define the following variables:
     ```env
     DATABASE_URL=mysql+pymysql://username:password@localhost/dbname
     SECRET_KEY=your_secret_key
     ALGORITHM=HS256
     ```
     - `DATABASE_URL`: The connection URL to your MySQL database. Replace `username`, `password`, and `dbname` with your MySQL credentials.
     - `SECRET_KEY`: A secret key for encoding and decoding JWT tokens.
     - `ALGORITHM`: The algorithm to use for encoding JWT tokens (e.g., `HS256`).

6. **Set Up the Database**:
   - Ensure that you have MySQL running and create the database specified in your `.env` file.


### Step 2: Run the Application

Once the setup is complete, you can run the FastAPI application using Uvicorn:

-
uvicorn app.main:app --reload
