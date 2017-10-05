import csv
import datetime

# current_time = datetime.datetime.now()

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

class OpendagIR:
    def __init__(self, data_file="/home/nao/uva-home-2018/open_day_uva/opendagdata.csv"):
        self.eventlist = []
        with open(data_file, 'r') as csvfile:
            timetablereader = csv.reader(csvfile, delimiter=';')
            for row in timetablereader:
                self.eventlist.append(row)
        self.templist = self.eventlist
        self.filtered_events = self.remove_duplicates()


    def get_next_event(self, eventlist):
        """Return the earliest event in a given list."""
        earliest_event = eventlist[0]

        for event in self.templist:
            found_starttime = event[1]
            if self.earlier_time(found_starttime, earliest_event[1]):
                earliest_event = event
        return earliest_event

    def get_events_after(self, currenttime):
        result_list = []
        for event in self.templist:
            if self.earlier_time(event[1], currenttime):
                continue
            else:
                result_list.append(event)
        self.templist = result_list


    def get_events_between(self, begin_time, time_distance):
        """Return all events between begin_time and begin_time + time_distance."""
        result_list = []
        begin_hour = int(begin_time[0:2])
        begin_minute = int(begin_time[3:5])

        check = begin_minute + time_distance
        overflow = False

        if (check > 59):
            end_minutes = check % 60
            end_hour = begin_hour + (check // 60)
            overflow = True

        for event in self.templist:
            event_start_time = event[1]
            event_start_hour = int(event_start_time[0:2])
            event_start_minutes = int(event_start_time[3:5])

            if overflow:
                for i in range(begin_hour,end_hour+1):
                    if i == begin_hour:
                        if (event_start_hour == i) and (event_start_minutes > begin_minute):
                            result_list.append(event)
                            break

                    elif i == end_hour:
                        if (event_start_hour == i) and (event_start_minutes <= end_minutes):
                            result_list.append(event)
                            break
                    else:
                        if event_start_hour == i:
                            result_list.append(event)
                            break

            elif (event_start_hour == begin_hour) and (event_start_minutes > begin_minute):
                    result_list.append(event)

        self.templist = result_list


    def get_events_subject(self, subject):
        """Return all events on given subject."""
        result_list = []
        for event in self.templist:
            if subject in event[0].lower() or subject in event[4].lower() or subject in event[5].lower():
                result_list.append(event)
        self.templist = result_list


    def get_events_age(self, age):
        """Return all events for given age and up."""
        result_list = []

        for event in self.templist:
            if event[3] == "all":
                result_list.append(event)
                continue
            if int(event[3]) <= age:
                result_list.append(event)

        self.templist = result_list


    def remove_duplicates(self):
        """Removes duplicate events, takes the earliest version of the event in list."""
        event_dict = {}
        result_list = []
        for event in self.templist:
            if event[0] in event_dict.keys():
                saved_starttime = event_dict[event[0]][1]
                found_starttime = event[1]
                if self.earlier_time(found_starttime, saved_starttime):
                    event_dict[event[0]] = event
            else:
                event_dict[event[0]] = event
        for event in event_dict.values():
            result_list.append(event)
        self.templist = result_list

    def earlier_time(self, time_a, time_b):
        """Returns true if a is earlier than b"""
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



def main():
    ir = OpendagIR()
    # filtered_events = get_events_between(current_time, time_distance, eventlist)
    # get all chemistry events
    # filtered_events = get_events_subject("chemistry", eventlist)
    filtered_events = ir.get_events_age(6)
    print(ir.filtered_events)
    print(len(ir.filtered_events))

if __name__ == '__main__':
    main()
