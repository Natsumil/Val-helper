import base64
import os
import pathlib
import time
import requests
import urllib3

from structs import GetFriendsResponse, Friend, EntitlementsTokenResponse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ValorantInternal:
    def __init__(self):
        LocalAppData = pathlib.Path(os.getenv("LocalAppData", ""))
        RiotClient = LocalAppData / "Riot Games" / "Riot Client"
        LockFilePath = RiotClient / "Config" / "lockfile"

        lockfile_data = open(LockFilePath, "r").read().split(":")

        self.auth = f"riot:{lockfile_data[3]}"
        self.url = f"https://127.0.0.1:{lockfile_data[2]}"
        self.internal_headers = {
            "Authorization": f"Basic {base64.b64encode(self.auth.encode()).decode()}"
        }
        self._token_cache = None
        self._token_expiry = 0

    def get_token(self) -> EntitlementsTokenResponse:
        if self._token_cache and time.time() < self._token_expiry:
            return self._token_cache

        resp = requests.get(f"{self.url}/entitlements/v1/token", headers=self.internal_headers, verify=False)
        if resp.status_code != 200:
            raise RuntimeError(resp.status_code)
        token_response = EntitlementsTokenResponse(**resp.json())

        self._token_cache = token_response
        self._token_expiry = time.time() + 3600
        return token_response

    def get_friends(self) -> GetFriendsResponse:
        resp = requests.get(f"{self.url}/chat/v4/friends", headers=self.internal_headers, verify=False)

        if resp.status_code != 200:
            raise RuntimeError(resp.status_code)
        return GetFriendsResponse(**resp.json())

    def remove_friend(self, friend: Friend) -> int:
        data = {
            "pid": friend.pid,
            "puuid": friend.puuid
        }
        resp = requests.delete(f"{self.url}/chat/v4/friends", headers=self.internal_headers, verify=False, json=data)
        return resp.status_code