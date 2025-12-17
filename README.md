ER Drawing
erDiagram
    USER ||--o{ ORDER : places
    RESTAURANT ||--o{ ORDER : receives
    RESTAURANT ||--o{ RESTAURANT_MENU_ITEM : sells
    GLOBAL_DISH ||--o{ RESTAURANT_MENU_ITEM : listed_as
    ORDER ||--o{ ORDER_ITEM : contains
    RESTAURANT_MENU_ITEM ||--o{ ORDER_ITEM : ordered_as

    USER {
        int id PK
        string name
        string email
        string phone_number
        datetime created_at
    }

    RESTAURANT {
        int id PK
        string name
        string address
        string city
        float rating
        bool is_open
    }

    GLOBAL_DISH {
        int id PK
        string name
        string description
        string category
        bool is_veg
    }

    RESTAURANT_MENU_ITEM {
        int id PK
        int restaurant_id FK
        int global_dish_id FK
        decimal price
        bool is_available
    }

    ORDER {
        int id PK
        int user_id FK
        int restaurant_id FK
        decimal total_amount
        string status
        string delivery_address
        datetime created_at
    }

    ORDER_ITEM {
        int id PK
        int order_id FK
        int menu_item_id FK
        int quantity
        decimal price_at_order
    }


How to Think Like a Backend Engineer
    Before writing an endpoint, ask:
        - Who can call this?
        - What role do they need?
        - Do they own the resource?
        - What happens if they don’t?


Authorization matrix

🔐 Authorization Matrix
Feature / API	        USER			RESTAURANT_ADMIN	       ADMIN			Extra Rules (ABAC)
View restaurants	    ✅			    ✅		                ✅			        —
View menu	            ✅			    ✅		                ✅			        —
Place order	            ✅			    ❌		                ❌			        —
View own orders	        ✅			    ❌		                ❌			        Must own order
Cancel order	        ✅			    ❌		                ❌			        Own order + status=PLACED
Add menu item	        ❌			    ✅		                ❌			        Own restaurant
Update menu price	    ❌			    ✅		                ❌			        Own restaurant
View restaurant orders	❌			    ✅		                ❌			        Own restaurant
Create global dish	    ❌			    ❌		                ✅			        Admin only
Create restaurant	    ❌			    ❌		                ✅			        Admin only
Block user	            ❌			    ❌		                ✅			        Admin only


Please check the logic of service layer/logic
    - when we need to do the same this for two different api endpoint then we should create a service layer/logic
    - Why this is the best way for you:
        - Single Entry Point: Whether I am a logged-in customer or a restaurant owner, I go to GET /restaurants. It is simple and intuitive.
        - Role Flexibility: If tomorrow you add a "Guest" role who can also see restaurants, you just add UserRole.GUEST to the require_roles list in one place.
        - Testing: You can test the "Chef" (the service logic) without even starting the FastAPI server. This makes your code much more robust.

    Since you want both a regular User and a Restaurant Admin to access the exact same data, the best approach is to define a single "Source of Truth" endpoint.

    In a professional API, you don't create two different URLs for the same data just because the person asking has a different title. Instead, you create one URL and authorize multiple roles to use it.

    1. The Unified Router (routers/restaurants.py)
    This is the most critical part. You define the endpoint under the /restaurants prefix and tell your require_roles dependency that both roles are welcome.

    Python

    from fastapi import APIRouter, Depends
    from sqlalchemy.orm import Session
    from app.dependencies import get_db, require_roles
    from app.models.user import UserRole
    from app.services import restaurant_service

    router = APIRouter(prefix="/restaurants", tags=["Restaurants"])

    @router.get("/")
    def read_all_restaurants(
        db: Session = Depends(get_db),
        # Allow both roles here
        current_user = Depends(require_roles(UserRole.USER, UserRole.RESTAURANT_ADMIN))
    ):
        # Call the shared service logic
        return restaurant_service.get_restaurants(db)
    2. The Shared Service Logic (services/restaurant_service.py)
    This function doesn't care who is calling it. It just knows how to talk to the database.
    
    Python
    
    from sqlalchemy.orm import Session
    from app.models.restaurant import Restaurant
    
    def get_restaurants(db: Session):
        return db.query(Restaurant).all()
    3. How main.py ties it together
    You simply register the router once. Because the router handles the permissions, FastAPI takes care of the rest.
    
    Python
    
    from fastapi import FastAPI
    from app.routers import restaurants, users, auth
    
    app = FastAPI()
    
    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(restaurants.router) # This handles BOTH Users and Admins
    Why this is better than having /users/restaurants:
    Frontend Simplicity: The developer building the website or mobile app only needs to remember one URL: GET /restaurants. They don't have to write logic like "If I'm a user call this, if I'm an admin call that."
    
    Clean Documentation: Your Swagger/OpenAPI docs stay clean and professional.
    
    Efficiency: You are following the DRY (Don't Repeat Yourself) principle. If you ever need to add a feature (like filtering restaurants by "Open" or "Closed"), you only change it in one file.