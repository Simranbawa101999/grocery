#Import the required Libraries.
from django.views import View
from .models import *
from .products import *
from .orders import *
from .users import *
from django.http import JsonResponse
from .utils.jwt_utils import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
import json
from rest_framework_jwt.settings import api_settings
from rest_framework import status


# The main page of our website. Does not require any authentication.
#Shows the list of all the products 
def grocery_store(request):
    if request.method == 'GET':
        product_list = get_added_products()  
        response_data = {
            "message": "Welcome to the Grocery Store.",
            "instructions": "You can view our products here.",
            "products": product_list[1]
        }
        return JsonResponse(response_data)

#Detailed view of a particular product.
def product_view(request, product_id):
    if request.method == 'GET':

        #calling function view product to view all the details of product.
        product = view_product(product_id)

        #if function return True.
        if product:
            response_data = {
                "message": "Product Details",
                "instructions": "You can view your product details here. Select quantity and click on add to cart to buy.",
                "product": product[1]
            }
            return JsonResponse(response_data)
        else:
            # Handle the case where the product doesn't exist
            return JsonResponse({"message": "Product not found."}, status=404)



#function to view cart of a existing user.
def view_cart(request):
    if request.method == 'GET':
        # Extract the token from the request headers
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

            # Verify the token
            token_info = verify_jwt_token(token)
            if token_info[0]:
                # Token is valid, and token_info[1] contains the user_id
                user_id = token_info[1]

                cart_items_for_user = get_cart_items(user_id)  # Function to return cart items

                if cart_items_for_user[0] == True:
                    response_data = {
                        "message": "Shopping Cart",
                        "instructions": "View the items in your cart.",
                        "cart_items": cart_items_for_user[1]
                    }
                    return JsonResponse(response_data, status=200)
                else:
                    # Handle the case where there are no cart items
                    response_data = {
                        "message": cart_items_for_user[1]
                    }
                    return JsonResponse(response_data, status=200)

            else:
                # Token is invalid
                response_data = {
                    "message": token_info[1]
                }
                return JsonResponse(response_data, status=401)

        else:
            # No token provided in the header
            response_data = {
                "message": "Unauthorized"
            }
            return JsonResponse(response_data, status=401)

#Function to view The list of all added products by admins
def view_added_products(request):
    if request.method == 'GET':
        # Extract the token from the request headers
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

            # Verify the token
            token_info = verify_jwt_token(token)
            #if token verification is successful.
            if token_info[0]:
                user_id = token_info[1]
                added_products = get_added_products(user_id)

                if added_products[0]:
                    response_data = {
                        "message": "List of added products",
                        "products": added_products[1]
                    }
                    return JsonResponse(response_data, status=200)
                else:
                    return JsonResponse({"message": added_products[1]}, status=401)
            else:
                return JsonResponse({"message": token_info[1]}, status=401)
        else:
            return JsonResponse({"message": "Unauthorized"}, status=401)

#function to view all the orders of a particular product.
def view_product_orders(request, encoded_product_id):
    #breakpoint()
    if request.method == 'GET':
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

            # Verify the token
            token_info = verify_jwt_token(token)
            if token_info[0]:
                user_id = token_info[1]

                # Fetch orders using a function, passing user_id and product_id
                orders = get_orders_for_product(user_id, encoded_product_id)

                #if there are existing orders for a product
                if orders[0]:
                    response_data = {
                        "message": f"Orders for product ID {encoded_product_id}",
                        "orders": orders[1]
                    }
                    return JsonResponse(response_data, status=200)
                else:
                    return JsonResponse({"message": str(orders[1])}, status=401)
            else:
                return JsonResponse({"message": token_info[1]}, status=401)
        else:
            return JsonResponse({"message": "Unauthorized"}, status=401)
          
            

#To handle other requests.
def custom_404_view(request, exception=None):
    response_data = {
        "message": "Bad Request",
        "instructions": "Page not found."
    }
    return JsonResponse(response_data, status=404)

def validate_required_fields(data, required_fields):
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    
    if missing_fields:
        missing_fields_str = ", ".join(missing_fields)
        error_message = f"Missing required field(s): {missing_fields_str}"
        return error_message
    return None

