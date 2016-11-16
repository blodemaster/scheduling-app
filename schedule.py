from datetime import *
from sys import exit
import pickle
import os.path


class Person(object):
    """class used for a person

    Attributes:
    name: person's name
    email: person's address
    schedule: person's datetime for meeting, passed meeting will be deleted when the show_schedule function are called
    meetings: meeting's date and its corresponding name. It will be kept in case of searching history
    """
    def __init__(self, name, email):
        """initial Person with name, email, upcoming schedule and information of meeting attended. """
        self.name = name
        self.email = email
        self.schedule = {}  # date as key, time set as value
        self.meetings = {}  # date as key, meetings as value

    def set_meeting(self, date, time, meeting):
        """add new meeting time and meeting information for this person"""
        if date not in self.schedule:   # initialize schedule/meetings if chosen date are not in database before.
            self.schedule[date] = set()
            self.meetings[date] = []
        else:
            if time in self.schedule[date]:  # check time is free or not
                print self.name + "'s time has been occupied, please choose other person."
                return 0
        self.schedule[date].add(time)
        self.meetings[date].append(meeting)
        return 1

    def find_meeting(self, time, date):
        """given date and time, return the name of it corresponding meeting"""
        for m in self.meetings[date]:
            if m.meetingTime == time:
                return m.ID

    def show_schedule(self):
        """print the schedule of this person"""
        self.remove_old_schedule()
        print "Below is the schedule of " + self.name
        print "Date        Time             Meeting name"
        for date in sorted(self.schedule):   # output date in chronological order
            print date.strftime("%Y-%m-%d") + " ",      # print date
            for time in sorted(self.schedule[date]):    # output time in chronological order
                print time.strftime("%I:%M%p") + "-" + (time + timedelta(hours=1)).strftime("%I:%M%p") + " ",
                print self.find_meeting(time, date),
            print ""

    # def show_certain_schedule(self):
    #     """display the schedule for a given day """
    #     raw_date = raw_input("please enter the date of the meeting(YYYY-MM-DD): ")
    #     date = datetime.strptime(raw_date, "%Y-%m-%d").date()
    #     for time in sorted(self.schedule[date]):
    #         print time.strftime("%I:%M%p") +"-" + (time + timedelta(hours=1)).strftime("%I:%M%p"),   # print time
    #         print self.find_meeting(time, date),
    #         print ""

    def remove_old_schedule(self):
        """remove the schedule information of meetings which have been held before today"""
        for date in sorted(self.schedule):  # remove elements that pass current day
            if date < date.today():
                del self.schedule[date]
            if date == date.today():    # remove elements that pass current time
                delSet = set()
                for time in self.schedule[date]:
                    if time.time() < datetime.now().time():
                        delSet.add(time)
                for i in delSet:
                    self.schedule[date].remove(i)
                if len(self.schedule[date]) == 0:
                    del self.schedule[date]


class Meeting(object):
    """class used for meeting

    Attributes:
    participants: naming list of participants
    meetingTime: when the meeting is held
    availableTime: meeting can only be held in certain time(
    """
    def __init__(self, availableTime):
        self.participants = []
        self.meetingTime = 0
        self.meetingDate = 0
        self.availableTime = availableTime
        self.ID = raw_input("please enter the name of meeting: ")

    def set_time(self):
        """set date and time for a meeting"""
        print "The meeting can only last one hour. "
        while True:
            try:
                # enter the date
                raw_date = raw_input("please enter the date of the meeting(YYYY-MM-DD): ")
                date = datetime.strptime(raw_date, "%Y-%m-%d").date()
                # check the date is valid or not
                if date < date.today():
                    print "this date passed, please choose new date"
                    continue

                while True:
                    # enter the time
                    print "Now enter the timing(24hour format)"
                    print "Time can only be at the hour mark and during working time"
                    print "If you want to quit, please enter 'q'"
                    raw_time = raw_input("please enter the start time of the meeting: ")
                    if raw_time == 'q':
                        return
                    # check whether time is within working time
                    time = datetime.strptime(raw_time, "%H")
                    # check whether time is early than current time
                    if date == date.today():
                        if time.time() < datetime.now().time():
                            print "this time passed, please choose new.\n"
                            continue
                    if time not in self.availableTime:
                        print "Time is invaild, please choose new time\n"
                        continue
                    else:
                        self.meetingTime = time     # set time for meeting
                        break
                # set date for meeting
                self.meetingDate = date
                break
            # if input is not a valid time(ex. 25 for time)
            except ValueError:
                print "Time is invalid, please re-enter"

    def add_participants(self, database):
        """add partcipants for this meeting"""
        while True:
            # check if given person exist in database
            name = raw_input("Please enter the name of a person who would attend this meeting: ")
            if name not in database:
                print "We do not have information for this person, please check"
            else:
                # identify the person of interest because sometime few persons could have same names
                person = identify_person(database, name)
                # add this meeting time to person
                check = person.set_meeting(self.meetingDate, self.meetingTime, self)
                # if time is avaiable, add this person to the meeting list
                if check == 1:
                    self.participants.append(person)
            while True:
                flag = raw_input("Enter 'y' to add participant for this meeting, Enter 'n' to stop: ")
                if flag == "y":
                    break
                elif flag == "n":
                    return
                else:
                    print 'Invalid input, please enter correct letter'
                    continue


