# exit notes: is this on the right track?
# because there is no simple P chemical, do we have to calculate
# blends involving blends?
# or because there is no simple P chemical, is it also sufficient
# to leave blends of blends out of the picture?
# the answer is: probably

# Products

# each product has a signature that shows which chemicals are in it
# for example
# 0b1101 = N, P and Z
# 0b0010 = S

# have permutations only create blends that match compound of existings blends
# REMEMBER, we are comparing prices, not making a tree of each possible combo!
# In other words, our goal is to prove that a mix, say MESZ, is actually
# more or less expensive that just throwing individual products together.
#  
# ok, so here is the problem.
# when there is a mixed/blended product, say, MESZ, which has
# n, p, s and z, the blended product (MESZ) is agnostic to
# the pricing of the chemicals compounded into it.  For example:
# total cost = $5.00
# n, p, s, z each contribute 25% of the product total weight.
# but n: $3.40, p: $.80, s: $0.05, z: $.75 per pound?
# or each $1.20 per pound?
# we *just don't know* without accessing information which the chemical maker
# has hidden.
#
# so....
#
# the solution is to take the *overall unit price* of the mixed product
# and simulate other chemicals blending to make a mixed product of 
# equal composition and weight, and compare the *overall unit price*
# of the simulated mixed product.
#
# the Products class provides this capability by
# giving us a way to create dummy sets of blended products
# and compare them with existing blends.
#
# but also keep in mind that the dummy blends can be manipulated to meet
# an *EXACT* need whereas the mixed blends will have to be supplemented
# with simple chemicals
#
#
# import needed libraries
import csv
import random
from farmrisk_lib import *

# define Product class
class Product():
    def __init__(self):

        # be verbose?
        self.be_verbose = True

#----data functions----#
    # This function creates (simulates) a new blended product
    def mix_a_product(product_list):
        """Warning: function mix_a_product is designed only to work if
        the user passes it chemicals that are in simple, unmixed form.
        It is up to the programmer to QA this -- the function doesn't handle
        the error of having to read a blended chemical!
        Error handling should occur before parameters are passed."""
        # lingo guidance: rat = ratio
        unit_price = 0
        for product in product_list:
            unit_price += product['unit_price'] * product['rat']
        return unit_price

    # populate product_info list with product data extracted from csv
    def read_products(self, filename1):
        # try to open file
        if 1 == 1:
        #try:
            with open(filename1) as f1:
                reader = csv.reader(f1)
                header_row = True # set to False if no header row
                i_product = 0
                i_unit = 0
                sql = []
                for row in reader:
                    # skip a header row if necessary
                    if header_row:
                        header_row = False
                    # else get to work and read the data for each row
                    else:
                        # read values from file into temporary variables
                        temp_n, temp_p, temp_s, temp_z = float(row[dft_col_prod_n]), float(row[dft_col_prod_p]), float(row[dft_col_prod_s]), float(row[dft_col_prod_z])

                        # determine product composition
                        composition = bin_0
                        if temp_n > 0: 
                            composition = composition | bin_n
                        if temp_p > 0: 
                            composition = composition | bin_p
                        if temp_s > 0: 
                            composition = composition | bin_s
                        if temp_z > 0: 
                            composition = composition | bin_z
                        composition_hr = get_composition_hr(composition)
                        if self.be_verbose:
                            if i_product == 0:
                                print("Loaded 1 product ok")
                            else:
                                print("Loaded " + str(i_product + 1) + " products ok")

                        # set application flag
                        if row[dft_col_app].lower() == dft_dry:
                            application = dft_dry_flag
                        else:
                            application = dft_liquid_flag
                        # set compound flag
                        if len(composition_hr) > 1:
                            compound = dft_compound_flag
                        else:
                            compound = dft_simple_flag

                        # we have to do this later because it is necessary
                        # to know if unit is linked to another unit
                        units = 0b0
                        if temp_n > 0:
                            temp = "insert into units(id_unit, id_chemical, weight, application, compound) values("+str(2**i_unit)+","+str(bin_n)+","+str(temp_n)+","+str(application)+","+str(compound)+")"
                            sql.append(temp)
                            units = units | 2**i_unit
                            i_unit += 1
                        if temp_p > 0:
                            temp = "insert into units(id_unit, id_chemical, weight, application, compound) values("+str(2**i_unit)+","+str(bin_p)+","+str(temp_p)+","+str(application)+","+str(compound)+")"
                            sql.append(temp)
                            units = units | 2**i_unit
                            i_unit += 1
                        if temp_s > 0:
                            temp = "insert into units(id_unit, id_chemical, weight, application, compound) values("+str(2**i_unit)+","+str(bin_s)+","+str(temp_s)+","+str(application)+","+str(compound)+")"
                            sql.append(temp)
                            units = units | 2**i_unit
                            i_unit += 1
                        if temp_z > 0:
                            temp = "insert into units(id_unit, id_chemical, weight, application, compound) values("+str(2**i_unit)+","+str(bin_z)+","+str(temp_z)+","+str(application)+","+str(compound)+")"
                            sql.append(temp)
                            units = units | 2**i_unit
                            i_unit += 1

                        # add new product to info list
                        temp = "insert into products(id_product, id_unit, parent_combo, name, price, composition, composition_hr, application, compound) values("+bin(2**i_product)+","+bin(units)+","+str(0b0)+",'"+row[dft_col_name]+"',"+str(float(row[dft_col_price]))+","+bin(composition)+",'"+composition_hr+"',"+bin(application)+","+bin(compound)+")"
                        sql.append(temp)
                        i_product += 1
            return sql

        # handle error if file couldn't load or populate
        else:
            print("done")
        #except:
        #    print("Could not load products from `" + filename1 + "'.  Did you specify a valid filename?")
    
    # calculate unit prices
    def calculate_unit_prices(self):
        # walk through list of products
        for product in self.info:
            
            # copy info from list of products to temp data and make calculations as necessary
            application = product['application']
            composition = product['composition']
            composition_hr = product['composition_hr']
            weight = product['n'] + product['p'] + product['s'] + product['z'] 
            temp = {'product_id': product['product_id'],
                    'composition': composition,
                    'composition_hr': composition_hr,
                    'application': application,
                    'name': product['name'],
                    'price': product['price'],
                    'weight': weight,
                    'unit_price': safe_divide(product['price'], weight),
                    'weight_n': product['n'],
                    'pct_of_total_n': safe_divide(product['n'], weight),
                    'source_n': 'unknown',
                    'weight_p': product['p'],
                    'pct_of_total_p': safe_divide(product['p'], weight),
                    'source_p': 'unknown',
                    'weight_s': product['s'],
                    'pct_of_total_s': safe_divide(product['s'], weight),
                    'source_s': 'unknown',
                    'weight_z': product['z'],
                    'pct_of_total_z': safe_divide(product['z'], weight),
                    'source_z': 'unknown'}

            # append to unit prices list
            self.unit_prices.append(temp)
            
