import time


import json
from datetime import datetime, date, timedelta
from loguru import logger


STATUS_WORK = dict([('mate','запліднення'),('palpation','пальпація'),('install_nest','монтаж гнізда'),
                    ('open_nest',"відкривання гнізда"),('prepare_nest','підготовка гнізда'),
                         ('remove_nest','демонтаж гнізда'),('resettle','переселення'),
                    ('vaccination_nest','вакцинація гнізда'),('swap_box','перміщення'),
                    ('mass_kill','забій'),('kindling','окрол')])
STATUS_FOR_STR = {'mated': 'очікує на пальпацію', 'waiting_for_kindling': 'очікує на окріл', 'mother': 'матір',
                    'mated_mother': 'запліднена матір', 'mother*': 'матір без гнізда', 'culling': 'вибраківка', None:'немає',
                    'new': 'молодь', 'male':'самець'}
DATE_FORMAT = '%d.%m.%Y'
DAYS = ['Понеділок',"Вівторок","Середа","Четвер","П'ятниця","Субота","Неділя"]
BOXES = dict([(1,20),(2,20),(3,20),(4,20),(5,20),(6,25),(7,20),(8,20),(9,20),(10,20),(11,12),(12,12)])

class Farm:
    def __init__(self, name='MeatBerry'):
        self.name = name
        self.rabbits: dict[str, Bunny] = {}
        self.third_room: dict[str, Box] = {}
        self.morgue = []
        self.morgue_for_third_room = {}
        self.defective = []
        self.history_logs = []
        self.notes = {}

    @property
    def active(self):
        active_rabbits = []

        for bunny in self.rabbits.values():
            if bunny.birthday is not None and bunny.status != 'culling':
                active_rabbits.append(bunny.name)
        return active_rabbits

    @property
    def rating_list(self):
        return sorted(self.active, key=lambda x: self.rabbits[x].rating, reverse=True)

    def report_bunny(self, name):
        return (f'{self.rabbits[name]}\n'
                f'Місце в рейтингу {self.rating_list.index(name) + 1}')

    def add_rabbit(self, name, date_birth: str, block, box):
        bunny_obj = Bunny(name, date_birth, block, box, status='new')
        if isinstance(bunny_obj, Bunny):
            if bunny_obj.name not in self.rabbits:
                self.rabbits[bunny_obj.name] = bunny_obj
                bunny_obj.planing_mate()
                logger.info(f'{date.today().strftime(DATE_FORMAT)}: Bunny {bunny_obj.name} add in box {bunny_obj.block}.{bunny_obj.box}')
                return True
            else:
                logger.warning(f'Error. Bunny {bunny_obj.name} is already exist!!!')
                return False
        else:
            logger.error('Error. Wrong type object!!!')

    def set_defective_mass(self, names: list):
        for name in names:
            if self.rabbits[name].status != 'waiting_for_kindling':
                self.rabbits[name].status = 'culling'
                if name not in self.defective:
                    self.defective.append(name)
                    logger.info(f'{name} set as defective.')
                else:
                    logger.info(f'{name} is already set.')
            else:
                logger.error(f'{name} waiting for kindling')

    def set_defective_single_for_app(self, name):
        obj = self.rabbits[name]
        if obj.status != 'waiting_for_kindling':
            obj.status = 'culling'
            if name not in self.defective:
                self.defective.append(name)
                report = f'{name} set as defective.'
                logger.info(report)
                return f'{name} встановлена на вибраківку.'
            else:
                report = f'{name} is already set.'
                logger.info(report)
                return f'{name} вже в вибраківці.'
        else:
            report = f'{name} waiting for kindling'
            logger.error(report)
            return f'{name} очікує окролу.'


    def cancel_defective(self, names: list):
        for name in names:
            self.rabbits[name].status = None
            if name in self.defective:
                self.defective.remove(name)
                logger.info(f'{name} cancel defective.')
            else:
                logger.info(f'{name} is already cancel.')

    def remove_rabbit_by_death(self, names: list):
        for name in names:
            if name in self.rabbits:
                old_box = self.rabbits[name].str_block_box
                self.morgue.append([name, self.rabbits[name].age, self.rabbits[name].history])
                del self.rabbits[name]
                if name in self.defective:
                    self.defective.remove(name)
                logger.info(f'{date.today().strftime(DATE_FORMAT)}: Bunny {name} dead. Box {old_box} free.')
            else:
                if name in self.morgue:
                    logger.info(f'{name} is already died.')
                else:
                    logger.error(f'{name} not founded.')

    def remove_rabbit_by_culling(self, names: list):
        for name in names:
            if name in self.rabbits:
                old_box = self.rabbits[name].str_block_box
                del self.rabbits[name]
                if name in self.defective:
                    self.defective.remove(name)
                logger.info(f'{date.today().strftime(DATE_FORMAT)}: Bunny {name} culled. Box {old_box} free.')

    def install_nests(self, names: list):
        for name in names:
            if name in self.rabbits:
                if self.rabbits[name].nest is None:
                    self.rabbits[name].nest.install_nest()
                    logger.info(f'{name} nest was install.')
                    self.rabbits[name].all_planing_dates.pop('install_nest', None)
                else:
                    logger.info(f'{name} has nest.')
            else:
                logger.info(f'{name} not founded.')

    def prepare_nests(self, names: list):
        for name in names:
            if name in self.rabbits:
                if self.rabbits[name].nest:

                    self.rabbits[name].nest.prepare_nest()
                    logger.info(f'{name} nest was fill.')
                    self.rabbits[name].all_planing_dates.pop('fill_nest', None)
                else:
                    logger.info(f'{name} has not nest.')
            else:
                logger.info(f'{name} not founded.')


    def open_nests(self, list_of_rabbits):
        for name in list_of_rabbits:
            if name in self.rabbits:
                if self.rabbits[name].nest:
                    if self.rabbits[name].status == 'mother':
                        result = self.rabbits[name].nest.open_nest()
                        if result:
                            self.rabbits[name].all_planing_dates.pop('open_nest', None)
                            logger.info(f'{name} nest was open.')
                    elif self.rabbits[name].status == 'mother*':
                        logger.info(f'{name} has not nest.')
                else:
                    logger.error(f'{name} has not nest.')
            else:
                logger.info(f'{name} not founded.')

    def remove_nests(self, list_of_rabbits, list_of_quantity):
        for name, quantity in zip(list_of_rabbits, list_of_quantity):
            if name in self.rabbits:
                if self.rabbits[name].nest is not None:
                    self.rabbits[name].nest.remove_nest()
                    self.rabbits[name].kindling[self.rabbits[name].last_kindling]['from_nest'] = quantity
                    logger.info(f'{name} nest was remove.')
                else:
                    logger.info(f'{name} has not nest.')
            else:
                logger.info(f'{name} not founded.')

    def mate(self, mate_info: dict, date_mate=None):
        if date_mate is None:
            date_mate = date.today()

        for name, info in mate_info.items():
            father = mate_info.get(name, None).get('on_fact', None)
            if father == '--':
                self.set_defective_mass([name])
            elif father == '*':
                next_try: date = self.find_next_dates('mate')
                self.rabbits[name].all_planing_dates['mate'] = next_try
                logger.info(f'{name} not mated. Next try {next_try.strftime(DATE_FORMAT)}.')
            else:
                self.rabbits[name].get_mate(date_mate, father)
                logger.info(f'{date_mate.strftime(DATE_FORMAT)}: {name} was mated by {father}.' if father is not None
                            else f'{date_mate.strftime(DATE_FORMAT)}: {name} not mated.')



    def pre_palp_add_new_boxes(self, name_sheet):
        tab = wwn.get_sheet_by_net(wwn.palpation_url, name_sheet)
        final_tab = wwn.change_sheet_for_mate_and_palp(tab)
        need_list = []
        names = [x for x in final_tab.loc[:, "ім'я"]] # if final_tab.loc[final_tab["ім'я"] == x, 'батько'].values[0] in ['X', 'Y', 'Z']
        fathers = [x for x in final_tab.loc[:, "батько"]]
        for name, father in zip(names, fathers):
            need_list.append([self.rabbits[name].str_block_box] if father in ['X','Y','Z'] and name in self.rabbits else [None])

        gs = gspread.service_account(filename='meatberry_farm_for_gspread.json')
        sheet = gs.open_by_key('1Nu4JlbhGVOEW1UNg9mCtW-C4rhTmNj0HZkjIAlqlLqo')
        worksheet = sheet.worksheet(name_sheet)
        worksheet.update(need_list, 'I9')

    def add_new_boxes_before_kindling(self, name_sheet):
        tab = wwn.get_sheet_by_net(wwn.kindle_url, name_sheet)
        final_tab = wwn.change_sheet_for_kindle(tab)
        print(final_tab)
        names = [x for x in final_tab.loc[:, "name"]]
        boxes = []
        for name in names:
            boxes.append([self.rabbits[name].str_block_box] if name in self.rabbits else [None])

        print(boxes)

        gs = gspread.service_account(filename='meatberry_farm_for_gspread.json')
        sheet = gs.open_by_key('1bghOnHANyqLeAKUbVX-SRjHMw4mFTD8LpN0I4dqARI4')
        worksheet = sheet.worksheet(name_sheet)
        worksheet.update(boxes, 'C2')

        print('Done!!!')

    def palpation(self, data: dict, palpation_date=None): # results = [(name, res)]
        if palpation_date is None:
            palpation_date = date.today()

        for name, res in data.items():
            if res:
                self.rabbits[name].get_palpation(res, palpation_date)

    def create_sheet_for_kindling(self, name_sheet: str):
        df = wwn.get_sheet_by_net(wwn.palpation_url, name_sheet)
        mate_tab = wwn.change_sheet_for_mate_and_palp(df)
        list_of_positive_palpation = [x for x in mate_tab.loc[:, "ім'я"] if mate_tab.loc[mate_tab["ім'я"] == x, 'результат'].values[0].strip() == '+']

        mate_day = datetime.strptime(name_sheet, DATE_FORMAT).date()
        kindling_day = mate_day + timedelta(days=31)
        name_sheet_kindling = kindling_day.strftime(DATE_FORMAT)

        data_to_fill = [[y for y in x] for x in zip(range(1,50), list_of_positive_palpation) if x[1] in self.active]
        print(data_to_fill)

        csap.create_kindling(name_sheet_kindling)
        print('Created')
        csap.upload_kindling(name_sheet_kindling, data_to_fill)

    def kindling(self, data_of_kindling, date_kindling=None):
        if date_kindling is None:
            date_kindling = date.today()
        for name, data_dict in data_of_kindling.items():
            if name in self.rabbits:
                alive = int(data_dict.get('alive', 0))
                dead = int(data_dict.get('dead', 0))
                formed = int(data_dict.get('formed', 0))
                total = alive + dead

                self.rabbits[name].get_kindling(total, alive, dead, formed, date_kindling)

                logger.info(f'{date_kindling.strftime(DATE_FORMAT)}: {name}: Birth {alive} + {dead}. {f'Formed {formed}' if formed else 'Not formed'}.')
            else:
                logger.error(f"{name} not found.")

    def create_box_in_third_room(self, block, box, quantity, birth: date, status):
        try:
            bunnies_obj = Box(block, box, quantity, birth, status)
            self.third_room[f'{block}.{box}'] = bunnies_obj
            bunnies_obj.set_kill_date()

            logger.info(f'{quantity} bunnies move to {block}.{box}')
            return True

        except Exception as e:
            return False

    def move_to_3rd_room_repare(self, block, box, quantity, birth):
        pass

    def death_bunny_in_third_room(self, block, box, quantity, date_of_death: date=None):
        if date_of_death is None:
            date_of_death = date.today()
        for obj in self.third_room.values():
            if obj.block == block and obj.box == box:
                obj.quantity -= quantity

                age_dead_bunny = date_of_death - obj.birth
                self.morgue_for_third_room.setdefault(obj.birth.strftime(DATE_FORMAT), []).append(age_dead_bunny.days)

    def who_in_box(self, block, box):
        who = []
        for obj in self.rabbits.values():
            if obj.block == block and obj.box == box:
                who.append(obj.name)

        return ','.join([x for x in who]) if who else 'порожньо'

    def change_box(self, name, to_box:str):
        old_block = self.rabbits[name].block
        old_box = self.rabbits[name].box
        new_block = int(to_box.split('.')[0])
        new_box = int(to_box.split('.')[1])
        name_in_new_box = ''
        for n, obj in self.rabbits.items():
            if obj.block == new_block and obj.box == new_box:
                name_in_new_box = n
                obj.block = old_block
                obj.box = old_box
                break
        self.rabbits[name].block = new_block
        self.rabbits[name].box = new_box

        logger.info(f'{name} stay in {to_box} box.') if name == name_in_new_box else logger.info(f'{name} move to {to_box} box.')

    def swap_box(self,from_address:str, to_address:str, name_who=None):
        name_in_from = name_who
        name_in_to = None
        from_block = int(from_address.split('.')[0])
        from_box = int(from_address.split('.')[1])
        to_block = int(to_address.split('.')[0])
        to_box = int(to_address.split('.')[1])

        for n, obj in self.rabbits.items():
            if obj.block == from_block and obj.box == from_box:
                name_in_from = n if not name_who else name_who
            elif obj.block == to_block and obj.box == to_box:
                name_in_to = n
            if name_in_from and name_in_to :
                break
        print(name_in_from,name_in_to)
        if name_in_from and name_in_to:
            self.rabbits[name_in_from].block, self.rabbits[name_in_to].block = to_block, from_block
            self.rabbits[name_in_from].box, self.rabbits[name_in_to].box = to_box, from_box
            logger.info(f'{name_in_from} -> {to_block}.{to_box}  '
                f'{name_in_to} -> {from_block}.{from_box}  ')
        elif name_in_to is None:
            self.rabbits[name_in_from].block = to_block
            self.rabbits[name_in_from].box = to_box
            logger.info(f'{name_in_from} -> {to_address}  '
                  f'{from_block}.{from_box} is empty.')
        elif name_in_from is None:
            self.rabbits[name_in_to].block = to_block
            self.rabbits[name_in_to].box = to_box
            logger.info(f'{name_in_to} -> {from_address}  '
                  f'{to_block}.{to_box} is empty.')

    def loose_nest(self, names: list):
        for name in names:
            obj = self.rabbits[name]
            obj.nest = None
            obj.status = 'mother*'
            for i in range(len(obj.history)-1, -1, -1):
                if isinstance(obj.history[i], list):
                    obj.history[i] = 'LN'
                    break
            logger.info(f'{name} loose nest.')

    def get_wrote_rating(self):

        elements = []
        elements_per = []
        non_kindling = []
        for name, obj in self.rabbits.items():
            if len(self.rabbits[name].history) > 0 and name not in self.defective:
                id_bunny = name
                rating_per = self.rabbits[name].rating / len(self.rabbits[name].history)
                ratings = self.rabbits[name].rating
                elements.append([id_bunny, ratings])
                elements_per.append([id_bunny, rating_per])
            if len(self.rabbits[name].history) == 0 or self.rabbits[name].history is None:
                non_kindling.append([name, self.rabbits[name].age if self.rabbits[name].age else None,
                                     self.rabbits[name].history])

        rating_list = sorted(elements, key=lambda x: x[1], reverse=True)
        rating_per = sorted(elements_per, key=lambda x: x[1], reverse=True)
        final_report = []
        report_per_one = []
        for el in rating_list:
            rating = round(el[1], 3)
            report = (
                f'{rating_list.index(el) + 1}. {el[0]} {"+" + str(rating) if rating > 0 else rating} by {len(self.rabbits[el[0]].history)},'
                f' tried. Age {self.rabbits[el[0]].age_in_month}  {self.rabbits[el[0]].history[-7:]}. {'незадіяна' if self.rabbits[el[0]].status is None else STATUS_FOR_STR[self.rabbits[el[0]].status]}, '
                f'{str(self.rabbits[el[0]].nest.nest_age) + "дн." if self.rabbits[el[0]].status in ['mother', 'mated_mother'] else ""}')
            final_report.append(report)
        for i in rating_per:
            rating = round(i[1], 3)
            report = (
                f'{rating_per.index(i) + 1}. {i[0]} {"+" + str(rating) if rating > 0 else rating} per try. Total try mate '
                f'{len(self.rabbits[i[0]].history)}. Age {self.rabbits[i[0]].age_in_month}. {self.rabbits[i[0]].history}')
            report_per_one.append(report)

        write_json('Ratings_by_sum.json', final_report)
        write_json('Ratings_per_kindling.json', report_per_one)
        write_json('RNon_mate.json', non_kindling)

    def upload_mated_for_rabbits(self, sheet_name, need_date):
        c = 1
        rating_list = sorted(self.rabbits, key=lambda x: self.rabbits[x].rating, reverse=True)
        artificial = []
        none_status_x = []
        none_status_minus = []
        new = []

        for name, obj in self.rabbits.items():
            if name in self.active and obj.sex == 'female':
                last_two_in_history = obj.history[-3:]
                for el in last_two_in_history.copy():
                    if isinstance(el, list):
                        last_two_in_history[last_two_in_history.index(el)] ='+'
                if obj.status in ['mother', 'mother*'] and obj.all_planing_dates.get('mate') <= need_date:
                    artificial.append([name, obj.str_block_box, f'шт. {str(last_two_in_history)}', rating_list.index(name) + 1, obj.age_in_month])
                elif obj.status is None and obj.all_planing_dates.get('mate', date(2026,8,19)) <= need_date:
                    if not obj.history and obj.all_planing_dates.get('mate', date(2026,8,19)) <= need_date:
                        new.append([name, obj.str_block_box, 'new', 0, obj.age_in_month])
                    elif obj.history[-1] == 'X':
                        none_status_x.append([name, obj.str_block_box, str(last_two_in_history), rating_list.index(name) + 1, obj.age_in_month])
                    elif obj.history[-1] == '-':
                        none_status_minus.append([name, obj.str_block_box, str(last_two_in_history), rating_list.index(name) + 1, obj.age_in_month])

        list_1 = sorted(artificial, key=lambda x: (int(x[1].split('.')[0]), int(x[1].split('.')[1])))
        list_2 = sorted(none_status_x, key=lambda x: (int(x[1].split('.')[0]), int(x[1].split('.')[1])))
        list_3 = sorted(none_status_minus, key=lambda x: (int(x[1].split('.')[0]), int(x[1].split('.')[1])))
        list_4 = sorted(new, key=lambda x: (int(x[1].split('.')[0]), int(x[1].split('.')[1])))
        final = [*list_1, *list_2, *list_3, *list_4]
        for el in final:
            el.insert(0, c)
            c += 1

        to_fill = csap.prepare_data_to_fill_tab(final)
        csap.create_and_publish(to_fill, sheet_name)
        print('Done!!!')

    def find_min_max_dates(self, func, process):
        dates = []
        for obj in self.rabbits.values():
            day = obj.all_planing_dates.get(process)
            if day is not None and day not in dates:
                dates.append(day)

        return func(dates)

    def find_next_dates(self, process):
        today = date.today()
        dates = []
        for obj in self.rabbits.values():
            day = obj.all_planing_dates.get(process)
            if day is not None and day not in dates:
                dates.append(day)

        for d in sorted(dates):
            if d > today:
                return d
        return None

    def empty_boxes(self):
        len_block = {1:20, 2:20, 3:20, 4:20, 5:20, 6:25, 7:20, 8:20, 9:20, 10:20, 11:12, 12:12}
        all_blocks = {}
        free = []
        more_then_one =[]
        for obj in self.rabbits.values():
            all_blocks.setdefault(obj.block, []).append(obj.box)

        for block, box in all_blocks.items():
            empty = set(range(1, len_block[block] + 1)) - set(box)
            if empty:
                free.append(f'{block}.{[x for x in empty]}')
            once = []
            duplicates = []
            for el in box:
                if el in once:
                    duplicates.append(el)
                else:
                    once.append(el)
                if duplicates:
                    more_then_one.append(f'{block}.{[x for x in duplicates]}')

        return f'Free {free},\n More then one {more_then_one}'

    def vacant_indexes(self, line):
        indexes = []
        for x in self.rabbits.keys():
            if len(x) > 2:
                name = x[:2]
                num = int(x[2:])
                if name == line:
                    indexes.append(num)
        if indexes:
            free = []
            for i in range(1, len(indexes)):
                if i not in indexes:
                    free.append(i)
            return str(free[0]) if free else str(max(indexes) + 1)

    def planned_work(self, start_date_planed:date, end_date_planed:date):
        c = 1
        work = {}
        new = {}
        name_file = f'PLANNED_SORT {start_date_planed.day}.{start_date_planed.month} - {end_date_planed.day}.{end_date_planed.month}.{end_date_planed.year}.json'
        while start_date_planed < end_date_planed:
            for name, obj in self.rabbits.items():
                obj: Bunny
                if name in self.active:
                    for process, dates in obj.all_planing_dates.items():
                        if obj.all_planing_dates and dates == start_date_planed:
                            work.setdefault(f'{dates.strftime(DATE_FORMAT)}, {DAYS[dates.weekday()]}', []).append([name, obj.str_block_box, STATUS_WORK[process], self.rating_list.index(name) + 1])

            start_date_planed += timedelta(days=1)

        for k, v in work.items():
            new[k] = sorted(v, key=lambda x: (x[2], self.rabbits[x[0]].block, self.rabbits[x[0]].box))

        for el in new.values():
            for i in el:
                i.insert(0, c)
                c += 1

        write_json(name_file, new)

    def planned_work_sheet(self, start, end):
        planned = {}
        kill = {}
        while start < end:
            for name, obj in self.rabbits.items():
                if name in self.active:
                    for process, dates in obj.all_planing_dates.items():
                        if obj.all_planing_dates and dates == start:
                            planned.setdefault(dates, []).append(
                                [name, obj.str_block_box, self.rating_list.index(name) + 1, STATUS_WORK[process]])

            for num, box_obj in self.third_room.items():
                if box_obj.kill_date is not None:
                    if box_obj.kill_date == start:
                        kill.setdefault(box_obj.kill_date, []).append(
                            [box_obj.birth.strftime(DATE_FORMAT), num, box_obj.quantity, 'забій'])

            start += timedelta(days=1)

        for day, data in planned.items():
            day: date
            date_ = day.strftime(DATE_FORMAT)
            to_fill = sorted(data, key=lambda x: (x[3], self.rabbits[x[0]].block, self.rabbits[x[0]].box))
            if day in kill:
                to_fill.extend(kill[day])
            csap.create_and_publish_planned_work(to_fill, date_)

            print('Done!!!')

    def mass_kill(self, block, box, quantity, status):
        for box_obj in self.third_room.values():
            if box_obj.block == block and box_obj.box == box:
                box_obj.status = status if quantity else None
                box_obj.quantity = quantity if quantity else 0
                box_obj.birth = box_obj.birth if quantity else None
                box_obj.kill_date = box_obj.kill_date if quantity else None

        return True

    def change_date_for_process(self, process, old_date, new_date):
        try:
            for obj in self.rabbits.values():
                if obj.all_planing_dates:
                    process_date = obj.all_planing_dates.get(process, None)
                    if process_date and process_date == old_date:
                        obj.all_planing_dates[process] = new_date

            return True
        except Exception:
            return False

    def create_notes(self, name: str, text: str):
        if text:
            today = date.today().strftime(DATE_FORMAT)
            note = {today: text}
            self.notes.setdefault(name, []).append(note)

            return True
        else:
            return False



    def save_to_json(self, file_name='MeatBerryFarm.json'):
        export_data = {
            'farm_name': self.name,
            'rabbits': {},
            'third_room': {},
            'morgue': self.morgue,
            'morgue_for_third_room': self.morgue_for_third_room,
            'defective': self.defective,
            'history_logs': self.history_logs,
            'notes': self.notes
        }
        for name, bunny_obj in self.rabbits.items():
            export_data['rabbits'][name] = bunny_obj.to_dict()
        for box_num, box_obj in self.third_room.items():
            export_data['third_room'][box_num] = box_obj.to_dict()

        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=4)
            print('Data saved.')

    def load_from_json(self, file_name='MeatBerryFarm_for_tests.json'):
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                farm_dict = json.load(f)
                self.name = farm_dict.get('farm_name', self.name)
                self.rabbits = {}
                self.third_room = {}
                self.morgue_for_third_room = farm_dict.get('morgue_for_third_room', {})
                self.morgue = farm_dict.get('morgue', [])
                self.defective = farm_dict.get('defective', [])
                self.history_logs = farm_dict.get('history_logs', [])
                self.notes = farm_dict.get('notes', {})
                raw_rabbits = farm_dict.get('rabbits', {})
                raw_boxes = farm_dict.get('third_room', {})

                for name, obj_dict in raw_rabbits.items():
                    new_bunny = Bunny(**obj_dict)
                    self.rabbits[name] = new_bunny
                print(f'{len(self.rabbits)} rabbits loaded.')
                for box_num, box_dict in sorted(raw_boxes.items(), key=lambda x:(x[1].get('block'),x[1].get('box'))):
                    new_box = Box(**box_dict)
                    self.third_room[box_num] = new_box
                print(f'{len(self.third_room)} boxes loaded.')



        except FileNotFoundError:
            print('File not found. Stat new farm.')

    def load_from_net(self, farm_dict: dict):

        self.name = farm_dict.get('farm_name', self.name)
        self.rabbits = {}
        self.third_room = {}
        self.morgue_for_third_room = farm_dict.get('morgue_for_third_room', {})
        self.morgue = farm_dict.get('morgue', [])
        self.defective = farm_dict.get('defective', [])
        self.history_logs = farm_dict.get('history_logs', [])
        self.notes = farm_dict.get('notes', {})
        raw_rabbits = farm_dict.get('rabbits', {})
        raw_boxes = farm_dict.get('third_room', {})

        for name, obj_dict in raw_rabbits.items():
            new_bunny = Bunny(**obj_dict)
            self.rabbits[name] = new_bunny
        print(f'{len(self.rabbits)} rabbits loaded.')
        for box_num, box_dict in sorted(raw_boxes.items(), key=lambda x:(x[1].get('block'),x[1].get('box'))):
            new_box = Box(**box_dict)
            self.third_room[box_num] = new_box
        print(f'{len(self.third_room)} boxes loaded.')

    def save_to_json_for_net(self):
        export_data = {
            'farm_name': self.name,
            'rabbits': {},
            'third_room': {},
            'morgue': self.morgue,
            'morgue_for_third_room': self.morgue_for_third_room,
            'defective': self.defective,
            'history_logs': self.history_logs,
            'notes': self.notes
        }
        for name, bunny_obj in self.rabbits.items():
            export_data['rabbits'][name] = bunny_obj.to_dict()
        for box_num, box_obj in self.third_room.items():
            export_data['third_room'][box_num] = box_obj.to_dict()

        return export_data



