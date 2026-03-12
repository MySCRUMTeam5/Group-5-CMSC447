from django.shortcuts import render

@require_http_methods(['"GET'])
def sort_filter_collection(request):  
    if request.method != 'GET':
        return JsonResponse({"error": "Method not allowed", status = 405})
    
    sort = request.GET.get("sort")
    
    filter_val = request.GET.get("filter")

    #DO WE WANT ANY OTHER SORT FEATURES?
    #Names may need to be changed based on how we store our data in the database
    sort_dict = {
        "p_price_ascend" : "purchase_price",
        "p_price_descend" : "-purchase_price",
        "alpha_ascend" : "alpha",
        "alpha_descend" : "-alpha",
        "date_ascend" : "purchase_date",
        "date_descend" : "-purchase_date"
    }

    #Right now, doing filter by preset buttons, may move to user input later
    #only doing one filter rn
    filter_dict = {
        "price_below" : ("price__lt", 10),
        "price_above" : ("price__gt", 10),
        "price_equal" : ("price", 10),
        "name" : ("name__contains", None)
    }

    con = sqlite3.connect("collection.db") #may need to change this name later

    cur = con.cursor()

    if sort:
        sort_by = sort_dict.get(sort)
        if sort_by:
            data_sorted = Item.objects.all().order_by(sort_by).values()
    
    elif filter_val:
        filter_by = filter_dict.get(filter_val)
        if filter_by:
            data_filtered = Item.objects.filter(**{filter_by})
    
    elif not sort_by or not filter_by:
        return JsonResponse({"error": "this action could not be completed", status = 400})