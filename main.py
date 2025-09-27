from typing import Dict, Any
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from schema import UserBioData, UserCreationResponse


app = FastAPI(
    title="User Bio Data API",
)

class ErrorResponse:
    """Standard error response format"""
    
    @staticmethod
    def create_error_response(
        message: str,
        error_code: str = None,
        details: Dict[str, Any] = None,
        status_code: int = 500
    ) -> Dict[str, Any]:
        """Create standardized error response"""
        response = {
            "success": False,
            "message": message,
            "status_code": status_code,
        }
        
        if error_code:
            response["error_code"] = error_code
            
        if details:
            response["details"] = details
            
        return response

@app.exception_handler(ValidationError)
async def handle_pydantic_validation_error(request: Request, exc: ValidationError) -> JSONResponse:
        """Handle Pydantic validation errors"""

        formatted_errors = []
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            formatted_errors.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"]
            })
        
        error_response = ErrorResponse.create_error_response(
            message="Data validation failed",
            error_code="DATA_VALIDATION_ERROR",
            details={"validation_errors": formatted_errors},
            status_code=status.HTTP_400_BAD_REQUEST
        )
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response
        )

@app.post(
    "/users",
    response_model=UserCreationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a user story",
)
async def create_user(user_data: UserBioData):
    """
    Create a user story with the user's biographical data.
    
    Returns the created user story.
    """
    try:
        user_story  = f"User {user_data.first_name} {user_data.last_name} created successfully."
        
        # Return success response
        return UserCreationResponse(
            message="User created successfully",
            user_story=user_story
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


