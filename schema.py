from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator
from typing import Optional, Union, List, Dict, Any
from datetime import datetime, date
from enum import Enum
import re


class GenderEnum(str, Enum):
    """Enumeration for gender options"""
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"
    OTHER = "other"


class MaritalStatusEnum(str, Enum):
    """Enumeration for marital status"""
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"
    SEPARATED = "separated"
    DOMESTIC_PARTNERSHIP = "domestic_partnership"


class Address(BaseModel):
    """Nested model for address information"""
    street: str = Field(..., min_length=1, max_length=200, description="Street address")
    city: str = Field(..., min_length=1, max_length=100, description="City name")
    state: Optional[str] = Field(None, min_length=2, max_length=50, description="State or province")
    postal_code: str = Field(..., pattern=r'^\d{5}(-\d{4})?$|^[A-Z]\d[A-Z] \d[A-Z]\d$', 
                           description="ZIP code (US) or postal code (Canada)")
    country: str = Field(default="US", min_length=2, max_length=3, description="Country code")
    is_primary: bool = Field(default=True, description="Whether this is the primary address")

    class Config:
        schema_extra = {
            "example": {
                "street": "123 Main Street",
                "city": "New York",
                "state": "NY",
                "postal_code": "10001",
                "country": "US",
                "is_primary": True
            }
        }


class PhoneNumber(BaseModel):
    """Nested model for phone number information"""
    number: str = Field(..., pattern=r'^\+?1?-?\.?\s?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$',
                       description="Phone number in various formats")
    type: str = Field(..., pattern=r'^(mobile|home|work|other)$', description="Type of phone number")
    is_primary: bool = Field(default=False, description="Whether this is the primary phone")
    
    @field_validator('number')
    @classmethod
    def clean_phone_number(cls, v):
        """Clean and standardize phone number format"""
        cleaned = re.sub(r'[^\d+]', '', v)
        return cleaned

    class Config:
        schema_extra = {
            "example": {
                "number": "+1-555-123-4567",
                "type": "mobile",
                "is_primary": True
            }
        }


class EmergencyContact(BaseModel):
    """Nested model for emergency contact information"""
    name: str = Field(..., min_length=1, max_length=100, description="Full name of emergency contact")
    relationship: str = Field(..., min_length=1, max_length=50, description="Relationship to user")
    phone: PhoneNumber = Field(..., description="Emergency contact phone number")
    email: Optional[EmailStr] = Field(None, description="Emergency contact email")


class EducationLevel(str, Enum):
    """Enumeration for education levels"""
    HIGH_SCHOOL = "high_school"
    ASSOCIATE = "associate"
    BACHELOR = "bachelor"
    MASTER = "master"
    DOCTORATE = "doctorate"
    PROFESSIONAL = "professional"
    OTHER = "other"


