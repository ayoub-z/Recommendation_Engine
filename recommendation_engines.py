import psycopg2
import random

#connect to the db
con = psycopg2.connect('host=localhost dbname=huwebshop user=postgres password=12345')

#cursor
cur = con.cursor()

# all the columns in the table product. Easier to remember names than their position in a string
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



def column_finder(productid):
	'''
	This function looks up the given product_id in the database to find rows that aren't empty. 
	Afterwhich it returns a variable and an sql query containing only those rows that are 
	left over after filtering.
	'''
	productID = str(productid) # puts product_id in a string

	cur.execute("SELECT * FROM product WHERE _id = %s",(productID,)) # retrieves all data from given product_id
	initial_product = cur.fetchone() # inputs product_id data in variable

	sql_query = "SELECT * FROM product WHERE " # sql query with a basic frame to look up products, will have more code added to it
	columns = [] # variable that will contain the data of each row. We will need this later for comparing
	
	if initial_product[doelgroep] != None: # checks if the column "doelgroep" isn't empty
		sql_query += ("doelgroep = %s AND ") # adds said column to the sql query
		columns.append(initial_product[doelgroep]) # appends the data inside the column to this a variable
	if initial_product[category] != None: # filtering process is repeated for all given columns.
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
	'''
	Function uses all useful filters to find similar products to the current product.
	If less than 4 similar products are found, one filter is removed and the step is repeated.
	This repeats until at least 4 similar products are found.
	Filters are in order of importance (most important first, least import last).
	Importance is decided by the amount of products each filter has.
	'''
	   
	productID = str(productid) # puts product_id in a string

	categories = [] 
	sub_ = []
	sub_sub_ =  []

	try:
		sql_query = column_finder(productID)[0] # variable containing retrieved sql query for given product_id
		columns = column_finder(productID)[1] # variable containing retrieved sql data for columns inside given product_id
	except TypeError: # error message in case product isn't in database. Should only be ~3000 products with corrupt data
		print("Dit product zit niet in de database.")
		quit()

	cur.execute("SELECT * FROM product WHERE _id = %s",[productID]) # retrieves all data for given product_id
	initial_product = cur.fetchone() # inputs product_id data in variable

	cur.execute("SELECT * FROM product") # retrieves all data from table "product"
	products = cur.fetchall() # inputs data of all products in variable

	# generates a list containing all individual categories in table "product"
	for product in products:
		if product[category] not in categories:
			categories.append(product[category])

	# generates a list containing all individual sub_categories in table "product"
	for product in products:
		if product[sub] not in sub_:
			sub_.append(product[sub])

	# generates a list containing all individual sub_sub_categories in table "product"
	for product in products:
		if product[sub_sub] not in sub_sub_:
			sub_sub_.append(product[sub_sub])		

	# generates a list containing duplicate category names in the column "sub_category"
	category_duplicates = [a for a in categories if a in sub_]

	# generates a list containing duplicate sub_category names in the column "sub_sub_category	""
	sub_category_duplicates = [a for a in sub_ if a in sub_sub_]

	while True: # loops until at least 4 similar products are found
		count = 0 # keeps track of amount of similar products
		raw_sql_query = "SELECT * FROM product WHERE " 

		cur.execute(sql_query, columns) # sql query to retrieve all leftover products after they've been filtered
		filtered_products = cur.fetchall() # inputs data of retrieved products in variable

		for product in filtered_products: # counts the amount of retrieved products
			count += 1 
		if count >= 4: 
			return (filtered_products) # returns list of retrieved products if it contains at least 4 products

		if count < 4:
			columns = columns[:-1] # if less than 4 products are found, remove 1 column from list containing column names

			# the following code is to check which columns are left over, after the last column is removed
			# after which a new sql query is generated containing the left over columns
			if initial_product[doelgroep] in columns: # checks if the column "doelgroep" is inside the list of leftover columns
				raw_sql_query += "doelgroep = %s AND "# adds said column to the sql query		
			if initial_product[category] in columns: # repeats for each column
				raw_sql_query += "category = %s AND "			
			if initial_product[sub] in columns:
				# check for duplicate named columns between category and sub_category. 
				if initial_product[sub] in category_duplicates and initial_product[sub] == initial_product[category]:
					if columns.count(initial_product[sub]) == 1: # checks if there is only one column with this column name
						pass # in which case it skips
					else: # if both columns have the same name and there exist 2 columns with that name, only then does it add said column to the sql query	
						raw_sql_query += "sub_category = %s AND "
				else:
					raw_sql_query += "sub_category = %s AND "
			if initial_product[sub_sub] in columns:
				# check for duplicate named columns in sub_category and sub_sub_category
				if initial_product[sub_sub] in sub_category_duplicates and initial_product[sub_sub] == initial_product[sub]:
					if columns.count(initial_product[sub_sub]) == 1: # same as earlier, check if there's only one column with this column name
						pass # skip if so
					else:
						raw_sql_query += "sub_sub_category = %s AND "
				else: 
					raw_sql_query += "sub_sub_category = %s AND "
			if initial_product[brand] in columns:
				raw_sql_query += "brand = %s AND "					

		raw_sql_query = raw_sql_query[:-4] # removes the extra "AND " at the end of the sql query
		sql_query = raw_sql_query # old sql query is replaced with new sql query

		cur.execute(sql_query, columns) # sql query to retrieve new set of leftover products after they've been filtered
		filtered_products = cur.fetchall() # inputs data of retrieved products in variable
		
		for product in filtered_products: # counts the amount of retrieved products
			count += 1
		if count >= 4:
			return(filtered_products) # returns list of retrieved products if it contains at least 4 products



