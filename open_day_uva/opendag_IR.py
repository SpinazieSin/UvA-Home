import csv
import datetime

current_time = datetime.datetime.now()

def main(filename):
    with open(filename, 'r') as csvfile:
        timetablereader = csv.reader(csvfile, delimiter=';')
        eventlist = []
        for row in timetablereader:
            eventlist.append(row)

    # filtered_events = get_events_between(current_time, time_distance, eventlist)
    # get all chemistry events

    # filtered_events = get_events_subject("chemistry", eventlist)
    filtered_events = remove_duplicates(eventlist)
    filtered_events = get_events_age(6, filtered_events)
    print(filtered_events)
    print(len(filtered_events))


#return a list with events that start within the hour
# noahs practice stuff
# def current_events(current_time):
#     for event in eventlist:
#         print("len event: ", len(event))
#         event_start = event[1]
#         event_end = event[2]
#
#         event_start_time = datetime.datetime.strptime(event_start, "%H:%M")
#         print(event_start)
#         #compare current_time to event_start_time
#         if current_time < event_start_time:


def get_events_between(begin_time, time_distance, eventlist):
    """Return all events between begin_time and begin_time + time_distance."""
    result_list = []
    return result_list


def get_events_subject(subject, eventlist):
    """Return all events on given subject."""
    result_list = []
    for event in eventlist:
        if subject in event[0].lower() or subject in event[4].lower() or subject in event[5].lower():
            result_list.append(event)
    return result_list


def get_events_age(age, eventlist):
    """Return all events for given age and up."""
    result_list = []

    for event in eventlist:
        if event[3] == "all":
            result_list.append(event)
            continue
        if int(event[3]) <= age:
            result_list.append(event)

    return result_list


def get_events(filename):
    with open(filename, 'r') as csvfile:
        timetablereader = csv.reader(csvfile, delimiter=';')
        eventlist = []
        for row in timetablereader:
            eventlist.append(row)
    return eventlist

def remove_duplicates(eventlist):
    """Removes duplicate events, takes the earliest version of the event in list."""
    event_dict = {}
    result_list = []
    for event in eventlist:
        if event[0] in event_dict.keys():
            saved_starttime = event_dict[event[0]][1]
            found_starttime = event[1]
            if earlier_time(found_starttime, saved_starttime):
                event_dict[event[0]] = event
        else:
            event_dict[event[0]] = event

    for event in event_dict.values():
        result_list.append(event)

    return result_list

def earlier_time(time_a, time_b):
    "Returns true if a is earlier than b"
    hour_a = int(time_a[0:2])
    hour_b = int(time_b[0:2])
    minutes_a = int(time_a[3:5])
    minutes_b = int(time_b[3:5])
    if hour_a < hour_b:
        return True
    elif hour_a == hour_b:
        if minutes_a < minutes_b:
            return True
    return False


if __name__ == '__main__':
    main()