class UserBioData(BaseModel):
    """
    Comprehensive user bio data model demonstrating various Pydantic features:
    - Different data types (str, int, float, bool, datetime, date, Enum)
    - Optional and Union types
    - Nested Pydantic models
    - Field validation and constraints
    - Custom validators
    - Lists and dictionaries
    """
    
    # Basic Personal Information
    first_name: str = Field(..., min_length=1, max_length=50, description="User's first name")
    last_name: str = Field(..., min_length=1, max_length=50, description="User's last name")
    middle_name: Optional[str] = Field(None, max_length=50, description="User's middle name")
    preferred_name: Optional[str] = Field(None, max_length=50, description="Preferred name or nickname")
    
    # Contact Information
    email: EmailStr = Field(..., description="Primary email address")
    secondary_emails: Optional[List[EmailStr]] = Field(default_factory=list, 
                                                     description="Additional email addresses")
    phone_numbers: List[PhoneNumber] = Field(default_factory=list, 
                                           description="List of phone numbers")
    
    # Demographics
    date_of_birth: date = Field(..., description="Date of birth")
    age: Optional[int] = Field(None, ge=0, le=150, description="Age in years (auto-calculated if not provided)")
    gender: Optional[GenderEnum] = Field(None, description="Gender identity")
    marital_status: Optional[MaritalStatusEnum] = Field(None, description="Current marital status")
    
    # Address Information
    addresses: List[Address] = Field(default_factory=list, description="List of addresses")
    
    # Physical Characteristics
    height_cm: Optional[float] = Field(None, ge=50.0, le=300.0, description="Height in centimeters")
    weight_kg: Optional[float] = Field(None, ge=20.0, le=500.0, description="Weight in kilograms")
    eye_color: Optional[str] = Field(None, max_length=20, description="Eye color")
    hair_color: Optional[str] = Field(None, max_length=20, description="Hair color")
    
    # Professional Information
    occupation: Optional[str] = Field(None, max_length=100, description="Current occupation")
    employer: Optional[str] = Field(None, max_length=100, description="Current employer")
    annual_income: Optional[Union[int, float]] = Field(None, ge=0, description="Annual income")
    education_level: Optional[EducationLevel] = Field(None, description="Highest education level")
    
    # Social and Personal
    languages_spoken: List[str] = Field(default_factory=list, description="Languages spoken")
    hobbies: List[str] = Field(default_factory=list, description="Hobbies and interests")
    social_media_handles: Optional[Dict[str, str]] = Field(default_factory=dict,
                                                          description="Social media platform to handle mapping")
    
    # Emergency Contact
    emergency_contacts: List[EmergencyContact] = Field(default_factory=list,
                                                     description="Emergency contact information")
    
    # Validation Methods
    @field_validator('age', mode='before')
    @classmethod
    def calculate_age(cls, v, info):
        """Calculate age from date of birth if age is not provided"""
        if v is not None:
            return v
        # Get other field values from info.data
        dob = info.data.get('date_of_birth')
        if dob:
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            return age
        return None

    @field_validator('date_of_birth')
    @classmethod
    def validate_birth_date(cls, v):
        """Ensure birth date is not in the future"""
        if v > date.today():
            raise ValueError('Date of birth cannot be in the future')
        return v
    
    @field_validator('languages_spoken')
    @classmethod
    def validate_languages(cls, v):
        """Ensure languages are valid strings and remove duplicates"""
        if not v:
            return v
        # Remove empty strings and duplicates
        languages = [lang.strip().title() for lang in v if lang.strip()]
        return list(set(languages))

    @model_validator(mode='after')
    def validate_phone_and_address_primary(self):
        """Ensure at least one phone number and address is marked as primary if they exist"""
        # Validate phone numbers
        if self.phone_numbers:
            primary_phones = [phone for phone in self.phone_numbers if phone.is_primary]
            if not primary_phones:
                # Mark the first phone as primary
                self.phone_numbers[0].is_primary = True
        
        # Validate addresses
        if self.addresses:
            primary_addresses = [addr for addr in self.addresses if addr.is_primary]
            if not primary_addresses:
                # Mark the first address as primary
                self.addresses[0].is_primary = True
        
        return self
    
    class Config:
        # Enable validation on assignment
        validate_assignment = True
        # Use enum values instead of enum objects in JSON
        use_enum_values = True
        # JSON schema customization
        schema_extra = {
            "example": {
                "first_name": "Sarah",
                "last_name": "Johnson",
                "middle_name": "Elizabeth",
                "preferred_name": "Sara",
                "email": "sarah.johnson@example.com",
                "secondary_emails": [
                    "sara.personal@gmail.com",
                    "s.johnson@work.com"
                ],
                "phone_numbers": [
                    {
                    "number": "+1-555-123-4567",
                    "type": "mobile",
                    "is_primary": True
                    },
                    {
                    "number": "555-987-6543",
                    "type": "home",
                    "is_primary": False
                    }
                ],
                "date_of_birth": "1988-07-22",
                "gender": "female",
                "marital_status": "married",
                "addresses": [
                    {
                    "street": "456 Oak Avenue",
                    "city": "San Francisco",
                    "state": "CA",
                    "postal_code": "94102",
                    "country": "US",
                    "is_primary": True
                    },
                    {
                    "street": "789 Pine Street, Apt 3B",
                    "city": "Berkeley",
                    "state": "CA",
                    "postal_code": "94704",
                    "country": "US",
                    "is_primary": False
                    }
                ],
                "height_cm": 168.5,
                "weight_kg": 65.2,
                "eye_color": "Brown",
                "hair_color": "Black",
                "occupation": "Data Scientist",
                "employer": "TechCorp Inc.",
                "annual_income": 125000,
                "education_level": "master",
                "languages_spoken": [
                    "English",
                    "Spanish",
                    "French"
                ],
                "hobbies": [
                    "Rock climbing",
                    "Photography",
                    "Cooking",
                    "Reading sci-fi novels"
                ],
                "social_media_handles": {
                    "twitter": "@sarahj_data",
                    "linkedin": "sarah-johnson-datascientist",
                    "instagram": "@sara_adventures",
                    "github": "sarahj-code"
                },
                "emergency_contacts": [
                    {
                    "name": "Michael Johnson",
                    "relationship": "Spouse",
                    "phone": {
                        "number": "+1-555-876-5432",
                        "type": "mobile",
                        "is_primary": True
                    },
                    "email": "michael.johnson@example.com"
                    },
                    {
                    "name": "Robert Johnson",
                    "relationship": "Father",
                    "phone": {
                        "number": "555-234-5678",
                        "type": "home",
                        "is_primary": True
                    },
                    "email": "robert.johnson@email.com"
                    }
                ]
            }
        }