def recommended_products(productid):
	'''
	
	'''	
	filtered_products = recommendation_filter(productid) # retrieves list of filtered products
	random_products = [productid]# list that will contain the initial_product and 4 other products for recommendation
	
	for i in range (0,4): # repeats 4 times
		random_choice = random.choice(filtered_products) # picks 4 random products from pre-filtered list
		random_products.append(random_choice[_id]) # adds the 4 picked products to product list
	return(random_products)



def create_sql_tables():
	'''
	
	'''
	# creates table for content_filtering in the database if it doesn't already exist
	sql_content_table = "CREATE TABLE IF NOT EXISTS content_recommendations \
						(main_product VARCHAR (40) PRIMARY KEY, \
						similar_product_1 VARCHAR (40) NOT NULL, \
						similar_product_2 VARCHAR (40) NOT NULL, \
						similar_product_3 VARCHAR (40) NOT NULL, \
						similar_product_4 VARCHAR (40) NOT NULL);"

	# creates table for collaborative_filtering in the database if it doesn't already exist 
	sql_collaborative_table = "CREATE TABLE IF NOT EXISTS collaborative_recommendations \
								(profile_id VARCHAR (40) PRIMARY KEY, \
								similar_product_1 VARCHAR (40) NOT NULL, \
								similar_product_2 VARCHAR (40) NOT NULL, \
								similar_product_3 VARCHAR (40) NOT NULL, \
								similar_product_4 VARCHAR (40) NOT NULL);"

	cur.execute(sql_content_table)
	con.commit()
	cur.execute(sql_collaborative_table)
	con.commit()



def content_recommendation_filler():
	'''
	
	'''
	sql_insert = "INSERT INTO content_recommendations \
				(main_product, similar_product_1, similar_product_2, similar_product_3, similar_product_4) \
				VALUES (%s, %s, %s, %s, %s)"
	cur.execute("SELECT * FROM product")
	products = cur.fetchall()
	insertcount = 0
	cur.execute("select count(*) from product")  
	product_amount = list(cur)
	try:
		for product in products:
			cur.execute(sql_insert,recommended_products(product[0]))
			con.commit()
			insertcount += 1
			print(f"{insertcount} out of {product_amount[0][0]}")
	except Exception as e:
		print("Error! ",e, product[0])



def profile_viewed_before(profile_id):
	'''

	'''
	profile_ID = str(profile_id) # puts product_id in a string
		
	cur.execute("SELECT product_id FROM viewed_before WHERE profile_id = %s", (profile_ID,))
	viewed_products = cur.fetchall()
	
	if len(viewed_products) == 0:
		return()

	viewed_before = []
	for r in viewed_products:
		viewed_before.append(r[0])
	viewed_before = tuple(viewed_before)

	cur.execute("SELECT profile_id FROM viewed_before WHERE product_id IN %s", (viewed_before,))
	similar_profiles = cur.fetchall()

	similar_product_dict = {}

	for profile in similar_profiles:
		cur.execute("SELECT product_id FROM viewed_before WHERE profile_id IN %s", (profile,))
		products = cur.fetchall()
		for product in products:
			if product[0] in similar_product_dict and product[0] not in viewed_before:
				similar_product_dict[product[0]] += 1
			elif product[0] not in similar_product_dict and product[0] not in viewed_before:
				similar_product_dict[product[0]] = 1
			else:
				continue
	# sorts dictionary from highest to lowest and returns the top 4 products
	similar_product_results = sorted(similar_product_dict.items(), key=lambda x: x[1], reverse=True)[:4]

	similar_products = []
	similar_products.append(profile_id)

	for product in similar_product_results:
		similar_products.append(product[0])

	return(similar_products)



def collaborative_recommendation_filler():
	'''
	This function makes use of previous functions to get collaborative recommendations for every profile 
	'''
	insertcount = 0	
	sql_insert = "INSERT INTO collaborative_recommendations \
				(profile_id, similar_product_1, similar_product_2, similar_product_3, similar_product_4) \
				VALUES (%s, %s, %s, %s, %s)"
	cur.execute("SELECT * FROM profile")
	profiles = cur.fetchall()

	# try:
	for profile in profiles:
		profile = profile_viewed_before(profile[0])
		if len(profile) == 0:
			print('Profile has yet to view a product')
			continue
		else:
			cur.execute(sql_insert, profile)
			con.commit()
			insertcount += 1
			print(f"Inserted {insertcount} rows")
	# except Exception as e:
	# 	except_count += 1
	# 	print("Error! ",e, profile[0], except_count) # in case of an error, I want the error message and profile id, to make debugging easier.



def main():
	create_sql_tables()
	content_recommendation_filler()	
	collaborative_recommendation_filler()	




create_sql_tables()
collaborative_recommendation_filler()



