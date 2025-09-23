import re

def extract_contact_info(text):
    email = re.findall(r'\S+@\S+', text)
    phone = re.findall(r'\+?[\s\-\(]?\d{0,3}[\s\-\)]?\d[\d\-\s]{8,12}\d', text)
    return {"email": email[0] if email else None,
            "phone": phone[0] if phone else None}

# Test with various phone number formats
test_texts = [
    "Phone: +1-555-123-4567",
    "Contact: (555) 123-4567",
    "Call me at 555.123.4567",
    "Mobile: 555 123 4567",
    "Phone number: 5551234567",
    "Tel: +91 98765 43210",
    "Contact: +44 20 7946 0958",
    "Phone: 123-456-7890",
    "Mobile: 123.456.7890",
    "Tel: (123) 456-7890",
    "Contact: 123 456 7890",
    "Phone: +1 (555) 123-4567",
    "Mobile: +91-98765-43210",
    "Tel: +44-20-7946-0958"
]

print("Testing phone number regex patterns:")
print("=" * 50)

for i, text in enumerate(test_texts, 1):
    result = extract_contact_info(text)
    print(f"{i:2d}. Text: '{text}'")
    print(f"    Phone detected: {result['phone']}")
    print()

# Test with a more comprehensive regex
def extract_contact_info_improved(text):
    email = re.findall(r'\S+@\S+', text)
    # More comprehensive phone regex
    phone_patterns = [
        r'\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',  # US format
        r'\+?[0-9]{1,4}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}',  # International
        r'\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',  # US without country code
        r'[0-9]{3}[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',  # Simple US format
        r'\+?[0-9]{10,15}'  # Long number format
    ]
    
    phones = []
    for pattern in phone_patterns:
        matches = re.findall(pattern, text)
        phones.extend(matches)
    
    return {"email": email[0] if email else None,
            "phone": phones[0] if phones else None}

print("\nTesting improved phone number regex patterns:")
print("=" * 50)

for i, text in enumerate(test_texts, 1):
    result = extract_contact_info_improved(text)
    print(f"{i:2d}. Text: '{text}'")
    print(f"    Phone detected: {result['phone']}")
    print()
