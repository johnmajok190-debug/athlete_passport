import os
import django

def run_manual_tests():
    import requests
    import json
    from sports.models import SportFormat

    BASE_URL = "http://127.0.0.1:8000/api"
    TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzg0ODg4OTM4LCJpYXQiOjE3ODQ4ODg2MzgsImp0aSI6IjgyMGNkZjI1YWVlOTQwY2U4MzY4NGQyM2QwYjRmZmM3IiwidXNlcl9pZCI6IjUifQ.wqxRgUcX_wUXUKZbDk00td0ERQxtgN1l0LytO2szKnQ"

    headers = {"Authorization": f"Bearer {TOKEN}"}

    print("=" * 60)
    print("Testing Games API")
    print("=" * 60)

    # Get format from database directly
    sport_id = "f1717260-3bf5-4e0d-827b-8eeea90d3498"  # Basketball
    format_obj = SportFormat.objects.first()
    format_id = str(format_obj.id) if format_obj else None

    print(f"\nAvailable format: {format_obj}")

    # Test 1: GET /api/games/ - List games
    print("\n1. GET /api/games/ - List games (empty)")
    response = requests.get(f"{BASE_URL}/games/", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 2: POST /api/games/ - Create a game
    if format_id:
        print(f"\n2. POST /api/games/ - Create a game")
        game_data = {
            "title": "Championship Match 2026",
            "sport": sport_id,
            "format": format_id,
            "location": "National Stadium",
        }
        response = requests.post(f"{BASE_URL}/games/", json=game_data, headers=headers)
        print(f"Status: {response.status_code}")
        resp_json = response.json()
        print(f"Response: {json.dumps(resp_json, indent=2)}")
        
        if response.status_code == 201:
            game_id = resp_json["id"]
            
            # Test 3: GET /api/games/{game_id}/ - Get game details
            print(f"\n3. GET /api/games/{game_id}/ - Get game details")
            response = requests.get(f"{BASE_URL}/games/{game_id}/", headers=headers)
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            # Test 4: PUT /api/games/{game_id}/ - Update game
            print(f"\n4. PUT /api/games/{game_id}/ - Update game")
            update_data = {"location": "Updated Stadium"}
            response = requests.put(f"{BASE_URL}/games/{game_id}/", json=update_data, headers=headers)
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            # Test 5: GET /api/games/ - List games (should show created game)
            print("\n5. GET /api/games/ - List games (updated)")
            response = requests.get(f"{BASE_URL}/games/", headers=headers)
            print(f"Status: {response.status_code}")
            games_list = response.json()
            print(f"Total games: {len(games_list)}")
            if games_list:
                print(f"First game: {json.dumps(games_list[0], indent=2)}")

    print("\n" + "=" * 60)
    print("[OK] Games API Test Completed Successfully!")
    print("=" * 60)

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    run_manual_tests()