def add_member(emailList, database):
    """add new person to database, add email to emailList
    emailList are used to make sure the process of checking email fast"""
    name = raw_input("please enter the name of a person: ")
    email = raw_input("please enter his/her email address: ")
    # email address should be unique
    if email in emailList:
        print "This email address has existed, please check."
    # add information to database
    else:
        if name in database:
            database[name].append(Person(name, email))
        else:
            database[name] = []
            database[name].append(Person(name, email))
        emailList.append(email)
        print "done"


def set_availableTime():
    """let user to define which hour can be used for meeting
    the start time of meeting will be stored"""
    availableTime = set()
    while True:
        input = raw_input("please enter the range of working hours(ex. 8-12 or 13-16)"
                          "if time is not continuous, please enter separately: ")
        input = input.split("-")
        # change time span to independent time points(ex, input:8-12, final:[8,9,10,11]. the reason why it does not
        # include '12' is because '12' is the end of time period, so it can not be the start time of a meeting)
        raw_time = int(input[0])
        while raw_time < int(input[-1]):
            time = datetime.strptime(str(raw_time), "%H")
            availableTime.add(time)
            raw_time += 1

        while True:
            f = raw_input("Enter 'y' to add more, Enter 'n' to end setting: ")
            if f == "y":
                break
            elif f == "n":
                return availableTime
            else:
                print "invalid input, please enter correct letter."
                continue


def identify_person(database, name):
    """ Sometimes there will be several people stored in database with same name, so showing their email
    to enable user can choose the one he/she wanted """
    if len(database[name]) > 1:
        print ("Database have more than one persons with same names."
        "Below is the different email information for given name")
        for i in database[name]:
            print i.email
        index = int(raw_input("please specify the person you wanted by entering his/her ranking(ex. 1 or 2):"))
        person = database[name][index - 1]
    # if name is unique, just return that person
    else:
        person = database[name][0]
    return person


def store_data(database, emailList, meetingSet):
    """create three files on local computer to store the information
    database: all person's information
    emailList: all email address
    meetingSet: all meeting details
    """
    output_person = open("PersonInformation.pkl", "wb")
    pickle.dump(database, output_person)
    output_person.close()

    output_email = open("EmailList.pkl", "wb")
    pickle.dump(emailList, output_email)
    output_email.close()

    output_meeting = open("MeetingInformation.pkl", "wb")
    pickle.dump(meetingSet, output_meeting)
    output_meeting.close()


def initialize_data():
    """initialize three files later used for storing information """
    emptyPersons = dict()
    emptyEmail = []
    emptyMeeting = []
    store_data(emptyPersons, emptyEmail, emptyMeeting)


def read_data():
    if (os.path.isfile("./PersonInformation.pkl") and os.path.isfile("./EmailList.pkl")
    and os.path.isfile("./MeetingInformation.pkl")):
        pass
    else:
        print "one or more files do not exist"
        opt = raw_input("If it is first time you run this program, please enter 'y'. "
                        "If not, please enter anything else to quit the program and contact software provider to avoid.\n")
        if opt == 'y':
            initialize_data()
        else:
            exit()
    database = pickle.load(open("PersonInformation.pkl", "rb"))
    emailList = pickle.load(open("EmailList.pkl", "rb"))
    meetingSet = pickle.load(open("MeetingInformation.pkl", "rb"))
    return database, emailList, meetingSet


