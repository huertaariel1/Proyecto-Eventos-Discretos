class Person:
    def __init__(self, _id, _age, _is_woman = False):
        self.id = _id
        self.age = int(_age)
        self.until_birthday = int((_age - int(_age)) * 12)
        self.is_woman = _is_woman
        self.is_ready =  False
        self.children_count = 0
        self.partner = 0
        self.death_age = 125
        self.is_dead = False
        self.want_partner_age = []
        self.max_children_number = 0
        self.next_range_wp_event = False
        self.next_range_p_event = False

    def month_goes_by(self, months):
        self.until_birthday = self.until_birthday + months
        if self.until_birthday >= 12:
            self.until_birthday -= 12
            self.age = self.age + 1
    
    def have_a_child(self, count = 1):
        self.children_count += count

class Woman(Person):
    def __init__(self, _id, _age, _is_woman = True):
        super().__init__(_id, _age, _is_woman)
        self.is_pregnant = False
        self.multiple_pregnancy = 0
        self.can_get_pregnant = []

            
            