def fetch_game_state(client):
    session_state = client.fetch_presence(client.puuid)
    return session_state["sessionLoopState"]