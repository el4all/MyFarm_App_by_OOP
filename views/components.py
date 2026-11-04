from zipfile import sizeCentralDir

import flet as ft

from models.bunny_class import Farm, Bunny

BOXES = dict([(1,20),(2,20),(3,20),(4,20),(5,20),(6,25),(7,20),(8,20),(9,20),(10,20),(11,12),(12,12)])
COLOR_STATUS = dict([('new', ft.Colors.GREEN_500), ('culling', ft.Colors.RED_500), ('waiting_for_kindling', ft.Colors.BLUE_500),
                     ('mated',ft.Colors.YELLOW_500), ('mated mother',ft.Colors.YELLOW_500),
                     (None, ft.Colors.WHITE), ('mother',ft.Colors.BROWN_500), ('mother*', ft.Colors.GREY_500),
                     ('порожньо',ft.Colors.ON_SURFACE)])

class FarmSortBar(ft.PopupMenuButton):
    def __init__(self, farm: Farm, on_change):
        self.farm = farm
        self.on_change = on_change
        super().__init__(
            icon=ft.Icon(ft.Icons.SORT),
            items=[
                    ft.PopupMenuItem(content=ft.Text('По імені A-Z'), data=(lambda obj: obj.name, False),
                                     on_click=lambda e: self.on_change(e)),
                   ft.PopupMenuItem(content=ft.Text('По імені Z-A'), data=(lambda obj: obj.name, True),
                                    on_click=lambda e: self.on_change(e)),
                   ft.PopupMenuItem(content=ft.Text('По черзі додавання'), data=(None,False),
                                    on_click=lambda e: self.on_change(e)),
                   ft.PopupMenuItem(content=ft.Text('По віку (зростання)'), data=(lambda obj: obj.age, False),
                                    on_click=lambda e: self.on_change(e)),
                   ft.PopupMenuItem(content=ft.Text('По віку (спадання)'), data=(lambda obj: obj.age, True),
                                    on_click=lambda e: self.on_change(e)),
                   ft.PopupMenuItem(content=ft.Text('По рейтингу (зростання)'), data=(lambda obj: obj.rating, False),
                                    on_click=lambda e: self.on_change(e)),
                   ft.PopupMenuItem(content=ft.Text('По рейтингу (спадання)'), data=(lambda obj: obj.rating, True),
                                    on_click=lambda e: self.on_change(e))]
            )


