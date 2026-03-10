#Logic of Sort and Filter - Assuming one collection in the database right now
#Step 1 - Access database - (assuming SQLite)
con = sqlite3.connect("collection.db") #may need to change this name later

cur = con.cursor()

#DO WE WANT ANY OTHER SORT FEATURES?
price_ascend = False
price_descend = False

newest_item = False
oldest_item = False

alpha_ascend = False
alpha_descend = False

#Step 2 - Go through database and find all items based on sort and filter parameters
#SORT ONLY (no filter yet)
#THIS IS PURE PYTHON RIGHT NOW, FIGURE OUT JS FRONT END CRAP LATER
if (sort == True):
    if (price_ascend == True): 
        for row in cur.execute('SELECT * FROM collection ORDER BY price DESC;'): 
    else if (price_descend == True):
        for row in cur.execute('SELECT * FROM collection ORDER BY price ASC')
            print(row)

    else if (newest_item == True):
        for row in cur.execute('SELECT * FROM collection ORDER BY date DESC;'): 
            print(row) 
    else if (oldest_item == True):
        for row in cur.execute('SELECT * FROM collection ORDER BY date ASC'):
            print(row)
    
    else if (alpha_descend == True):
        for row in cur.execute('SELECT * FROM collection ORDER BY name DESC;'): 
            print(row) 
        for row in cur.execute('SELECT * FROM collection ORDER BY name ASC'):
            print(row)
