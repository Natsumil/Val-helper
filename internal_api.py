import base64
import os
import pathlib

import requests

import structs


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
        self.headers = {
            "Authorization": f"Bearer {self.get_token().accessToken}",
            "X-Riot-Entitlements-JWT": self.get_token().token
        }

    def get_token(self) -> structs.EntitlementsTokenResponse:
        resp = requests.get(f"{self.url}/entitlements/v1/token", headers=self.internal_headers, verify=False)

        if resp.status_code != 200:
            raise RuntimeError(resp.status_code)
        return structs.EntitlementsTokenResponse(**resp.json())

    def get_friends(self) -> structs.GetFriendsResponse:
        resp = requests.get(f"{self.url}/chat/v4/friends", headers=self.internal_headers, verify=False)

        if resp.status_code != 200:
            raise RuntimeError(resp.status_code)
        return structs.GetFriendsResponse(**resp.json())

    def remove_friend(self, friend: structs.Friend) -> int:
        data = {
            "pid": friend.pid,
            "puuid": friend.puuid
        }
        resp = requests.delete(f"{self.url}/chat/v4/friends", headers=self.internal_headers, verify=False, json=data)
        return resp.status_code
