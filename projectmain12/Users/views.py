import json
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login as auth_login,logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from camp.models import product,Category
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from volunteerhead.models import Camp
from superadmin.models import Zone

def Users(request):
    if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
       
        data = json.loads(request.body)
        mode = data.get('mode')   
        print(data)
        if mode=="1":
            category_id = data.get('category_id')
            selectedcampId = data.get('selectedcampId')

            camp = Camp.objects.get(id=selectedcampId)
            camp_name = camp.name

            products1=product.objects.filter(product_Category_id=category_id,camp1_id=selectedcampId)
            products = list(products1.values('id', 'product_Name', 'product_Quantity', 'product_unit','product_Limit'))
            return JsonResponse({'message': "R.",'products':products,'camp_name':camp_name})
    if request.method == "POST":
        zone_id = request.POST.get('zone')
        camps = Camp.objects.filter(campHead1__zone1_id=zone_id).select_related('campHead1__zone1')
        categories=Category.objects.all()
        zone = Zone.objects.get(id=zone_id)
        zone_name = zone.name


        return render(request, 'user.html',{'camps':camps,'categories':categories,'zone_name':zone_name})
                        






