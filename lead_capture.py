"""
Lead capture tool for collecting user information.
"""
from typing import Dict


def mock_lead_capture(name: str, email: str, platform: str) -> Dict[str, str]:
    """
    Mock API function for lead capture.
    
    Args:
        name: User's name
        email: User's email
        platform: Creator platform (YouTube, Instagram, etc.)
        
    Returns:
        Dictionary with capture status
    """
    print(f"Lead captured successfully: {name}, {email}, {platform}")
    return {
        "status": "success",
        "message": f"Lead captured successfully: {name}, {email}, {platform}",
        "name": name,
        "email": email,
        "platform": platform
    }


def validate_email(email: str) -> bool:
    """
    Basic email validation.
    
    Args:
        email: Email string to validate
        
    Returns:
        True if email format is valid
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def extract_info_from_message(message: str) -> Dict[str, str]:
    """
    Extract name, email, and platform from user message.
    
    Args:
        message: User message
        
    Returns:
        Dictionary with extracted info (name, email, platform)
    """
    import re
    
    extracted = {}
    
    # Extract email (most reliable)
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, message)
    if email_match:
        extracted['email'] = email_match.group()
    
    # Extract platform (common platforms) - check for variations
    platforms = {
        'youtube': 'YouTube',
        'instagram': 'Instagram',
        'tiktok': 'TikTok',
        'facebook': 'Facebook',
        'twitter': 'Twitter',
        'x': 'Twitter',  # X (formerly Twitter)
        'linkedin': 'LinkedIn',
        'twitch': 'Twitch',
        'vimeo': 'Vimeo',
        'snapchat': 'Snapchat'
    }
    message_lower = message.lower()
    for platform_key, platform_name in platforms.items():
        if platform_key in message_lower:
            extracted['platform'] = platform_name
            break
    
    # Try to extract name (look for various patterns)
    name_patterns = [
        r"(?:i'?m|i am|my name is|this is|call me|it'?s)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        r"name[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)(?:\s|$)",  # Name at start of message
        r"([A-Z][a-z]+\s+[A-Z][a-z]+)",  # Two capitalized words (likely first + last name)
    ]
    for pattern in name_patterns:
        name_match = re.search(pattern, message, re.IGNORECASE)
        if name_match:
            potential_name = name_match.group(1).strip()
            # Basic validation: name shouldn't be too long or contain email-like patterns
            if len(potential_name) < 50 and '@' not in potential_name:
                extracted['name'] = potential_name
                break
    
    return extracted
