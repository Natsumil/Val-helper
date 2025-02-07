import flet
from flet import (
    Page,
    Container,
    Column,
    Row,
    Text,
    ElevatedButton,
    IconButton,
    Theme,
    ThemeMode,
    Colors,
    Icons,
    padding,
    alignment,
    GestureDetector,
    DragStartEvent,
    DragUpdateEvent,
    Switch,
    Dropdown,
    dropdown,
)
import threading
import os
import psutil
import time

from api import Client
from internal_api import ValorantInternal
from game_utils import fetch_game_state
from agent_mapping import AGENT_MAPPING


def main(page: Page):
    root_dir = os.path.dirname(os.path.abspath(__file__))
    page.title = "VAL-Helper"
    page.window.width = 300
    page.window.height = 460  # Increased height
    page.window.frameless = True
    page.window.icon = os.path.join(root_dir, "assets", "icon.ico")
    page.window.top = 100
    page.window.left = 100
    page.padding = 8
    page.theme_mode = ThemeMode.DARK
    page.dark_theme = Theme(color_scheme_seed=Colors.DEEP_PURPLE_800)

    client = Client(region="ap")
    valorant_internal = ValorantInternal()

    try:
        client.activate()
    except Exception as e:
        print(f"Failed to activate client: {e}")

    result_text = Text("", color=Colors.GREY_300, text_align="center")
    status_text = Text("Status: Initializing...", color=Colors.YELLOW_200, text_align="center")
    server_location_text = Text("", color=Colors.GREEN_200, text_align="center") # Initialize as empty

    auto_pick_enabled = False
    selected_agent = "None"
    pick_delay = 5

    auto_pick_switch = Switch(label="Auto Pick Agent", value=False)
    agent_dropdown = Dropdown(
        options=[dropdown.Option(agent) for agent in AGENT_MAPPING.keys()],
        value="None",
        width=150,
        disabled=True,
    )

    def auto_pick_changed(e):
        nonlocal auto_pick_enabled
        auto_pick_enabled = auto_pick_switch.value
        agent_dropdown.disabled = not auto_pick_enabled
        page.update()

    auto_pick_switch.on_change = auto_pick_changed

    def agent_selected(e):
        nonlocal selected_agent
        selected_agent = agent_dropdown.value
        page.update()

    agent_dropdown.on_change = agent_selected

    def auto_pick_task():
        while True:
            if auto_pick_enabled:
                try:
                    game_state = fetch_game_state(client)
                    if game_state == "PREGAME":
                        time.sleep(pick_delay)
                        agent_id = AGENT_MAPPING[selected_agent]
                        client.pregame_select_character(agent_id)
                        client.pregame_lock_character(agent_id)
                        result_text.value = f"Agent {selected_agent} selected!"
                        page.update()
                except Exception as e:
                    result_text.value = f"Auto-pick Error: {e}"
                    page.update()
            time.sleep(1)

    threading.Thread(target=auto_pick_task, daemon=True).start()

    def update_status():
        while True:
            try:
                game_state = fetch_game_state(client)
                status_text.value = game_state

                server_location_text.value = ""
                try:
                    if game_state == "PREGAME":
                        match_info = client.pregame_fetch_match()
                    elif game_state == "INGAME":
                        match_info = client.coregame_fetch_match()
                    else:
                        match_info = None

                    if match_info:
                        game_pod_id = match_info.get("GamePodID", "Unknown")
                        location = game_pod_id.split("-")[-2] if game_pod_id != "Unknown" and len(game_pod_id.split("-")) > 2 else "Unknown"
                        server_location_text.value = location
                    else:
                        server_location_text.value = ""


                except Exception as e:
                    server_location_text.value = f"Server Location: Error: {e}"

            except Exception as e:
                status_text.value = f"Status: Error fetching game state: {e}"
            page.update()
            time.sleep(30)

    threading.Thread(target=update_status, daemon=True).start()

    drag_start_x = 0
    drag_start_y = 0

    def close_app(e):
        page.window.close()

    close_button = IconButton(icon=Icons.CLOSE, icon_color=Colors.RED_500, on_click=close_app)

    def reload_client_click(e):
        try:
            client.activate()
            result_text.value = "Client reloaded successfully!"
        except Exception as err:
            result_text.value = f"Error: {err}"
        page.update()

    reload_button = IconButton(icon=Icons.REFRESH, icon_color=Colors.BLUE_ACCENT_400, on_click=reload_client_click)

    def check_side_click(e):
        try:
            ally = client.pregame_fetch_match()['AllyTeam']
            ally_team = ally['TeamID']
            ally_result = "Attacker" if ally_team == 'Red' else "Defender" if ally_team == 'Blue' else "Unknown"
            result_text.value = f"Your side: {ally_result}"
        except Exception as err:
            result_text.value = f"Error: {err}"
        page.update()

    check_side_button = ElevatedButton("Check Side", bgcolor=Colors.INDIGO_500, width=260, on_click=check_side_click)

    def dodge_game_click(e):
        try:
            client.pregame_quit_match()
            result_text.value = "Successfully dodged the game!"
        except Exception as err:
            result_text.value = f"Error: {err}"
        page.update()

    dodge_game_button = ElevatedButton("Dodge Game", bgcolor=Colors.AMBER_600, color=Colors.BLACK, width=260, on_click=dodge_game_click)

    def remove_all_friends(e):
        def remove_friends():
            try:
                friends = valorant_internal.get_friends().friends
                if not friends:
                    result_text.value = "No friends to remove."
                    page.update()
                    return

                for friend in friends:
                    valorant_internal.remove_friend(friend)

                result_text.value = f"Friends removed successfully."
            except Exception as err:
                result_text.value = f"Error: {err}"
            page.update()

        threading.Thread(target=remove_friends, daemon=True).start()

    remove_friends_button = ElevatedButton("Remove Friends", bgcolor=Colors.RED_700, color=Colors.WHITE, width=260, on_click=remove_all_friends)

    # VALORANTを終了
    def multiple_valorant_click(e):
        try:
            killed = False
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == "VALORANT.exe":
                    proc.kill()
                    killed = True
                    break
            result_text.value = "Multiple Valorant Ready!" if killed else "VALORANT not found."
        except Exception as err:
            result_text.value = f"Error: {err}"
        page.update()

    multiple_valorant_button = ElevatedButton("Multiple Valorant", bgcolor=Colors.PINK_ACCENT_700, color=Colors.WHITE, width=260, on_click=multiple_valorant_click)

    def header_pan_start(e: DragStartEvent):
        nonlocal drag_start_x, drag_start_y
        drag_start_x = e.local_x
        drag_start_y = e.local_y

    def header_pan_update(e: DragUpdateEvent):
        nonlocal drag_start_x, drag_start_y
        page.window.left = max(0, page.window.left + e.delta_x)
        page.window.top = max(0, page.window.top + e.delta_y)
        page.update()

    custom_header = GestureDetector(
        on_pan_start=header_pan_start,
        on_pan_update=header_pan_update,
        drag_interval=10,
        content=Container(
            content=Row(
                controls=[
                    Text("VAL-Helper", color=Colors.WHITE, weight="bold"),
                    Row(
                        controls=[reload_button, close_button],
                        alignment="end"
                    )
                ],
                alignment="spaceBetween"
            ),
            expand=True,
            height=32,
        ),
    )

    page.add(
        Column(
            [
                custom_header,
                auto_pick_switch,
                agent_dropdown,
                check_side_button,
                dodge_game_button,
                remove_friends_button,
                multiple_valorant_button,
                # Swapped the order of server location and status
                Row(
                    controls=[
                        Text("Status:", color=Colors.WHITE70),
                        status_text,
                    ],
                    alignment=alignment.center,  # alignment.centerを正しく使用
                ),
                Row(
                    controls=[
                        Text("Server:", color=Colors.WHITE70),
                        server_location_text,
                    ],
                    alignment=alignment.center,  # alignment.centerを正しく使用
                ),
                Container(
                    content=result_text,
                    alignment=alignment.center,
                    padding=padding.only(top=10),
                ),
            ],
            alignment="center",
            horizontal_alignment="center",
        )
    )


if __name__ == "__main__":
    flet.app(target=main)