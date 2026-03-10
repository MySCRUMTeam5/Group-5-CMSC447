#Logic of Sort and Filter - Assuming one collection in the database right now
#Step 1 - Access database - (assuming SQLite)
con = sqlite3.connect("collection.db") #may need to change this name later

cur = con.cursor()

#Step 2 - Go through database and find all items based on sort and filter parameters
#SORT ONLY (no filter yet)
#THIS IS PURE PYTHON RIGHT NOW, FIGURE OUT JS FRONT END CRAP LATER
if (sort == True):
    price = False
    if (price == True): 
        for row in cur.execute('SELECT * FROM price;'): # are we doing rows or columns?
            #sort data here based on low --> high
            #sort data here based on high --> low
            print(row) 

    date_created = False
    if (data_created == True):
        for row in cur.execute('SELECT * FROM date;'): # are we doing rows or columns?
            #sort data here based on recent --> oldest
            #sort data here based on oldest --> recent
            print(row) 
    
    alpha = False
    if (alpha == True):
        for row in cur.execute('SELECT * FROM name;'): # are we doing rows or columns?
            #sort data here based on A --> Z
            #sort data here based on Z --> A
            print(row) 
    
#Step 3 - Display? 