class UserCreationResponse(BaseModel):
    """Response model for user creation"""
    message: str
    user_story: str

# Usage example and testing
if __name__ == "__main__":
    # Example of creating a user bio with various data types
    user_data = {
        "first_name": "Sarah",
        "last_name": "Johnson",
        "middle_name": "Elizabeth",
        "preferred_name": "Sara",
        "email": "sarah.johnson@example.com",
        "secondary_emails": [
            "sara.personal@gmail.com",
            "s.johnson@work.com"
        ],
        "phone_numbers": [
            {
            "number": "+1-555-123-4567",
            "type": "mobile",
            "is_primary": "true"
            },
            {
            "number": "555-987-6543",
            "type": "home",
            "is_primary": "false"
            }
        ],
        "date_of_birth": "1988-07-22",
        "gender": "female",
        "marital_status": "married",
        "addresses": [
            {
            "street": "456 Oak Avenue",
            "city": "San Francisco",
            "state": "CA",
            "postal_code": "94102",
            "country": "US",
            "is_primary": "true"
            },
            {
            "street": "789 Pine Street, Apt 3B",
            "city": "Berkeley",
            "state": "CA",
            "postal_code": "94704",
            "country": "US",
            "is_primary": "false"
            }
        ],
        "height_cm": 168.5,
        "weight_kg": 65.2,
        "eye_color": "Brown",
        "hair_color": "Black",
        "occupation": "Data Scientist",
        "employer": "TechCorp Inc.",
        "annual_income": 125000,
        "education_level": "master",
        "languages_spoken": [
            "English",
            "Spanish",
            "French"
        ],
        "hobbies": [
            "Rock climbing",
            "Photography",
            "Cooking",
            "Reading sci-fi novels"
        ],
        "social_media_handles": {
            "twitter": "@sarahj_data",
            "linkedin": "sarah-johnson-datascientist",
            "instagram": "@sara_adventures",
            "github": "sarahj-code"
        },
        "emergency_contacts": [
            {
            "name": "Michael Johnson",
            "relationship": "Spouse",
            "phone": {
                "number": "+1-555-876-5432",
                "type": "mobile",
                "is_primary": "true"
            },
            "email": "michael.johnson@example.com"
            },
            {
            "name": "Robert Johnson",
            "relationship": "Father",
            "phone": {
                "number": "555-234-5678",
                "type": "home",
                "is_primary": "true"
            },
            "email": "robert.johnson@email.com"
            }
        ]
    }
    
    try:
        user = UserBioData(**user_data)
        print("User created successfully!")
        print(f"User: {user.first_name} {user.last_name}")
        print(f"Age: {user.age}")  # Should be auto-calculated
        print(f"Languages: {user.languages_spoken}")  # Should be deduplicated and capitalized
        print(f"JSON representation:\n{user.model_dump_json(indent=2)}")
    except Exception as e:
        print(f"Validation error: {e}")



