from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth import DUMMY_HASH
import schemas
from typing import List
from schemas import Role
import services
from auth import (
    verify_password,
    create_access_token,
    hash_password,
    verify_token,
    DUMMY_HASH
)

app = FastAPI(title="Library Management System")
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    user = services.get_user_by_id(int(user_id))
    if user is None:
        raise credentials_exception
    return user

class RoleChecker:
    def __init__(self, allowed_roles: List[Role]):
        self.allowed_roles = [r.value for r in allowed_roles]

    def __call__(
        self,
        current_user = Depends(get_current_user)
    ):
        if current_user["role"] not in self.allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="Forbidden"
            )
        return current_user


admin_only = RoleChecker([Role.admin])
student_only = RoleChecker([Role.student])

admin_or_student = RoleChecker([
    Role.admin,
    Role.student
])

@app.post("/register")
def register_user(
    user: schemas.UserCreate,
):
    existing_user = services.get_user_by_email(user.email)

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    hashed_pwd = hash_password(user.password)
    user_id = services.create_user(
    user.name,
    user.email,
    hashed_pwd,
    user.role.value
)
    return {
    "message": "User registered successfully",
    "user_id": user_id
}


@app.post("/login", response_model=schemas.TokenResponse)
def login_user(
    user: schemas.UserLogin,
):
    db_user = services.get_user_by_email(user.email)
    if not db_user:
        verify_password(user.password, DUMMY_HASH)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Email, Password or Role"
        )
    if not verify_password(
        user.password,
        db_user["password"]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Email, Password or Role"
        )

    if db_user["role"] != user.role.value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Role"
        )

    access_token = create_access_token(
        data={
            "sub": str(db_user["id"]),
            "role": db_user["role"]
        }
    )
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/me")
def get_profile(
    current_user = Depends(get_current_user)
):
    return current_user


@app.post("/books")
def add_book(
    book: schemas.BookCreate,
    current_user = Depends(admin_only)
):
    book_id = services.add_book(
        book.title,
        book.author,
        book.quantity
    )
    return {
        "message": "Book added successfully",
        "book_id": book_id
    }

@app.get("/books")
def get_books(
    current_user = Depends(get_current_user)
):
    books = services.get_all_books()
    return books

@app.delete("/book/{book_id}")
def delete_book(
    book_id: int,
    current_user = Depends(admin_only)
):
    book = services.get_book_by_id(book_id)
    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    services.delete_book(book_id)

    return {
        "message": "Book Deleted Successfully"
    }

@app.post("/issue_book")
def issue_book(
    data: schemas.IssueBook,
    current_user = Depends(get_current_user)
):
    user = services.get_user_by_id(data.user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    book = services.get_book_by_id(data.book_id)
    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    if book["quantity"] <= 0:
        raise HTTPException(
            status_code=400,
            detail="Book out of stock"
        )

    issue_id = services.issue_book(
        data.user_id,
        data.book_id
    )
    return {
        "message": "Book Issued Successfully",
        "issue_id": issue_id
    }

@app.post("/return-book")
def return_book(
    data: schemas.ReturnBook,
    current_user = Depends(get_current_user)
):
    services.return_book(
        data.user_id,
        data.book_id
    )
    return {
        "message": "Book Returned Successfully"
    }

@app.get("/issued-books")
def get_books(
    current_user = Depends(get_current_user)
):
    issued_books = services.get_issued_books()
    return issued_books