class BlockForVisual(ft.Container):
    def __init__(self, main_page: ft.Page, farm: Farm, id_block, filter_status=None):
        super().__init__()
        self.main_page = main_page
        self.farm = farm
        self.id_block = id_block
        self.quantity_of_boxes = BOXES.get(self.id_block)
        self.nums_of_blocks = [x for x in range(1, self.quantity_of_boxes + 1)]

        self.filter_status = filter_status


        self.left_lower = []
        self.left_higher = []
        self.right_lower = []
        self.right_higher = []
        self.right_higher_second_row = []

    def _build_main_container(self):
        self.border = ft.Border.all(2, ft.Colors.ON_SURFACE_VARIANT)
        self.border_radius = 5
        self.padding = 10
        self.expand = True
        self.data = dict([('rabbits_obj_list', [x for x in sorted(self.farm.rabbits.values(), key=lambda x: (x.block, x.box))
                                                if x.block == self.id_block]),
                             ('block', self.id_block)])
        self.on_click = lambda e: self._to_next_screen(e, '/rabbits_list')
        self.left_cont, self.num_cont, self.right_cont = self.get_inner_for_main_container()
        self.content = ft.Row(controls=[self.left_cont,self.num_cont,self.right_cont],
                              alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                              vertical_alignment=ft.CrossAxisAlignment.CENTER)

    def _to_next_screen(self, e, next_screen: str):
            self.main_page.data = e.control.data
            self.main_page.navigate(next_screen)

    def get_inner_for_main_container(self):
        left_low = self.get_all_boxes_for_block(self.left_lower)
        left_high = self.get_all_boxes_for_block(self.left_higher)
        left_cont = ft.Container(ft.Row([left_low, left_high], tight=True), expand=True)

        num_cont = ft.Container(content=ft.Text(str(self.id_block), expand=True, weight=ft.FontWeight.BOLD))

        right_low = self.get_all_boxes_for_block(self.right_lower)
        right_high = self.get_all_boxes_for_block(self.right_higher)
        right_high_second_row = self.get_all_boxes_for_block(self.right_higher_second_row)
        right_cont = ft.Container(ft.Row(controls=[right_high_second_row, right_high, right_low] if self.id_block == 6
                                                  else [right_high, right_low], tight=True),
                                  expand=True)

        return left_cont, num_cont, right_cont

    def get_all_boxes_for_block(self, list_of_nums):
        line_of_boxes = ft.Column(controls=[ft.Container(content=ft.Text(f'{x}' if len(str(x))>1 else f' {x} ', size=10),
                                                         expand=True,
                                                         border=ft.Border.all(1, ft.Colors.ON_SURFACE_VARIANT),
                                                         border_radius=2, padding=2,
                                                         data=(None if self.farm.who_in_box(self.id_block, x) == 'порожньо'
                                                                       or ',' in self.farm.who_in_box(self.id_block, x)
                                                               else self.farm.rabbits[self.farm.who_in_box(self.id_block, x)]),
                                                         bgcolor=self.get_color_for_box(self.id_block, x),
                                                         on_click=lambda e: self._to_next_screen(e, '/rabbit_card'))
                                            for x in list_of_nums], alignment=ft.MainAxisAlignment.CENTER)

        return ft.Container(line_of_boxes, expand=True)

    def get_color_for_box(self, block, box):
        name = self.farm.who_in_box(block, box)
        if ',' not in name:
            if self.filter_status:
                return (ft.Colors.ON_SURFACE if name == 'порожньо' or self.farm.rabbits[name].status != self.filter_status
                        else COLOR_STATUS.get(self.farm.rabbits[name].status))
            else:
                if name != 'порожньо':
                    return COLOR_STATUS.get(self.farm.rabbits[name].status)
                return ft.Colors.ON_PRIMARY
        else:
            return ft.Colors.PINK_800


class RightBlock(BlockForVisual):
    def __init__(self, main_page, farm: Farm, id_block, filter_status=None):
        super().__init__(main_page, farm,  id_block,filter_status)
        self.left_lower = self.nums_of_blocks[int(self.quantity_of_boxes / 2):-int(self.quantity_of_boxes / 4)]
        self.left_higher = self.nums_of_blocks[-int(self.quantity_of_boxes / 4):]
        self.right_lower = reversed(self.nums_of_blocks[: int(self.quantity_of_boxes / 4)])
        self.right_higher = reversed(self.nums_of_blocks[int(self.quantity_of_boxes / 4):int(self.quantity_of_boxes / 2)])

        self._build_main_container()


class LeftBlock(BlockForVisual):
    def __init__(self, main_page, farm: Farm, id_block, filter_status=None):
        super().__init__(main_page, farm, id_block, filter_status)
        self.left_lower = self.nums_of_blocks[:int(self.quantity_of_boxes / 4)]
        self.left_higher = self.nums_of_blocks[int(self.quantity_of_boxes / 4):int(self.quantity_of_boxes / 2)]
        self.right_lower = reversed(self.nums_of_blocks[int(self.quantity_of_boxes / 2):-int(self.quantity_of_boxes / 4)])
        self.right_higher = reversed(self.nums_of_blocks[-int(self.quantity_of_boxes / 4):])

        self._build_main_container()


class BlockNumberSix(BlockForVisual):
    def __init__(self, main_page, farm: Farm, id_block, filter_status=None):
        super().__init__(main_page, farm, id_block, filter_status)
        self.left_lower = [16,17,18,19,20]
        self.left_higher = [21,22,23,24,25]
        self.right_lower = [5,4,3,2,1]
        self.right_higher = [14,12,10,8,6]
        self.right_higher_second_row = [15,13,11,9,7]

        self._build_main_container()



