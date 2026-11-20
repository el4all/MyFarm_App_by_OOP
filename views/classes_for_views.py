

import flet as ft

from datetime import date, timedelta



from helper_defs import (file_upload_google,get_value_for_checkboxes,get_temp_for_dict_type, save_value_for_checkboxes,
                         save_temp_for_dict_type)
from models.bunny_class import Farm, Bunny, Box, STATUS_FOR_STR, STATUS_WORK
from views.components import (FarmSortBar,LeftBlock,RightBlock,BlockNumberSix,
                              get_widget_for_works_by_day, get_container_with_date)
from models.python_logic import (preparing_work_data,preparing_data_for_blocks_in_third_room,average_age_farm,
                                 get_planned_work, get_status_for_mate, get_data_for_widget_for_works_by_day)

COLOR_STATUS = dict([('new', ft.Colors.GREEN_500), ('culling', ft.Colors.RED_500), ('waiting_for_kindling', ft.Colors.BLUE_500),
                     ('mated',ft.Colors.YELLOW_500), ('mated_mother',ft.Colors.YELLOW_500),
                     (None, ft.Colors.WHITE), ('mother',ft.Colors.BROWN_500), ('mother*', ft.Colors.GREY_500)])
BOXES = dict([(1,20),(2,20),(3,20),(4,20),(5,20),(6,25),(7,20),(8,20),(9,20),(10,20),(11,12),(12,12)])
DATE_FORMAT = '%d.%m.%Y'


def _go_back(e: ft.Event):
    page = e.page
    if page and len(page.views) > 1:
        page.views.pop()
        previous_screen = page.views[-1]
        page.navigate(previous_screen.route)

def on_keyboard_event(e: ft.KeyboardEvent):
    if e.key == "Escape":
        _go_back(e)


