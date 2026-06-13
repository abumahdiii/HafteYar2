import re

def normalize_phone(phone: str) -> str:
    """
    Normalizes Iranian phone numbers to 09xxxxxxxxx (11 digits).
    Raises ValueError if the format is invalid.
    """
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Handle country codes
    if digits.startswith("0098") and len(digits) == 14:
        digits = "0" + digits[4:]
    elif digits.startswith("98") and len(digits) == 12:
        digits = "0" + digits[2:]
    elif digits.startswith("9") and len(digits) == 10:
        digits = "0" + digits
        
    if not re.match(r'^09\d{9}$', digits):
        raise ValueError(f"Invalid Iranian phone number format: {phone}")
        
    return digits