class Bunny:
    def __init__(self, name, birthday: str,  block, box, status=None, sex=None, **kwargs):

        self.name: str = name   # ID bunny

        self.block = block

        self.box = box

        self.birthday: str = birthday

        self.status = status

        self.sex = sex

        def parse_date(value):
            if isinstance(value, str):
                return datetime.strptime(value, DATE_FORMAT).date()
            return value

        self.last_mate = parse_date(kwargs.get('last_mate'))

        self.last_palpation = parse_date(kwargs.get('last_palpation'))

        self.last_kindling = parse_date(kwargs.get('last_kindling'))

        def restore_dict_all_dates(from_json_dict):
            if not from_json_dict:
                return {}
            return {k: datetime.strptime(v, DATE_FORMAT).date() if isinstance(v, str) else v for k, v in from_json_dict.items()}

        def restore_dict(from_json_dict):
            if not from_json_dict:
                return {}
            return {datetime.strptime(k, DATE_FORMAT).date() if isinstance(k, str) else k:v for k, v in from_json_dict.items()}

        self.all_planing_dates = restore_dict_all_dates(kwargs.get('all_planing_dates'))  # ['mate', 'palpation', 'kindling', 'install/open/remove nest', 'resettle']

        self.mate = restore_dict(kwargs.get('mate'))       # dict_structure {data_of_mate: {'line_father': line_father, 'result': result}}

        self.palpation = restore_dict(kwargs.get('palpation'))   # dict_structure {data_of_palpation: {result: status}} . status is 'waiting', 'positive' or 'negative'

        self.kindling = restore_dict(kwargs.get('kindling'))    # dict_structure {data_of_kindling: quantity: (total, alive, dead)}

        self.history = kwargs.get('history', [])

        self.nest_archive = kwargs.get('nest_archive')

        self.nest: Nest | None = None

        from_json_nest = kwargs.get('nest')
        if from_json_nest:
            self.nest = Nest(**from_json_nest)


    def __str__(self):
        kindling = len(self.kindling)
        alive = sum(v.get('alive',0) for v in self.kindling.values())
        dead = sum(v.get('dead',0) for v in self.kindling.values())
        formed = 0
        resettle = 0
        for x in self.history:
            if isinstance(x, list) and isinstance(x[-1], int):
                resettle += x[-1]
                formed += x[2]


        return (f'Кролиця {self.name}, клітка {self.str_block_box}:\n'
                f'Дата народження {self.birthday},\n'
                f'Вік - {self.age_in_month},\n'
                f'Статус - {STATUS_FOR_STR[self.status]},\n'
                f'Кількість окролів - {kindling},\n'
                f'Народжено {alive} живих, {dead} мертвих,\n'
                f'Переселено {round(resettle/formed if formed!=0 else 0, 3)*100} %\n'
                f'Історія - {self.history}')

    @property
    def age(self):         # age in 'days'
        today = date.today()

        return (today - datetime.strptime(self.birthday, DATE_FORMAT).date()).days if self.birthday is not None else None

    @property
    def age_in_month(self):
        birth = datetime.strptime(self.birthday, DATE_FORMAT).date()
        today = date.today()
        days = (today - birth).days
        years = days // 365
        month = round(days / 30.42) if not years else round(days % 365 / 30.42)

        return f'{years} p. {int(month)} м.'

    @property
    def str_block_box(self):
        return f'{self.block}.{self.box}'

    @property
    def rating(self):
        if not self.history:
            return 0
        diapason = self.history if len(self.history) <= 7 else self.history[-7:]
        quantity_birth = 0
        good_mother = 0
        for x in diapason:
            if isinstance(x, list) :
                quantity_birth += x[0] * 0.125
                good_mother += round(x[3] / x[2], 2) if x[2] != 0 and isinstance(x[3], int) else 0
        if len(diapason) == 1:
            fertility = 0
            if diapason == ['-']:
                fertility = -0.5
            elif diapason == ['X']:
                fertility = -0.3
            return quantity_birth + good_mother + fertility
        shifted = iter(diapason)
        next(shifted)
        count_minus = 0
        count_xx = 0
        count_plus = len([i for i in diapason if isinstance(i, list)])
        for el, next_el in zip(diapason, shifted):
            if el == '-' and next_el == '-':
                count_minus += 1
            elif el == "X" and next_el == 'X':
                count_xx += 1
            elif isinstance(el, list) and isinstance(next_el, list):
                count_plus += 1
        fertility = count_plus - count_minus * 0.5 - count_xx * 0.3

        return quantity_birth + good_mother + fertility

    def planing_mate(self):
        # if first time - (date = birthdate + 128 days), if not - (date = day_of_negative_palpation + 3 day) or (day_of_kindling + 19 days)
        mate_day = None        # Тут треба доробити логіку, якщо пальпація позитивна. Мабуть, треба дату з функції, котра буде відмічати окрол.
        if not self.mate:
            mate_day = datetime.strptime(self.birthday, DATE_FORMAT).date() + timedelta(days=128)
        else:
            if not self.palpation:

                return None
            else:
                if self.last_palpation is None:
                    pass
                else:
                    if self.palpation[self.last_palpation].get('result') == 'negative':
                        mate_day = self.last_palpation + timedelta(days=1)


                    elif self.palpation[self.last_palpation].get('result') == 'positive':
                        mate_day = self.last_kindling + timedelta(days=19)


        self.all_planing_dates['mate'] = mate_day
        return mate_day

    def get_mate(self, date_mate=None, father=None):
        today = date.today()
        if date_mate is None:
            date_mate = today
        if father is not None and father in ['X','Y','Z']:
            date_mate_obj = datetime.strptime(date_mate, DATE_FORMAT).date() if isinstance(date_mate, str) else date_mate
            self.mate.setdefault(date_mate_obj, {})['father_line'] = father
            self.mate.setdefault(date_mate_obj, {})['result'] = '?'
            self.status = 'mated_mother' if self.status == 'mother' else 'mated'
            self.last_mate = date_mate_obj
            self.all_planing_dates.pop('mate', None)
            self.planing_palpation()
            return True
        else:
            self.history.append('X')
            self.status = None

            return False

    def planing_palpation(self)-> date:
        palpation_day = self.last_mate + timedelta(days=13)
        self.all_planing_dates['palpation'] = palpation_day

        return palpation_day

    def get_palpation(self, result, palp_date=None):
        if palp_date is None:
            palp_date = date.today()
        if result == '-':
            self.palpation.setdefault(palp_date, {})['result'] = 'negative'
            self.mate.setdefault(self.last_mate, {})['result'] = 'negative'
            self.history.append('-')
            self.last_palpation = datetime.strptime(palp_date, DATE_FORMAT).date() if isinstance(palp_date, str) else palp_date
            self.status = self.status if self.status in ['mother','mother*'] else None
            self.all_planing_dates.pop('palpation', None)
            self.planing_mate()
            logger.info(f'{palp_date}: {self.name} palpation result -')
            return False
        elif result == '+':
            self.palpation.setdefault(palp_date, {})['result'] = 'positive'
            self.mate.setdefault(self.last_mate, {})['result'] = 'positive'
            self.history.append('+')
            self.last_palpation = datetime.strptime(palp_date, DATE_FORMAT).date() if isinstance(palp_date, str) else palp_date
            self.status = 'waiting_for_kindling'
            self.all_planing_dates.pop('palpation')
            father = self.mate[[x for x in self.mate][-1]].get('father_line')
            self.nest = Nest(mother=self.name, father=father)
            self.planing_kindling()

            logger.info(f'{palp_date}: {self.name} palpation result +')
            return True
        elif result == '?':
            self.all_planing_dates['palpation'] = palp_date + timedelta(days=5)
            logger.info(f'{palp_date}: {self.name} palpation result ?. Next try for 7 days.')
            return None
        else:
            print(f'{self.name} not palpated.')
            return None

    def planing_kindling(self)-> date:
        kindling_date = self.last_mate + timedelta(days=31)
        self.all_planing_dates['kindling'] = kindling_date
        self.all_planing_dates['swap_box'] = kindling_date - timedelta(days=9)
        self.all_planing_dates['install_nest'] = self.nest.planning_date_for_install_and_prepare_nest(kindling_date)[0]
        self.all_planing_dates['prepare_nest'] = self.nest.planning_date_for_install_and_prepare_nest(kindling_date)[1]

        return kindling_date

    def get_kindling(self, total, alive, dead, formed, kind_date: date=None):
        if kind_date is None:
            kind_date = date.today()
        self.kindling[kind_date] = dict([('total',total),('alive',alive),('dead',dead),('formed',formed)])
        self.last_kindling = datetime.strptime(kind_date, DATE_FORMAT).date() if isinstance(kind_date, str) else kind_date
        self.history[-1] = [alive, dead, formed, '?'] if self.history[-1] == '+' else self.history.append([alive, dead, formed, '?'])
        self.status = 'mother' if formed else 'mother*'
        self.all_planing_dates.pop('kindling', None)
        self.all_planing_dates.pop('install_nest', None)
        self.all_planing_dates.pop('prepare_nest', None)
        if formed:
            father = self.mate[[x for x in self.mate][-1]].get('father_line')
            self.nest = Nest(mother=self.name, father=father)
            self.nest.date_birth = kind_date
            self.planning_resettle()
            dates = self.nest.planning_open_and_remove_nest_vaccination(datetime.strptime(kind_date, DATE_FORMAT).date() if isinstance(kind_date, str) else kind_date)
            self.all_planing_dates['open_nest'] = dates[0]
            self.all_planing_dates['remove_nest'] = dates[1]
            self.all_planing_dates['vaccination_nest'] = dates[2]
            self.nest.formed_nest(formed)
        else:
            self.nest = None
        self.planing_mate()

    def planning_resettle(self):
        resettle_day = self.last_kindling + timedelta(days=35)
        self.all_planing_dates['resettle'] = resettle_day

        return resettle_day

    def get_resettle_bunnies(self, resettle_date: date=None, bunnies: int=None, new_cage=None):
        date_resettle = resettle_date.strftime(DATE_FORMAT) if resettle_date is not None else date.today().strftime(DATE_FORMAT)
        quantity = bunnies if bunnies is not None else self.nest.get_resettle_nest(new_cage)
        self.kindling[self.last_kindling]['resettle'] = quantity
        self.history[-2][3] = quantity
        print(self.name, self.history)
        print(f'{quantity} bunnies moved to box {new_cage}.')
        self.all_planing_dates.pop('resettle', None)
        self.all_planing_dates.pop('open nest', None)
        self.all_planing_dates.pop('remove nest', None)
        self.nest = None
        self.status = None if self.status in ['mother', 'mother*'] else self.status

    def to_dict(self):
        data = self.__dict__.copy()

        data['birthday'] = self.birthday
        if self.last_mate:
            data['last_mate'] = self.last_mate.strftime(DATE_FORMAT)
        if self.last_palpation:
            data['last_palpation'] = self.last_palpation.strftime(DATE_FORMAT)
        if self.last_kindling:
            data['last_kindling'] = self.last_kindling.strftime(DATE_FORMAT)

        data['mate'] = {k.strftime(DATE_FORMAT) if isinstance(k, date) else k: v for k, v in self.mate.items()}
        data['palpation'] = {k.strftime(DATE_FORMAT) if isinstance(k, date) else k: v for k, v in self.palpation.items()}
        data['kindling'] = {k.strftime(DATE_FORMAT) if isinstance(k, date) else k: v for k, v in self.kindling.items()}
        data['all_planing_dates'] = {k: v.strftime(DATE_FORMAT) if isinstance(v, date) else v for k, v in self.all_planing_dates.items()}

        if self.nest is not None:
            data['nest'] = self.nest.to_dict()
        else:
            data['nest'] = None

        return data

