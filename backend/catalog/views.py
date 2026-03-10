from django.shortcuts import render

# Create your views here.
def sort_filter_collection(request):
    #DO WE WANT ANY OTHER SORT FEATURES?
    price_ascend = False
    price_descend = False

    newest_item = False
    oldest_item = False

    alpha_ascend = False
    alpha_descend = False

    sort = request.GET.get("sort")
    
    filter_val = request.GET.get("filter")

    con = sqlite3.connect("collection.db") #may need to change this name later

    cur = con.cursor()

    #THIS IS PURE PYTHON RIGHT NOW, FIGURE OUT JS FRONT END CRAP LATER
    if sort:
        #find sort field and mark as a bool true
        if (price_ascend == True): 
            for row in cur.execute('SELECT * FROM collection ORDER BY price DESC;'): 
                print(row)
        elif (price_descend == True):
            for row in cur.execute('SELECT * FROM collection ORDER BY price ASC')
                print(row)

        elif (newest_item == True):
            for row in cur.execute('SELECT * FROM collection ORDER BY date DESC;'): 
                print(row) 
        elif (oldest_item == True):
            for row in cur.execute('SELECT * FROM collection ORDER BY date ASC'):
                print(row)
        
        elif (alpha_descend == True):
            for row in cur.execute('SELECT * FROM collection ORDER BY name DESC;'): 
                print(row) 
            for row in cur.execute('SELECT * FROM collection ORDER BY name ASC'):
                print(row)
    
    elif filter_val:
        #find all the values from filter and display