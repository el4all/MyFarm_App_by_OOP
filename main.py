import flet as ft


from views.classes_for_views import (MainMenuView,MainRabbitsList,RabbitCard,BlocksFarm,ThirdRoom,BoxInfo,FarmInfo,
                                     ProcessFarm,ShowProcess)
from models.bunny_class import Farm
from helper_defs import file_from_google


# def save_value_for_checkboxes(process_key: str, completed_ids: list):
#     data = {}
#     if os.path.exists(TEMP_FOR_CHECKBOX):
#         try:
#             with open(TEMP_FOR_CHECKBOX, 'r',encoding='utf-8') as f:
#                 data = json.load(f)
#         except Exception:
#             data = {}
#     data[process_key] = completed_ids
#     with open(TEMP_FOR_CHECKBOX, 'w',encoding='utf-8') as f:
#         json.dump(data, f, ensure_ascii=False, indent=2)
#
# def get_value_for_checkboxes(process_key: str):
#     if not os.path.exists(TEMP_FOR_CHECKBOX):
#         return []
#     try:
#         with open(TEMP_FOR_CHECKBOX, 'r', encoding='utf-8') as f:
#             data = json.load(f).get(process_key,[])
#             return data
#     except Exception:
#         return []
#
# def get_temp_for_dict_type(process_key: str):
#     if not os.path.exists(TEMP_FOR_CHECKBOX):
#         return {}
#     try:
#         with open(TEMP_FOR_DICT, 'r', encoding='utf-8') as f:
#             data = json.load(f).get(process_key, {})
#             return data
#     except Exception:
#         return {}
#
# def save_temp_for_dict_type(process_key: str, individual_process_data: dict):
#     data = {}
#     if os.path.exists(TEMP_FOR_CHECKBOX):
#         try:
#             with open(TEMP_FOR_CHECKBOX, 'r',encoding='utf-8') as f:
#                 data = json.load(f)
#         except Exception:
#             data = {}
#     data[process_key] = individual_process_data
#     with open(TEMP_FOR_CHECKBOX, 'w',encoding='utf-8') as f:
#         json.dump(data, f, ensure_ascii=False, indent=2)
#
# def get_farm_from_disc():
#     with open('../offline/ACTUALLY_FARM.json','r',encoding='utf-8') as f:
#         data = json.load(f)
#
#     return data


farm_dict =  file_from_google()  #get_farm_from_disc()
file_name = 'ACTUALLY_FARM.json'
meatberry = Farm('MeatBerry')
meatberry.load_from_net(farm_dict)

tasks = []




def main(page: ft.Page):

    ROUTES = {'/main_menu': MainMenuView, '/rabbits_list':MainRabbitsList, '/rabbit_card':RabbitCard,
              '/blocks_farm': BlocksFarm, '/third_room':ThirdRoom, '/box_info':BoxInfo, '/farm_info':FarmInfo,
              '/process_farm':ProcessFarm, '/show_process':ShowProcess}

    def route_change(e):

        need_class = ROUTES.get(page.route)
        if need_class:
            new_screen = need_class(page, meatberry)
            if new_screen.route not in [x.route for x in page.views]:
                page.views.append(new_screen)
        page.update()

    def view_pop(e):
        page.views.pop()
        previous_screen = page.views[-1]

        if hasattr(previous_screen, 'refresh'):
            previous_screen.refresh()
        elif hasattr(previous_screen, 'controls_update'):
            previous_screen.controls_update()

        page.navigate(previous_screen.route)

        # page.route = previous_screen.route
        # page.update()


    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.views.clear()
    page.navigate('/main_menu')
    page.update()

ft.run(main=main, assets_dir='assets')
