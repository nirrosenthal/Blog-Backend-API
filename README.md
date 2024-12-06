# Blog-Backend-API
Backend Design of a Message Blog, allowing to post, edit and delete messages 

## Table Of Contents
- [Key Features](#key-features)
- [Installation](#installation)
- [Running](#running)
- [Using REST API](#using-rest-api)

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
3. Run Docker Compose container (see [Using REST API](#using-rest-api))
```bash
docker-compose up -d
```
4. See test/server/flask/routes for examples and API usage

5. Stop Container Run:
```bash
docker-compose down
```

## Using REST API
After Running Docker Compose, the directory test/flask/routes have built in functions for every request of the REST API

