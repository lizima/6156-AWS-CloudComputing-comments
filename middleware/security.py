import json

secure_paths = [
    "/users",
    "/addresses"
]

def check_security(request, google):
    path = request.path
    result_ok = False

    if path in secure_paths:
        google_data = None

        user_info_endpoint = "/oauth2/v1/userinfo"
        if google.authorized:
            google_data = google.get(user_info_endpoint)
            print(google_data.json())

            result_ok = True
    else:
        result_ok = True
    return result_ok
