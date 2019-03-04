# import needed libraries
import csv
import random
from farmrisk_needs import *
from farmrisk_products import *
import pymysql

# define Farmrisk class
class Farmrisk():
    # init class and connect to MySQL
    def __init__(self, user, password):
        self.connection = pymysql.connect(   host='localhost',
                                    user=user,
                                    database='farmrisk',
                                    password=password,
                                    charset='utf8mb4',
                                    port=5136
                                    )
        self.names = []
        
        # module to load values for random product name generation
        self.blend_word = ' Blend' # static word value for custom product names
        text_file = []
        text_file.append(word_file)
        text_file.append(surname_file)
        with open(text_file[1]) as f:
            self.valid_words = f.read().split()

        # variable to set verbose mode on or off
        self.be_verbose = False

    # print verbose messages if requested
    def verbose(self, message):
        if self.be_verbose:
            print(message)

    # use PyMySql with a condensed function
    def sql(self, cursor, sql, fetch = '', commit = ''):
        # execute the query
        cursor.execute(sql)

        # commit connection if desired
        if commit == dft_commit:
            self.connection.commit()

        # return query if desired
        if fetch == dft_fetch:
            return cursor.fetchall()
        else:
            return 0

    # populate database with data
    def populate(self, filename1, filename2):
        # get need and product data
        need1 = Need()
        need_list = need1.read_needs(filename1)
        self.verbose("Pulling need data from " + filename1)

        product1 = Product()
        product1.be_verbose = False
        product_list = product1.read_products(filename2)
        self.verbose("Pulling product data from " + filename2)

        # write to database
        self.verbose("Populating database with need and product data")
        with self.connection.cursor() as cursor:
            # wipe table so we're not writing duplicate data
            cursor.execute("delete from needs")
            cursor.execute("delete from products")
            cursor.execute("delete from units")
            # read and write the new data
            # from needs table
            for sql in need_list:
                cursor.execute(sql)
            # from products table
            for sql in product_list:
                cursor.execute(sql)
        self.verbose("Data successfully written.")

        # commit changes to database
        self.connection.commit()

    # return a list of individual positions of binary values
    def break_bins(self, value):
        # make a list with every single positional value in value
        # for example
        # possible of values of 0b101
        #   0b001
        #   0b10
        bins = []
        for i in range(1, value + 1):
            if i | value == value:
                value = value ^ i
                bins.append(i)
        return bins

    # return a list of individual binary values contained in an impression
    def get_combos(self, value):
        # make a list with every possible combination of values in value
        # for example
        # possible values of 0b101
        #   0b001
        #   0b100
        #   0b101
        # but not
        #   0b010 <- needs to be disallowed as we walk through the number range
        bins = []
        for i in range(1, value):
            if i | value == value:
                bins.append(i)
        return bins

    # return a value (called an impression) that represents multiple products
    def get_impression(self, cursor, application):
        # load products by application type
        if application == dft_all_flag: # get all products
            products = [ x[0] for x in  (self.sql(cursor, "select id_product from products", dft_fetch))]
        else: # get only dry or liquid depending on how flag is set
            products = [ x[0] for x in  (self.sql(cursor, "select id_product from products where application = " + str(application), dft_fetch))]

        # combine all product ids into a single binary value and return
        impression = 0b0
        for product in products:
            impression = impression | product
        return products, impression
    
    # calculate a ratio and find the greatest if more than one calculation necessary
    def calculate_ratio(self, list_1, list_2):
        this_rat = 0
        for i in range(0, len(list_1)):
            rat = safe_divide(list_1[i], list_2[i])
            # this finds the greatest ratio when comparing multiple items
            if rat > this_rat:
                this_rat = rat
        return this_rat

    # trim a dense product list down to pertinent products and write to database
    def qualify_combos_and_write(self, cursor, products, combo_list, application = '', for_needs = ''):
        # make sure we have the correct table selected
        if for_needs == dft_for_needs:
            current_table = "combos"
        else:
            current_table = "temp"

        # create temp lists from each product in the combo
        qualified = []
        for combo in combo_list:
            temp_products = []
            count = 0
            for product in products:
                # break each combo into its individual products 
                if product & combo == product:
                    temp_products.append(product)
                    count += 1

            # force count higher if we are doing this for needs, in which 
            # case we do want to analyze simples as well as compound
            if for_needs == dft_for_needs: count = 2

            # make sure we don't waste processing power analyzing a simple
            if count > 1:
                # now, we are trimming down the combo list
                # (by appending qualified combos the the qualified list)
                # to include only combos where the products
                # each meet a different chemical need
                qualified = True
                temp_mix = 0b0
                if for_needs == dft_for_needs:
                    application = 0b0
                for product in temp_products:
                    # pull composition and composition_hr from database
                    temp_composition = [ x[0] for x in (self.sql(cursor,  "select composition from products where id_product = " + str(product), dft_fetch))]
                    
                    # if temp_composition == temp_mix, we have
                    # two products containing the same chemical, and 
                    # must disqualify
                    if temp_mix & temp_composition[0] != 0:
                        qualified = False
                        break
                    else: # always resolves to true on first iteration
                        temp_mix = temp_mix | temp_composition[0]
                        if for_needs == dft_for_needs:
                            application = application | [ x[0] for x in (self.sql(cursor, "select application from products where id_product = " + str(product), dft_fetch))][0]

                # add qualified products to database
                if qualified:
                    self.sql(cursor, "insert into " + current_table + " (id_temp, composition, composition_hr, application) values (" + str(combo) + "," + str(temp_mix) + ",'" + get_composition_hr(temp_mix) + "'," + str(application) + ")", '', dft_commit)
        
    # generate a random name to name a new mix
    def get_random_name(self):
        # get a non-duplicate name
        already_picked = True # just checking to see if name has been picked, not if there is a duplicate of the product
        while already_picked:
            already_picked = False
            name = random.choice(self.valid_words).title() + self.blend_word
            if name in self.names:
                already_picked = True
            else:
                self.names.append(name)
        return name

    # complete a complex mathematical operation to create new blends that are mathematically tied to existing blends
    # so they can be compared to find the lowest unit price
    def make_new_blends(self, cursor, application):
        # fetch all combos from temp list that match a compound dry need
        matches = [ x[0] for x in self.sql(cursor, "select id_temp from temp where composition in (select composition from products where compound = 1 and application = " + str(application) + ") ", dft_fetch)]

        # walk through matches one at a time
        row_product = [ x[0] for x in self.sql(cursor, "select count(id_product) from products", dft_fetch) ][0]
        for match in matches:
            new_id_product = 2 ** row_product
            new_list = self.break_bins(match)
            # fetch product(s) we are building out to with our match
            # the blend is the product that alrea
            existing_composition = [ x[0] for x in self.sql(cursor, "select composition from temp where id_temp = " + str(match), dft_fetch) ][0]
            existing_composition_hr = [ x[0] for x in self.sql(cursor, "select composition_hr from temp where id_temp = " + str(match), dft_fetch) ][0]
            existing_products = [ x[0] for x in self.sql(cursor, "select id_product from products where composition = " + str(existing_composition), dft_fetch) ]
            for existing in existing_products:
                existing_units = [ x[0] for x in self.sql(cursor, "select id_unit from products where id_product = " + str(existing), dft_fetch) ]
                existing_unit_list = self.break_bins(existing_units[0])
                temp_new_records = []
                total_price = 0
                total_id_unit = 0b0
                for new in new_list:
                    # get target weights of new blend
                    new_units = [ x[0] for x in self.sql(cursor, "select id_unit from products where id_product = " + str(new), dft_fetch) ]
                    new_unit_list = self.break_bins(new_units[0])
                    weight_list_new = [ float(x[0]) for x in self.sql(cursor, "select weight from units where id_unit in (" + ", ".join(str(s) for s in new_unit_list) + ")", dft_fetch) ]

                    # pull up weights of existing blend
                    compare_chems = [ x[0] for x in self.sql(cursor, "select id_chemical from units where id_unit in (" + ", ".join(str(s) for s in new_unit_list) + ")", dft_fetch) ]
                    weight_list_existing = [ float(x[0]) for x in self.sql(cursor, "select weight from units where id_unit in (" + ", ".join(str(s) for s in existing_unit_list) + ") and id_chemical in (" + ", ".join(str(s) for s in compare_chems) + ")", dft_fetch) ]

                    # grab ratios
                    ratio = self.calculate_ratio(weight_list_existing, weight_list_new)
                    # grab current row to prepare new unit record insertion
                    row_unit = [ x[0] for x in self.sql(cursor, "select count(id_unit) from units", dft_fetch) ][0]
                    for unit in new_unit_list:
                        # ok, here we go. big fancy calculation to create a new unit.
                        new_id_unit = 2 ** row_unit
                        self.sql(cursor, "insert into units(id_unit, id_chemical, weight, application, compound) values (" +
                                str(new_id_unit)  + ", (select U.id_chemical from units U where U.id_unit = " + str(unit) + 
                                "), ((select V.weight from units V where V.id_unit = " + str(unit) + ") * " + str(ratio) + ")," +
                                str(application) + "," + str(dft_compound_flag) + ")", '', dft_commit) 
                        row_unit += 1
                        total_id_unit = total_id_unit | new_id_unit
                    price = ([ float(x[0]) for x in self.sql(cursor, "select price from products where id_product = " + str(new), dft_fetch) ][0])
                    total_price = total_price + (price * ratio)

                # get random new name for blend and write
                name = self.get_random_name()
                self.sql(cursor, "insert into products(id_product, id_unit, parent_combo, name, price, composition, composition_hr, application, compound) values (" + str(new_id_product) + "," + str(total_id_unit) + "," + str(match) + ",'" + self.get_random_name() + "'," +
                        str(total_price) + "," + str(existing_composition) + ",'" + existing_composition_hr + "'," + str(application) + "," + str(dft_compound_flag) + ")", '', dft_commit)
            row_product += 1

    # top-level function to calculate new blended products that calls other functions
    def calculate(self, current_table, for_needs = ''):
        # OR all the products by list type
        self.verbose("Attempting to calculate combinations of products.")
        with self.connection.cursor() as cursor:

            # clear out current table so we are working with clean data
            self.sql(cursor, "delete from " + current_table, '', dft_commit)

            # DRY PRODUCTS #
            self.verbose("Calculating dry products.")

            # get products and a value that represents all dry products together
            products, impression = self.get_impression(cursor, dft_dry_flag)

            # find all possible combos of that value
            combo_list = self.get_combos(impression)

            # limit possible combos only to useful ones that
            #   do not use two products that have the same chemical composition
            #   have the same mix as a pre-made product
            #   and add to database
            self.qualify_combos_and_write(cursor, products, combo_list, dft_dry_flag, for_needs)

            # ok, sweet.  Now we have a list (all_dry_qualified)
            # of every possible combination of products
            # without repeating chemicals

            # now,
            # match qualified products to original products with identical compositio
            # generate a *new* product from that using same unit blends as mixed product
            # write the new product to database
            # do not do this step if calculating for needs
            self.make_new_blends(cursor, dft_dry_flag)
            self.verbose("Completed dry product calculation.")
     

            # LIQUID PRODUCTS #

            self.verbose("Calculating liquid products.")
            # same steps as DRY products but with LIQUID application flag set
            products, impression = self.get_impression(cursor, dft_liquid_flag)
            combo_list = self.get_combos(impression)
            self.qualify_combos_and_write(cursor, products, combo_list, dft_liquid_flag, for_needs)
            self.make_new_blends(cursor, dft_liquid_flag)
     
    def calculate_combo(self, current_table):
        # OR all the products by list type
        with self.connection.cursor() as cursor:

            # clear out current table so we are working with clean data
            self.sql(cursor, "delete from " + current_table, '', dft_commit)

            self.verbose("Calculating all products.")

            # get products and a value that represents all dry products together
            products, impression = self.get_impression(cursor, dft_all_flag)

            # find all possible combos of that value
            combo_list = self.get_combos(impression)

            # limit possible combos only to useful ones that
            #   do not use two products that have the same chemical composition
            #   have the same mix as a pre-made product
            #   and add to database
            self.qualify_combos_and_write(cursor, products, combo_list, '', dft_for_needs)

            # ok, sweet.  Now we have a list (all_dry_qualified)
            # of every possible combination of products
            # without repeating chemicals

            # now,
            # match qualified products to original products with identical compositio
            # generate a *new* product from that using same unit blends as mixed product
            # write the new product to database
            # do not do this step if calculating for needs
            self.verbose("Completed product calculation.")

    def unit_prices(self):
        with self.connection.cursor() as cursor:
            product_list = [ x[0] for x in self.sql(cursor, "select id_product from products", dft_fetch) ]
            for product in product_list:
                units = [ x[0] for x in self.sql(cursor, "select id_unit from products where id_product = " + str(product), dft_fetch) ][0] 
                unit_list = self.break_bins(units)
                total_weight = 0
                for unit in unit_list:
                    total_weight = total_weight + [ float(x[0]) for x in self.sql(cursor, "select weight from units where id_unit = " + str(unit), dft_fetch) ][0]
                price = [ float(x[0]) for x in self.sql(cursor, "select price from products where id_product = " + str(product), dft_fetch) ][0]
                unit_price = safe_divide(price, total_weight)
                self.sql(cursor, "update products set unit_price = " + str(unit_price) + " where id_product = " + str(product), '', dft_commit)

    def fetch_need_weights(self, cursor, id_need, chems):
        weight_list = []
        for chem in chems:
            temp = [ float(x[0]) for x in self.sql(cursor, "select " + chem + " from needs where id_need = " +
                str(id_need), dft_fetch) ][0]
            if temp == '': temp = 0
            weight_list.append(temp)
        
        return weight_list

    def fetch_product_weights(self, cursor, unit_list, chems):
        weight_list = []
        for chem in chems:
            # unable to use pre-built sql function here because we need to get rowcount
            # and would not be good to force rowcount on every single call to sql just for the sake of this one function
            sql = "select weight from units where id_unit in (" + ", ".join(str(s) for s in unit_list) + ") and id_chemical = " + str(get_composition_bin(chem))
            cursor.execute(sql)
            if cursor.rowcount == 0:
                temp = 0
            else:
                temp = [ float(x[0]) for x in cursor.fetchall() ][0]
            weight_list.append(temp)
        return weight_list

    def meet_needs(self):
        with self.connection.cursor() as cursor:
            self.sql(cursor, "delete from purchases", '', dft_commit)
            id_purchase = 1 # starting at 1 instead of 0 since other id numbers in the database have to start at 1
            need_list = [ x[0] for x in self.sql(cursor, "select id_need from needs", dft_fetch) ]
            product_list = [ x [0] for x in self.sql(cursor, "select id_product from products", dft_fetch) ]
            for need in need_list:
                for product in product_list:
                    units = [ x[0] for x in self.sql(cursor, "select id_unit from products where id_product = " + str(product), dft_fetch) ][0]
                    unit_list = self.break_bins(units)
                    composition_hr = [ x[0] for x in self.sql(cursor, "select composition_hr from products where id_product = " + str(product), dft_fetch) ][0]
                    application = [ x[0] for x in self.sql(cursor, "select application from products where id_product = " + str(product), dft_fetch) ][0]
                    weight_list_product = self.fetch_product_weights(cursor, unit_list, composition_hr)
                    weight_list_need = self.fetch_need_weights(cursor, need, composition_hr)
                    #ratio = self.calculate_ratio(weight_list_product, weight_list_need)
                    ratio = self.calculate_ratio(weight_list_need, weight_list_product)
                    if ratio > 0: # don't add if not buying any
                        price = ratio * [ float(x[0]) for x in self.sql(cursor, "select price from products where id_product = " + str(product), dft_fetch) ][0]
                        self.sql(cursor,"insert into purchases(id_purchase, id_product, id_need, ratio_purchased, price, application) values(" + 
                            str(id_purchase) + "," + str(product) + "," + str(need) + "," + str(ratio) + "," + str(price) + "," + str(application) + ")", '', dft_commit)
                        id_purchase += 1

    def report(self):
        with self.connection.cursor() as cursor:
            # fetch a list of needs
            need_list = [ x[0] for x in self.sql(cursor, "select id_need from needs", dft_fetch) ]

            # walk through the needs one by one
            for need in need_list:
                with open(filename3) as write_file:
                    # set up CSV writer
                    f = csv.writer(write_file, delimiter=',',quotechar='"')

                    # pull up information about the need
                    need_record = [ x for x in self.sql(cursor, "select name, grain, n, p, s, z from needs where id_need = " + str(need), dft_fetch) ][0]
                    name, grain, n, p, s, z = need_record[0], need_record[1], float(need_record[2]), float(need_record[3]), float(need_record[4]), float(need_record[5])
                
                    record_print_heading(name, grain, str(n), str(p), str(s), str(z))

                    # fetch combos that meet this need
                    combo_list = [ x[0] for x in self.sql(cursor, "select id_temp from combos where composition_hr in (select composition_hr from needs where id_need = " + str(need) + ")", dft_fetch) ]

                    # this is a bit annoying, but since we don't actually know
                    # the total price until we walk through the combo list,
                    # we first have to calculate prices, put in a temp combo list,
                    # order that list, and then walk back through to get prices
                    # in descending order

                    # be sure to delete temp combo list first
                    self.sql(cursor,"delete from combos_temp",'',dft_commit)
                    for combo in combo_list:
                        total_price, total_application = 0, 0b0 purchase_list = [ x[0] for x in self.sql(cursor,
                            "select id_purchase from purchases where id_need = " +
                            str(need) + " and id_product in (" + ", ".join( str(x) for x in self.break_bins(combo)) + ")", dft_fetch) ]
                        for purchase in purchase_list:

                            # fetch the product information for this purchase
                            purchase_record = [ x for x in self.sql(cursor,
                                "select id_product, ratio_purchased from purchases where id_purchase = " + str(purchase), dft_fetch) ][0]

                            # note some important information about the product
                            ratio_purchased = float(purchase_record[1])
                            product_record = [ x for x in self.sql(cursor,
                                "select price, application from products where id_product = " + str(purchase_record[0]), dft_fetch) ][0]
                            total_application = total_application | product_record[1]
                            price = float(product_record[0]) * ratio_purchased
                            total_price += price
                        total_price += get_application_price(total_application) 

                        # put record in temp list
                        self.sql(cursor, "insert into combos_temp(id_temp, price) values(" + str(combo) + ", " + str(total_price) + ")", '', dft_commit)

                    # now, recapture the combo list ordered nicely by price
                    i = 1
                    combo_list = [ x[0] for x in self.sql(cursor, "select id_temp, price from combos_temp order by price", dft_fetch) ]
                    # walk through combos that meet need one by one
                    for combo in combo_list:
                        print('\n')
                        # tricking this function into printing a heading
                        record_print_product(str(i), "Product","Composition","Application","Default Price","Ratio Purchased","Purchase Price",dft_n.upper(),dft_p.upper(),dft_s.upper(),dft_z.upper())
                       total_application, total_price, total_n, total_p, total_s, total_z = 0b0,0,0,0,0,0 
                       # fetch the individual purchases that make up the combo;
                        purchase_list = [ x[0] for x in self.sql(cursor,
                            "select id_purchase from purchases where id_need = " +
                            str(need) + " and id_product in (" + ", ".join( str(x) for x in self.break_bins(combo)) + ")", dft_fetch) ]

                        # walk through purchases one by one
                        for purchase in purchase_list:

                            # fetch the product information for this purchase
                            purchase_record = [ x for x in self.sql(cursor,
                                "select id_product, ratio_purchased from purchases where id_purchase = " + str(purchase), dft_fetch) ][0]

                            # note some important information about the product
                            ratio_purchased = float(purchase_record[1])
                            product_record = [ x for x in self.sql(cursor,
                                "select id_unit, name, price, composition_hr, application from products where id_product = " + str(purchase_record[0]), dft_fetch) ][0]
                            application = get_application(product_record[4])
                            total_application = total_application | product_record[4]
                            # here, I was tempted to select parent_combo and show
                            # the parentage of artificial products we mixed
                            # from existing products.
                            # however, easier to simply print these separately
                            # on the spreadsheet, i.e.
                            #   PRODUCT X
                            #      Comprised of Product Y (.55) and PRODUCT Z (.45)
                            price = float(product_record[2]) * ratio_purchased
                            total_price = total_price + price

                            # fetch units that make up this product
                            units = [ x for x in self.sql(cursor, "select id_chemical, weight from units where id_unit in (" + ", ".join(str(s) for s in self.break_bins(product_record[0])) + ")", dft_fetch) ]
                            unit_n, unit_p, unit_s, unit_z = 0, 0, 0, 0

                            # walk through units to calculate totals
                            for unit in units:
                                if unit[0] == bin_n:
                                    unit_n = float(unit[1]) * ratio_purchased
                                    total_n += unit_n
                                if unit[0] == bin_p:
                                    unit_p = float(unit[1]) * ratio_purchased
                                    total_p += unit_p
                                if unit[0] == bin_s:
                                    unit_s = float(unit[1]) * ratio_purchased
                                    total_s += unit_s
                                if unit[0] == bin_z:
                                    unit_z = float(unit[1]) * ratio_purchased
                                    total_z += unit_z

                            # print the product record
                            record_print_product('',str(product_record[1]), str(product_record[3]), application.title(), str(float(product_record[2])), str(ratio_purchased), str(price), str(unit_n), str(unit_p), str(unit_s), str(unit_z)) 

                        # tricking this function into printing a footer
                        print('\n')
                        record_print_product('', '', "TOTAL",'','','',str(total_price), str(total_n), str(total_p), str(total_s), str(total_z))
                        record_print_product('', '', "Needed",'','','','', str(n), str(p), str(s), str(z))
                        record_print_product('', '', "Difference",'','','','', str(total_n - n), str(total_p - p), str(total_s - s), str(total_z - z))
                        total_application_price = get_application_price(total_application)
                        print(make_tabbed(['','',"Application",get_application(total_application).title(),str(total_application_price),'',str(total_application_price + total_price)]))
                    

                        



                        i += 1
                    print('\n') # then, "umbrella" the combos #for id in combos select products from break_bins id_temp 

# 1. display a warm welcome
display_welcome()

# 2. create class and open database connection
farmrisk1 = Farmrisk('farmrisk', 'zRC56%jT#**X')

# 3. set verbose mode (True = be verbose, False = not verbose)
farmrisk1.be_verbose = False

# 4. get need and product data and write to database
# you only need to perform this step if you haven't done it on fresh data
farmrisk1.populate(filename1, filename2) # uncomment to populate

# 5. calculate all possible products
# you only need to perform this step if you haven't done it on fresh data
farmrisk1.calculate("temp") # uncomment to calculate

# 6. calculate all unit prices
# you only need to perform this step if you haven't done it on fresh data
farmrisk1.unit_prices() # uncomment to calculate

# 7. calculate all possible products that can meet a need
# this is similar to step 5.
# you only need to perform this step if you haven't done it on fresh data
farmrisk1.calculate_combo("combos") # uncomment to calculate

# 8. for each need, see what it would cost to meet it with each and every product
# you only need to perform this step if you haven't done it on fresh data
farmrisk1.meet_needs() # uncomment to calculate

# 9. now, generate a beautiful report
farmrisk1.report()
