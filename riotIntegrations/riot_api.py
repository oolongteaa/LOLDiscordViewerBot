import requests
import time
from multiprocessing import Process

def spawn_game_monitor(api_key, region, game_id, username, tag, match_region):
    """
    Spawn a new process to monitor a game.

    :param api_key: Riot API key
    :param region: Region for Summoner/Spectator API
    :param match_region: Region for Match API
    :param username: Summoner's in-game name
    :param game_id: Game ID to monitor
    """
    process = Process(target=monitor_game, args=(api_key, region, game_id, username, tag, match_region))
    process.start()
    print(f"Spawned new process for {username}'s game (Game ID: {game_id}).")
    return process  # Return the process handle

def monitor_game(api_key: str, region: str, game_id: int, username: str, tag: str, match_region: str) -> dict:
    """
    Monitor a League of Legends game and return the result once it finishes.

    :param api_key: Your Riot Games API key
    :param region: The spectator region
    :param game_id: The ID of the game to monitor
    :param puuid: The player's PUUID for result tracking
    :param match_region: The match region for Match-V5 API
    :return: A dictionary containing the game result
    """
    headers = {"X-Riot-Token": api_key}
    encrypted_puuid = get_puuid(api_key, region, username, tag)
    spectator_url = f"https://{match_region}.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{encrypted_puuid}"
    puuid_url = f"https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{encrypted_puuid}"
    puuid = requests.get(puuid_url, headers=headers).json()["puuid"]
    match_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=20"

    match_url = match_url + '&api_key=' + api_key

    # Poll the spectator endpoint to monitor the game's progress
    print(f"Monitoring game {game_id}...")
    while True:
        print(spectator_url)
        response = requests.get(spectator_url, headers=headers)
        if response.status_code == 404:  # Game no longer active
            print("Game has ended. Fetching results...")
            break
        elif response.status_code != 200:
            print(f"Unexpected error: {response.status_code}")
            return None

        time.sleep(10)  # Wait for 10 seconds before polling again

    # Get match results once game is over
    match_response = requests.get(match_url)
    match_ids = match_response.json()
    print(match_ids)
    if match_response.status_code != 200:
        print(f"Failed to fetch match results: {match_response.status_code}")
        return None

    latest_match = match_ids[0]

    detailed_match_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{latest_match}"
    match_details = requests.get(detailed_match_url, headers=headers)
    match_json = match_details.json()
    if match_details.status_code == 200:
        #TODO NEED TO DETERMINE WHO WON THE GAME
        print(f"game finished {match_json}")
        return match_json
    else:
        print(f"Failed to fetch detailed match data: {match_details.status_code}")
        return None


def get_puuid(api_key: str, riot_region: str, username: str, tag: str):
    # Base URLs for the API endpoints
    summoner_url = f"https://{riot_region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{username}/{tag}"
    headers = {"X-Riot-Token": api_key}
    print(summoner_url)

    try:
        # Get encrypted summoner ID
        summoner_response = requests.get(summoner_url, headers=headers)
        print(summoner_response)
        if summoner_response.status_code != 200:
            print(f"Failed to fetch summoner data: {summoner_response.status_code}")
            return None

        summoner_data = summoner_response.json()
        summoner_puuid = summoner_data["puuid"]
        print(summoner_puuid)

        return summoner_puuid

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def is_in_game(api_key: str, riot_region: str, lol_region: str, username: str, tag: str) -> dict:
    """
    Check if a League of Legends user is currently in a game.

    :param api_key: Your Riot Games API key
    :param riot_region: The riot games region (americas)
    :param lol_region: the lol server region (na1)
    :param summoner_name: The summoner's in-game name
    :return: A dictionary with game info if in a game, or None if not
    """
    headers = {"X-Riot-Token": api_key}
    summoner_puuid = get_puuid(api_key, riot_region, username, tag)

    # Step 2: Check if the summoner is in a live game
    spectator_url = f"https://{lol_region}.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{summoner_puuid}"
    game_response = requests.get(spectator_url, headers=headers)

    if game_response.status_code == 200:
        # Summoner is in a game
        return game_response.json()
    elif game_response.status_code == 404:
        # Summoner is not in a game
        return None
    else:
        print(f"Error checking game status: {game_response.status_code}")
        return None