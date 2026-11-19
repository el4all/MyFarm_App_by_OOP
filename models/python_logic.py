from datetime import  date, timedelta
from models.bunny_class import Farm, Bunny, STATUS_WORK, DATE_FORMAT


def preparing_work_data(farm: Farm):
    yesterday_dict = {}
    today_dict = {}
    tomorrow_dict = {}

    yesterday = date.today() - timedelta(days=1)
    today = date.today()
    tomorrow = date.today() + timedelta(days=1)

    for r in farm.rabbits.values():
        for work, day in r.all_planing_dates.items():
            if day == yesterday:
                yesterday_dict.setdefault(r.name, STATUS_WORK[work])
            elif day == today:
                today_dict.setdefault(r.name, STATUS_WORK[work])
            elif day == tomorrow:
                tomorrow_dict.setdefault(r.name, STATUS_WORK[work])

    print('Y:',yesterday_dict)
    print('T:',today_dict)
    print('T+1:',tomorrow_dict)

    return yesterday_dict, today_dict, tomorrow_dict


def get_data_widget_for_works_by_day(data: dict[str, str] | None):
    if data:
        processes = {}
        for name, process in data.items():
            processes.setdefault(process, []).append(name)

        return processes
    else:
        return {}

def preparing_data_for_blocks_in_third_room(block, farm: Farm):

    data = {}
    dates_of_group = sorted(list(set([x.birth for x in farm.third_room.values() if x.birth])))

    if dates_of_group:
        for b in farm.third_room.values():
            if b.block == block and b.birth in dates_of_group:
                data.setdefault(b.box_age, []).append(b.quantity if b.quantity else 0)

    return data

def average_age_farm(farm: Farm, sex: str):
    quantity = len([x for x in farm.rabbits.values() if x.sex == sex])
    age = sum([x.age for x in farm.rabbits.values() if x.sex == sex])

    return round(age//quantity)

def get_planned_work(farm: Farm, need_date: date):

    filtered_data = {}
    final_data = {}

    for obj in farm.rabbits.values():
        for process, day in obj.all_planing_dates.items():
            if day == need_date and obj.status != 'culling':
                filtered_data.setdefault(process, []).append(obj.name)

    for box in farm.third_room.values():
        if box.kill_date == need_date:
            filtered_data.setdefault('mass_kill', []).append(box.address)
    print('from python_logic.py',filtered_data)
    if filtered_data:
        for p,l in filtered_data.items():
            final_data[p] = (sorted(l, key=lambda x: (farm.third_room[x].block,farm.third_room[x].box))
                if p == 'mass_kill' else sorted(l, key=lambda x: (farm.rabbits[x].block,farm.rabbits[x].box)))

    return final_data

def get_status_for_mate(farm: Farm, name: str):
    if farm.rabbits[name].status == 'new':
        return 'new'
    elif farm.rabbits[name].status == 'mother' or 'mother*' and isinstance(farm.rabbits[name].history[-1], list):
        return 'mother'
    else:
        return None