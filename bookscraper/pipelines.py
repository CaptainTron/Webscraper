# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
import mysql.connector
from itemadapter import ItemAdapter, adapter


class BookscraperPipeline:

  def process_item(self, item, spider):

    adapter = ItemAdapter(item)
    field_names = adapter.field_names()

    for field_name in field_names:
      if field_name != 'description':
        value = adapter.get(field_name)
        adapter[field_name] = value[0].strip()

    lowercase_keys = ['product_type']
    for lowercase_key in lowercase_keys:
      value = adapter.get(lowercase_key)
      adapter[lowercase_key] = value.lower()

    price_keys = ['price', 'price_incl_tax', 'price_excl_tax', 'tax']
    for price_key in price_keys:
      value = adapter.get(price_key)
      value = value.replace('£', '')
      adapter[price_key] = float(value)

    availability_string = adapter.get('availability')
    split_string_array = availability_string.split('(')
    if len(split_string_array) < 2:
      adapter['availability'] = 0
    else:
      availability_array = split_string_array[1].split(' ')
      adapter['availability'] = int(availability_array[0])

    Number_of_reviews = adapter.get('Number_of_reviews')
    adapter['Number_of_reviews'] = int(Number_of_reviews)

    # stars_string = adapter.get('stars')
    # split_stars_array = stars_string.split(' ')
    # stars_text_value = split_stars_array[1].lower()

    # if(stars_text_value) == "zero":
    #   adapter['stars'] = 0
    # elif stars_text_value == "one":
    #   adapter['stars'] = 1
    # elif stars_text_value == "two":
    #   adapter['stars'] = 2
    # elif stars_text_value == "three":
    #   adapter['stars'] = 3
    # elif stars_text_value == "four":
    #   adapter['stars'] = 4
    # elif stars_text_value == "five":
    #   adapter['stars'] = 5

    return item


import pymysql
class Savetomysql:

  def __init__(self):

    # timeout = 10
    # self.conn = pymysql.connect(
    #   charset="utf8mb4",
    #   connect_timeout=timeout,
    #   # cursorclass=pymysql.cursors.DictCursor,
    #   db="defaultdb",
    #   host="mysql-327568c0-vaibhavwateam-0bb0.a.aivencloud.com",
    #   password="AVNS_VLU3aK7WPzCitgcvOGo",
    #   read_timeout=timeout,
    #   port=15903,
    #   user="avnadmin",
    #   write_timeout=timeout,
    # )

    # self.cur = self.conn.cursor()
    # try:
    #   self.cur.execute("CREATE TABLE mytest (id INTEGER PRIMARY KEY)")
    #   self.cur.execute("INSERT INTO mytest (id) VALUES (1), (2)")
    #   self.cur.execute("SELECT * FROM mytest")
    #   print(self.cur.fetchall())
    # finally:  
    #   self.conn.close()



    
    # host = 'mysql-327568c0-vaibhavwateam-0bb0.a.aivencloud.com'
    print("**************** Starting Connection ***********************")
    self.conn = mysql.connector.connect(
        db="defaultdb",
        host="mysql-327568c0-vaibhavwateam-0bb0.a.aivencloud.com",
        password="AVNS_VLU3aK7WPzCitgcvOGo",
        port=15903,
        user="avnadmin",
    )
    print("Connected to database**********************", self.conn)

    self.cur = self.conn.cursor()

    self.cur.execute("""
    CREATE TABLE IF NOT EXISTS books(
        id int NOT NULL auto_increment, 
        url VARCHAR(255),
        title text,
        product_type VARCHAR(255),
        price_excl_tax DECIMAL,
        price_incl_tax DECIMAL,
        tax DECIMAL,
        price DECIMAL,
        availability INTEGER,
        Number_of_reviews INTEGER,
        description text,
        PRIMARY KEY (id)
    )
    """)

  def process_item(self, item, spider):

    ## Define insert statement
    self.cur.execute(
        """ INSERT INTO books (
          url, 
          title, 
          product_type, 
          price_excl_tax,
          price_incl_tax,
          tax,
          price,
          availability,
          Number_of_reviews,
          description
          ) values (
              %s,
              %s,
              %s,
              %s,
              %s,
              %s,
              %s,
              %s,
              %s,
              %s,
              )""",
        (
         item["url"], 
         item["title"], 
         item["product_type"], 
         item["price_excl_tax"], 
         item["price_incl_tax"], 
         item["tax"],
         item["price"], 
         item["availability"], 
         item["Number_of_reviews"],
         item["description"][0]
        )
    )

    # ## Execute insert of data into database
    self.conn.commit()
    return item



  def close_spider(self):

    ## Close cursor & connection to database
    self.cur.close()
    self.conn.close()
