import psycopg2
import random

#connect to the db
con = psycopg2.connect('host=localhost dbname=huwebshop user=postgres password=12345')

#cursor
cur = con.cursor()

# all the columns in table product
_id = 0
name = 1
brand = 2
category = 3
description = 4
fast_mover = 5
herhaalaankopen = 6
selling_price = 7
doelgroep = 8
sub = 9
sub_sub = 10
sub_sub_sub = 11

categories = []
sub_ = []
sub_sub_ =  []

cur.execute("SELECT * FROM PRODUCT")
products = cur.fetchall()

for product in products:
	if product[category] not in categories:
		categories.append(product[category])

for product in products:
	if product[sub] not in sub_:
		sub_.append(product[sub])

for product in products:
	if product[sub_sub] not in sub_sub_:
		sub_sub_.append(product[sub_sub])		

duplicates_1 = [a for a in categories if a in sub_]
duplicates_2 = [a for a in sub_ if a in sub_sub_]



def column_finder(productid):
	'''
	
	'''
	productID = str(productid)

	cur.execute("SELECT * FROM product WHERE _id = %s",(productID,))
	initial_product = cur.fetchone()

	sql_query = "SELECT * FROM product WHERE "
	columns = []	
	
	if initial_product[doelgroep] != None:
		sql_query += ("doelgroep = %s AND ")
		columns.append(initial_product[doelgroep])
	if initial_product[category] != None:
		sql_query += ("category = %s AND ")
		columns.append(initial_product[category])							
	if initial_product[sub] != None:
		sql_query += ("sub_category = %s AND ")			
		columns.append(initial_product[sub])		
	if initial_product[sub_sub] != None:
		sql_query += ("sub_sub_category = %s AND ")	
		columns.append(initial_product[sub_sub])	
	if initial_product[brand] != None:
		sql_query += ("brand = %s AND ")
		columns.append(initial_product[brand])		
	if initial_product[sub_sub_sub] != None:
		sql_query += ("sub_sub_sub_category = %s AND ")	
		columns.append(initial_product[sub_sub_sub])		
	sql_query = sql_query[:-4] # removes the extra "AND " at the end of the sql query

	return(sql_query, columns)	



def recommendation_filter(productid):
	'''Function uses all useful filters to find similar products to the current product.
	   If less than 4 similar products are found, one filter is removed and the step is repeated.
	   This repeats until at least 4 similar products are found.
	   Filters are in order of importance (most important first, least import last).
	   Importance is decided by the amount of products each filter has.'''
	   
	productID = str(productid)

	try:
		sql_query = column_finder(productID)[0]
		columns = column_finder(productID)[1]
	except TypeError:
		print("Dit product zit niet in de database.")
		quit()

	cur.execute("SELECT * FROM product WHERE _id = %s",[productID])
	initial_product = cur.fetchone()

	# loop until there are at least 4 similar products are found
	while True:
		count = 0 # keeps track of amount of similar products
		raw_sql_query = "SELECT * FROM product WHERE "

		cur.execute(sql_query, columns)
		filtered_products = cur.fetchall()

		for product in filtered_products:
			count += 1 
		if count >= 4: # checks if there are already 4 or more products available
			return (filtered_products)

		if count < 4:
			columns = columns[:-1]
			if initial_product[doelgroep] in columns:
				raw_sql_query += "doelgroep = %s AND "			
			if initial_product[category] in columns:
				raw_sql_query += "category = %s AND "			
			if initial_product[sub] in columns:
				if initial_product[sub] in duplicates_1 and initial_product[sub] == initial_product[category]:
					if columns.count(initial_product[sub]) == 1:
						pass #	
					else:
						raw_sql_query += "sub_category = %s AND "
				else:
					raw_sql_query += "sub_category = %s AND "
			if initial_product[sub_sub] in columns:
				if initial_product[sub_sub] in duplicates_2 and initial_product[sub_sub] == initial_product[sub]:
					if columns.count(initial_product[sub_sub]) == 1:
						pass # 	
					else:
						raw_sql_query += "sub_sub_category = %s AND "
				else: 
					raw_sql_query += "sub_sub_category = %s AND "
			if initial_product[brand] in columns:
				raw_sql_query += "brand = %s AND "					

		raw_sql_query = raw_sql_query[:-4] # removes the extra "AND " at the end of the sql query
		sql_query = raw_sql_query
		cur.execute(sql_query, columns)
		filtered_products = cur.fetchall()
		
		for product in filtered_products:
			count += 1
		if count >= 4:
			# print(f'Recommenadble products after filtering: {count}')
			return(filtered_products)



def recommended_products(productid):
	'''
	
	'''	
	filtered_products = recommendation_filter(productid)
	random_products = [productid]# contains current product. 4 similar products will be appended
	
	for i in range (0,4): # repeats 4 times
		random_choice = random.choice(filtered_products) # picks 4 random products from pre-filtered list
		random_products.append(random_choice[_id]) # adds the 4 picked products to product list
	return(random_products)



def create_table():
	'''
	
	'''
	sql_create_table = "CREATE TABLE IF NOT EXISTS product_recommendations \
					(main_product VARCHAR (40) PRIMARY KEY, \
						similar_product_1 VARCHAR (40) NOT NULL, \
						similar_product_2 VARCHAR (40) NOT NULL, \
						similar_product_3 VARCHAR (40) NOT NULL, \
						similar_product_4 VARCHAR (40) NOT NULL);"

	cur.execute(sql_create_table)
	con.commit()



def recommendation_filler():
	'''
	
	'''
	sql_insert = "INSERT INTO product_recommendations \
				(main_product, similar_product_1, similar_product_2, similar_product_3, similar_product_4) \
				VALUES (%s, %s, %s, %s, %s)"
	cur.execute("SELECT * FROM product")
	products = cur.fetchall()
	insertcount = 0
	cur.execute("select count(*) from product")  
	product_amount = list(cur)
	# print(products[40328])
	try:
		for product in products:
			cur.execute(sql_insert,recommended_products(product[0]))
			con.commit()
			insertcount += 1
			print(f"{insertcount} out of {product_amount[0][0]}")
	except Exception as e:
		print("Error! ",e, product[0])
	
 
def main():
	create_table()
	recommendation_filler()


main()




