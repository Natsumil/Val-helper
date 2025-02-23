import base64
import requests
import structs
import constants
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ValorantAPI:
    @staticmethod
    def get_version():
        """Valorantのバージョン情報を取得する"""
        resp = requests.get("https://valorant-api.com/v1/version")
        resp.raise_for_status()
        return resp.json()

class ValorantInternal:
    def __init__(self):
        """Riot Clientのロックファイルから認証情報を取得し、初期化する"""
        if not os.path.exists(constants.lock_file_path):
            exit(1)

        lockfile_data = open(constants.lock_file_path, "r").read().split(":")

        self.auth = f"riot:{lockfile_data[3]}"
        self.url = f"https://127.0.0.1:{lockfile_data[2]}"
        self.internal_headers = {
            "Authorization": f"Basic {base64.b64encode(self.auth.encode()).decode()}"
        }

        version_data = ValorantAPI.get_version()
        client_version = version_data["data"]["riotClientVersion"] if version_data and "data" in version_data and "riotClientVersion" in version_data["data"] else "unknown"

        self.headers = {
            "Authorization": f"Bearer {self.get_token().accessToken}",
            "X-Riot-Entitlements-JWT": self.get_token().token,
            "X-Riot-ClientVersion": client_version,
            "X-Riot-ClientPlatform": "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9"
        }

    def get_token(self) -> structs.EntitlementsTokenResponse:
        """エンタイトルメントトークンを取得する"""
        resp = requests.get(f"{self.url}/entitlements/v1/token", headers=self.internal_headers, verify=False)
        resp.raise_for_status()
        return structs.EntitlementsTokenResponse(**resp.json())

    def get_friends(self) -> structs.GetFriendsResponse:
        """フレンドリストを取得する"""
        resp = requests.get(f"{self.url}/chat/v4/friends", headers=self.internal_headers, verify=False)
        resp.raise_for_status()
        return structs.GetFriendsResponse(**resp.json())

    def remove_friend(self, friend: structs.Friend) -> int:
        """フレンドを削除する"""
        data = {
            "pid": friend.pid,
            "puuid": friend.puuid
        }
        resp = requests.delete(f"{self.url}/chat/v4/friends", headers=self.internal_headers, verify=False, json=data)
        resp.raise_for_status()
        return resp.status_code

    def get_preferences(self) -> dict:
        """プレイヤーの設定を取得する"""
        resp = requests.get(
            "https://player-preferences-usw2.pp.sgp.pvp.net/playerPref/v3/getPreference/Ares.PlayerSettings",
            headers=self.headers,
            verify=False
        )
        resp.raise_for_status()
        return resp.json()

    def set_preferences(self, preferences: dict) -> int:
        """プレイヤーの設定を更新する"""
        resp = requests.put(
            "https://player-preferences-usw2.pp.sgp.pvp.net/playerPref/v3/savePreference",
            headers=self.headers,
            json=preferences,
            verify=False
        )
        resp.raise_for_status()
        return resp.status_code