#function to handle Signup requests.
@csrf_exempt #to disable csrf security.
def signup(request):
    #breakpoint()
    
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            user_data = json.loads(request.body.decode('utf-8'))
            # Decompose the request data
            required_fields = ["first_name", "middle_name", "last_name", "email", "phone_no", "password"]
            
            validation_error = validate_required_fields(user_data, required_fields)
            
            if validation_error:
                return JsonResponse({"error": validation_error}, status=400)

            first_name = user_data.get('first_name', '')
            middle_name = user_data.get('middle_name', '')
            last_name = user_data.get('last_name', '')
            email = user_data.get('email', '')
            phone_no = user_data.get('phone_no', '')
            password = user_data.get('password', '')
            #role_id = user_data.get('role_id', '')
            #call create_user
            user = create_user(first_name, middle_name, last_name,email, phone_no, password)
            if user[0]==True:
                return JsonResponse({"message": "Sign up Successful", "user_id": user[1]}, status=201)
            else:     
                return JsonResponse({"message": user[1]}, status=400)


        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON data"}, status=400)

    # Handle other HTTP methods here
    return JsonResponse({"message": "Method not allowed"}, status=405)    

@csrf_exempt
def login(request):
   
    if request.method == 'POST':
        #breakpoint()
        try:
            # Parse the JSON data from the request body
            entered_user_data = json.loads(request.body.decode('utf-8'))
            
            # Define the required fields for login
            required_fields = ["email", "password"]

            validation_error = validate_required_fields(entered_user_data, required_fields)

            if validation_error:
                return JsonResponse({"error": validation_error}, status=400)

            # Get the email and password from the request data
            email = entered_user_data.get('email', '')
            password = entered_user_data.get('password', '')

            user = authenticate(email=email, password=password)
            print("user", user)

            if user is not None:
                # User is valid, generate a JWT token
                jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
                jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

                payload = jwt_payload_handler(user)
                print("payload",payload )
                token = jwt_encode_handler(payload)
                print("token:",token)

                return JsonResponse({"message": "Login successful.", "token": token}, status=200)
            else:
                return JsonResponse({"message": "Incorrect email or password."}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON data"}, status=400)
    return JsonResponse({"message": "Method not allowed"}, status=405)

@csrf_exempt
def addtocart(request):
    #breakpoint()
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            user_data = json.loads(request.body.decode('utf-8'))
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

                # Verify the token
                token_info = verify_jwt_token(token)
                if token_info[0]:
                    user_id = token_info[1]

                    # Define the required fields for adding to the cart
                    required_fields = ["product_id", "qty"]

                    validation_error = validate_required_fields(user_data, required_fields)

                    if validation_error:
                        return JsonResponse({"error": validation_error}, status=400)

                    product_id = user_data.get('product_id')
                    qty = user_data.get('qty')    

                    # Check if the product with the given product_id exists
                    # Try to fetch the product with the given product_id
                    try:
                        product = Product.objects.get(id=product_id)
                    except Product.DoesNotExist:
                        return JsonResponse({"message": "Product does not exist"}, status=404)


                    order_details = add_or_update_order_item(user_id, product_id, qty)  

                    if order_details[0]:
                        response_data = {
                            "message": order_details[1]
                            
                        }
                        return JsonResponse(response_data, status=201)
                    else:
                        return JsonResponse({"message": order_details[1]}, status=400)
                else:
                    return JsonResponse({"message": token_info[1]}, status=401)
            else:
                return JsonResponse({"message": "Unauthorized"}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON data"}, status=400)

    return JsonResponse({"message": "Method not allowed"}, status=405)              


@csrf_exempt
def addproduct(request):
    #breakpoint()
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            product_data = json.loads(request.body.decode('utf-8'))
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

                # Verify the token
                token_info = verify_jwt_token(token)
                if token_info[0]:
                    user_id_from_token = token_info[1]
                    # Define the required fields for adding a product
                    required_fields = ["name", "description", "price", "stock_count", "category_ids"]

                    validation_error = validate_required_fields(product_data, required_fields)

                    if validation_error:
                        return JsonResponse({"error": validation_error}, status=400)

                # Fetch the user
                    #try:
                    user = User.objects.get(id=user_id_from_token)

                    # Fetch the role of the user
                    user_role = user.role  

                    # Fetch the role ID of the admin (You may need to adjust this query)
                    admin_role_id = Role.objects.get(name='admin').id 

                    # Check if the user's role matches the admin role
                    if user_role.id == admin_role_id: 
                        name = product_data.get('name')
                        description = product_data.get('description')        
                        price = product_data.get('price')
                        stock_count = product_data.get('stock_count')     
                        category_ids = product_data.get('category_ids')

                        product_create_result= create_product(user_id_from_token, name, description, price, stock_count, category_ids)         
                        if product_create_result[0]:
                            response_data = {
                                "message": product_create_result[1]
                                
                            }
                            return JsonResponse(response_data, status=201)
                        else:
                            return JsonResponse({"message": product_create_result[1]}, status=400)
                    #when users role id is not same as admin's role id.        
                    else:
                        # User does not have permission to update this product
                        response_data = {
                            "message": "You are not authorized to add product."
                        }
                        return JsonResponse(response_data, status=403)
                else:
                    return JsonResponse({"message": token_info[1]}, status=401)
            else:
                return JsonResponse({"message": "Unauthorized"}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON data"}, status=400)

    return JsonResponse({"message": "Method not allowed"}, status=405)              


@csrf_exempt
def add_address(request):
    if request.method == 'POST':
        try:
            # Decompose the request data
            
            address_data = json.loads(request.body.decode('utf-8'))
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

                # Verify the token
                token_info = verify_jwt_token(token)
                if token_info[0]:
                    user_id = token_info[1]
                    #to verify if all the fields are present or not.
                    required_fields = ["country_id", "state_id", "city_id", "pincode", "address", "isdefault"]

                    validation_error = validate_required_fields(address_data, required_fields)

                    if validation_error:
                        return JsonResponse({"error": validation_error}, status=400)                    
                    country_id = address_data.get('country_id')
                    state_id = address_data.get('state_id')
                    city_id = address_data.get('city_id')
                    pincode = address_data.get('pincode')
                    address = address_data.get('address')
                    isdefault = address_data.get('isdefault')

                    # Call a function to create an address entry for the user
                    address_details = create_address(user_id, country_id, state_id, city_id, pincode, address, isdefault)

                    if address_details[0]:
                        return JsonResponse({"message": address_details[1]}, status=201)
                    else:
                        return JsonResponse({"message": address_details[1]}, status=400)
                else:
                    return JsonResponse({"message": token_info[1]}, status=401)
            else:
                return JsonResponse({"message": "Unauthorized"}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON data"}, status=400)

    return JsonResponse({"message": "Method not allowed"}, status=405)      



@csrf_exempt
def update_user_info(request):
    #breakpoint()
    if request.method == 'PUT':
        try:
            # Decompose the request data
            user_data = json.loads(request.body.decode('utf-8'))

            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

                # Verify the token
                token_info = verify_jwt_token(token)
                if token_info[0]:
                    user_id = token_info[1]

                    # Define the allowed fields
                    allowed_fields = ['first_name', 'middle_name', 'last_name', 'phone_no', 'password', 'role_id', 'email']

                    # Check if any disallowed fields are present in user_data
                    disallowed_fields = [field for field in user_data if field not in allowed_fields]

                    if disallowed_fields:
                        # Disallowed fields are present in user_data
                        # Print a message and return a response indicating that it's an invalid argument
                        invalid_fields = ", ".join(disallowed_fields)
                        print(f"Invalid argument(s): {invalid_fields}")
                        response_data = {'error': f'Invalid argument(s): {invalid_fields}'}
                        return JsonResponse(response_data, status=400)    

                    # Either 'email' or 'role_id' is present in user_data
                    if 'email' in user_data or 'role_id' in user_data:                    
                        response_data = {'error': 'Cannot update email or role_id'}
                        return JsonResponse(response_data, status=400)    

            # Fetch user's old information (You might need to implement this function)
                    old_user_data = get_user_info(user_id)
                    
                    # Creating a dictionary with user's new information for each field (if provided)
                    update_kwargs = {
                        "first_name": user_data.get('first_name', old_user_data['first_name']),
                        "middle_name": user_data.get('middle_name', old_user_data['middle_name']),
                        "last_name": user_data.get('last_name', old_user_data['last_name']),
                        #"email": user_data.get('email', old_user_data['email']),
                        "phone_no": user_data.get('phone_no', old_user_data['phone_no']),
                        "password": user_data.get('password', old_user_data['password']),
                        #"role_id": user_data.get('role_id', old_user_data['role_id'])
                    }

                    # Call a function to update user's info, with user_id and update_kwargs
                    updated_user_result = update_user(user_id, **update_kwargs)

                    if updated_user_result[0]:
                        return JsonResponse({"message": updated_user_result[1]}, status=201)
                    else:
                        return JsonResponse({"message": updated_user_result[1]}, status=400)
                else:
                    return JsonResponse({"message": token_info[1]}, status=401)
            else:
                return JsonResponse({"message": "Unauthorized"}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON data"}, status=400)

    return JsonResponse({"message": "Method not allowed"}, status=405)      

@csrf_exempt
def update_user_address(request):
    #breakpoint()
    if request.method == 'PUT':    
        try:
            # Extract user_id from the authenticated user
            address_data= json.loads(request.body.decode('utf-8'))

            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

                # Verify the token
                token_info = verify_jwt_token(token)
                if token_info[0]:
                    user_id = token_info[1]    

                    # Define the allowed fields
                    allowed_fields = ['address_id', 'pincode', 'address', 'isdefault', 'city_id', 'state_id', 'country_id']

                    # Check if any disallowed fields are present in user_data
                    disallowed_fields = [field for field in address_data if field not in allowed_fields]

                    if disallowed_fields:
                        # Disallowed fields are present in user_data
                        # Print a message and return a response indicating that it's an invalid argument
                        invalid_fields = ", ".join(disallowed_fields)
                        print(f"Invalid argument(s): {invalid_fields}")
                        response_data = {'error': f'Invalid argument(s): {invalid_fields}'}
                        return JsonResponse(response_data, status=400)    


                    # Either 'email' or 'role_id' is present in user_data
                    if 'state_id' in address_data or 'city_id' in address_data or 'country_id' in address_data:                    
                        response_data = {'error': 'Cannot update country, state or city'}
                        return JsonResponse(response_data, status=400) 


                # Fetch address_id from the request data
                    address_id = address_data.get('address_id')                  

                    # Fetch the initial info of the address (you can replace this with your own logic)
                    old_address_data_tuple = get_address_info(address_id)
                    if old_address_data_tuple[0]==True:
                        old_address_data = old_address_data_tuple[1]
                        if old_address_data['user_id'] == user_id:
                            # Create a dictionary with the updated info for each column (if provided)
                            update_kwargs = {
                                #"country_id": address_data.get('country_id', old_address_data.get('country_id')),
                                #"state_id": address_data.get('state_id', old_address_data.get('state_id')),
                                #"city_id": address_data.get('city_id', old_address_data.get('city_id')),
                                "pincode": address_data.get('pincode', old_address_data.get('pincode')),
                                "address": address_data.get('address', old_address_data.get('address')),
                                "isdefault": address_data.get('isdefault', old_address_data.get('isdefault'))
                            }

                            # Call a function to update the address info
                            updated_address_result = update_address(user_id, address_id, **update_kwargs)

                            if updated_address_result[0]:
                                return JsonResponse({"message": updated_address_result[1]}, status=status.HTTP_201_CREATED)
                            else:
                                return JsonResponse({"message": updated_address_result[1]}, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            return JsonResponse({"message": "You are not authorized to update this address."}, status=status.HTTP_400_BAD_REQUEST)

                    else:
                        return JsonResponse({"message": "Address does not exists."}, status=status.HTTP_400_BAD_REQUEST )  
                else:
                    return JsonResponse({"message": token_info[1]}, status=401)
            else:
                return JsonResponse({"message": "Unauthorized"}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON data"}, status=400)

    return JsonResponse({"message": "Method not allowed"}, status=405)      


@csrf_exempt
def update_order(request):
    #breakpoint()
    if request.method == 'PUT':
        try:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

                token_info = verify_jwt_token(token)  # Implement this function to verify the token
                if token_info[0]:
                    user_id_from_token = token_info[1]
                    print("token wala blok")

                    # Fetch the most recent order for the user
                    try:
                        order = Order.objects.filter(user_id=user_id_from_token, status__in=['In Cart', 'Placed']).latest('id')
                        order_id_from_token = order.id
                        #fecth the data in request body
                        order_data = json.loads(request.body.decode('utf-8'))
                        #print("oder id", order_id_from_token)

                        # Ensure that the "status" field is present
                        if "status" not in order_data:
                            return JsonResponse({"message": "Missing 'status' field"}, status=400)

                        # Rest of your logic here...
                        # Decompose the request data for status, address_id, and use_default_address
                        #order_data = json.loads(request.body.decode('utf-8'))
                        status = order_data['status']
                        address_id = order_data.get('address_id', None)
                        use_default_address = order_data.get('use_default_address', False)

                        # Calling function to update your order status to place order or cancel order
                        updated_order_result = update_orders(order_id_from_token, status, address_id, use_default_address)
                        print("updte orders",updated_order_result )

                        if updated_order_result[0]:
                            print("print wala block")
                            return JsonResponse({"message": updated_order_result[1]}, status=201)
                        else:
                            print("else wala block")
                            return JsonResponse({"message": updated_order_result[1]}, status=400)

                    except Order.DoesNotExist:
                        return JsonResponse({"message": "No Order found."}, status=404)

                else:
                    return JsonResponse({"message": token_info[1]}, status=401)

            else:
                return JsonResponse({"message": "Unauthorized"}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON data"}, status=400)


    # Handle other HTTP methods if needed
    return JsonResponse({"message": "Method not allowed"}, status=405)

#to update info of a product.
@csrf_exempt
def update_product(request):
    #breakpoint()
    if request.method == 'PUT':    
        try:
            # Extract user_id from the authenticated user
            product_data= json.loads(request.body.decode('utf-8'))

            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

                # Verify the token
                token_info = verify_jwt_token(token)
                if token_info[0]:
                    user_id_from_token = token_info[1] 
                # Fetch the user
                    #try:
                    user = User.objects.get(id=user_id_from_token)

                    # Fetch the role of the user
                    user_role = user.role  

                    # Fetch the role ID of the admin (You may need to adjust this query)
                    admin_role_id = Role.objects.get(name='admin').id 

                    # Check if the user's role matches the admin role
                    if user_role.id == admin_role_id: 
                        #check if request has product id field or not.
                        if "product_id" not in product_data:
                            return JsonResponse({"message": "Missing 'product_id' field"}, status=400)    

                     # Fetch initial product data
                        product_id = product_data.get('product_id')                  
                        old_product_data_tuple = get_product_info(product_id)
                        print("old product data ", old_product_data_tuple)

                        #if product found in the database
                        if old_product_data_tuple[0]==True:
                            old_product_data = old_product_data_tuple[1]

                            #extract the list of categories of the product.
                            category_ids = Productcategory.objects.filter(product_id =product_id).values_list('category_id', flat=True)
                            old_product_data['category_ids'] = list(category_ids)
                            
                            print("category ids:",list(category_ids) )
                            print("category ids without list", category_ids)
                            print("category new wali", product_data['category_ids'])

                            # Create a dictionary with the updated info for each column 
                            update_kwargs = {
                                "description": product_data.get('description', old_product_data.get('description')),
                                "price": product_data.get('price', old_product_data.get('price')),
                                "stock_count": product_data.get('stock_count', old_product_data.get('stock_count')),
                                "category_ids": product_data.get('category_ids', old_product_data.get('category_ids'))
                                
                            }
                            print("update_kwards:", update_kwargs)

                            # Call a function to update the address info
                            updated_product_result = update_products_info(user_id_from_token, product_id, **update_kwargs)
                            print("result:", updated_product_result)

                            if updated_product_result[0]:
                                return JsonResponse({"message": updated_product_result[1]}, status=status.HTTP_201_CREATED)
                            else:
                                return JsonResponse({"message": updated_product_result[1]}, status=status.HTTP_400_BAD_REQUEST)

                        else:
                            return JsonResponse({"message": old_product_data_tuple[1]}, status=status.HTTP_400_BAD_REQUEST )  

                    #when users role id is not same as admin's role id.        
                    else:
                        # User does not have permission to update this product
                        response_data = {
                            "message": "You are not authorized to update this product."
                        }
                        return JsonResponse(response_data, status=403)

                    #except User.DoesNotExist:
                        #return JsonResponse({"message": "No User found."}, status=status.HTTP_404_NOT_FOUND)                            


                #when token verification fails.           
                else:
                    return JsonResponse({"message": token_info[1]}, status=401)
            else:
                return JsonResponse({"message": "Unauthorized"}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON data"}, status=400)

    return JsonResponse({"message": "Method not allowed"}, status=405)      

####helper 
def check_allowed_fields(data, allowed_fields):
    # Check if any disallowed fields are present in data
    disallowed_fields = [field for field in data if field not in allowed_fields]

    if disallowed_fields:
        # Disallowed fields are present in data
        # Construct and return an error message
        invalid_fields = ", ".join(disallowed_fields)
        error_message = f'Invalid argument(s): {invalid_fields}'
        return JsonResponse({'error': error_message}, status=400)
    else:
        # All fields in data are allowed
        return None