class CustomBottomBar(ft.BottomAppBar):
    def __init__(self, main_page: ft.Page):
        self.main_page = main_page
        home, blocks, nests, processes, feeding ,info = self.get_elements_for_bottom_bar()

        super().__init__(bgcolor=ft.Colors.WHITE_70,
                         content=ft.Row(controls=[home, blocks, nests, processes, feeding, info],
                                      alignment=ft.MainAxisAlignment.SPACE_BETWEEN))

    def get_elements_for_bottom_bar(self):
            home = ft.Container(
                ft.Column(
                    [
                        ft.Icon(ft.Icons.HOME, size=20),
                        ft.Text('Головна', size=10)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                on_click=lambda e: self._to_next_screen('/main_menu')
            )

            blocks = ft.Container(
                ft.Column(
                    [
                        ft.Icon(ft.Icons.APPS, size=20),
                        ft.Text('Блоки', size=10)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                on_click=lambda e: self._to_next_screen('/blocks_farm')
            )

            nests = ft.Container(
                ft.Column(
                    [
                        ft.Icon(ft.Icons.CRUELTY_FREE, size=20),
                        ft.Text('Гнізда', size=10)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                on_click=lambda e: self._to_next_screen('/nests_list')
            )

            info = ft.Container(
                ft.Column(
                    [
                        ft.Icon(ft.Icons.INFO, size=20),
                        ft.Text('Інфо', size=10)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                on_click=lambda e: self._to_next_screen('/farm_info')
            )

            feeding = ft.Container(
                ft.Column(
                    [
                        ft.Icon(ft.Icons.GRASS, size=20),
                        ft.Text('Відгодівля', size=10)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                on_click=lambda e: self._to_next_screen('/third_room')
            )

            processes = ft.Container(
                ft.Column(
                    [
                        ft.Icon(ft.Icons.CALENDAR_MONTH, size=20),
                        ft.Text('Процеси', size=10)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                on_click=lambda e: self._to_next_screen('/process_farm')
            )

            return home, blocks, nests, processes, feeding, info

    def _to_next_screen(self, next_screen: str):
        self.main_page.navigate(next_screen)


class CustomAppBar(ft.AppBar):
    def __init__(self, left_up=None, title=None, right_up=None):
        super().__init__(leading=ft.Container() if left_up is None else left_up,
                         title=ft.Container() if title is None else title,
                         actions=ft.Container() if right_up is None else right_up,
                         center_title=True)


class MainMenuView(ft.View):
    def __init__(self, main_page: ft.Page, farm: Farm):
        super().__init__(route='/main_menu')
        self.main_page = main_page
        self.farm = farm
        self.title_label = ft.Text('Головне меню ферми', size=20)
        self.theme_change_btn = ft.IconButton(icon=ft.Icon(ft.Icons.SETTINGS), on_click=self.change_theme)
        self.sync_btn = ft.IconButton(icon=ft.Icon(ft.Icons.SYNC), on_click=self._synchronization)
        self.bottom_appbar = CustomBottomBar(main_page)
        self.appbar = CustomAppBar(left_up=self.theme_change_btn, title=self.title_label, right_up=self.sync_btn)
        # self.controls = [ft.Column(controls=[ft.Text('Головне меню ферми', size=16, weight=ft.FontWeight.W_500),
        #                                   ft.ListTile(leading=ft.Icon(ft.Icons.PETS), title=ft.Text('Кролиці'),
        #                                               on_click=lambda e: self._to_next_screen('/rabbits_list')),
        #                                   ft.ListTile(leading=ft.Icon(ft.Icons.GRID_VIEW), title=ft.Text('Блоки'),
        #                                               on_click=lambda e: self._to_next_screen('/blocks_farm')),
        #                                   ft.ListTile(leading=ft.Icon(ft.Icons.CRUELTY_FREE), title=ft.Text('Гнізда'),
        #                                               on_click=lambda e: self._to_next_screen('/nests_list')),
        #                                   ft.ListTile(leading=ft.Icon(ft.Icons.MENU_BOOK), title=ft.Text('Відгодівля'),
        #                                               on_click=lambda e: self._to_next_screen('/third_room')),
        #                                   ft.ListTile(leading=ft.Icon(ft.Icons.DELETE_FOREVER), title=ft.Text('Вибраківка'),
        #                                               on_click=lambda e: self._to_next_screen('/rabbits_list')),
        #                                   ft.ListTile(leading=ft.Icon(ft.Icons.ADS_CLICK), title=ft.Text('Процеси'),
        #                                               on_click=lambda e: self._to_next_screen('/process_farm')),
        #                                   ft.ListTile(leading=ft.Icon(ft.Icons.INFO), title=ft.Text('Інформація'),
        #                                               on_click=lambda e: self._to_next_screen('/farm_info'))])]
        self.get_elements_for_today_works()
        total_working_rabbits_widget, feeding_rabbits_widget, bunnies_widget, culling_widget = self.get_elements_for_quantity_widget()
        yesterday_widget, today_widget, tomorrow_widget = self.get_elements_for_today_works()
        self.controls = [
            ft.Column(
                [
                    ft.Container(
                        ft.Row(
                            [
                                total_working_rabbits_widget,
                                feeding_rabbits_widget,
                                bunnies_widget,
                                culling_widget
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            spacing=2
                        ),
                        border=ft.Border.all(2, ft.Colors.ON_SURFACE_VARIANT),
                        border_radius=5,
                        padding=ft.Padding.all(2)
                    ),
                    ft.Container(
                        ft.Column(
                            [
                                yesterday_widget,
                                today_widget,
                                tomorrow_widget
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            spacing=2,
                            expand=True
                        ),
                        border=ft.Border.all(2, ft.Colors.ON_SURFACE_VARIANT),
                        border_radius=5,
                        padding=ft.Padding.all(2),
                        expand=True
                    )
                ],
                height=self.main_page.height - 270
            )
        ]

    def change_theme(self):
        self.main_page.theme_mode = ft.ThemeMode.DARK if self.main_page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        self.bottom_appbar.bgcolor = ft.Colors.WHITE_70 if self.main_page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.BLACK_12
        self.main_page.update()

    def _to_next_screen(self, e, next_screen: str):
        if e.control.data:
            self.main_page.data = e.control.data

        self.main_page.navigate(next_screen)

    def _synchronization(self):
        sync = file_upload_google(self.farm)
        text = ft.Text('Cинхронізовано') if sync else ft.Text('Помилка синхронізації')
        color = ft.Colors.BLUE_700 if sync else ft.Colors.RED_700

        self.snack_bar = ft.SnackBar(content=text, bgcolor=color, duration=2000, show_close_icon=True)
        self.main_page.overlay.append(self.snack_bar)
        self.snack_bar.open = True
        self.main_page.update()

    def get_elements_for_quantity_widget(self):
        total_working_rabbits = len([x for x in self.farm.rabbits.values() if x.status != 'culling'])
        feeding_rabbits = sum([x.quantity for x in self.farm.third_room.values() if x.quantity])
        bunnies = sum([x.nest.bunnies.get('alive',0) for x in self.farm.rabbits.values() if x.nest])
        culling = len([x for x in self.farm.rabbits.values() if x.status == 'culling'])

        total_working_rabbits_widget = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.CRUELTY_FREE, color=ft.Colors.BLUE_700),
                    ft.Text('Робоче\n стадо',  weight=ft.FontWeight.W_500),
                    ft.Text(f'{total_working_rabbits}', size=20, weight=ft.FontWeight.BOLD)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            border=ft.Border.all(1, ft.Colors.ON_SURFACE_VARIANT),
            border_radius=5,
            expand=True,
            bgcolor=ft.Colors.SURFACE,
            data={'rabbits_obj_list':
                      sorted([x for x in self.farm.rabbits.values() if x.name in self.farm.active],
                             key=lambda x: (x.block, x.box))},
            on_click=lambda e: self._to_next_screen(e,'/rabbits_list')
        )

        feeding_rabbits_widget = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.CRUELTY_FREE),
                    ft.Text('Відгодівля\n ', weight=ft.FontWeight.W_500),
                    ft.Text(f'{feeding_rabbits}', size=20, weight=ft.FontWeight.BOLD)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            border=ft.Border.all(1, ft.Colors.ON_SURFACE_VARIANT),
            border_radius=5,
            expand=True,
            bgcolor=ft.Colors.SURFACE,
            on_click=lambda e: self._to_next_screen(e,'/third_room')
        )

        bunnies_widget = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.CRUELTY_FREE, color=ft.Colors.GREEN_700),
                    ft.Text('Кролики\n ', weight=ft.FontWeight.W_500),
                    ft.Text(f'{bunnies}', size=20, weight=ft.FontWeight.BOLD)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            border=ft.Border.all(1, ft.Colors.ON_SURFACE_VARIANT),
            border_radius=5,
            expand=True,
            bgcolor=ft.Colors.SURFACE,
            on_click=lambda e: self._to_next_screen(e,'/nests_list')
        )

        culling_widget = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.CRUELTY_FREE, color=ft.Colors.RED_700),
                    ft.Text('Брак\n ', weight=ft.FontWeight.W_500),
                    ft.Text(f'{culling}', size=20, weight=ft.FontWeight.BOLD)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            border=ft.Border.all(1, ft.Colors.ON_SURFACE_VARIANT),
            border_radius=5,
            expand=True,
            bgcolor=ft.Colors.SURFACE,
            data={'rabbits_obj_list':
                      sorted([x for x in self.farm.rabbits.values() if x.status == 'culling'],
                             key=lambda x: (x.block, x.box))},
            on_click=lambda e: self._to_next_screen(e,'/rabbits_list')
        )

        return total_working_rabbits_widget, feeding_rabbits_widget, bunnies_widget, culling_widget

    def get_elements_for_today_works(self):
        yesterday, today, tomorrow = preparing_work_data(self.farm)

        yesterday_data = get_data_for_widget_for_works_by_day(yesterday)
        today_data = get_data_for_widget_for_works_by_day(today)
        tomorrow_data = get_data_for_widget_for_works_by_day(tomorrow)

        yesterday_date_widget = get_container_with_date(date.today() - timedelta(days=1))
        yesterday_date_widget.bgcolor = ft.Colors.RED_300
        today_date_widget = get_container_with_date(date.today())
        today_date_widget.bgcolor = ft.Colors.GREEN_300
        tomorrow_date_widget = get_container_with_date(date.today() + timedelta(days=1))
        tomorrow_date_widget.bgcolor = ft.Colors.YELLOW_300

        yesterday_widget = ft.Container(
            ft.Row(
                [
                    yesterday_date_widget,
                    ft.Container(
                        content=get_widget_for_works_by_day(yesterday_data)or ft.Column([ft.Text('Немає невиконаних робіт')],expand=True),
                        border=ft.Border.all(1, ft.Colors.ON_SURFACE_VARIANT),
                        border_radius=5,
                        padding=ft.Padding.all(2),
                        expand=True
                    )
                ],
                spacing=2
            ),
            expand=True,
            data=date.today() - timedelta(days=1),
            on_click=lambda e: self._to_next_screen(e,'/show_process')
        )
        today_widget = ft.Container(
            ft.Row(
                [
                    today_date_widget,
                    ft.Container(
                        content=get_widget_for_works_by_day(today_data) or ft.Column([ft.Text('Немає запланованих робіт')],expand=True),
                        border=ft.Border.all(1, ft.Colors.ON_SURFACE_VARIANT),
                        border_radius=5,
                        padding=ft.Padding.all(2),
                        expand=True
                    )
                ],
                spacing=2
            ),
            expand=True,
            data=date.today(),
            on_click=lambda e: self._to_next_screen(e,'/show_process')
        )
        tomorrow_widget = ft.Container(
            ft.Row(
                [
                    tomorrow_date_widget,
                    ft.Container(
                        content=get_widget_for_works_by_day(tomorrow_data)or ft.Column([ft.Text('Немає запланованих робіт')],expand=True),
                        border=ft.Border.all(1, ft.Colors.ON_SURFACE_VARIANT),
                        border_radius=5,
                        padding=ft.Padding.all(2),
                        expand=True
                    )
                ],
                spacing=2
            ),
            expand=True,
            data=date.today() + timedelta(days=1),
            on_click=lambda e: self._to_next_screen(e,'/show_process')
        )

        return yesterday_widget, today_widget, tomorrow_widget


class MainRabbitsList(ft.View):
    def __init__(self, main_page: ft.Page, farm: Farm):
        super().__init__(scroll = ft.ScrollMode.AUTO, route='/rabbits_list')
        self.main_page = main_page
        self.farm = farm

        received_data = main_page.data
        if isinstance(received_data, dict):
            self.rabbits_obj_list = received_data.get('rabbits_obj_list')
            self.block = received_data.get('block')
            main_page.data = None
        else:
            self.rabbits_obj_list = sorted([x for x in self.farm.rabbits.values()], key=lambda x: (x.block, x.box))

        self.title_label = ft.Text('Список кролиць', size=20)

        self.dialog_for_create_rabbit = ft.AlertDialog(title=ft.Text("Додавання кролиці"))

        self.date_picker = ft.DatePicker(on_change=self.set_name_for_create_rabbit)
        self.cancel_btn, self.line_text_field, self.block_field, self.box_field, self.result_field, self.next_btn = self.get_elements_for_create_rabbit()

        self.sort_menu = FarmSortBar(farm, self.sort_rabbits)
        add_bunny_btn = ft.TextButton(ft.Row([ft.Icon(ft.Icons.ADD_CIRCLE), ft.Text('Додати\nкролицю')]),
                               on_click=self.set_date_for_create_rabbit)

        self.appbar = CustomAppBar(left_up=None, title=self.title_label, right_up=ft.Row([add_bunny_btn,self.sort_menu]))
        self.bottom_appbar = CustomBottomBar(self.main_page)
        self.controls=[self.create_rabbit_tile(x) for x in self.rabbits_obj_list]

    def sort_rabbits(self, e):
        key, is_reverse = e.control.data
        self.rabbits_obj_list = sorted([x for x in self.farm.rabbits.values()], key=key, reverse=is_reverse)
        self.controls_update()

    def refresh(self):
        self.controls = [self.create_rabbit_tile(x) for x in sorted(self.farm.rabbits.values(),
                                                                                        key=lambda x: (x.block, x.box))]
        self.main_page.update()

    def controls_update(self):
        self.controls = [self.create_rabbit_tile(x) for x in self.rabbits_obj_list]
        self.main_page.update()

    def create_rabbit_tile(self, obj: Bunny):
        color = COLOR_STATUS.get(obj.status)
        return ft.ListTile(leading=ft.Icon(ft.Icons.BLOCK, color=ft.Colors.RED_500) if obj.status == 'culling' else ft.Icon(ft.Icons.PETS, color=color),
                           title=ft.Text(obj.name),
                           subtitle=ft.Column(controls=[ft.Text(f"Клітка: {obj.str_block_box}"),
                                                        ft.Text(f"Вік: {obj.age_in_month}")]),
                           data=obj, trailing=self.trailing_for_work_rabbit_tile(obj),
                           content_padding=ft.Padding.symmetric(horizontal=16, vertical=9),
                           on_click=lambda e, x=obj: self._to_next_screen(e, '/rabbit_card'))

    def _to_next_screen(self, e, next_screen: str):
        self.main_page.data = e.control.data
        self.main_page.navigate(next_screen)

    def _open_dialog(self):
        self.main_page.overlay.append(self.dialog_for_create_rabbit)
        self.dialog_for_create_rabbit.open = True
        self.main_page.update()

    def _close_dialog(self):
        self.dialog_for_create_rabbit.open = False
        self.dialog_for_create_rabbit.update()

    def _open_picker(self):
        self.main_page.overlay.append(self.date_picker)
        self.date_picker.open = True
        self.main_page.update()

    def get_elements_for_create_rabbit(self):
        cancel_btn = ft.TextButton('Скасувати', on_click=self._close_dialog)
        line_text_field = ft.TextField(width=150, hint_text='Лінія', on_change=self.handle_input_for_name)
        block_field = ft.TextField(max_length=4, hint_text='Блок', keyboard_type=ft.KeyboardType.NUMBER,
                                   width=120, counter=ft.Container(), on_change=self.handle_input_for_location)
        box_field = ft.TextField(max_length=4, hint_text='Клітка', keyboard_type=ft.KeyboardType.NUMBER,
                                 width=120, counter=ft.Container(), on_change=self.handle_input_for_location)
        result_field = ft.Text('В цій клітці ...')
        next_btn = ft.TextButton('Далі', on_click=self.set_name_for_create_rabbit)

        return cancel_btn, line_text_field, block_field, box_field, result_field, next_btn

    def handle_input_for_name(self):
        line = self.line_text_field.value
        self.line_text_field.suffix = self.farm.vacant_indexes(line) if len(line) >= 2 else ''

    def handle_input_for_location(self):
        self.block_field.error = None
        self.box_field.error = None
        is_error = False

        if not self.block_field.value or not self.block_field.value.strip().isdigit():
            self.block_field.error = 'Введіть число'
            is_error = True

        if not self.box_field.value or not self.box_field.value.strip().isdigit():
            self.box_field.error = 'Введіть число'
            is_error = True

        if not is_error:
            self.next_btn.disabled = False
            self.next_btn.on_click = self.final_create_rabbit
            name = self.farm.who_in_box(int(self.block_field.value), int(self.box_field.value))
            self.result_field.value = f'В цій клітці {name}'
        else:
            self.next_btn.disabled = True
            self.result_field.value = f'В цій клітці ...'

    def set_date_for_create_rabbit(self):
        self.dialog_for_create_rabbit.title = ft.Text('КРОК 1. Дата народження')
        self.dialog_for_create_rabbit.content = ft.Column([ft.Text('Оберіть дату народження кролиці')], tight=True)
        self.dialog_for_create_rabbit.actions = [ft.Row([self.cancel_btn, ft.Button('Відкрити календар', on_click=self._open_picker)],
                                                       alignment=ft.MainAxisAlignment.SPACE_BETWEEN)]

        self._open_dialog()

    def set_name_for_create_rabbit(self):
        self.dialog_for_create_rabbit.title = ft.Text('КРОК 2. Призначення імені')
        self.dialog_for_create_rabbit.content = ft.Column([ft.Text('Введіть лінію кролиці')], tight=True,
                                                          horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self.dialog_for_create_rabbit.actions = [ft.Column([self.line_text_field,
                                                            ft.Row([self.cancel_btn, ft.TextButton('Далі',
                                                                   on_click=self.set_address)],
                                                                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN)],
                                                           tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)]

        if len(self.line_text_field.value) >=2:
            print('Suffix calculate')
            self.line_text_field.suffix = self.farm.vacant_indexes(self.line_text_field.value)
            print(self.line_text_field.suffix)
            self.line_text_field.update()

    def set_address(self):
        self.next_btn.disabled = True
        self.next_btn.on_click = self.final_create_rabbit
        self.dialog_for_create_rabbit.title = ft.Text('КРОК 3. Розміщення')
        self.dialog_for_create_rabbit.content = ft.Column([ft.Text('Введіть блок та клітку')], tight=True,
                                                          horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self.dialog_for_create_rabbit.actions = [ft.Column([ft.Row([self.block_field,self.box_field],
                                                                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                                            self.result_field,
                                                            ft.Row([self.cancel_btn, self.next_btn],
                                                                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN)],
                                                           tight=True,
                                                           horizontal_alignment=ft.CrossAxisAlignment.CENTER)]

    def final_create_rabbit(self):
        self._close_dialog()
        name = f'{self.line_text_field.value}{self.line_text_field.suffix}'
        birthday = (self.date_picker.value + timedelta(hours=3)).date().strftime(DATE_FORMAT)
        block = int(self.block_field.value)
        box = int(self.box_field.value)

        result = self.farm.add_rabbit(name, birthday, block, box)

        text = ft.Text('Успішно додано') if result else ft.Text('Помилка створення')
        color = ft.Colors.BLUE_700 if result else ft.Colors.RED_700

        self.snack_bar = ft.SnackBar(content=text, bgcolor=color, duration=2000, show_close_icon=True)
        self.main_page.overlay.append(self.snack_bar)
        self.snack_bar.open = True
        self.main_page.update()

    def trailing_for_work_rabbit_tile(self, rabbit: Bunny):
        yesterday, today, tomorrow = preparing_work_data(self.farm)

        future_work = tomorrow.get(rabbit.name,None)
        today_work = today.get(rabbit.name,None)
        past_work = yesterday.get(rabbit.name,None)

        cont_for_future = ft.Container(content=ft.Text(future_work, size=10),
                                       width=100, bgcolor=ft.Colors.YELLOW_300,
                                       padding=ft.Padding.symmetric(horizontal=6, vertical=4),
                                       border_radius=4) if future_work else ft.Container(width=100)
        cont_for_today = ft.Container(content=ft.Text(today_work, size=10),
                                      width=100, bgcolor=ft.Colors.GREEN_300,
                                      padding=ft.Padding.symmetric(horizontal=6, vertical=4),
                                      border_radius=4) if future_work else ft.Container(width=100)
        cont_for_past = ft.Container(content=ft.Text(past_work, size=10),
                                     width=100, bgcolor=ft.Colors.RED_300,
                                     padding=ft.Padding.symmetric(horizontal=6, vertical=4),
                                     border_radius=4) if future_work else ft.Container(width=100)

        return ft.Container(ft.Column(controls=[cont_for_future, cont_for_today, cont_for_past]),
                            width=100, height=70)


class RabbitCard(ft.View):
    def __init__(self, main_page: ft.Page, farm: Farm):
        super().__init__(route='/rabbit_card')
        self.farm = farm
        self.main_page = main_page
        receive_data = main_page.data
        if isinstance(receive_data, Bunny):
            self.rabbit: Bunny | None = receive_data
            main_page.data = None
        else:
            self.rabbit = None

        self.cancel_btn, self.confirm_btn, self.block_field, self.box_field, self.result_field = self.get_elements_for_dialog()
        self.notes_text_field = ft.TextField(label='Нотатка', multiline=True, min_lines=3, max_lines=5,
                                             max_length=300, filled=True, bgcolor=ft.Colors.GREY_100,
                                             on_change=lambda e: self.processing_input_for_note(e))

        self.dialog_swap_box = ft.AlertDialog(
            title=ft.Text("Нова адреса"),
            actions=[
                ft.Container(content=ft.Column(controls=[
                    ft.Row([self.block_field,self.box_field], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                    ft.Row([self.result_field], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([self.cancel_btn, self.confirm_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ]))
            ]
        )

        operation_button = ft.PopupMenuButton(
            icon=ft.Row([ft.Icon(ft.Icons.FRONT_HAND_ROUNDED), ft.Icon(ft.Icons.ARROW_DROP_DOWN)]),
            items=[
                ft.PopupMenuItem(content=ft.Text('Видалити кролицю (смерть)'),
                                 on_click=lambda e: self.delete_rabbit()),
                ft.PopupMenuItem(content=ft.Text('Видалити кролицю (забій)'),
                                 on_click=lambda e: self.delete_rabbit(nature_death=False)),
                ft.PopupMenuItem(content=ft.Text('Встановити вибраківку'),
                                 on_click=lambda e: self.set_status()),
                ft.PopupMenuItem(content=ft.Text('Відмінити вибраківку'),
                                 on_click=lambda e: self.set_status(culling=False)),
                ft.PopupMenuItem(content=ft.Text('Втрата гнізда'),
                                 on_click=self.loose_nest),
                ft.PopupMenuItem(content=ft.Text('Переміщення'),
                                 on_click=lambda e: self.swap_boxes()),
                ft.PopupMenuItem(content=ft.Text('Зробити замітку'),
                                 on_click=lambda e: self.add_remove_text_field_for_note()),
                ft.PopupMenuItem(content=ft.Text('Видалити замітку'),
                                 on_click=lambda e: self.swap_boxes())
            ]
        )
        self.bottom_appbar = CustomBottomBar(self.main_page)
        self.appbar = CustomAppBar(right_up=operation_button) if self.rabbit else CustomAppBar()
        self.controls=[
            ft.Column(
                [
                    ft.Container(self.rabbit_info()),
                    ft.Container(self.rabbit_note(), expand=True,
                                 alignment=ft.alignment.Alignment.BOTTOM_LEFT)
                ],
                expand=True
        )
        ]

    def get_elements_for_dialog(self):
        cancel_btn = ft.TextButton('Скасувати', on_click=self._close_dialog)
        confirm_btn = ft.TextButton('Перемістити', disabled=True, on_click=self.rewrite_boxes)
        block_field = ft.TextField(max_length=4, hint_text='Блок', keyboard_type=ft.KeyboardType.NUMBER,
                                   width=120, counter=ft.Container(),
                                   on_change=lambda e: self.handle_input())
        box_field = ft.TextField(max_length=4, hint_text='Клітка', keyboard_type=ft.KeyboardType.NUMBER,
                                 width=120, counter=ft.Container(),
                                 on_change=lambda e: self.handle_input())
        result_field = ft.Text('')

        return cancel_btn, confirm_btn, block_field, box_field, result_field

    def handle_input(self):
        self.block_field.error = None
        self.box_field.error = None
        self.confirm_btn.disabled = True
        self.confirm_btn.update()
        is_error = False

        block = self.block_field.value.strip() if self.block_field.value else ''
        if not block or not block.isdigit():
            self.block_field.error = 'Введіть число'
            is_error = True
        self.block_field.update()

        box = self.box_field.value.strip() if self.box_field.value else ''
        if not box or not box.isdigit():
            self.box_field.error = 'Введіть число'
            is_error = True
        self.box_field.update()

        if not is_error:
            name_in_moved_box = self.farm.who_in_box(int(block), int(box))
            if name_in_moved_box:
                self.result_field.value = f'В клітці {block}.{box} - {name_in_moved_box}'
                self.result_field.color = ft.Colors.ORANGE
            else:
                self.result_field.value = 'Клітка порожня'
                self.result_field.color = ft.Colors.GREEN
            self.confirm_btn.disabled = False
        self.dialog_swap_box.update()

    def processing_input_for_note(self, e):
        text = e.control.value

    def result_quick_message(self, text: str, is_error: bool):
        
        color = ft.Colors.BLUE_700 if not is_error else ft.Colors.RED_700

        self.snack_bar = ft.SnackBar(content=text, bgcolor=color, duration=2000, show_close_icon=True)
        self.main_page.overlay.append(self.snack_bar)
        self.snack_bar.open = True
        self.main_page.update()

    def rewrite_boxes(self):
        name = self.rabbit.name if self.rabbit else None
        from_block = self.rabbit.block
        from_box = self.rabbit.box
        to_block = int(self.block_field.value)
        to_box = int(self.box_field.value)
        self.farm.swap_box(from_block, from_box, to_block, to_box, name)
        self._close_dialog()
        self.renew_card()

    def rabbit_info(self):
        info = ft.Text('', size=20) if self.rabbit is None else ft.Text(value=str(self.rabbit), size=20)
        return ft.Column([ft.Divider(), ft.Text('Клітка порожня' if self.rabbit is None else f'Картка: {self.rabbit.name}',
                                                  size=22, weight=ft.FontWeight.BOLD), info])

    def rabbit_note(self):
        notes = ft.Column(alignment=ft.MainAxisAlignment.END, scroll=ft.ScrollMode.AUTO)
        if self.farm.notes.get(self.rabbit.name, None):
            for x in self.farm.notes.get(self.rabbit.name):
                for date_, note in x.items():
                    item = ft.ListTile(leading=ft.Text(f'{date_}', size=18, color=ft.Colors.RED_500),
                                       title=ft.Text(f'{note}', size=15),
                                       trailing=ft.IconButton(icon=ft.Icon(ft.Icons.DELETE))
                                       )
                    notes.controls.append(item)
        else:
            notes.controls = [ft.Container()]
        return notes

    def delete_rabbit(self, nature_death=True):
        if nature_death:
            self.farm.remove_rabbit_by_death([self.rabbit.name])
        else:
            self.farm.remove_rabbit_by_culling([self.rabbit.name])
        self.main_page.views.pop()
        self.main_page.views.pop()

        self.main_page.navigate('/rabbits_list')

    def set_status(self, culling=True):
        if culling:
            report = self.farm.set_defective_single_for_app(self.rabbit.name)
            is_error = False if report == f'{self.rabbit.name} встановлена на вибраківку.' else True

            self.result_quick_message(report, is_error)
        else:
            self.farm.cancel_defective([self.rabbit.name])
        self.renew_card()

    def loose_nest(self):
        self.farm.loose_nest([self.rabbit.name])
        self.renew_card()

    def renew_card(self):
        self.controls = [
            ft.Container(self.rabbit_info())
        ]
        self.update()

    def swap_boxes(self):
        self._open_dialog()

    def _open_dialog(self):
        self.main_page.overlay.append(self.dialog_swap_box)
        self.dialog_swap_box.open = True
        self.main_page.update()

    def _close_dialog(self):
        self.dialog_swap_box.open = False
        self.dialog_swap_box.update()

    def create_notes(self):
        name = self.rabbit.name
        text = self.notes_text_field.value

        print(name, '+', text)

        self.farm.create_notes(name, text)

        self.add_remove_text_field_for_note(remove=True)

    def add_remove_text_field_for_note(self, remove=False):
        if not remove:
            self.controls = [
                ft.Column(
                    [
                        ft.Container(self.rabbit_info(), expand=True,),
                        ft.Container(self.rabbit_note(), expand=True),
                        ft.Row([self.notes_text_field,
                                ft.IconButton(icon=ft.Icon(ft.Icons.ADD),
                                              on_click=lambda e: self.create_notes())])
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    expand=True
                )
            ]
        else:
            self.controls = [
                ft.Column(
                    [
                        ft.Container(self.rabbit_info()),
                        ft.Container(self.rabbit_note())
                    ],
                    scroll=ft.ScrollMode.AUTO
                )
            ]
        self.main_page.update()


class BlocksFarm(ft.View):
    def __init__(self, main_page: ft.Page, farm: Farm):
        super().__init__(scroll = ft.ScrollMode.AUTO,route='/blocks_farm')
        self.main_page = main_page
        self.farm = farm
        self.is_visual = False
        self.open_tiles = set()
        print(f'Init _{self.open_tiles}')

        self.pop_info_colors = ft.PopupMenuButton(icon=ft.Icon(ft.Icons.INFO),
                                                  items=[ft.PopupMenuItem(ft.Row([ft.Container(border=ft.Border.all(1, ft.Colors.ON_SURFACE_VARIANT),
                                                                                               border_radius=2,
                                                                                               content=ft.Icon(ft.Icons.SQUARE, color=color)),
                                                                 ft.Text(STATUS_FOR_STR.get(status))]),
                                                                          data=status,
                                                                          on_click=lambda e: self.filter_by_color(e))
                                                         for status, color in COLOR_STATUS.items()])

        self.bottom_appbar = CustomBottomBar(self.main_page)

        self._build_page()

    def _build_page(self):

        self.switch_to_visual_blocks = ft.Row([ft.Container(ft.Icon(ft.Icons.GRID_VIEW),
                                                            on_click=self._switch_to_visual),
                                               ft.Text(5 * ' ')])
        self.switch_mode_to_list = ft.Row([ft.Container(ft.Icon(ft.Icons.LIST),
                                                        on_click=self._switch_to_list),
                                           self.pop_info_colors])

        if not self.is_visual:
            self.appbar = CustomAppBar(title='Список блоків', right_up=self.switch_to_visual_blocks)

            self.controls = [
                ft.ExpansionTile(f'Блок {block}',
                                 controls=[
                                     ft.ListTile(
                                         leading=ft.Row(
                                             controls=[
                                                 ft.Icon(ft.Icons.PETS,
                                                         color=COLOR_STATUS.get(x.status)) if x.status != 'culling' else
                                                                                        ft.Icon(ft.Icons.BLOCK, ft.Colors.RED_500),
                                                 ft.Text(x.name, size=18),ft.Text(x.str_block_box, size=14)],
                                             alignment=ft.MainAxisAlignment.START,
                                             tight=True),
                                         trailing=ft.Container(ft.Icon(ft.Icons.BOOKMARK)) if x.name in self.farm.notes else ft.Container(),
                                         data=x,
                                         on_click=lambda e, obj=x: self._to_next_screen(e, '/rabbit_card'))
                                                   for x in sorted(self.farm.rabbits.values(), key=lambda x: int(x.box)) if x.block == block],
                                 on_change=lambda e, b=block: self._handle_expended(b,e.control.expanded),
                                 expanded=block in self.open_tiles
                                 )
                             for block in sorted([x for x in set([r.block for r in self.farm.rabbits.values()])])]
        else:
            self.appbar = CustomAppBar(title='Блоки', right_up=self.switch_mode_to_list)

            self.blocks = [2, 1, 4, 3, 6, 5, 8, 7, 10, 9, 12, 11]
            list_of_box_classes = []
            for x in self.blocks:
                if x == 6:
                    list_of_box_classes.append(BlockNumberSix(self.main_page, self.farm, x))
                elif x % 2 == 0:
                    list_of_box_classes.append(RightBlock(self.main_page, self.farm, x))
                else:
                    list_of_box_classes.append(LeftBlock(self.main_page, self.farm,x))

            self.controls = [ft.GridView(controls=[x for x in list_of_box_classes],
                                         runs_count=2, spacing=10, run_spacing=50)]

    def _to_next_screen(self, e, next_screen: str):
            self.main_page.data = e.control.data
            self.main_page.navigate(next_screen)

    def _handle_expended(self, block: int, is_expanded: bool):
        if is_expanded:
            self.open_tiles.add(block)
        else:
            self.open_tiles.discard(block)
        print(self.open_tiles)

    def _switch_to_visual(self, e):
        self.is_visual = True
        self._controls_update()

    def _switch_to_list(self, e):
        self.is_visual = False
        self._controls_update()

    def _controls_update(self):
        self._build_page()
        self.update()

    def filter_by_color(self, e):
        status = e.control.data

        list_of_box_classes = []
        for x in self.blocks:
            if x == 6:
                list_of_box_classes.append(BlockNumberSix(self.main_page, self.farm, x, status))
            elif x % 2 == 0:
                list_of_box_classes.append(RightBlock(self.main_page, self.farm, x, status))
            else:
                list_of_box_classes.append(LeftBlock(self.main_page, self.farm, x, status))

        self.controls = [ft.GridView(controls=[x for x in list_of_box_classes],
                                     runs_count=2, spacing=10, run_spacing=50)]


class ThirdRoom(ft.View):
    def __init__(self, main_page: ft.Page, farm: Farm):
        super().__init__(scroll=ft.ScrollMode.AUTO, route='/third_room')
        self.main_page = main_page
        self.farm = farm

        self.expanded_tile = set()
        self.killed_boxes = set()
        self.state_dict_for_mass_kill = {}

        self.add_box_btn = ft.Container(content=ft.Icon(ft.Icons.ADD_HOME_OUTLINED), on_click=self._open_picker)
        self.mass_kill_btn = ft.Container(content=ft.Icon(ft.Icons.GROUP_REMOVE_OUTLINED),
                                          on_click=self.get_main_expansion_for_mass_kill)
        self.for_main_btn = ft.Container(content=ft.Icon(ft.Icons.REMOVE_RED_EYE_OUTLINED),
                                         on_click=self.get_main_expansion_for_main)

        self.appbar = CustomAppBar(title='Відгодівля', right_up=ft.Row([self.add_box_btn, self.mass_kill_btn,ft.Text(5*' ')]))
        self.bottom_appbar = CustomBottomBar(self.main_page)

        self.mass_kill_approve = ft.Container(content=ft.Text('Провести\n  забій', size=10),
                                           border=ft.Border.all(color=ft.Colors.RED_500, width=3),
                                           border_radius=3, bgcolor=ft.Colors.RED_100,
                                              on_click=self.approving_mass_kill)
        self.cancel_btn, self.final_add_btn, self.block_field, self.box_field, self.quantity_field, self.status_menu = (
            self.get_elements_for_dialog())

        self.add_box_dialog = ft.AlertDialog(title = ft.Text('Відгодівля'))
        self.main_page.overlay.append(self.add_box_dialog)

        self.date_picker = ft.DatePicker(help_text='Дата народження групи', cancel_text='Скасувати',
                                         confirm_text='Ввести дані',
                                         on_change=self._open_dialog)
        self.main_page.overlay.append(self.date_picker)

        self.controls = [
            ft.ExpansionTile(
                title=ft.Row([ft.Icon(ft.Icons.GRID_VIEW),ft.Text(f'Блок {block}')]),
                    on_change=lambda e, b=block: self._handle_expended(b,e.control.expanded),
                    expanded=block in self.expanded_tile,
                    subtitle=ft.Text(self.get_info_for_blocks(block)),
                    controls=[self.get_tile_for_expansion(x, False)
                                                    for x in
                                                    sorted(self.farm.third_room.values(), key=lambda x: int(x.box)) if
                                                    x.block == block])
                         for block in sorted([x for x in set([r.block for r in self.farm.third_room.values()]
                                                             )
                                              ]
                                             )
        ]

    def _to_next_screen(self, e, next_screen: str):
        self.main_page.data = e.control.data
        self.main_page.navigate(next_screen)

    def _actions_with_box(self, e):
        box_obj = e.control.data
        plus = ft.Container(ft.Icon(ft.Icons.PLUS_ONE, color=ft.Colors.BLUE_500),
                            on_click=lambda e: self.change_quantity(box_obj, True))
        minus = ft.Container(ft.Icon(ft.Icons.EXPOSURE_MINUS_1, color=ft.Colors.RED_500),
                             on_click=lambda e: self.change_quantity(box_obj, False))
        delete = ft.Container(ft.Icon(ft.Icons.DELETE_FOREVER))
        back = ft.Container(ft.Icon(ft.Icons.ARROW_BACK_IOS), on_click=lambda e: _go_back(e))
        close = ft.Container(ft.Icon(ft.Icons.CLOSE), on_click=self.change_bottom_appbar_to_started)
        self.bottom_appbar.content = ft.Row([plus,minus,delete,close,back], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        self.bottom_appbar.update()

    def _open_dialog(self):
        self._restore_dialog()
        self.add_box_dialog.open = True
        self.main_page.update()

    def _close_dialog(self):
        print(self.add_box_dialog.open)
        self.add_box_dialog.open = False
        print(self.add_box_dialog.open)
        #self.main_page.overlay.remove(self.add_box_dialog)
        self.main_page.update()

    def _handle_input_for_mass_kill(self, box_obj: Box, element_name: str, e):
        e.control.error = None
        value = e.control.value

        if value and not value.strip().isdigit():

            e.control.error = 'Введіть число'
            is_error = True
            e.control.update()


        self.state_dict_for_mass_kill.setdefault(f'{box_obj.block}.{box_obj.box}',{})[element_name] = e.control.value

    def _handle_input_for_add(self, e):
        self.block_field.error = None
        self.box_field.error = None
        self.quantity_field.error = None
        is_error = False

        if not self.block_field.value or not self.block_field.value.strip().isdigit():
            self.block_field.error = 'помилка'
            is_error = True
            self.block_field.update()
        else:
            self.block_field.update()

        if not self.box_field.value or not self.box_field.value.strip().isdigit():
            self.box_field.error = 'помилка'
            is_error = True
            self.box_field.update()
        else:
            self.box_field.update()

        if not self.quantity_field.value or not self.quantity_field.value.strip().isdigit():
            self.quantity_field.error = 'помилка'
            is_error = True
            self.quantity_field.update()
        else:
            self.quantity_field.update()

        if not self.status_menu.value:
            is_error = True


        self.final_add_btn.disabled = False if not is_error else True
        self.final_add_btn.update()

    def _open_picker(self):

        self.date_picker.open = True
        self.main_page.update()

    def get_elements_for_dialog(self):
        cancel_btn = ft.TextButton('Скасувати', on_click=self._close_dialog)
        final_add_btn = ft.TextButton('Додати', on_click=self.final_create_box, disabled=True)
        block_field = ft.TextField(max_length=3, label='Блок', keyboard_type=ft.KeyboardType.NUMBER,
                                   width=130, counter=ft.Container(),
                                   on_change=lambda e: self._handle_input_for_add(e))
        box_field = ft.TextField(max_length=3, label='Клітка', keyboard_type=ft.KeyboardType.NUMBER,
                                 width=130, counter=ft.Container(),
                                 on_change=lambda e: self._handle_input_for_add(e))
        quantity_field = ft.TextField(max_length=2, label='Кількість', keyboard_type=ft.KeyboardType.NUMBER,
                                   width=130, counter=ft.Container(),
                                   on_change=lambda e: self._handle_input_for_add(e))
        status_menu = ft.Dropdown(width=130, label='Статус',on_select=lambda e: self._handle_input_for_add(e),
                                  options=[ft.DropdownOption(key=""),
                                           ft.DropdownOption(key="м'ясо"),
                                           ft.DropdownOption(key="ремонт"),
                                           ft.DropdownOption(key="догодівля")])

        return cancel_btn,final_add_btn,block_field,box_field,quantity_field,status_menu

    def get_tile_for_expansion(self, box_obj: Box, mass_kill: bool):
        if not mass_kill:
            return ft.ListTile(leading=ft.Row(controls=[ft.Icon(ft.Icons.ACCOUNT_BOX),
                                                        ft.Text(f'{box_obj.block}.{box_obj.box}', size=18)],
                                              alignment=ft.MainAxisAlignment.START, tight=True),
                               title=ft.Row(controls=[ft.Divider(),
                                                      ft.Icon(ft.Icons.CALENDAR_MONTH),
                                                        ft.Text(f'{box_obj.box_age} дн.', size=12),
                                                      ft.Divider(),
                                                      ft.Icon(ft.Icons.NOT_INTERESTED, color=ft.Colors.RED_300),
                                                      ft.Text(f'{box_obj.kill_date}', size=12)],
                                              alignment=ft.MainAxisAlignment.START, tight=True),
                               trailing=ft.Row(controls=[ft.Icon(ft.Icons.CRUELTY_FREE, color=ft.Colors.BLUE_500),
                                                        ft.Text(f'{box_obj.quantity}', size=18)],
                                              alignment=ft.MainAxisAlignment.START, tight=True),
                               on_long_press=lambda e: self._actions_with_box(e), data=box_obj,
                               on_click=lambda e: self._to_next_screen(e, '/box_info'))
        else:
            return ft.ListTile(leading=ft.Row(controls=[ft.Icon(ft.Icons.ACCOUNT_BOX),
                                                        ft.Text(f'{box_obj.block}.{box_obj.box}', size=18)],
                                              alignment=ft.MainAxisAlignment.START, tight=True),
                               title=ft.Row([ft.TextField(max_length=2, label='Кількість', keyboard_type=ft.KeyboardType.NUMBER,
                                                          width=130, counter=ft.Container(),
                                                          on_change=lambda e, b=box_obj: self._handle_input_for_mass_kill(b,'quantity',e)),
                                             ft.Dropdown(width=130, label='Статус',
                                                         on_select=lambda e, b=box_obj: self._handle_input_for_mass_kill(b,'status',e),
                                                         options=[ft.DropdownOption(key=""),
                                                                  ft.DropdownOption(key="м'ясо"),
                                                                  ft.DropdownOption(key="ремонт"),
                                                                  ft.DropdownOption(key="догодівля")]),
                                             ft.Checkbox(label="OK!", data=box_obj, label_position=ft.LabelPosition.RIGHT,
                                                         on_change=lambda e: self._for_checkboxes(e))])
                               )

    def final_create_box(self):
        birth = self.date_picker.value + timedelta(hours=3)
        block = int(self.block_field.value)
        box = int(self.box_field.value)
        quantity = int(self.quantity_field.value)
        status = self.status_menu.value
        created = self.farm.create_box_in_third_room(block,box,quantity,birth.date(),status)
        if created:
            self._changed_dialog()

    def get_main_expansion_for_mass_kill(self):
        self.controls = [ft.ExpansionTile(title=ft.Row([ft.Icon(ft.Icons.GRID_VIEW), ft.Text(f'Блок {block}')]),
                                          on_change=lambda e, b=block: self._handle_expended(b, e.control.expanded),
                                          expanded=block in self.expanded_tile,
                                          subtitle=ft.Text(self.get_info_for_blocks(block)),
                                          controls=[self.get_tile_for_expansion(x, True)
                                                    for x in
                                                    sorted(self.farm.third_room.values(), key=lambda x: int(x.box)) if
                                                    x.block == block])
                         for block in sorted([x for x in set([r.block for r in self.farm.third_room.values()])])]
        self.appbar.actions = [ft.Row([self.for_main_btn,self.mass_kill_approve,ft.Text(5*' ')])]
        self.main_page.update()

    def get_main_expansion_for_main(self):
        self.controls = [ft.ExpansionTile(title=ft.Row([ft.Icon(ft.Icons.GRID_VIEW),ft.Text(f'Блок {block}')]),
                                          on_change=lambda e, b=block: self._handle_expended(b,e.control.expanded),
                                          expanded=block in self.expanded_tile,
                                          subtitle=ft.Text(self.get_info_for_blocks(block)),
                                          controls=[self.get_tile_for_expansion(x, False)
                                                    for x in
                                                    sorted(self.farm.third_room.values(), key=lambda x: int(x.box)) if
                                                    x.block == block])
                         for block in sorted([x for x in set([r.block for r in self.farm.third_room.values()])])]
        self.appbar.actions = [ft.Row([self.add_box_btn, self.mass_kill_btn,ft.Text(5*' ')])]
        self.main_page.update()

    def _changed_dialog(self):
        self.add_box_dialog.content = ft.Text(f'Група {(self.date_picker.value+ timedelta(hours=3)).date().strftime(DATE_FORMAT)}\n'
                                              f'Клітка {self.block_field.value}.{self.box_field.value}\n'
                                              f'Кількість {self.quantity_field.value}, статус "{self.status_menu.value}"\n'
                                              f'CТВОРЕНО!')
        self.add_box_dialog.actions = [ft.TextButton('Нова група', on_click=self._open_picker),
                                       ft.TextButton('Нова клітка', on_click=self._open_dialog),
                                       ft.TextButton('Завершити', on_click=self._close_dialog),]
        self.add_box_dialog.update()

    def _restore_dialog(self):
        self.add_box_dialog.content = ft.Text('Введіть дані')
        self.add_box_dialog.actions = [ft.Row([self.block_field, self.box_field],
                                              alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                       ft.Divider(),
                                       ft.Row([self.quantity_field, self.status_menu],
                                              alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                       ft.Row([self.cancel_btn, self.final_add_btn],
                                              alignment=ft.MainAxisAlignment.SPACE_BETWEEN)]
        self.add_box_dialog.update()


        self.main_page.update()

    def _controls_update(self):
        self.controls = [ft.ExpansionTile(title=ft.Text(f'Блок {block}'),
                                          subtitle=ft.Text(self.get_info_for_blocks(block)),
                                          on_change=lambda e, b=block: self._handle_expended(b, e.control.expanded),
                                          expanded=block in self.expanded_tile,
                                          controls=[self.get_tile_for_expansion(x, False)
                                                    for x in
                                                    sorted(self.farm.third_room.values(), key=lambda x: int(x.box)) if
                                                    x.block == block])
                         for block in sorted([x for x in set([r.block for r in self.farm.third_room.values()])])]

        self.update()

    def _handle_expended(self, block_num, is_expended):
        self.expanded_tile.add(block_num) if is_expended else self.expanded_tile.discard(block_num)

    def _for_checkboxes(self, e):
        box_obj = e.control.data
        self.killed_boxes.add((box_obj.block,box_obj.box)) \
            if e.control.value else self.killed_boxes.discard((box_obj.block,box_obj.box))

    def change_bottom_appbar_to_started(self):
        back = ft.Container(ft.Icon(ft.Icons.ARROW_BACK_IOS), on_click=lambda e: _go_back(e))
        self.bottom_appbar.content = ft.Row([ft.Container(),back], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        self.bottom_appbar.update()

    def get_info_for_blocks(self, num_block):
        data = preparing_data_for_blocks_in_third_room(num_block, self.farm)
        report = []

        for age, quantity in data.items():
            report.append(f'{age} дн. -- {sum(quantity)} шт.')
        return '\n'.join([x for x in report])

    def change_quantity(self, box_obj: Box, increase: bool):
        if increase:
            box_obj.quantity += 1
        else:
            if box_obj.quantity >= 1:
                box_obj.quantity -= 1
            else:
                box_obj.quantity = 0
        self._controls_update()

    def approving_mass_kill(self):
        for tuple_ in self.killed_boxes:
            block, box = tuple_
            key = f'{block}.{box}'
            quantity = int(self.state_dict_for_mass_kill.get(key)['quantity'])
            status = self.state_dict_for_mass_kill.get(key)['status']
            if quantity and status:
                res = self.farm.mass_kill(block, box, quantity, status)

                text = ft.Text('Успішно проведено') if res else ft.Text('Щось пішло не так...')
                color = ft.Colors.BLUE_700 if res else ft.Colors.RED_700
                snack_bar = ft.SnackBar(content=text, bgcolor=color, duration=2000, show_close_icon=True)
                self.main_page.overlay.append(snack_bar)
                snack_bar.open = True
                self.main_page.update()


class BoxInfo(ft.View):
    def __init__(self, main_page: ft.Page, farm: Farm):
        super().__init__(route='/box_info')
        self.main_page = main_page
        self.farm = farm

        receive_data = main_page.data
        self.box_obj = receive_data if isinstance(receive_data, Box) else None
        self.appbar = CustomAppBar(title=f'Клітка {self.box_obj.block}.{self.box_obj.box}')
        self.bottom_appbar = CustomBottomBar(self.main_page)

        self.controls = [ft.Text(str(self.box_obj))]

    def _to_next_screen(self, e, next_screen: str):
        self.main_page.data = e.control.data
        self.main_page.navigate(next_screen)


class FarmInfo(ft.View):
    def __init__(self, main_page: ft.Page, farm: Farm):
        super().__init__(route='/farm_info')
        self.main_page = main_page
        self.farm = farm

        self.appbar = CustomAppBar(title='Інформація')
        self.bottom_appbar = CustomBottomBar(self.main_page)

        self.controls = [self.get_average_age(), self.get_quantity_of_farm(), self.get_farm_by_status()]

    def get_average_age(self):

        return ft.ExpansionTile(title=ft.Row([ft.Icon(ft.Icons.CALENDAR_MONTH), ft.Text(f'Середній вік ферми')]),
                                          controls=[ft.ListTile(
                                              ft.Row([ft.Icon(ft.Icons.FEMALE, color=ft.Colors.PINK_500),
                                                      ft.Text(f'Cамиці - {average_age_farm(self.farm, "female")} дн.')])),
                                              ft.ListTile(
                                                  ft.Row([ft.Icon(ft.Icons.MALE, color=ft.Colors.BLUE_500),
                                                          ft.Text(f'Cамці - {average_age_farm(self.farm, "male")} дн.')]))])

    def get_quantity_of_farm(self):

        female = len([x for x in self.farm.rabbits.values() if x.sex == 'female'])
        male = len([x for x in self.farm.rabbits.values() if x.sex == 'male'])
        feeding = sum([x.quantity for x in self.farm.third_room.values() if x.quantity])

        return ft.ExpansionTile(title=ft.Row([ft.Icon(ft.Icons.ARTICLE_OUTLINED), ft.Text(f'Кількість ферми')]),
                                controls=[ft.ListTile(
                                    ft.Row([ft.Icon(ft.Icons.FEMALE, color=ft.Colors.PINK_500),
                                            ft.Text(f'Самиці - {female} шт.')])),
                                    ft.ListTile(
                                        ft.Row([ft.Icon(ft.Icons.MALE, color=ft.Colors.BLUE_500),
                                            ft.Text(f'Самці - {male} шт.')])),
                                    ft.ListTile(
                                        ft.Row([ft.Icon(ft.Icons.CRUELTY_FREE, color=ft.Colors.GREY_500),
                                                ft.Text(f'Відгодівля - {feeding} шт.')])),
                                ])

    def get_farm_by_status(self):

        work_group = len([x for x in self.farm.rabbits.values() if x.sex == 'female' and x.status != 'culling'])
        culling = len([x for x in self.farm.rabbits.values() if x.status == 'culling'])
        new = len([x for x in self.farm.rabbits.values() if x.status == 'new'])
        mother = len([x for x in self.farm.rabbits.values() if x.status == 'mother'])
        pregnant = len([x for x in self.farm.rabbits.values() if x.status == 'waiting_for_kindling'])
        mated = len([x for x in self.farm.rabbits.values() if x.status and 'mated' in x.status])

        return ft.ExpansionTile(
            title=ft.Row([ft.Icon(ft.Icons.WORKSPACE_PREMIUM_OUTLINED),ft.Text('Статус ферми')]),
            controls=[ft.ExpansionTile(
                title=ft.Row([ft.Icon(ft.Icons.ASSIGNMENT_TURNED_IN_OUTLINED),
                              ft.Text(f'Робоче стадо - {work_group} шт.')]),
                controls=[
                    ft.ListTile(
                        ft.Row([ft.Icon(ft.Icons.NEW_RELEASES_OUTLINED, color=ft.Colors.GREEN_500),
                                ft.Text(f'Молодь {new} шт.')])
                    ),
                    ft.ListTile(
                        ft.Row([ft.Icon(ft.Icons.CHILD_FRIENDLY_OUTLINED),
                                ft.Text(f'Матері {mother} шт.')])
                    ),
                    ft.ListTile(
                        ft.Row([ft.Icon(ft.Icons.CELEBRATION_OUTLINED),
                                ft.Text(f'Чекають окролу {pregnant} шт.')])
                    ),
                    ft.ListTile(
                        ft.Row([ft.Icon(ft.Icons.QUESTION_MARK_OUTLINED),
                                ft.Text(f'Чекають пальпацію {mated} шт.')])
                    ),
                ]
            ),
            ft.ListTile(
                ft.Row([ft.Icon(ft.Icons.DELETE_OUTLINE, color=ft.Colors.RED_500),
                        ft.Text(f'Вибраківка {culling} шт.')]
                    )
                )
                      ]
        )


class ProcessFarm(ft.View):
    def __init__(self, main_page: ft.Page, farm: Farm):
        super().__init__(route='/process_farm')
        self.main_page = main_page
        self.farm = farm

        self.appbar = CustomAppBar(title='Процеси ферми')
        self.bottom_appbar = CustomBottomBar(self.main_page)

        self.date_picker = ft.DatePicker(help_text='Яка дата вас цікавить?', cancel_text='Скасувати',
                                         confirm_text='Подивитися\n   процеси',
                                         on_change=lambda e: self._to_next_screen(e, '/show_process', False))

        self.controls = [ft.ListTile(title=ft.Row([ft.Icon(ft.Icons.ACCESS_ALARM_OUTLINED),ft.Text('Заплановані роботи')]),
                                     on_click=lambda e: self._open_picker()),
                         ft.ListTile(title=ft.Row([ft.Icon(ft.Icons.ACCESS_TIME_OUTLINED),ft.Text('Роботи на сьогодні')]),
                                     on_click=lambda e: self._to_next_screen(e, '/show_process', True)),
                         ft.ListTile(title=ft.Row([ft.Icon(ft.Icons.DONE),ft.Text('Проведені роботи')]))]

    def _to_next_screen(self, e, next_screen: str, today:bool):
        if not today:
            self.main_page.data = (e.control.value + timedelta(hours=3)).date()
        else:
            self.main_page.data = date.today()
        self.main_page.navigate(next_screen)


    def _open_picker(self):
        if self.date_picker in self.main_page.overlay:
            self.main_page.overlay.remove(self.date_picker)
        self.main_page.overlay.append(self.date_picker)
        self.date_picker.open = True
        self.main_page.update()


class ShowProcess(ft.View):
    def __init__(self, main_page: ft.Page, farm: Farm):
        super().__init__(route='/show_process', scroll=ft.ScrollMode.AUTO)
        self.main_page = main_page
        print(f'main_page.data = {main_page.data}')
        main_page.data = main_page.data if main_page.data else date.today()
        self.farm = farm

        self.need_date = self.main_page.data
        self.text_for_title = ft.Text(f'Роботи на {self.need_date.strftime(DATE_FORMAT)}.')

        self.elements_for_processes = {}
        self.data_for_processes = {}
        self.open_tiles = set()

        self.appbar = CustomAppBar(left_up=ft.IconButton(icon=ft.Icon(ft.Icons.ARROW_BACK_IOS),
                                                         on_click=lambda e: self.turn_process_by_date(False)),
                                   title=self.text_for_title,
                                   right_up=ft.IconButton(icon=ft.Icon(ft.Icons.ARROW_FORWARD_IOS),
                                                          on_click=lambda e: self.turn_process_by_date(True))
                                   )
        self.bottom_appbar = CustomBottomBar(self.main_page)
        self.date_picker = ft.DatePicker(help_text='Оберіть нову дату', cancel_text='Скасувати',
                                         confirm_text='Змінити\n   дату',
                                         on_change=lambda e:self.change_process_data(e))

        self.controls = self.get_controls()

    def get_controls(self) -> list[ft.BaseControl]:
        need_data: dict|None = get_planned_work(self.farm, self.need_date)
        print(need_data)
        if need_data:
            return [ft.ExpansionTile(title=ft.Row(controls=[ft.TextButton(ft.Text(f'{STATUS_WORK.get(process).capitalize()} '
                                                                                  f'({len(need_data.get(process))})'),
                                                                          on_click=lambda e, p=process: self.finally_get_process(p)),
                                                            ft.Row([
                                                                ft.TextButton(ft.Text('Змінити дату',color=ft.Colors.RED_500),
                                                                          on_click=lambda e, t=process: self.open_picker_with_task_in_data(e,t)),
                                                            ft.Text(10*' ')])],
                                                  alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                     controls=[
                                         ft.Container(content=ft.Row([ft.Icon(ft.Icons.PETS,
                                                                              color=COLOR_STATUS.get(self.farm.rabbits[x].status, None))
                                                                         if process != 'mass_kill' else ft.Icon(ft.Icons.GRID_VIEW),
                                                                      ft.Text(value=f'{x} -- {self.farm.rabbits[x].str_block_box}')
                                                                      if process != 'mass_kill'
                                                                      else ft.Text(f'{x} -- {self.farm.third_room[x].quantity} шт.'),
                                                                      self.get_trailing_tile_by_process(process, x)],
                                                                     alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                                      expand=True, data=self.farm.rabbits[x] if process != 'mass_kill' else self.farm.third_room[x],
                                                      on_click=lambda e: self._to_next_screen(e, '/rabbit_card'))
                                         for x in names
                                     ],
                                     on_change=lambda e: self._is_open(e, process),
                                     expanded=process in self.open_tiles) for process, names in need_data.items()]
        else:
            return [ft.Container()]

    def _is_open(self, e, process):
        self.open_tiles.add(process) if e.data else self.open_tiles.discard(process)

    def _to_next_screen(self, e, next_screen: str):
            self.main_page.data = e.control.data
            self.main_page.navigate(next_screen)

    def quick_message(self, text: str, is_error: bool):

        color = ft.Colors.BLUE_700 if not is_error else ft.Colors.RED_700

        self.snack_bar = ft.SnackBar(content=text, bgcolor=color, duration=2000, show_close_icon=True)
        self.main_page.overlay.append(self.snack_bar)
        self.snack_bar.open = True
        self.main_page.update()

    def turn_process_by_date(self, forward: bool):

        self.need_date += timedelta(days=1) if forward else timedelta(days=-1)
        self.text_for_title.value = f'Роботи на {self.need_date.strftime(DATE_FORMAT)}.'
        self.text_for_title.update()
        self.appbar.update()
        self._renew_screen()

    def change_process_data(self, e):
        process = e.control.data
        old_date = self.need_date
        new_date = (self.date_picker.value + timedelta(hours=3)).date()

        if process and old_date and new_date:
            result = self.farm.change_date_for_process(process, old_date, new_date)

            text = ft.Text('Успішно поміняно') if result else ft.Text('Помилка перенесення')
            color = ft.Colors.BLUE_700 if result else ft.Colors.RED_700

            self.snack_bar = ft.SnackBar(content=text, bgcolor=color, duration=2000, show_close_icon=True)
            self.main_page.overlay.append(self.snack_bar)
            self.snack_bar.open = True
            self.main_page.update()

        self._renew_screen()

    def _renew_screen(self):
        self.controls = self.get_controls()
        self.main_page.update()

    def _open_picker(self):
        if self.date_picker in self.main_page.overlay:
            self.main_page.overlay.remove(self.date_picker)
        self.main_page.overlay.append(self.date_picker)
        self.date_picker.open = True
        self.main_page.update()

    def _handle_checkbox_for_process(self, e: ft.Event[ft.Checkbox], process: str, name: str):
        process_key = process
        values_for_checkboxes = set(get_value_for_checkboxes(process_key))
        checked = e.control.value

        if checked:
            values_for_checkboxes.add(name)
        else:
            values_for_checkboxes.discard(name)

        save_value_for_checkboxes(process_key, list(values_for_checkboxes))

    def result_quick_message(self, text: str, is_error: bool):

        color = ft.Colors.BLUE_700 if not is_error else ft.Colors.RED_700

        self.snack_bar = ft.SnackBar(content=text, bgcolor=color, duration=2000, show_close_icon=True)
        self.main_page.overlay.append(self.snack_bar)
        self.snack_bar.open = True
        self.main_page.update()

    def open_picker_with_task_in_data(self,e, task):
        self.date_picker.data = task
        self._open_picker()

    def get_trailing_tile_by_process(self, process, name):
        trailing = None
        match process:
            case 'mate':
                mate_checkbox, on_fact_father, block = self.get_elements_for_mate(name)
                self.elements_for_processes.setdefault(name, {})['mate_on_fact_father'] = on_fact_father
                trailing = ft.Row([on_fact_father, block, mate_checkbox])
            case 'palpation':
                res_palpation, block = self.get_elements_for_palpation(name)
                self.elements_for_processes.setdefault(name, {})['palpation_result'] = res_palpation
                trailing = ft.Row([res_palpation, block])
            case 'install_nest' | 'open_nest' | 'vaccination_nest' | 'prepare_nest':
                checkbox = self.get_checkboxes_for_simple_operations(process, name)
                trailing = checkbox
            case 'kindling':
                block, alive, dead, formed = self.get_elements_for_kindling(name)
                self.elements_for_processes.setdefault(name, {})['alive'] = alive
                self.elements_for_processes.setdefault(name, {})['dead'] = dead
                self.elements_for_processes.setdefault(name, {})['formed'] = formed
                trailing = ft.Row([alive, dead, formed, block])
            case 'remove_nest':
                checkbox, quantity_field = self.get_elements_for_remove_nest(name)
                self.elements_for_processes.setdefault(name, {})['remove_nest_quantity'] = quantity_field
                trailing = ft.Row([quantity_field, checkbox])
            case 'resettle':
                checkbox, quantity_field = self.get_elements_for_resettle(name)
                self.elements_for_processes.setdefault(name, {})['resettle_quantity'] = quantity_field
                trailing = ft.Row([quantity_field, checkbox])
            case 'swap_box':
                new_block, new_box, block = self.get_elements_for_swap_box(name)
                trailing = ft.Row([new_block, new_box, block])
                self.elements_for_processes.setdefault(name, {})['swap_box_new_block'] = new_block
                self.elements_for_processes.setdefault(name, {})['swap_box_new_box'] = new_box
            case _:
                trailing = ft.Text('Ще не зроблено')

        return trailing

    def get_content_for_controls(self, process: str, name: str):
        main_cont = ft.Container(
            ft.Row(
                [
                    ft.Container(
                        ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Icon(ft.Icons.PETS, color=COLOR_STATUS.get(self.farm.rabbits[name].status,
                                                                                      None)) if process != 'mass_kill' else ft.Icon(
                                            ft.Icons.GRID_VIEW),
                                        ft.Text(
                                            value=f'{name} -- {self.farm.rabbits[name].str_block_box}') if process != 'mass_kill' else ft.Text(
                                            f'{name} -- {self.farm.third_room[name].quantity} шт.')
                                    ]
                                )
                            ]
                        )
                    )
                ]
            )
        )

    def get_elements_for_mate(self, name):

        process_key = 'mate'
        values_for_checkboxes = set(get_value_for_checkboxes(process_key))

        mate_checkbox = ft.Checkbox(label='OK', data=name, value=name in values_for_checkboxes,
                                    label_position=ft.LabelPosition.RIGHT,
                                    on_change=lambda e, process='mate': self._handle_checkbox_for_process(e, process, name))
        on_fact_father = ft.Dropdown(width=110, label='Факт', dense=True,
                                     on_select=lambda e, state='on_fact': self._handle_processing_mate(e, state, name),
                                      options=[ft.DropdownOption(key="X"),
                                               ft.DropdownOption(key="Y"),
                                               ft.DropdownOption(key="Z"),
                                               ft.DropdownOption(key="*"),
                                               ft.DropdownOption(key="--")])

        block = ft.IconButton(icon=ft.Icon(ft.Icons.LOCK_OPEN), on_click=lambda e: self.blocking_unblocking_drop_menu_mate(e, name))


        return mate_checkbox, on_fact_father, block

    def get_elements_for_palpation(self, name):
        palpation_result = ft.Dropdown(width=110, label='Рез.', dense=True,
                                     on_select=lambda e: self._handle_processing_palpation(e, name),
                                     options=[ft.DropdownOption(key="+"),
                                              ft.DropdownOption(key="-"),
                                              ft.DropdownOption(key="?"),
                                              ft.DropdownOption(key="")])

        block = ft.IconButton(icon=ft.Icon(ft.Icons.LOCK_OPEN),
                              on_click=lambda e: self.blocking_unblocking_drop_menu_palpation(e, name))

        return palpation_result, block

    def get_elements_for_kindling(self, name):

        block = ft.IconButton(icon=ft.Icon(ft.Icons.LOCK_OPEN),
                              on_click=lambda e: self.blocking_unblocking_drop_menu_kindling(e, name))

        alive = ft.TextField(label="🐇",bgcolor=ft.Colors.BLUE_500, width=50, keyboard_type=ft.KeyboardType.NUMBER,)
        dead = ft.TextField(label="☠️",bgcolor=ft.Colors.RED_500, width=50,keyboard_type=ft.KeyboardType.NUMBER,)
        formed = ft.TextField(label="🏡",width=50,keyboard_type=ft.KeyboardType.NUMBER,)


        return block, alive, dead, formed

    def get_elements_for_remove_nest(self, name):

        quantity_field = ft.TextField(label='Кількість', width=100, keyboard_type=ft.KeyboardType.NUMBER,
                                      on_change=lambda e: self._handle_processing_for_remove_nest(e, name, True))
        checkbox = ft.Checkbox(label='OK', data=name, value=name in get_value_for_checkboxes('remove_nest'),
                               on_change=lambda e, process='remove_nest': self._handle_checkbox_for_process(e, process, name))
        return checkbox, quantity_field

    def get_elements_for_resettle(self, name):
        quantity_field = ft.TextField(label='Кількість', width=100, keyboard_type=ft.KeyboardType.NUMBER,
                                      on_change=lambda e: self._handle_processing_for_remove_nest(e, name, False))
        checkbox = ft.Checkbox(label='OK', data=name, value=name in get_value_for_checkboxes('resettle'),
                               on_change=lambda e, process='resettle': self._handle_checkbox_for_process(e, process, name))
        return checkbox, quantity_field

    def get_elements_for_swap_box(self, name):
        new_block = ft.TextField(label='Новий блок', width=100, keyboard_type=ft.KeyboardType.NUMBER,
                                      on_change=lambda e: self.color_field_for_swap_box(e))
        new_box = ft.TextField(label='Нова клітка', width=100, keyboard_type=ft.KeyboardType.NUMBER,
                                     on_change=lambda e: self.color_field_for_swap_box(e))
        block = ft.IconButton(icon=ft.Icon(ft.Icons.LOCK_OPEN),
                              on_click=lambda e: self.blocking_unblocking_drop_menu_swap_box(e, name))

        return new_block, new_box, block

    def get_checkboxes_for_simple_operations(self, process, name):
        return ft.Checkbox(label='OK', data=name, value=name in get_value_for_checkboxes(process),
                           on_change=lambda e, process=process: self._handle_checkbox_for_process(e, process, name))

    def _handle_processing_for_remove_nest(self, e, name, stay_in_box: bool):
        field = e.control
        field.filled = True
        if field.value and field.value.strip().isdigit():
            field.fill_color = ft.Colors.GREEN_500
            if stay_in_box:
                self.data_for_processes.setdefault('remove_nest', {})[name] = field.value
            else:
                self.data_for_processes.setdefault('resettle', {})[name] = field.value
        elif field.value and not field.value.strip().isdigit():
            field.fill_color = ft.Colors.RED_500
        else:
            field.fill_color = ft.Colors.YELLOW_300
        field.update()

    def _handle_processing_mate(self, e, state: str, name: str):
        field = e.control
        field.filled = True
        if field.value in ['X','Y','Z']:
            field.fill_color = ft.Colors.GREEN_500
        elif field.value == '--':
            field.fill_color = ft.Colors.RED_500
        elif field.value == '*':
            field.fill_color = ft.Colors.YELLOW_300
        field.update()

        self.data_for_processes.setdefault('mate', {}).setdefault(name, {})[state] = field.value

    def _handle_processing_palpation(self,e, name):
        field = e.control
        field.filled = True
        if field.value == '+':
            field.fill_color = ft.Colors.GREEN_500
        elif field.value == '-':
            field.fill_color = ft.Colors.RED_500
        elif field.value == '?':
            field.fill_color = ft.Colors.YELLOW_300
        field.update()

        self.data_for_processes.setdefault('palpation', {})[name] = field.value

    def color_field_for_swap_box(self, e):
        field = e.control
        field.filled = True
        if field.value and field.value.strip().isdigit():
            field.fill_color = ft.Colors.GREEN_500
        elif field.value and not field.value.strip().isdigit():
            field.fill_color = ft.Colors.RED_500
        else:
            field.fill_color = ft.Colors.YELLOW_300
        field.update()

    def blocking_unblocking_drop_menu_mate(self, e, name):

        block = e.control
        on_fact_father = self.elements_for_processes.get(name, None).get('mate_on_fact_father', None)

        if not on_fact_father.disabled:
            block.icon = ft.Icon(ft.Icons.LOCK)
            if  on_fact_father:
                on_fact_father.disabled = True
                on_fact_father.update()
            block.update()
        else:
            block.icon = ft.Icon(ft.Icons.LOCK_OPEN)
            if on_fact_father:
                on_fact_father.disabled = False
                on_fact_father.update()
            block.update()

    def blocking_unblocking_drop_menu_palpation(self, e, name):
        block = e.control
        palpation_result = self.elements_for_processes.get(name, None).get('palpation_result', None)

        if not palpation_result.disabled:
            block.icon = ft.Icon(ft.Icons.LOCK)
            if palpation_result:
                palpation_result.disabled = True
                palpation_result.update()

        else:
            block.icon = ft.Icon(ft.Icons.LOCK_OPEN)
            if palpation_result:
                palpation_result.disabled = False
                palpation_result.update()

        block.update()

    def blocking_unblocking_drop_menu_kindling(self, e, name):
        block = e.control
        alive = self.elements_for_processes.get(name, None).get('alive', None)
        dead = self.elements_for_processes.get(name, None).get('dead', None)
        formed = self.elements_for_processes.get(name, None).get('formed', None)

        if alive.disabled and dead.disabled and formed.disabled:
            block.icon = ft.Icon(ft.Icons.LOCK_OPEN)
            if alive:
                alive.disabled = False
                alive.update()
            if dead:
                dead.disabled = False
                dead.update()
            if formed:
                formed.disabled = False
                formed.update()
        else:
            val_alive = alive.value.strip() or '0'
            val_dead = dead.value.strip() or '0'
            val_formed = formed.value.strip() or '0'

            if val_alive.isdigit() and val_dead.isdigit() and val_formed.isdigit():
                block.icon = ft.Icon(ft.Icons.LOCK)
                if alive:
                    self.data_for_processes.setdefault('kindling', {}).setdefault(name, {})['alive'] = val_alive
                    alive.disabled = True
                    alive.update()
                if dead:
                    self.data_for_processes.setdefault('kindling', {}).setdefault(name, {})['dead'] = dead.value.strip() or '0'
                    dead.disabled = True
                    dead.update()
                if formed:
                    self.data_for_processes.setdefault('kindling', {}).setdefault(name, {})['formed'] = formed.value.strip() or '0'
                    formed.disabled = True
                    formed.update()
            else:
                self.result_quick_message('Перевірте дані', True)
            print(self.data_for_processes)

        block.update()

    def blocking_unblocking_drop_menu_swap_box(self, e, name):
        block = e.control
        new_block = self.elements_for_processes.get(name, None).get('swap_box_new_block', None)
        new_box = self.elements_for_processes.get(name, None).get('swap_box_new_box', None)
        fields = [new_block, new_box]

        if new_block.disabled and new_box.disabled:
            block.icon = ft.Icon(ft.Icons.LOCK_OPEN)
            if new_block:
                new_block.disabled = False
                new_block.update()
            if new_box:
                new_box.disabled = False
                new_box.update()
        else:
            if all(x.value and x.value.strip().isdigit() for x in fields):
                self.data_for_processes.setdefault('swap_box', {}).setdefault(name, {})['new_block'] = int(new_block.value.strip())
                self.data_for_processes.setdefault('swap_box', {}).setdefault(name, {})['new_box'] = int(new_box.value.strip())
                block.icon = ft.Icon(ft.Icons.LOCK)
                if new_block:
                    new_block.disabled = True
                    new_block.update()
                if new_box:
                    new_box.disabled = True
                    new_box.update()
            else:
                self.result_quick_message('Перевірте дані', True)

        block.update()

    def finally_get_process(self, process):
        data: dict|None = self.data_for_processes.get(process, None)
        values_for_checkboxes = set(get_value_for_checkboxes(process))

        print('data is',data)
        print('val_checkboxes is',values_for_checkboxes)

        if process == 'mate':
            if data and values_for_checkboxes:
                planned_mated_rabbits = [x for x in data if data.get(x, None).get('on_fact', None)]
                if set(planned_mated_rabbits) == values_for_checkboxes:
                    self.farm.mate(data)

                    save_value_for_checkboxes(process, [])
                    self.data_for_processes[process] = {}
                else:
                    not_mated = list(set(planned_mated_rabbits) - values_for_checkboxes)
                    report = ', '.join([x for x in not_mated])
                    self.result_quick_message(f'{report} не спаровані', True)
            else:
                self.result_quick_message('Нікого не спарували', True)

        elif process == 'palpation':

            if data:
                self.farm.palpation(data)

                self.result_quick_message('Записано', False)
                self.data_for_processes[process] = {}
                save_value_for_checkboxes('palpation', [])
            else:
                self.result_quick_message('Нікого не пальпували', True)

        elif process == 'open_nest':
            if values_for_checkboxes:
                opened_nests = [x for x in values_for_checkboxes]
                self.farm.open_nests(opened_nests)
                save_value_for_checkboxes(process, [])
                self.result_quick_message('Записано', False)
            else:
                self.result_quick_message('Нічого не відкривали', True)

        elif process == 'install_nest':
            if values_for_checkboxes:
                installed_nests = [x for x in values_for_checkboxes]
                self.farm.open_nests(installed_nests)
                save_value_for_checkboxes(process, [])
                self.result_quick_message('Записано', False)
            else:
                self.result_quick_message('Нічого не встановлювали', True)

        elif process == 'prepare_nest':
            if values_for_checkboxes:
                prepared_nests = [x for x in values_for_checkboxes]
                self.farm.prepare_nests(prepared_nests)
                save_value_for_checkboxes(process, [])
                self.result_quick_message('Записано', False)
            else:
                self.result_quick_message('Нічого не наповнювали', True)

        elif process == 'kindling':
            if data:
                self.farm.kindling(data)
                self.result_quick_message('Записано', False)

                save_value_for_checkboxes(process, [])
                self.data_for_processes[process] = {}
            else:
                self.result_quick_message('Ніхто ще не окролився', True)

        elif process == 'remove_nest':
            if data:
                self.farm.remove_nests(data)
                self.result_quick_message('Записано', False)

                save_value_for_checkboxes(process, [])
                self.data_for_processes[process] = {}
            else:
                self.result_quick_message('Ще не видаляли гнізда', True)

        elif process == 'resettle':
            if data:
                self.farm.resettle(data)
                self.result_quick_message('Записано', False)

                save_value_for_checkboxes(process, [])
                self.data_for_processes[process] = {}
            else:
                self.result_quick_message('Ще не переселяли', True)

        elif process == 'swap_box':
            if data:
                for name, address in data.items():
                    old_block = self.farm.rabbits[name].block
                    old_box = self.farm.rabbits[name].box
                    new_block = address.get('new_block')
                    new_box = address.get('new_box')
                    self.farm.swap_box(old_block, old_box, new_block, new_box, name)
                self.result_quick_message('Записано', False)

                save_value_for_checkboxes(process, [])
                self.data_for_processes[process] = {}
            else:
                self.result_quick_message('Нікого не переселяли', True)


        self._renew_screen()


class NestsList(ft.View):
    def __init__(self, main_page: ft.Page, farm: Farm):
        super().__init__(route='/nests_list', scroll=ft.ScrollMode.AUTO)
        self.main_page = main_page
        self.farm = farm

        self.appbar = CustomAppBar(title='Гнізда')
        self.bottom_appbar = CustomBottomBar(self.main_page)

        self.controls = self._get_controls()

    def _get_controls(self):
        return [self.get_tile_for_nest(rabbit) for rabbit in self.farm.rabbits.values() if rabbit.nest]

    def _controls_update(self):
        self.controls = self._get_controls()
        self.update()

    def _to_next_screen(self, e, next_screen: str):
            self.main_page.data = e.control.data
            self.main_page.navigate(next_screen)

    def get_tile_for_nest(self, rabbit: Bunny):
        status_nest_dict = {'install': ft.Icon(ft.Icons.HOURGLASS_EMPTY),
                            'prepare': ft.Icon(ft.Icons.HOURGLASS_TOP),
                            'open': ft.Icon(ft.Icons.LOCK_OPEN),
                            'closed': ft.Icon(ft.Icons.LOCK),
                            'remove': ft.Icon(ft.Icons.REMOVE)}
        return ft.ListTile(leading=ft.Icon(ft.Icons.PETS),
                           title=ft.Row([ft.Text(f'{rabbit.name} -- {rabbit.str_block_box}'),
                                         ft.Divider(),
                                         ft.Text(f'🐇 {rabbit.nest.bunnies.get('alive',0)}/{rabbit.nest.bunnies.get('formed',0)}'),
                                         ft.Divider(),
                                         ft.Text(f'📅 {rabbit.nest.nest_age} дн.')],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                           data=rabbit, trailing=status_nest_dict.get(rabbit.nest.status, ft.Icon(ft.Icons.HELP_OUTLINE)),
                           on_click=lambda e: self._to_next_screen(e, '/rabbit_card'),
                           on_long_press=lambda e: self._actions_with_nest(e)
                           )

    def _actions_with_nest(self, e):
        rabbit_obj = e.control.data
        plus = ft.Container(ft.Icon(ft.Icons.PLUS_ONE, color=ft.Colors.BLUE_500),
                            on_click=lambda e: self.change_quantity(rabbit_obj, True))
        minus = ft.Container(ft.Icon(ft.Icons.EXPOSURE_MINUS_1, color=ft.Colors.RED_500),
                             on_click=lambda e: self.change_quantity(rabbit_obj, False))
        delete = ft.Container(ft.Text('LN', size=20, weight=ft.FontWeight.BOLD),
                              on_click=lambda e: (self.farm.loose_nest([rabbit_obj.name]), self._controls_update()))
        back = ft.Container(ft.Icon(ft.Icons.ARROW_BACK_IOS), on_click=lambda e: _go_back(e))
        close = ft.Container(ft.Icon(ft.Icons.CLOSE), on_click=self.change_bottom_appbar_to_started)
        self.bottom_appbar.content = ft.Row([plus,minus,delete,close,back], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        self.bottom_appbar.update()

    def change_bottom_appbar_to_started(self):
        back = ft.Container(ft.Icon(ft.Icons.ARROW_BACK_IOS), on_click=lambda e: _go_back(e))
        self.bottom_appbar.content = ft.Row([ft.Container(),back], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        self.bottom_appbar.update()

    def change_quantity(self, rabbit_obj: Bunny, increase: bool):
        if increase:
            rabbit_obj.nest.bunnies['alive'] += 1
        else:
            if rabbit_obj.nest.bunnies['alive'] >= 1:
                rabbit_obj.nest.bunnies['alive'] -= 1
            else:
                rabbit_obj.nest.bunnies['alive'] = 0
        self._controls_update()