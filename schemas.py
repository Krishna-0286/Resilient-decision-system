from pydantic import BaseModel, Field

# This is our blueprint for an incoming request (e.g., a Loan or Job Application)
class ApplicationRequest(BaseModel):
    applicant_name: str = Field(..., min_length=2, description="Full name of the applicant")
    age: int = Field(..., ge=18, description="Applicant must be at least 18 years old")
    income: float = Field(..., ge=0, description="Annual income in INR")
    documents_provided: bool = Field(..., description="Did they upload mandatory ID?")