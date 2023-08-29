from collections import UserDict
from datetime import date, datetime
import json, csv

# Додамо функціонал перевірки на правильність наведених значень для полів Phone, Birthday


class Field(): # буде батьківським для всіх полів, у ньому потім реалізуємо логіку, загальну для всіх полів
    def __init__(self, value):
        self.__value = None # захищенне поле
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value = None):
        if value:
            self.__value = value
        else:
            raise ValueError('You forgot to fill in this field')


class Phone(Field): # необов'язкове поле з телефоном та таких один запис (Record) може містити кілька
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value=None):
        cleaned_value = self.is_phone(value)
        if cleaned_value:
            self.__value = cleaned_value
        else:
            raise ValueError('Phone not valid')

    @staticmethod
    def is_phone(value):
        result = ''
        if len(value) > 0:
            for i in value:
                if i.isdigit():
                    result += i
        if len(value) == 0 or len(result) > 12 or len(result) < 10:
            raise ValueError("A phone number is a set of numbers!")
        return result




class Name(Field): # обов'язкове поле з ім'ям
    pass

class Birthday(Field): # поле не обов'язкове, але може бути тільки одне
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value=None):
        cleaned_value = self.is_date_birthday(value)
        if cleaned_value:
            self.__value = cleaned_value
        else:
            raise ValueError('Date not valid')

    @staticmethod
    def is_date_birthday(value):
        delimiter = ' ,./-'
        if len(value) == 10:
            for s in value:
                if s in delimiter:
                    value = value.replace(s,'-')
                elif not s.isdigit():
                    raise ValueError("Pleas, enter the date of birth in the format: DD-MM-YYY.")
        return value



class Email(Field):
    pass


class Record(): #відповідає за логіку додавання/видалення/редагування необов'язкових полів та зберігання
    # обов'язкового поля Name.
    def __init__(self, name: Name, phone: Phone = None, birthday: Birthday = None) -> None:
        self.name = name
        self.phones = []
        if phone:
            self.phones.append(phone)  # якщо телефон прийде як обьект классу то додамо його в список
        self.birthday = None
        if birthday:
            self.birthday = birthday


    def add_phone(self, phone: Phone):
        phone_number = Phone(phone)
        clean_number = Phone.is_phone(phone_number)
        if clean_number.value not in [ph.value for ph in self.phones]:
            self.phones.append(clean_number)
        return self


    def edit_phone(self, phone_old, phone_new: Phone):
        phone_number_old = Phone(phone_old)
        phone_number_new = Phone(phone_new)
        if phone_number_old.value in [ph.value for ph in self.phones]:
            # print(phone_number_old.value in [ph.value for ph in self.phones])
            # print('self.phones[0].value =', self.phones[0].value)
            self.phones[0].value = phone_number_new.value
        else:
            self.phones.append(phone_number_new)
            # print('self.phones[1].value =', self.phones[1].value)


    def del_phone(self, phone: Phone): # не розумію, як видалити об"єкт (пише, що його не існує)
        # phone_number = Phone(phone)
        # if phone_number.value in [ph.value for ph in self.phones]:
            # self.phones.remove(phone_number)
        pass


    def days_to_birthday(self):  # повертає кількість днів до наступного дня народження
        birthday_day = date.today()
        now_day = date.today()
        new_birthday_day = date.today()
        if self.birthday.value[2] == '-' and self.birthday.value[5]:
            birthday_day = datetime.strptime(self.birthday.value, '%d-%m-%Y').date()
        elif self.birthday.value[4] == '-' and self.birthday.value[7]:
            birthday_day = datetime.strptime(self.birthday.value, '%Y-%m-%d').date()
        # print('birthday_day = ', birthday_day, type(birthday_day))
        if now_day.month > birthday_day.month:
            new_birthday_day = birthday_day.replace(year=now_day.year + 1)

        elif now_day.month < birthday_day.month:
            new_birthday_day = birthday_day.replace(year=now_day.year)
        elif now_day.month == birthday_day.month:
            if now_day.day >= birthday_day.day:
                new_birthday_day = birthday_day.replace(year=now_day.year + 1)
            elif now_day.day < birthday_day.day:
                new_birthday_day = birthday_day.replace(year=now_day.year)
        # print('new birthday_day = ', new_birthday_day)
        delta_day = new_birthday_day - now_day
        return f'{delta_day.days} days until next birthday'


    def __str__(self):
        return f"Contact {self.name.value}. Phones {[ph.value for ph in self.phones]}. Birthday {self.birthday.value}. {self.days_to_birthday()}"

