from datetime import date, timedelta
from requests_html import HTMLSession
import json


def get_string_date(inputDay):
    day_string = str(inputDay.month) + '/' + str(inputDay.day) + '/' + str(inputDay.year)
    return day_string


def make_date_type(day):
    daySplit = day.split("/")
    day = date(int(daySplit[2]), int(daySplit[1]), int(daySplit[0]))
    return day


def user_login():
    first_name = input("First name: ")
    last_name = input("Last name: ")
    return first_name + "." + last_name


def get_html_data(username, day):
    session = HTMLSession()
    url = 'http://edtmobilite.wigorservices.net/WebPsDyn.aspx?Action=posETUD&serverid=i&tel=' + username + '&date=' + day + '%208:00'
    response = session.get(url)
    return response


def get_lessons_info(htmldata):
    lessons = dict()
    lines = htmldata.html.find('.Ligne')
    if lines:
        for i in range(len(lines)):
            matiere = (lines[i].find('.Matiere', first="true")).text
            debut = (lines[i].find('.Debut', first="true")).text
            fin = (lines[i].find('.Fin', first="true")).text
            prof = (lines[i].find('.Prof', first="true")).text
            salle = (lines[i].find('.Salle', first="true")).text
            lessons[str(i)] = {"matiere": matiere, "debut": debut, "fin": fin, "prof": prof, "salle": salle}
        return lessons
    else:
        return None


def get_day_info(day, htmldata):
    dayInfo = dict()
    day_lessons = get_lessons_info(htmldata)
    if day_lessons:
        dayInfo[day] = day_lessons
    else:
        dayInfo[day] = None
    return dayInfo


def save_to_json(data):
    with open('../data/data.json', 'w') as outfile:
        json.dump(data, outfile)


def user_choice_menu():
    print("Input 1 to get info from a specific day")
    print("Input 2 to get info from a special week")
    print("Input 3 save calendar until specific day")
    user_input = input()
    return user_input


def day_info_choice():
    day = input("What day do you want to see (dd/mm/yyyy)")
    day = make_date_type(day)
    day = get_string_date(day)
    response = get_html_data(username, day)
    if response.html.search("Erreur"):
        print("Could not get from the calendar with the date " + day + "and username " + username)
    else:
        info = get_day_info(day, response)
        return info


def week_info_choice():
    week = dict()
    firstDay = input("Enter the date of the first day of the week you want to see (dd/mm/yyyy)")
    firstDay = make_date_type(firstDay)
    for i in range(5):
        day = firstDay + timedelta(i)
        day = get_string_date(day)
        response = get_html_data(username, day)
        if response.html.search("Erreur"):
            print("Could not get from the calendar with the date " + date + "and username " + username)
        else:
            dayInfo = get_day_info(day, response)
            week.update(dayInfo)
    return week


def save_calendar():
    agenda = dict()
    last_day = input("Enter the day you wish to save your calendar to (dd/mm/yyyy)")
    last_day = make_date_type(last_day)
    today = date.today()
    total_days = (last_day - today).days - 1
    for i in range(total_days):
        day = today + timedelta(i)
        if day.weekday() < 5:
            day = get_string_date(day)
            response = get_html_data(username, day)
            if response.html.search("Erreur"):
                print("Could not get from the calendar with the date " + date + "and username " + username)
            else:
                dayInfo = get_day_info(day, response)
                agenda.update(dayInfo)
    return agenda


username = user_login()
dictdata = dict()
user_choice = user_choice_menu()
if user_choice == "1":
    day_info = day_info_choice()
    dictdata.update(day_info)
    save_to_json(dictdata)
elif user_choice == "2":
    dictdata = week_info_choice()
    save_to_json(dictdata)
elif user_choice == "3":
    dictdata = save_calendar()
    save_to_json(dictdata)
else:
    print("You did not input the right value")
