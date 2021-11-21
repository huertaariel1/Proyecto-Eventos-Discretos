from .auxiliar_methods import *
from .person import *
from .const import *
from sortedcontainers import SortedSet

class Event:
    def __init__(self, event_time, event_id, event_name, person_list):
        self.time = event_time
        self.id = event_id
        self.name = event_name
        self.list = person_list

class Evolving_Population:
    def __init__(self,M, H):
        self.M = M
        self.H = H
        self.n = M + H
        self.population = []
        self.t = 0
        self.event_count = 0
        self.T = 1200
        self.death_count = 0
        self.want_a_partner_count = 0
        self.establish_couple_count = 0
        self.breakup_count = 0
        self.get_pregnant_count = 0
        self.giving_birth_count = 0
        self.lonely_time_over_count = 0
        
        population = []
        for i in range(M + H):
            age = uniform(0,100)
            if i + 1 > M :
                person = self.new_person(i+1, age, False)
            else:
                person = self.new_person(i+1, age)

            population.append(person)

        self.population = population

    def new_person(self, _id, age, is_woman = True):
        person = None

        if is_woman:
            person = Woman(_id, age)

            for key in pregnancy_prob.keys():
                if person.age > key[1]:
                    continue
                X = uniform(0,1)
                if X < pregnancy_prob[key]:
                    person.can_get_pregnant.append(key)
        
        else:
            person = Person(_id, age)
        
        death_age = 125
        #X = uniform(0,1)
        for key in death_prob.keys():
            if person.age > key[1]:
                continue
            X = uniform(0,1)
            prob = death_prob[key][1] if person.is_woman else death_prob[key][0]
            if X < prob:
                lb = key[0] if key[0] >= person.age else person.age
                death_age = int(uniform(lb, key[1] - 1))
                break
        person.death_age = death_age

        event_time = self.t + (person.death_age - person.age) * 12
        event_name = "death_event"
        self.add_event(event_name, event_time, [person])

        for key in want_a_partner_prob.keys():
            if person.age > key[1]:
                continue
            X = uniform(0,1)
            if X < want_a_partner_prob[key]:
                person.want_partner_age.append(key)
        
        if len(person.want_partner_age) > 0:
            lb = person.want_partner_age[0][0]
            ub = person.want_partner_age[0][1]

            if lb <= person.age and person.age < ub:
                person.is_ready = True
                event_name = "want_a_partner_event"
                event_time = self.t
                self.add_event(event_name,event_time,[person])
            else:
                event_time = self.t + (lb - person.age) * 12 - person.until_birthday
                event_name = "want_a_partner_event"
                self.add_event(event_name,event_time,[person])
        
        p = uniform(0,1)
        person.max_children_number = get_max_children_number(p)
        
        return person
    
    def death_event(self,person):
        if person.partner > 0:
            event_time = self.t
            event_name = "widow_event"
            partner = self.find_person(person.partner)
            if partner != -1:
                self.add_event(event_name, event_time, [partner])

        person.is_dead = True
        self.population.remove(person)

        self.n -= 1
        if person.is_woman:
            self.M -= 1
        else:
            self.H -= 1
    
    def want_a_partner_event(self, person):
        if person.partner > 0 or not person.is_ready:
            return
        
        single_list = self.get_single_people()
        if person.is_woman:
            single_list = single_list[1]
        
        else:
            single_list = single_list[0]

        for single in single_list:
            age_gap = abs(single.age - person.age)
            for key in establish_couple_prob.keys():
                if key[0] <= age_gap < key[1]:
                    X = uniform(0,1)
                    if X < establish_couple_prob[key] and person.partner == 0 and single.partner == 0:
                        event_time = self.t
                        event_name = "establish_couple_event"
                        person.partner = single.id
                        single.partner = person.id
                        person_list = [person, single] if person.is_woman else [single, person]
                        self.add_event(event_name,event_time,person_list)
                        return
        
        if len(person.want_partner_age) > 0:

            for age_range in person.want_partner_age:
                lb = age_range[0]
                ub = age_range[1]
                age_next_month = person.age + 1 if person.until_birthday + 1 == 12 else person.age
            if lb <= age_next_month and age_next_month < ub:
                person.is_ready = True
                event_name = "want_a_partner_event"
                event_time = self.t + 1
                self.add_event(event_name,event_time,[person])
                return

            person.is_ready = False        

    def establish_couple_event(self, woman, man):
        p = uniform(0,1)
        if p < breakup_prob:
            event_time = int(uniform(self.t, self.t + 50 * 12))
            event_name = "breakup_event"
            self.add_event(event_name,event_time,[woman,man])
        
        if man.children_count >= man.max_children_number or woman.children_count >= woman.max_children_number:
            return

        boolean = False
        for range in woman.can_get_pregnant:
            if range[0] <= woman.age and woman.age < range[1]:
                boolean = True
                break

        if boolean and not woman.is_pregnant:
            woman.is_pregnant = True
            event_time = self.t
            event_name = "get_pregnant_event"
            self.add_event(event_name,event_time, [woman, man])
    
    def get_pregnant_event(self, woman, man):
        p = uniform(0,1)
        multipregnancy_count = get_multipregnancy_count(p)
        woman.multiple_pregnancy = multipregnancy_count
        event_time = self.t + 9
        event_name = "giving_birth_event"
        self.add_event(event_name,event_time,[woman, man])
    
    def breakup_event(self, woman, man):
        for key in waiting_time_lambda.keys():
            waiting_time = 0

            if woman.age > key[1] and man.age > key[1]:
                continue

            if key[0] <= woman.age and woman.age < key[1]:
                waiting_time =  exponential_inverse_trans(1/waiting_time_lambda[key])
                woman.partner = 0
                woman.is_ready = False
                event_name = "lonely_time_over_event"
                event_time = self.t + int(waiting_time)
                self.add_event(event_name,event_time,[woman])
            
            if key[0] <= man.age and man.age < key[1]:
                waiting_time =  int(exponential_inverse_trans(1/waiting_time_lambda[key]) )
                man.partner = 0
                man.is_ready = False
                event_name = "lonely_time_over_event"
                event_time = self.t + int(waiting_time)
                self.add_event(event_name,event_time,[man])

    def widow_event(self, person):
        for key in waiting_time_lambda.keys():
            waiting_time = 0

            if person.age > key[1]:
                continue

            if key[0] <= person.age and person.age < key[1]:
                waiting_time =  exponential_inverse_trans(1 / waiting_time_lambda[key])
                person.partner = 0
                person.is_ready = False
                event_name = "lonely_time_over_event"
                event_time = self.t + int(waiting_time)
                self.add_event(event_name, event_time, [person])
                break
    
    def lonely_time_over_event(self, person):
        if person.is_dead:
            return

        person.ready = True
        for range in person.want_partner_age:
            if range[0] <= person.age and person.age < range[1]:
                event_name = "want_a_partner_event"
                event_time = self.t 
                self.add_event(event_name,event_time,[person])

    def giving_birth_event(self, woman, man):       
        #Population growth
        if woman.is_dead:
            return
        last_index = self.population[-1].id 
        for i in range(woman.multiple_pregnancy):
            id = i + 1 + last_index
            X = uniform(0,1)
            if X < sex_baby_prob:
                new_child = self.new_person(id,0)     
                self.M += 1
            else:
                new_child = self.new_person(id, 0, False)
                self.H += 1
            self.population.append(new_child)
            self.n += 1

        woman.multiple_pregnancy = 0
        woman.is_pregnant = False
        woman.have_a_child(woman.multiple_pregnancy)
        man.have_a_child(woman.multiple_pregnancy)

        if man.partner != woman.id:
            return

        if man.children_count >= man.max_children_number or woman.children_count >= woman.max_children_number:
            return

        boolean = False
        for _range in woman.can_get_pregnant:
            if _range[0] <= woman.age and woman.age < _range[1]:
                boolean = True
                break

        if boolean and not woman.is_pregnant:
            woman.is_pregnant = True
            event_time = self.t
            event_name = "get_pregnant_event"
            self.add_event(event_name,event_time, [woman, man])
    
    def find_person(self, _id):
        for person in self.population:
            if person.id == _id:
                return person
    
        return -1
    
    def get_single_people(self):
        single_men = []
        single_women = []

        for person in self.population:
            if person.is_woman and person.is_ready and person.partner == 0:
                single_women.append(person)
            if not person.is_woman and person.is_ready and person.partner == 0:
                single_men.append(person)

        return [single_women,single_men]
    
    def print_terminal(self, event_name):
        year = int(self.t / 12)
        print("<------------------------ Month: ",self.t ," Year: ",year ," --------------------------------------->")
        print("--------------------------------------------------------------------------------------------")
        print()
        print("------------------------- Event: ",event_name, " -------------------------------------")
        print()
        print()
        print("------------------------- Total number of people: ",self.n, " -------------------------------------")
        print()
        print("------------------------- Total number of men: ",self.H, "    -------------------------------------" )
        print("------------------------- Total number of women: ",self.M, "  -------------------------------------" )
        print("---------------------------------------------------------------------------------------------")
        print()
        print()
        print("------------------------- Count of death events: ",self.death_count, "    -------------------------------------" )
        print("------------------------- Count of want a partner events: ",self.want_a_partner_count, "    -------------------------------------" )
        print("------------------------- Count of establish couple events: ",self.establish_couple_count, "    -------------------------------------" )
        print("------------------------- Count of get pregnant events: ",self.get_pregnant_count, "    -------------------------------------" )
        print("------------------------- Count of giving birth events: ",self.giving_birth_count, "    -------------------------------------" )
        print("------------------------- Count of breakup events: ",self.breakup_count, "    -------------------------------------" )
        print("------------------------- Count of lonely time over events: ",self.lonely_time_over_count, "    -------------------------------------" )
        print()
        print()

    def add_event(self, event_name, event_time, person_list):
        if event_time > self.T:
            return
        self.event_count += 1
        event_id = self.event_count
        event = Event(event_time,event_id,event_name,person_list)
        if self.event_count == 1:
            sorted_key = lambda x : (x.time, x.id)
            self.event_list = SortedSet([event], key = sorted_key)
        else:
            self.event_list.add(event)

    def next_event(self):
        if len(self.event_list) == 0:
            return
        
        next_event = self.event_list.pop(0)
        return next_event

    def run(self):
        while True:
            event = self.next_event()
            if event is None:
                break

            if event.time > self.t:
                time_passed = event.time - self.t
                self.t = event.time
                for person in self.population:
                    person.month_goes_by(time_passed)
                self.print_terminal(event.name)
            
            if event.name == "death_event":
                self.death_event(event.list[0])
                self.death_count += 1
                #self.print_terminal(event.name)
            elif event.name == "want_a_partner_event":
                self.want_a_partner_event(event.list[0])
                self.want_a_partner_count += 1
            elif event.name == "establish_couple_event":
                self.establish_couple_event(event.list[0], event.list[1])
                self.establish_couple_count += 1
                #self.print_terminal(event.name)
            elif event.name == "get_pregnant_event":
                self.get_pregnant_event(event.list[0], event.list[1])
                self.get_pregnant_count += 1
                #self.print_terminal(event.name)
            elif event.name == "breakup_event":
                self.breakup_event(event.list[0], event.list[1])
                self.breakup_count += 1
                #self.print_terminal(event.name)
            elif event.name == "widow_event":
                self.widow_event(event.list[0])
                self.breakup_count += 1
                #self.print_terminal(event.name)
            elif event.name == "lonely_time_over_event":
                self.lonely_time_over_event(event.list[0])
                self.lonely_time_over_count += 1
                #self.print_terminal(event.name)
            else:
                self.giving_birth_event(event.list[0], event.list[1])
                self.giving_birth_count += 1
                #self.print_terminal(event.name)
                
            

