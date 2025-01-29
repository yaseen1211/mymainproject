import json
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login as auth_login,logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import product,Category
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from volunteerhead.models import Camp,Volunteer
from django.core.signing import Signer, BadSignature
from django.views.decorators.cache import cache_control


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@csrf_exempt
def Volunteer(request):
    if not hasattr(request.user, 'camp_head'):
        return render(request, 'login.html', {'error': 'you are not Access'})
    
    signer = Signer()
    signed_value = request.COOKIES.get('login')
    camp_id = signer.unsign(signed_value)
    
    camp3 = Camp.objects.get(id=camp_id)

    

        

    if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = json.loads(request.body)
        mode = data.get('mode')
        
        if mode=="1":    # Handle product editing
            try:
                product_id = data.get('product_id')
                ins = product.objects.get(pk=product_id)
                quantity = data.get('item-quantity1')
                limit = data.get('item-limit1')
                print(quantity)

                ins.product_Quantity = quantity
                ins.product_Limit = limit
                ins.save()

                return JsonResponse({
                    'new_quantity': quantity,
                    'new_limit': limit,
                   })

            except product.DoesNotExist:
                return JsonResponse({'error': 'Product not found'})


        elif mode == "2": #add a new product
        
                product_Name = data.get('item-name')
                product_Category_id = data.get('item-category')
                product_Quantity = data.get('item-quantity')
                product_unit = data.get('item-unit')
                product_Limit = data.get('item-limit')

        

                product_Category = Category.objects.get(id=product_Category_id)
              
                products = product(
                    product_Name=product_Name, 
                    product_Category=product_Category, 
                    product_Quantity=product_Quantity, 
                    product_unit=product_unit, 
                    product_Limit=product_Limit, 
                
                    camp1=camp3
                )
                products.save()
                      
                return JsonResponse({
                    'message': 'Item added successfully!'
                     })

 
        elif mode == "3":
                category_id =  data.get('category_id')
                product1_ = product.objects.filter(camp1=camp3, product_Category_id=category_id)
                
                product1_data = list(product1_.values('id', 'product_Name', 'product_Quantity', 'product_Limit','product_unit'))
                return JsonResponse({
                    'product1': product1_data,
                        })
        
        elif mode=="4":

            data = json.loads(request.body)
            product_id = data.get('product_id')
            print("9")
            ins =product.objects.get(pk=product_id)
            ins.delete()
            return JsonResponse({'message': 'Item deleted successfully'}, status=200)
        
        elif mode=="5":

            volunteers1 = camp3.camp2.all()

                
            Volunteers2 = list(volunteers1.values('id', 'name', 'email', 'phone'))
            print(Volunteers2)
            return JsonResponse({
                    'Volunteers2': Volunteers2,
                        })

  

    categories  = Category.objects.all()      
    return render(request, 'Volunteer.html', {'categories':categories})

