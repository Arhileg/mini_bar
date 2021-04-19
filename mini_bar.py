"""The module contains a class for working with a mini bar.
keeping records in sqlite tables."""
import datetime
import sqlite3
from sqlite3 import Error
from prettytable import from_db_cursor
from prettytable import DEFAULT, FRAME


class Bar:
    """class bar: mini bar for storage of leftovers and operation with drinks."""
    name: str

    def __init__(self, name=''):
        """set name bar. create db and table for bar."""
        self.name = name
        self.create_connection(r'bar_storage.db')
        self.create_table(r'bar_tables_schema.sql')
        # self.create_table(r'bar_operation_schema.sql')

    def create_connection(self, db_file):
        """ create a database connection to the SQLite database
            specified by db_file
        :param db_file: database file
        :return: Connection object or None
        """
        self.conn = None
        try:
            self.conn = sqlite3.connect(db_file)
        except Error as error:
            print(error)

    def create_table(self, create_table_sql):
        """ create a table from the create_table_sql statement
        :param create_table_sql: a CREATE TABLE statement
        :return:
        """
        try:
            # print(create_table_sql)
            with open(create_table_sql, 'r') as file:
                schema = file.read()
                self.conn.executescript(schema)
        except Error as error:
            print(error)

    @staticmethod
    def take_date_now():
        """date for table operation."""
        return datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

    def get_drink(self, name_drink):
        """sale drink from bar."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM drinks WHERE name=?', (name_drink,))
        found_drink = cursor.fetchone()
        if not found_drink:
            result = 'there is no such drink.\nanything else?'
        else:
            amount = 1
            id_drink = found_drink[0]
            qty = found_drink[2]
            price = found_drink[3]
            if amount<=qty:
                update_drink = tuple([amount, id_drink,])
                sql_query = """
                UPDATE drinks
                SET quantity=quantity-?
                WHERE id=?
                """
                cursor.execute(sql_query, update_drink)
                operation = [self.take_date_now(),
                            id_drink,
                            name_drink,
                            'sale',
                            amount,
                            price
                ]
                sql_query = """
                INSERT INTO operation(date, id_drink, name_drink, operation, amount, price)
                VALUES(?, ?, ?, ?, ?, ?)
                """
                cursor.execute(sql_query, tuple(operation))
                self.conn.commit()
                result = '- a good choice'
            else:
                result = '- there is no more this drink'
        return result

    def supply(self, name_drink, amount, price):
        """add drink to bar and operation."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM drinks WHERE name=?', (name_drink,))
        found_drink = cursor.fetchone()
        if not found_drink:
            sql_query = """
            INSERT INTO drinks(name, quantity, selling_price, purchase_price)
            VALUES(?, ?, ?, ?)
            """
            cursor.execute(sql_query, (name_drink, amount, price, price))
            id_drink = cursor.lastrowid
        else:
            new_drink_tuple = tuple([amount, price, price, found_drink[0]])
            sql_query = """
            UPDATE drinks
            SET quantity=quantity+?, selling_price=?, purchase_price=?
            WHERE id=?
            """
            cursor.execute(sql_query, new_drink_tuple)
            id_drink = found_drink[0]
        operation = [self.take_date_now(),
                    id_drink,
                    name_drink,
                    'arrive',
                    amount,
                    price
        ]
        sql_query = """
        INSERT INTO operation(date, id_drink, name_drink, operation, amount, price)
        VALUES(?, ?, ?, ?, ?, ?)
        """
        cursor.execute(sql_query, tuple(operation))
        self.conn.commit()
        return name_drink

    def take_log(self, to_html=False):
        """take all operation sale / arrived."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM operation')
        log_table = from_db_cursor(cursor)
        log_table.align["operation"] = "l"
        log_table.align["name_drink"] = "l"
        log_table.align["amount"] = "r"
        log_table.align["price"] = "c"
        log_table.set_style(DEFAULT)
        log_table.vrules = FRAME
        if to_html:
            result = log_table.get_html_string(title="Operation logs",)
        else:
            result = log_table.get_string(title="Operation logs",)
        return result

    def take_menu(self, to_html=False):
        """take menu bar for user."""
        cursor = self.conn.cursor()
        cursor.execute(
        """SELECT
        name as Drink,
        quantity as Quantity,
        selling_price as Price
        FROM drinks
        WHERE quantity>0""")
        menu_table = from_db_cursor(cursor)
        menu_table.align["Drink"] = "l"
        menu_table.align["Quantity"] = "r"
        menu_table.align["Price"] = "c"
        menu_table.set_style(DEFAULT)
        menu_table.vrules = FRAME
        
        if to_html:
            result = menu_table.get_html_string(title="Menu", sortby="Drink")
        else:
            result = menu_table.get_string(title="Menu", sortby="Drink")
        return result

    def __str__(self):
        return 'uppsss...'

def main():
    """terminal interface."""
    new_bar = Bar('Bormotuha')
    # new_bar.supply('vodka', 4, 40.9)
    # new_bar.supply('wine', 10, 85.3)
    # new_bar.supply('absent', 5, 300.4)

    print('Welcome to ours robo-bar!!! \nlook at the commands:')
    print('\'menu\' - see the menu')
    print('\'drink\' - buy a drink at the bar')
    print('\'supply\' - supply drinks to the bar ')
    print('\'log\' - log sales and arrivals ')
    print('\'exit\' - leave the bar\n')

    while True:
        command = input('- Could you tell me the command,'+\
                        ' please \n(menu/drink/supply/log/exit)? : ').strip()
        if command=='exit':
            print('- Goodbye')
            break
        if command=='menu':
            # print(new_bar)
            print(new_bar.take_menu(),'\n')
        elif command=='drink':
            drink = input('- What drink do you want ? : ').strip()
            print(command,' buy: ', new_bar.get_drink(drink))
        elif command=='supply':
            drink, amount, price = input(
				'write \'drink\'  \'amount\' \'price\' for suppling: '
			).split()
            print(command,': ', new_bar.supply(drink.strip(), int(amount), float(price)))
        elif command=='log':
            print(new_bar.take_log(),'\n')
        else:
            print('- unknow command')


if __name__=="__main__":
    main()
