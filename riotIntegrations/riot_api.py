import requests

def is_in_game(api_key: str, riot_region: str, lol_region: str, username: str, tag: str) -> bool:
    """
    Check if a League of Legends user is currently in a game.

    :param api_key: Your Riot Games API key
    :param riot_region: The riot games region (americas)
    :param lol_region: the lol server region (na1)
    :param summoner_name: The summoner's in-game name
    :return: A dictionary with game info if in a game, or None if not
    """
    # Base URLs for the API endpoints
    summoner_url = f"https://{riot_region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{username}/{tag}"
    headers = {"X-Riot-Token": api_key}
    print(summoner_url)

    try:
        # Step 1: Get encrypted summoner ID
        summoner_response = requests.get(summoner_url, headers=headers)
        print(summoner_response)
        if summoner_response.status_code != 200:
            print(f"Failed to fetch summoner data: {summoner_response.status_code}")
            return False

        summoner_data = summoner_response.json()
        summoner_puuid = summoner_data["puuid"]
        print(summoner_puuid)

        # Step 2: Check if the summoner is in a live game
        spectator_url = f"https://{lol_region}.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{summoner_puuid}"
        game_response = requests.get(spectator_url, headers=headers)

        if game_response.status_code == 200:
            # Summoner is in a game
            return True
        elif game_response.status_code == 404:
            # Summoner is not in a game
            return False
        else:
            print(f"Error checking game status: {game_response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return False