class AddressBook(UserDict): # наслідується від UserDict, та ми потім додамо логіку пошуку за записами до цього класу
    N = 2 # по замовчуванню поставимо по 2 записи
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def iterator(self, n=None):
        if n:
            AddressBook.N = n
        return self.__next__()

    def __iter__(self):
        temp_lst = []
        counter = 0

        for var in self.data.values():
            temp_lst.append(var)
            counter += 1
            if counter >= AddressBook.N:
                yield temp_lst
                temp_lst.clear()
                counter = 0
        yield temp_lst

    def __next__(self):
        generator = self.__iter__()
        page = 1
        while True:
            user_input = input("Press ENTER")
            if user_input == "":
                try:
                    result = next(generator)
                    if result:
                        print(f"{'*' * 20} Page {page} {'*' * 20}")
                        page += 1
                    for var in result:
                        print(var)
                except StopIteration:
                    print(f"{'*' * 20} END {'*' * 20}")
                    break
            else:
                break

    def serialize(self, filename): # функціонал збереження адресної книги на диск
        contact_dict = {}
        with open(filename, 'w', encoding='utf-8') as f:
            for var in self.data.values():
                contact_dict[var.name.value] = {
                    'phones': [ph.value for ph in var.phones],
                    'birthday': var.birthday.value}
            # print(contact_dict)
            json.dump(contact_dict, f, ensure_ascii=False, indent=4)

    @staticmethod
    def deserialize(filename): # функціонал відновлення з диска
        with open(filename, 'r', encoding='utf-8') as f:
            restore_data = json.load(f)
            return restore_data

    @staticmethod
    def input_str():  # введення з клавіатури пошукового запроса
        try:
            input_str = input('Enter search element >>> ')
            return input_str
        except ValueError():
            print("Search not possible")

    def search(self): # пошуку вмісту книги контактів, щоб можна було знайти всю інформацію про одного
        # або кількох користувачів за кількома цифрами номера телефону або літерами імені тощо
        search_str = self.input_str()
        no_search = 0
        for var in self.data.values():
            if search_str.isdigit():
                for contact in var.phones:
                    if search_str in contact.value:
                        yield var
            elif search_str.isalpha() and search_str.lower() in var.name.value.lower():
                yield var
            else:
                no_search += 1
        if no_search == len(self.data):
            yield f'No contacts matching search'


    def search_output(self): # виводить список користувачів, які мають в імені або номері телефону є збіги із введеним рядком
        for i in self.search():
            print(i)



if __name__ == "__main__":
    name = Name('Bill')
    phone = Phone('+ 38 050 321 31 31')
    birthday = Birthday('08-08/1999')
    rec = Record(name, phone, birthday)
    ab = AddressBook()
    ab.add_record(rec)

    name3 = Name('Ann')
    phone3 = Phone('+ 38 (050) 585 - 58 - 58')
    # phone11 = Phone('+ 38 067 670-16-16')
    birthday3 = Birthday('1944/02-20')
    rec3 = Record(name3, phone3, birthday3)
    ab.add_record(rec3)

    name1 = Name('Bob')
    phone1 = Phone('+ 38 067 670-16-16')
    birthday1 = Birthday('2001.08.21')
    rec1 = Record(name1, phone1, birthday1)
    name2 = Name('Gill')
    phone2 = Phone('+ 38 067 670-16-16')
    birthday2 = Birthday('1999.01.25')
    rec2 = Record(name2, phone2, birthday2)
    ab.add_record(rec1)
    ab.add_record(rec2)

    name4 = Name('Annet')
    phone4 = Phone('+ 38 (044) 585 - 66 - 58')
    birthday4 = Birthday('2001/06-20')
    rec4 = Record(name4, phone4, birthday4)
    ab.add_record(rec4)

    # assert isinstance(ab['Bill'], Record)
    # assert isinstance(ab['Bill'].name, Name)
    # assert isinstance(ab['Bill'].phones, list)
    # assert isinstance(ab['Bill'].phones[0], Phone)


    # print(isinstance(ab['Bill'].birthday, Birthday))
    # print("ab: ",ab['Bill'].birthday.value)
    #
    # print(rec.birthday.value, type(rec.birthday.value))
    # # print(Birthday.is_date_birthday(birthday))
    # print(rec.days_to_birthday())
    #
    # print(rec1.name.value)
    # print(rec1.phones[0].value)
    # print(rec1.birthday.value)
    # print(rec1.days_to_birthday())

    # print(Phone.is_phone(phone1))
    # print(rec1.phones[0].value)
    # print(rec1.phones[0].value)
    # print(rec.phones[0].value)


    # print(ab.iterator(3))


    ab.serialize('a_b.json')
    print(ab.deserialize('a_b.json'))

    print(AddressBook.deserialize('a_b.json')) # Програма не втрачає дані після виходу з програми та відновлює їх з файлу.

    ab.search_output() # Програма виводить список користувачів, які мають в імені або номері телефону є збіги із введеним рядком.