import os
import pathlib

local_app_data = pathlib.Path(os.getenv("LocalAppData", ""))
riot_client = local_app_data / "Riot Games" / "Riot Client"
lock_file_path = riot_client / "Config" / "lockfile"

profile_path = "profiles"