def create_meeting(availableTime, database, meetingSet):
    """create new meeting of given date/time, and add participant to meeting"""
    new_meeting = Meeting(availableTime)
    meetingSet.append(new_meeting)
    new_meeting.set_time()
    new_meeting.add_participants(database)


def show_schedule(database):
    """display the schedule for given person"""
    name = raw_input("please enter the name of person: ")
    if name in database:
        person = identify_person(database, name)
        person.show_schedule()
    else:
        print "this name does not exsit, please check."


def print_timeslots(timeSet):
    """if several free time intervals are continuous, then add them together
    ex. data: set([8.00-9.00, 9.00-10.00]) then output is '8.00-10.00' """
    timeSet = sorted(timeSet)
    begin = 0
    for i in range(len(timeSet)-1):
        if (timeSet[i] + timedelta(hours=1)) != timeSet[i+1]:
            print timeSet[begin].strftime("%H:%M%p") + "-" + (timeSet[i] + timedelta(hours=1)).strftime("%H:%M%p")
            begin = i+1
    print timeSet[begin].strftime("%H:%M%p") + "-" + (timeSet[-1] + timedelta(hours=1)).strftime("%H:%M%p")


def common_free_time(database, availableTime):
    """find the available meeting time for choosen people """
    group = []
    # add people that you want to find available time for meeting
    flag = True
    while flag:
        name = raw_input("select a person: ")
        person = identify_person(database, name)
        group.append(person)
        while True:
            f = raw_input("type 'y' to add more, type 'n' to end setting: ")
            if f == "y":
                break
            elif f == "n":
                flag = False
                break
            else:
                print "Invalid input, please enter correct letter."
                continue
    # initialize day with today and try to find common free time for given persons
    day = date.today()
    # find union of unavailable time for given persons
    while True:
        union = set()
        for individual in group:
            if day in individual.schedule:
                union = union | individual.schedule[day]
        # find free time
        free_time = availableTime - union
        # check whether selected day has free time, if answer is no, move on next day
        if len(free_time) == 0:
            day = day + timedelta(days=1)
            continue
        else:
            # if date is today, make sure free time is later than current time
            if day == date.today():
                delSet = set()
                for time in free_time:
                    if time.time() < datetime.now().time():
                        delSet.add(time)
                for i in delSet:
                    free_time.remove(i)
                if len(free_time) != 0:
                    print day.strftime("%Y-%m-%d")
                    print_timeslots(free_time)
                else:
                    day = day + timedelta(days=1)
                    continue

            else:
                print day.strftime("%Y-%m-%d")
                print_timeslots(free_time)

        # decide whether to show more free time for later days.
        choose = raw_input("if you want to see more free time, type 'y', type any letter to quit: ")
        if choose == "y":
            day += timedelta(days=1)
            continue
        else:
            break


def main():
    print "****************************Welcome****************************"

    # load pre-defined available meeting time
    try:
        f = open("AvailableHours.pkl", "rb")
        available_hour = pickle.load(f)
    # if local path does not include the file that stores information for available working hours
    except IOError:
        print "You have not set the working hour, please set the available hours for meeting of a day."
        available_hour = set_availableTime()
        f = open("AvailableHours.pkl", "wb")
        pickle.dump(available_hour, f)
        f.close()

    database, emailList, meetingSet = read_data()

    while True:
        print "---------------------------------------------------------------"
        print "enter '1' to create a new person."
        print "enter '2' to create a new meeting."
        print "enter '3' to show the schedule of a given person."
        print "enter '4' to find available timeslot for a given group of people"
        print "enter '5' to quit program"

        option = raw_input("please type your option: ")
        if option == "1":
            print "---------------------------------------------------------------"
            add_member(emailList, database)
        elif option == "2":
            print "---------------------------------------------------------------"
            create_meeting(available_hour, database, meetingSet)
        elif option == "3":
            print "---------------------------------------------------------------"
            show_schedule(database)
        elif option == "4":
            print "---------------------------------------------------------------"
            common_free_time(database, available_hour)
        elif option == "5":
            store_data(database, emailList, meetingSet)
            exit()
        else:
            print "invalid input, please re-enter"
        continue

main()