class Nest:
    def __init__(self, **kwargs):
        self.mother = kwargs.get('mother')
        self.father = kwargs.get('father')
        self.status = kwargs.get('status')
        self.bunnies = kwargs.get('bunnies', {})
        self.output_cage = kwargs.get('output_cage')
        def parse_date(value):
            if isinstance(value, str):
                return datetime.strptime(value, DATE_FORMAT).date()
            return value
        self.date_birth = parse_date(kwargs.get('date_birth'))
        self.date_install = parse_date(kwargs.get('date_install'))
        self.date_open = parse_date(kwargs.get('date_open'))
        self.date_remove = parse_date(kwargs.get('date_remove'))

    def __str__(self):
        return (f'Mother {self.mother}, father {self.father}.'
                f' {self.nest_age}. Status - {self.status}'
                f'{self.bunnies}.')

    @property
    def nest_age(self):
        return (date.today() - self.date_birth).days if self.date_birth is not None else None

    def planning_date_for_install_and_prepare_nest(self, date_of_kindling):
        date_install = date_of_kindling - timedelta(days=7)
        date_prepare = date_of_kindling - timedelta(days=1)
        return date_install, date_prepare

    def planning_open_and_remove_nest_vaccination(self, date_kind):
        open_date = date_kind + timedelta(days=10)
        remove_date = date_kind + timedelta(days=20)
        vaccination_date = date_kind + timedelta(days=28)

        return open_date, remove_date, vaccination_date

    def clear_dates_for_nest(self):
        self.date_install = None
        self.date_open = None
        self.date_remove = None

    def install_nest(self, install: date=None):
        if install is None:
            install = date.today()

        self.status = 'install'
        self.bunnies = dict([('formed', 0), ('alive', 0)])
        self.date_install = install

    def prepare_nest(self):
        self.status = 'prepare'


    def formed_nest(self, formed: int):

        self.status = 'closed'
        self.bunnies['formed'] = formed
        self.bunnies['alive'] = formed

    def correct_quantity_of_nest(self, alive=0, dead=0):
         if self.bunnies.get('alive') is not None:
             self.bunnies['alive'] += alive
         if self.bunnies.get('dead') is not None:
             self.bunnies['dead'] += dead
             self.bunnies['alive'] -= dead

         self.bunnies['alive'] = alive

    def open_nest(self):

        if self.status != 'open':
            self.status = 'open'
            return True
        else:
            return False



    def remove_nest(self, remove=None):
        if remove is None:
            remove = date.today()
        self.status = 'remove'
        self.clear_dates_for_nest()
        self.date_remove = remove

    def get_resettle_nest(self, block=None, box=None):
        quantity = self.bunnies.get('alive', 0)
        self.output_cage = f'{block}.{box}'

        return quantity

    def to_dict(self):
        export_data = {
            'mother': self.mother,
            'father': self.father,
            'status': self.status,
            'bunnies': self.bunnies,
            'date_birth': self.date_birth.strftime(DATE_FORMAT) if isinstance(self.date_birth,date) else self.date_birth,
            'date_install': self.date_install.strftime(DATE_FORMAT) if isinstance(self.date_install, date) else self.date_install,
            'date_open': self.date_open.strftime(DATE_FORMAT) if isinstance(self.date_open, date) else self.date_open,
            'date_remove': self.date_remove.strftime(DATE_FORMAT) if isinstance(self.date_remove, date) else self.date_remove,
            'output_cage': self.output_cage
        }

        return export_data

