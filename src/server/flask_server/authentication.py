from enum import Enum

class Role(Enum):
    BASIC_USER = "user"
    POSTER_USER = "post_user"
    ADMIN = "admin"

class Permissions(Enum):
    VIEW_MESSAGE = 1
    CREATE_MESSAGE = 2
    EDIT_MESSAGE = 4
    DELETE_MESSAGE = 8
    MANAGE_USERS = 16
    BAN_USER = 32



