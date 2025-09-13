import re

def extract_phone_number(text: str) -> str:
    """Extract and normalize phone number from text"""
    
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', text)
    
    # Check if it looks like a phone number (at least 10 digits)
    if len(re.sub(r'[^\d]', '', cleaned)) < 10:
        return None
        
    # Remove + and any leading zeros for processing
    phone = cleaned.replace('+', '').lstrip('0')
    
    # Handle Indonesian phone numbers
    if phone.startswith('62'):
        # Convert +62 to 0
        phone = '0' + phone[2:]
    elif len(phone) >= 10 and not phone.startswith('0'):
        # If it's a long number without country code, assume it's Indonesian
        # and add 0 prefix
        phone = '0' + phone
    elif not phone.startswith('0') and len(phone) < 15:
        # For shorter numbers, assume local format and add 0
        phone = '0' + phone
        
    return phone if len(phone) >= 10 else None