from enum import Enum

class UserRole(str,Enum):
    ATHELETE = "ATHELETE"
    TECHNICAL_STAFF = "TECHNICAL_STAFF"
    MEDICAL_STAFF = "MEDICAL_STAFF"
    ORGANIZER = "ORGANIZER"