class Box:
    def __init__(self, block, box, quantity, birth, status, mother=None, father=None,  kill_date=None):
        self.block = block
        self.box = box
        self.status = status
        self.quantity = quantity
        self.birth = birth
        if self.birth:
            self.birth: date|None = birth if isinstance(birth, date) else datetime.strptime(birth, DATE_FORMAT).date()
        else:
            self.birth = None
        self.mother = mother
        self.father = father
        self.kill_date: date|None = datetime.strptime(kill_date, DATE_FORMAT).date() if kill_date else None

    def __str__(self):
         return (f'Дата народження {self.birth}\n'
                 f'Статус {self.status if self.status else 'немає'}\n'
                f'Вік {self.box_age}\n'
                f'Кількість {self.quantity}\n'
                f'Дата забою {self.kill_date}') if self.birth else 'Клітка порожня'

    @property
    def box_age(self):
        if self.birth:
            return (date.today() - self.birth).days
        return 0

    @property
    def address(self):
        return f'{self.block}.{self.box}'

    @classmethod
    def from_dict_box(cls, data: dict):
        block = data['block']
        box = data['box']
        status = data['status']
        mother = data['mother']
        father = data['father']
        quantity = data['quantity']
        birth = datetime.strptime(data['birth'], DATE_FORMAT).date() if data.get('birth', None) else None
        kill_date = datetime.strptime(data['kill_date'], DATE_FORMAT).date() if data.get('kill_date', None) else None

        cage = cls(block=block, box=box, quantity=quantity, birth=birth, status=status, mother=mother, father=father, kill_date=kill_date)

        return cage

    def to_dict(self):
        data = self.__dict__.copy()
        if self.birth:
            data['birth'] = self.birth.strftime(DATE_FORMAT) if isinstance(data['birth'], date) else data['birth']
        else:
            data['birth'] = None

        if self.kill_date:
            data['kill_date'] = self.kill_date.strftime(DATE_FORMAT) if isinstance(data['kill_date'], date) else data['kill_date']
        else:
            data['kill_date'] = None
        return data

    def set_kill_date(self):
        if self.birth:
            date_of_kill = self.birth + timedelta(days=100)
            self.kill_date = date_of_kill