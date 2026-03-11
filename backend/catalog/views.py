from django.shortcuts import render

@require_http_methods(["GET"])
def sort_filter_collection(request):  
    sort = request.GET.get("sort")
    
    filter_val = request.GET.get("filter")

    #DO WE WANT ANY OTHER SORT FEATURES?
    #Names may need to be changed based on how we store our data in the database
    sort_values = {
        "p_price_ascend" : "purchase_price",
        "p_price_descend" : "-purchase_price",
        "alpha_ascend" : "alpha",
        "alpha_descend" : "-alpha",
        "date_ascend" : "purchase_date",
        "date_descend" : "-purchase_date"
    }

    filter_values = {
        #add in filter values here
    }

    sort_by = sort_values.get(sort)

    con = sqlite3.connect("collection.db") #may need to change this name later

    cur = con.cursor()

    if sort and sort_by:
        data_sorted = Collection.objects.all().order_by(sort_by).values()
    
    elif filter_val and filter_by:
        #fill in parameter for filter function here
        data_filtered = Collection.objects.filter().values()
    
    elif not sort_by or not filter_by:
        return JsonResponse({"error": "this action could not be completed", status = 400})