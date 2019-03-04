# this class exists to extract data from a csv file
# and return it formatted for persistence into a MySql database

# import needed libraries
import csv
from farmrisk_lib import *

# define Product class
class Need():
    # def __init__(self):
        
#----data functions----#

    # populate product_info list with product data extracted from csv
    def read_needs(self, filename1):
        try:
            with open(filename1) as f1:
                reader = csv.reader(f1)
                # set True if there is a header row
                # header_row = True
                header_row = False
                i = 0
                sql = []
                for row in reader:
                    if header_row:
                        header_row = False
                    else:
                        # extract field information from file
                        temp_n, temp_p, temp_s, temp_z = float(row[dft_col_n]), float(row[dft_col_p]), float(row[dft_col_s]), float(row[dft_col_z])
                        composition = 0b0000 # bit version for programming purposes
                        if temp_n > 0:
                            composition = composition | 0b1000
                        if temp_p > 0:
                            composition = composition | 0b0100
                        if temp_s > 0:
                            composition = composition | 0b0010
                        if temp_z > 0:
                            composition = composition | 0b0001

                        composition_hr = get_composition_hr(composition)
                        # note: the following line doesn't save the data
                        # it creates a list of sql commands
                        # that the calling module will handle
                        # to persist the data to the database
                        temp = "insert into needs(id_need, name, grain, n, p, s, z, composition, composition_hr) values("+str(bin(2**i))+",'"+str(row[0])+"','"+str(row[1])+"',"+str(temp_n)+","+str(temp_p)+","+str(temp_s)+","+str(temp_z)+","+str(bin(composition))+",'"+composition_hr+"')"
                        sql.append(temp)
                        i += 1
            return sql
        except:
            print("Attempted to load field need information from " + filename1 + " and could not. Did you specify a valid filename?")