#----printing functions----#

    # Print the unit prices in a nicely formatted way
    # options
    #   fmt = fmt_product       print the products listed in order of id (0, 1, 2, 3)
    #   fmt = fmt_chemical      print a table of products sorted by chemical
    # about mk_pct
    #   I couldn't decide if it was better to format percentage data for viewing as 31.444% or 0.314444
    #   in farmrisk_lib.py, change mk_pct to `100' for the former or `1' for the latter
    def print_unit_prices(self, fmt = fmt_chemical):
        # sort it by product ID
        if fmt.lower() == fmt_product:
            print('Unit prices')
            print('===========')
            for product in self.unit_prices:
                print('\n')
                make_pretty(product['name'])
                print('\tProduct ID\t' + product['product_id'])
                print('\tComposition\t' + product['composition_hr'].upper() + ' (' + str(bin(product['composition'])) + ')')
                print('\tWeight\t\t' + str(product['weight']))
                print('\tUnit Price\t$' + str(product['unit_price']))
                print('\tApplication\t' + product['application'].title() + '\n')
                if product['composition'] & bin_n == bin_n:
                    print('\tNitrogen (N)')
                    print('\t------------')
                    print('\t\tWeight\t\t' + str(product['weight_n']))
                    print('\t\t% of total\t' + str(product['pct_of_total_n'] * mk_pct))
                if product['composition'] & bin_p == bin_p:
                    print('\tPhosphorus (P)')
                    print('\t--------------')
                    print('\t\tWeight\t\t' + str(product['weight_p']))
                    print('\t\t% of total\t' + str(product['pct_of_total_p'] * mk_pct))
                if product['composition'] & bin_s == bin_s:
                    print('\tSulfur (S)')
                    print('\t----------')
                    print('\t\tWeight\t\t' + str(product['weight_s']))
                    print('\t\t% of total\t' + str(product['pct_of_total_s'] * mk_pct))
                if product['composition'] & bin_z == bin_z:
                    print('\tZinc (Z)')
                    print('\t--------')
                    print('\t\tWeight\t\t' + str(product['weight_z']))
                    print('\t\t% of total\t' + str(product['pct_of_total_z'] * mk_pct))

        # sort it by chemical or chemical compound
        if fmt.lower() == fmt_chemical:
            print('Unit prices')
            print('===========')
            for composition in self.composition:
                c = ''
                do_n, do_p, do_s, do_z = False, False, False, False
                if composition & bin_n == bin_n:
                    c += '\nNitrogen (N)'
                    do_n = True
                if composition & bin_p == bin_p:
                    c += '\nPhosphorus (P)'
                    do_p = True
                if composition & bin_s == bin_s:
                    c += '\nSulfur (S)'
                    do_s = True
                if composition & bin_z == bin_z:
                    c += '\nZinc (Z)'
                    do_z = True
                print('\n' + c)
                print('--------------')
                for product in self.unit_prices:
                    if product['composition'] == composition:
                        print('\n\t'+product['name'])
                        print('\t----------')
                        print('\tProduct ID\t' + product['product_id'])
                        print('\tWeight\t\t' + str(product['weight']))
                        print('\tUnit Price\t$' + str(product['unit_price']))
                        print('\tApplication\t' + product['application'].title() + '\n')
                        if do_n: print('\tN % of total\t' + str(product['pct_of_total_n'] * mk_pct))
                        if do_p: print('\tP % of total\t' + str(product['pct_of_total_p'] * mk_pct))
                        if do_s: print('\tS % of total\t' + str(product['pct_of_total_s'] * mk_pct))
                        if do_z: print('\tZ % of total\t' + str(product['pct_of_total_z'] * mk_pct))
