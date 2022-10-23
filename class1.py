import sqlite3 as sq

class sfgo_db:
    def __init__(self):
        with sq.connect('sfgo1.db') as con:
            cur = con.cursor()
            print("Подключение к базе данных")
            # инициализация значений из журналов
            
            ##### SQLite запросы в текстовом виде ####

            # столбцы для добавления в military_staff
            self.person_col = '''(position_id, mas_number, position_code, military_rank_code, full_name,
year_of_birth, education, civil_specialty, mc_id, family_status, address, date_appointment, id_equipment, category)'''
            
            #  столбцы для добавления в приписанную технику
            self.equipment_col = '''(brand, state_number, year_of_release, mc_id, company_id, date_of_study, condition)'''
            
            # показать бд
            self.show_sql = '''SELECT o_p.position_id ID, o_p.position_code Должность_штат, m_s.position_code Должность_факт, o_p.mas_number ВУС_штат, m_s.mas_number ВУС_факт,
o_p.military_rank_code В_зв_штат, m_s.military_rank_code В_зв_факт, o_p.equipment_by_state Тех_штат, i_e.brand техника_факт, m_s.full_name ФИО,
m_s.year_of_birth год_рожд, m_s.mc_id ВК, m_s.education образов, m_s.civil_specialty гр_спец,  m_s.family_status статус, m_s.address адрес,
m_s.category разряд FROM original_positions o_p LEFT JOIN military_staff m_s ON m_s.position_id = o_p.position_id LEFT JOIN intended_equipment i_e USING(id_equipment);'''

            #  свободные должности
            self.free_pos_sql = f'SELECT position_id, position_name FROM original_positions JOIN position_name USING(position_code) WHERE position_id NOT IN (SELECT position_id FROM original_positions JOIN military_staff USING (position_id))'
           
            sfgo_db.acceptable_values(self)

    #  получаем значение из журналов БД
    def acceptable_values(self):
        with sq.connect('sfgo1.db') as con:
            cur = con.cursor()

            # Список кортежей военно-учетных специальностей (номер, наименование)
            cur.execute(f'SELECT mas_name, mas_number FROM mas ORDER BY 1')
            self.mas = dict(cur.fetchall())

            # Список кортежей должностей (код, наименование)
            cur.execute(f'SELECT position_name, position_code FROM position_name ORDER BY 1')
            self.position_name = dict(cur.fetchall())

            # Список кортежей военкоматов (id, название)
            cur.execute(f'SELECT mc_name, mc_id FROM military_commissariat ORDER BY 1')
            self.mc = dict(cur.fetchall())

            # Список кортежей в.зв. (код, звание)
            cur.execute(f'SELECT military_rank_name, military_rank_code FROM military_rank ORDER BY 1')
            self.rank = dict(cur.fetchall())

            # Список кортежей организаций-поставщиков (название, код)
            cur.execute(f'SELECT company_name, company_id FROM supplier_company ORDER BY 1')
            self.company = dict(cur.fetchall())

            # список свободных должнсотей
            cur.execute(self.free_pos_sql)
            self.free_position = list([f'{key} {value}' for key, value in dict(cur.fetchall()).items()])

            


############  Добавить военнослужащего  ############

    # обновление словаря свободных должностей
    def update_free_position(self):
        c = list()
        with sq.connect('sfgo1.db') as con:
            cur = con.cursor()
            cur.execute(self.free_pos_sql)
            c = list([f'{key} {value}' for key, value in dict(cur.fetchall()).items()])
        self.free_position = c
        

    #  Проверка полученного списка 
    def __check_person_info(self, person_info):
        if 0 in (len(person_info[1]), len(person_info[2]), len(person_info[4])):
            return False
        for i in range(len(person_info)):
            #  проверка на числовое значение
            if i in (1, 2, 5):
                if not person_info[i].isdigit():
                    return False

        #  проверка на соответствие значениям в базе   
        if not int(person_info[1]) in (i[0] for i in self.mas.keys()) and int(person_info[2]) in (i[0] for i in self.position_name.keys()):
            return False

        # занята ли эта должность
        with sq.connect('sfgo1.db') as con:
                cur = con.cursor()
                temp = tuple(cur.execute(f'SELECT position_id FROM original_positions JOIN military_staff USING (position_id)'))
                
                temp = tuple(str(i[0]) for i in temp)
                print(temp)
                print(person_info[0].split()[0])
        if person_info[0].split()[0] in temp:
            return False
        return True
     
    
    #  Траснформация данных для записи в БД ВОЕННОСЛУЖАЩИЙ
    def __transform_person(self, person_info):
        person_info[0] = int(person_info[0].split()[0])
        person_info[3] = self.rank[person_info[3]] # Звание
        person_info[8] = self.mc[person_info[8]] # Военный комиссариат
        if person_info[12] != '':
            person_info[12] = int(person_info[12].split()[0]) # id техники
        #else: 
        #   person_info[12] = 'Null'
        for i in range(len(person_info)):
            if i in (1, 2, 5, 13):
                person_info[i] = int(person_info[i])

        return tuple(person_info)
        
    # добавить данные
    def add_person(self, person_info):
        message = ""
        if sfgo_db.__check_person_info(self, person_info):
            print("Проверку прошли!")
            with sq.connect('sfgo1.db') as con:
                cur = con.cursor()
                cur.execute(f'INSERT INTO military_staff {self.person_col} VALUES{sfgo_db.__transform_person(self, person_info)}')
            message = "Данные сохранены в базе."
        return message

    # список техники и id
    def get_eq(self):
        with sq.connect('sfgo1.db') as con:
            cur = con.cursor()
            cur.execute(f'SELECT id_equipment, brand FROM intended_equipment')
            res = list([f'{key} {value}' for key, value in dict(cur.fetchall()).items()])
        return res



