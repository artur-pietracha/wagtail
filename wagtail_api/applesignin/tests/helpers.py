def mock_apple_verify_oauth2_valid_token(*args, **kwargs):
    return {
        "access_token": "valid",
        "token_type": "Bearer",
        "expires_in": 3600,
        "refresh_token": "reb3dd4048e7c4839a8572604ba7714cb.0.mxts.MN0peV9-sDp25pfpTo1iIg",
        "id_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2FwcGxlaWQu"
        "YXBwbGUuY29tIiwiYXVkIjoiY29tLmthcm1hYmFieXMuYXBwLmNsaWVudCIsImV4cCI6MTU3NTQwNjg2N"
        "ywiaWF0IjoxNTc1NDA2MjY3LCJzdWIiOiIwMDA3MzIuYWEwNzkwYWVjMDBlNzQwN2JjMTMwYmY0ODI2YWM"
        "3MWQuMTUwNSIsImF0X2hhc2giOiJXdzhITUcxQjRFaEYxYnEyTWVfbXlnIiwiZW1haWwiOiJ1c2VyQGdtYW"
        "lsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjoidHJ1ZSIsImF1dGhfdGltZSI6MTU3NTQwNjIyMH0.VvaExUoOw0"
        "g2BL-NJe667OTV4pkH74qBR3E5wTJHcGQ",
    }


def mock_apple_verify_oauth2_invalid_token(*ags, **kwargs):
    return {"error": "invalid_grant"}
