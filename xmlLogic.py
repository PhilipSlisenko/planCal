import random
import string
import urllib.request
import xml.etree.ElementTree as ET
from ics import Calendar, Event
import arrow

def getDataFromXml(url):
    """
    input: PlanZajec url
    output: {groupName, od, do, [classes]}
            returns unique classes
    """

    xml = urllib.request.urlopen(url + "&xml")  # making request
    tree = ET.parse(xml)

    dataToReturn = dict()

    root = tree.getroot()
    try:
        groupName, od, do = root.attrib["nazwa"], root.attrib["od"], root.attrib["do"]
    except:
        groupName, od, do = "Group Name", "", ""

    dataToReturn['groupName'] = groupName
    dataToReturn['od'] = od
    dataToReturn['do'] = do
    dataToReturn['url'] = url

    classes = list()
    keys = list()  # list of keys (concatenated values of each class). Used to check if class was already encountered
    # indexes of columns ['termin', 'dzien', 'od-godz', 'do-godz', 'przedmiot', 'typ', 'nauczyciel', 'sala', 'uwagi']
    interestedIndexes = [1, 2, 3, 4, 5]
    countOfOccurances = dict()
    for event in tree.iter("zajecia"):
        newEvent = dict()
        key = str()
        for i in interestedIndexes:
            key += event[i].text or ""
            newEvent[event[i].tag] = event[i].text or ""
        if key not in keys:
            newEvent["key"] = key
            classes.append(newEvent)
            keys.append(key)
            countOfOccurances[key] = 1
        else:
            countOfOccurances[key] += 1
    for clas in classes:
        clas['num'] = countOfOccurances[clas['key']]
        # del clas['key'] dont know yet
    classes.sort(key=lambda dic: (
        dic['przedmiot'], dic['typ'], dic['od-godz'], dic['num']))
    # for dic in classes:
    #     print("{:<60}{:<20}{:<10}{:<10}{:<10}{:<10}".format(
    #         dic['przedmiot'], dic['typ'], dic['dzien'], dic['od-godz'], dic['do-godz'], dic['num']))
    dataToReturn['classes'] = classes

    return dataToReturn


def addCheckedProperty(timetable):
    timetable = timetable.copy()
    for c in timetable['classes']:
        c['checked'] = True
    return timetable


def prepareDataForIcsConvertor(keys_and_url):
    keys = keys_and_url['classes']
    url = keys_and_url['url']  # NEED IN REQ
    xml = urllib.request.urlopen(url + "&xml")
    tree = ET.parse(xml)
    keyIndexes = [1, 2, 3, 4, 5]  # same as interestedIndexes in getDataFromXml
    # ['termin', 'dzien', 'od-godz', 'do-godz', 'przedmiot', 'typ', 'nauczyciel', 'sala', 'uwagi']
    interestedIndexes = [0, 2, 3, 4, 5, 6, 7]
    dataToReturn = list()
    for event in tree.iter("zajecia"):
        newEvent = dict()
        #create key for each class
        key = str()
        for i in keyIndexes:
            key += event[i].text or ""

        if key not in keys:
            continue
        for i in interestedIndexes:
            newEvent[event[i].tag] = event[i].text or ""

        dataToReturn.append(newEvent)
    return dataToReturn

def gen_cal_and_save(events_info):
    c = Calendar()
    for event_info in events_info:
        e = Event()
        e.name = event_info['przedmiot']
        e.begin = arrow.get(event_info['termin'] + " " + event_info['od-godz'],
                            "YYYY-MM-DD HH:mm").replace(tzinfo="Europe/Warsaw")  # "2019-03-26 16:45"
        print(e.begin)
        e.end = arrow.get(event_info['termin'] + " " + event_info['do-godz'],
                          "YYYY-MM-DD HH:mm").replace(tzinfo="Europe/Warsaw")
        print(e.end)
        e.location = event_info['sala']
        e.description = event_info['typ'] + "\n" + event_info['nauczyciel']
        c.events.add(e)
    cal_file_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    with open('./converted_cals/' + cal_file_name + '.ics', 'w', encoding="utf-8") as f:
        f.writelines(c)
    return cal_file_name


def create_cal(keys_and_url_arr):
    dict_arr = list() #array of dictioanaries with info about each class (time beg, end, Title, Professor...)
    for keys_and_url in keys_and_url_arr:
        dict_arr.extend(prepareDataForIcsConvertor(keys_and_url))
    return gen_cal_and_save(dict_arr)

