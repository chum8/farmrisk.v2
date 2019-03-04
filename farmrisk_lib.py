# some static values for farmrisk modules to share
bin_0 = 0b0000 # default value (zero)
bin_n = 0b1000 # N (Nitrogen exists)
bin_p = 0b0100 # P (Phosphorus exists)
bin_s = 0b0010 # S (sulfur exists)
bin_z = 0b0001 # Z (zinc exists
bin_all_products = [bin_n, bin_p, bin_s, bin_z]
price_dry = 6 # current price per acre to apply dry
price_liquid = 11 # current price per acre to apply liquid
mk_pct = 100 # useful to quickly change formatting from displaying as decimal or percentage -- 100 makes a number appear as 13.44, 1 makes it .1344

# some more default values
filename1, filename2, filename3 = 'data/needs-01.csv', 'data/fertilizers-01.csv', 'data/report-01.csv'
word_file, surname_file = 'data/words_alpha.txt', 'data/surnames.txt'
dft_dry = "dry"
dft_liquid = "liquid"
dft_all = "both"
dft_dry_flag = 0b1
dft_liquid_flag = 0b10
dft_all_flag = 0b11
dft_simple_flag = 0b0
dft_compound_flag = 0b1
dft_for_needs = "n3j28,J]s4nZ"
dft_n = "n"
dft_p = "p"
dft_s = "s"
dft_z = "z"
dft_all_products = dft_n + dft_p + dft_s + dft_z
dft_fetch = "fetch"
dft_commit = "commit"
dft_col_size = 9
dft_tab_size = 3
dft_col_n = 3
dft_col_p = 4
dft_col_s = 5
dft_col_z = 6
dft_col_prod_n = 1
dft_col_prod_p = 2
dft_col_prod_s = 3
dft_col_prod_z = 4
dft_col_app = 5  
dft_col_name = 0
dft_col_price = 6

# formatting variables
fmt_product = "product"
fmt_chemical = "chemical"

# We need a division by zero safe function
def safe_divide(num1, num2):
    if num1 > 0 and num2 > 0:
        return float(num1 / num2)
    else:
        return float(0)

# We need a nice heading formatting function
def make_heading(s):
    line, t = '', ''
    for i in range(0, len(s) + 4):
        line += '-'
    line2 = '|' + line[2:] + '|'
    t += line
    t += '\n' + line2
    t += '\n| ' + s + ' |'
    t += '\n' + line2
    t += '\n' + line
    return t

# We need a nice tab formatting function
def make_tabbed(items):
    tab = ''.join(' ' for i in range(0, dft_tab_size))
    t = ''
    for s in items:
        if len(s) > dft_col_size:
            s = s[:dft_col_size]
        if len(s) < dft_col_size:
            s = s + (''.join(' ' for i in range(len(s), dft_col_size)))
        t += s + tab
    return t

# We need to print a record heading
def record_print_heading(name, grain, n, p, s, z):
    print(make_heading(name.upper() + ' ' + grain))
    print("Needed")
    print(make_tabbed([dft_n.upper(), dft_p.upper(), dft_s.upper(), dft_z.upper()]))
    print(make_tabbed([n, p, s, z]))

# We need to print a product
def record_print_product(heading, name, composition, application, price, ratio, this_price, n, p, s, z):
    print(make_tabbed([heading, name, composition, application, price, ratio, this_price, n, p, s, z]))

# We need a function that converts binary chemical values to human readable
def get_composition_hr(composition):
    composition_hr = ''
    if composition | bin_n == composition:
        composition_hr += dft_n
    if composition | bin_p == composition:
        composition_hr += dft_p
    if composition | bin_s == composition:
        composition_hr += dft_s
    if composition | bin_z == composition:
        composition_hr += dft_z
    return composition_hr

# We need a function that returns the corresponding letter to binary value
def get_composition_letter(value):
    letter = ''
    if value == bin_n : letter = dft_n
    if value == bin_p : letter = dft_p
    if value == bin_s : letter = dft_s
    if value == bin_z : letter = dft_z
    return letter

# and vice versa
def get_composition_bin(value):
    binary = ''
    if value == dft_n: binary = bin_n
    if value == dft_p: binary = bin_p
    if value == dft_s: binary = bin_s
    if value == dft_z: binary = bin_z
    return binary

# We need a function that returns the corresponding application to binary value
def get_application(value):
    application = ''
    if value == dft_dry_flag: application = dft_dry
    if value == dft_liquid_flag: application = dft_liquid
    if value == dft_dry_flag | dft_liquid_flag: application = dft_all
    return application

def get_application_price(value):
    price = 0
    if value | dft_dry_flag == value: price += price_dry
    if value | dft_liquid_flag == value : price += price_liquid
    return price

# We need a nice welcome message
def display_welcome():
    print("Welcome to Farmrisk!")
    print("Version 1.0")
    print("by Douglas Michael Singer")
    print("Licensed to Steiner Farms, LLC")
    print("Copyright (c) 2018-2019, all rights reserved.")
