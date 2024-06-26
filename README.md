
# Social Networking API

## Overview

The Social Networking API enables users to connect and interact through various functionalities including user authentication, friend management.

## Installation

### Prerequisites
- Docker installed and Docker service running.

To run the Social Networking API locally, follow these steps:

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/Deepak3168/social_networking.git
   cd social_networking
   ```

2. **Start the Application:**

   Run the following command to start the application using Docker Compose:

   ```bash
   docker-compose up
   ```

   The API will be accessible at `http://127.0.0.1:8000`.

## Testing

To run tests for the Social Networking API:

1. **Open a New Command Line Interface** in the project directory.

2. **Run Authentication and User Search Tests:**

   ```bash
   docker-compose exec web python manage.py test users
   ```

   This command tests functionalities related to user authentication and search.

3. **Run Friend Model Tests:**

   Execute the following commands to test the Friend model functionalities:

   ```bash
   docker-compose exec web python manage.py test tests.friends.FriendRequestTests
   docker-compose exec web python manage.py test tests.friends.FriendRequestsTests
   docker-compose exec web python manage.py test tests.friends.FriendRequestRateLimitTests
   ```

## Postman Collection

For quick access and testing of API endpoints, you can import the Postman collection using the following link:

https://drive.google.com/file/d/1oeOAbG5zJX81GQUglCXDNyC0r-BIn_rM/view?usp=sharing




