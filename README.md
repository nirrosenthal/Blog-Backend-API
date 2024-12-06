# Blog-Backend-API
Backend Design of a Message Blog, allowing to post, edit and delete messages 

## Table Of Contents
- [Key Features](#key-features)
- [Requirements](#requirements)
- [Running](#running)
- [REST API Endpoints](#rest-api-endpoints)

## Key Features
- Written in Python
- Basic Authentication with JWT
- Rest API
- Input Validation
- MongoDB
- Repository pattern
- Error Handling 
- Docker Compose

## Requirements
1. Docker
2. Docker Compose
3. Python

## Running:
1. Go to root diectory of the project

2. Build MongoDB and Flask Images:
```bash
docker-compose build
```
3. Run Docker Compose container (see test/ directory for request examples)
```bash
docker-compose up -d
```
4. Stop Container Run:
```bash
docker-compose down
```
## REST API Endpoints

### Authentication API Endpoints

| **Endpoint**                             | **Method**  | **Description**                                                                                             | **Request Parameters**                                                                                               |
|------------------------------------------|-------------|-------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------|
| `/api/v0/auth/login`                     | `POST`      | Verifies user credentials (user_id and password) and returns a generated JWT token.                          | - `user_id` (string): The user's unique identifier. <br> - `password` (string): The user's password.               |
| `/api/v0/auth/register`                  | `POST`      | Creates a new user with the provided `user_id`, `password`, and `roles`.                                      | - `user_id` (string): The unique identifier for the user. <br> - `password` (string): The password. <br> - `roles` (array): A list of roles (e.g., `["post_user"]`). |
| `/api/v0/auth/account/delete`            | `DELETE`    | Deletes a user account.                                                                        | - user_id (string): The user's unique identifier.                                                                                                                |

---

### Messages API Endpoints

| **Endpoint**                             | **Method**  | **Description**                                                                                             | **Request Parameters**                                                                                               |
|------------------------------------------|-------------|-------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------|
| `/api/v0/messages/posts`                | `GET`       | Retrieves a list of posts from the blog database.                                                            | - `start_index` (integer, optional): The index to start retrieving posts from (default is `0`). <br> - `limit` (integer, optional): The number of posts to return (default is `input_validation.POSTS_GET_LIMIT`).                                                                                                                |
| `/api/v0/messages/create`               | `POST`      | Creates a new message in the blog database. This could be a Post or Comment, depending on `reply_to_message_id`. Only 'post_user' role can create a Post | - `content` (string): The content of the message. <br> - `reply_to_message_id` (optional, string): The message ID being replied to. |
| `/api/v0/messages/edit`                 | `POST`      | Edits a message that the requesting user owns.                                                                | - `message_id` (string): The ID of the message to edit. <br> - `content` (string): The updated message content.     |
| `/api/v0/messages/delete`               | `DELETE`    | Deletes a message that the requesting user owns.                                                              | - `message_id` (string): The ID of the message to delete.                                                            |
| `/api/v0/messages/like/add`             | `PUT`       | Adds a like to a message from the user. No error if the user already likes the message.                      | - `message_id` (string): The ID of the message to like.                                                              |
| `/api/v0/messages/like/remove`          | `PUT`       | Removes a like from a message from the user. No error if the user doesn't like the message.                   | - `message_id` (string): The ID of the message to remove the like from.                                               |
| `/api/v0/messages/get`                  | `GET`       | Searches for a message by `message_id` and returns the corresponding Message object if found.                | - `message_id` (string): The ID of the message to search for.                                                         |