############  Добавить технику  ############

    # Проверка полученного списка данных по технике
    def __check_equipment_info(self, equipment_info):
        # пустые значения
        if 0 in (len(equipment_info[0]), len(equipment_info[1])):
            return False
        
        if equipment_info[2].isdigit():
            return True
        else:
            return False
    
    #  Траснформация данных для записи в БД
    def __transform_equipment(self, equipment_info):
        equipment_info[3] = self.mc[equipment_info[3]] # Военный комиссариат
        equipment_info[4] = self.company[equipment_info[4]] # Компания - поставщик
        
        #  год выпуска
        if equipment_info[2] != '':
            equipment_info[2] = int(equipment_info[2])
        else: 
            equipment_info[2] = 'Null'
        return tuple(equipment_info)

    def add_equipment(self, equipment_info):
        message = ""
        if sfgo_db.__check_equipment_info(self, equipment_info):
            print("Данные о технике проверку прошли!")
            with sq.connect('sfgo1.db') as con:
                cur = con.cursor()
                cur.execute(f'INSERT INTO intended_equipment {self.equipment_col} VALUES{sfgo_db.__transform_equipment(self, equipment_info)}')
            message = "Данные сохранены в базе."
        return message





########### Показать базу данных ###################
    def show_db(self):
        with sq.connect('sfgo1.db') as con:
                cur = con.cursor()
                cur.execute(self.show_sql)
                res = list(cur.fetchall())
                def temp_func(b):
                    if b is None:
                        return ""
                    else:
                        return str(b)
                res = [[temp_func(b) for b in a] for a in res]
                res_0 = []
                for p in res:
                    res_0.append([p[0]] + [p[i] + " / " + p[i + 1] for i in range(1, 9, 2)] + p[9:])
                    
        return res_0



########### Анализ данных ###################
    def analysis_db(self):

        analysis_info = []
        with sq.connect('sfgo1.db') as con:
                cur = con.cursor()

                #  Укомлектованность личным составом в %
                cur.execute('''SELECT ((SELECT COUNT(position_id) * 100 FROM military_staff JOIN original_positions
                USING (position_id))/(SELECT COUNT(position_id) FROM original_positions)) Укомлектованность;''')
                analysis_info.append(("Укомлектованность личным составом", str(cur.fetchall()[0][0]) + ' %'))

                #  Прямая должностная положенность в %
                cur.execute('''SELECT (SELECT COUNT(position_id) * 100 FROM military_staff m_s JOIN original_positions o_p USING (position_id)
                WHERE m_s.position_code = o_p.position_code) / (SELECT COUNT(position_id) FROM military_staff JOIN original_positions USING (position_id)) ПДП;''')
                pdp = cur.fetchall()[0][0]
                if pdp is None:
                    pdp = 0    
                analysis_info.append(("Прямая должностная положенность", str(pdp) + ' %'))

                #  По прямым ВУС в %
                cur.execute('''SELECT (SELECT COUNT(position_id) * 100 FROM military_staff m_s JOIN original_positions o_p USING (position_id)
                WHERE m_s.mas_number = o_p.mas_number) / (SELECT COUNT(position_id) FROM military_staff JOIN original_positions USING (position_id)) ВУС;''')
                mas_per = cur.fetchall()[0][0]
                if mas_per is None:
                    mas_per = 0 
                analysis_info.append(("По прямым ВУС", str(mas_per) + ' %'))

                #  Укомлектованность техникой в %
                cur.execute('''SELECT (SELECT COUNT(military_id) * 100 FROM military_staff WHERE id_equipment != '') /
                (SELECT COUNT(position_id) FROM original_positions WHERE equipment_by_state IS NOT NULL) Техника;''')
                analysis_info.append(("Укомлектованность техникой", str(cur.fetchall()[0][0]) + ' %'))

                #  Средний возраст (лет)
                cur.execute('''SELECT ROUND((SELECT strftime('%Y', 'now')) - (SELECT AVG(year_of_birth) FROM military_staff));''')
                age = cur.fetchall()[0][0]
                if age is None:
                    age = 0
                analysis_info.append(("Средний возраст", str(age)))

                #  Разряды учета (разряд - процент)
                cur.execute('''SELECT category, COUNT(*) FROM military_staff GROUP BY category;''')
                analysis_info.append(("Разряды учета", ''.join([("Первый: ", ", второй: ", ", третий: ")[i[0] - 1] + str(i[1]) for i in cur.fetchall()])))
                
        return analysis_info
        




