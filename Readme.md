
# Note-Taking Application API

## Project Overview

This note-taking application API provides a secure and efficient way for users to create, manage, and share notes. Built with Django and Django Rest Framework (DRF), it features user authentication, CRUD operations for notes, note sharing among users, and version history tracking to ensure robust note management.

## Technical Specifications

### Endpoints Implemented

-   **User Registration** (`POST /signup`)
    -   Allows new users to create an account by providing a username, email, and password.
-   **User Login** (`POST /login`)
    -   Authenticates users and returns a token for subsequent API requests.
-   **Create Note** (`POST /notes/create`)
    -   Enables authenticated users to create new notes.
-   **Retrieve Note** (`GET /notes/{id}`)
    -   Allows users to retrieve details of a specific note, accessible only to the note's owner and shared users.
-   **Update Note** (`PUT /notes/{id}`)
    -   Permits updates to a note's content, with access restricted to the note's owner and shared users.
-   **Delete Note** (`DELETE /notes/{id}`)
    -   Allows for the deletion of a specific note, restricted to the note's owner.
-   **Share Note** (`POST /notes/share`)
    -   Enables a note's owner to share it with other specified users by their usernames.
-   **Note Version History** (`GET /notes/version-history/{id}`)
    -   Retrieves the version history of a note, showing all changes made since its creation.

### Test Cases

Comprehensive test cases were developed to ensure the reliability and security of the API, covering:

-   Successful and unauthorized access scenarios for CRUD operations on notes.
-   User registration with valid and invalid data (e.g., invalid email format, short password).
-   User login with correct and incorrect credentials.
-   Sharing notes with valid users and handling attempts to share with nonexistent users.
-   Retrieving the version history of a note.

### Security and Best Practices

-   User passwords are securely hashed using Django's built-in mechanisms.
-   Token-based authentication secures API endpoints against unauthorized access.
-   Cross-Origin Resource Sharing (CORS) is configured to allow requests from trusted domains, enhancing security for web clients hosted on different domains.

## Setup Instructions

### Prerequisites

-   Python (3.8 or newer)
-   pip
-   Virtual environment (recommended)

### Installation Steps

 1. **Clone the Repository**

    `git clone https://github.com/your-username/your-repo-name.git` 
	`cd your-repo-name`

 2. **Create and Activate Virtual Environment**
 
	 - For Linux/macOS:
    		`git clone https://github.com/your-username/your-repo-name.git`
		    `cd your-repo-name`


	 - For Windows:
    		`python -m venv venv`
		    ``.\venv\Scripts\activate``

 3. **Install Dependencies**

		`pip install -r requirements.txt`

 4. **Apply Migrations**
		`python manage.py makemigrations`
		`python manage.py migrate`

 5. **Create Superuser(Optional)**
		 `python manage.py createsuperuser`
		 

 6. **Run the dev server**
		 `python manage.py runserver`

 7. **Running Tests**
		 Execute the following command to run the automated test suite:
		`python manage.py test`

 7. **Accessing API Documentation**

	Navigate to `http://127.0.0.1:8000/swagger/` for Swagger UI or `http://127.0.0.1:8000/redoc/` for ReDoc, providing interactive API documentation




		 
