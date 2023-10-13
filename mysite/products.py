from  .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist


def create_product(user_id, name, description, price, stock_count, category_ids):
    try:
        with transaction.atomic():
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                error_message = "User does not exist."
                return (False, error_message)

            admin_role = Role.objects.get(name='admin')            

            if user.role != admin_role:
                error_message = "You do not have permission to create products."
                return (False, error_message)

            
            # Check if a product with the same name already exists.            
            if Product.objects.filter(name__iexact=name).exists():
                error_message = "Product with the same name already exists."
                return (False, error_message)

            # Create the product and save it to the database.
            product = Product(
                name=name,
                description=description,
                price=price,
                stock_count=stock_count,
                createdby=user_id
            )
            #product.save()

            # Create a list to store ProductCategory instances
            product_categories = []

            # Associate the product with specified categories.
            for category_id in category_ids:
                try:
                    # Check if the category ID exists in the Category table
                    category = Category.objects.get(pk=category_id)
                    product_category = Productcategory(
                        product=product,
                        category=category,
                        createdby=user_id
                    )
                    product_categories.append(product_category)
                    product.save()
                except Category.DoesNotExist:
                    # Handle the case where a category with the specified ID does not exist
                    error_message = f"Category with ID {category_id} does not exist."
                    return (False, error_message)

            # Save all ProductCategory instances in a single batch
            Productcategory.objects.bulk_create(product_categories)

            print(f"Product added: {product}")
            return (True, f"Product created successfully! product id : {product.id}")

    except Exception as e:
        error_message = f"Error: {e}"
        return (False, error_message)


def create_category(category_name):
    try:
        with transaction.atomic():
            # Normalize the category name (convert to lowercase).
            normalized_category_name = category_name.lower()

            # Check if a category with the same name already exists.
            if Category.objects.filter(name__iexact=normalized_category_name).exists():
                error_message = "Category with the same name already exists."
                return (False, error_message)

            # Create the category and save it to the database.
            category = Category(name=category_name)
            category.save()
            return (True, category.id)

    except Exception as e:
        error_message = f"Error: {e}"
        return (False, error_message)


def get_added_products(user_id=None):
    try:
        with transaction.atomic():

            # Common fields to fetch for all users
            common_fields = ['name', 'price']
            additional_fields=[]

            # Perform necessary queries to retrieve product data
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    return (False, "User does not exist.")

                admin_role = Role.objects.get(name="admin")


                if user.role == admin_role:
                    # Additional fields for admin users
                    additional_fields = ['id','description', 'stock_count', 'datecreated', 'dateupdated','datedeleted','createdby','updateby','deletedby']
                    

                else:
                    return (False, "You do not have permission for this activity.")
                    # Additional fields for non-admin users
                    #pass
                
            fields_to_fetch = common_fields + additional_fields

                # Fetch products with selected fields
            products = Product.objects.values(*fields_to_fetch)

                # Convert the result to a list of dictionaries
            product_list = list(products)

            return (True, product_list)

    except Exception as e:
        error_message = f"Error: {e}"
        return (False, error_message)

#Detailed view of a particular Product
def view_product(product_id):
    try:        
        with transaction.atomic():  #for the database consistency
            # Fetch the product using Django's model
            product = Product.objects.get(id=product_id)

            # Create a dictionary containing product details
            product_details = {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": str(product.price)
            }

            return ( True , product_details)

#Exception if product does not exists.
    except Product.DoesNotExist:
        error_message = "Product not found."
        return(False, error_message)

#To handle other exceptions in database.
    except Exception as e:
        error_message = f"Error: {e}"
        return ( False, error_message)


def update_products_info(user_id, product_id, **kwargs):
    #breakpoint()
    try:
        with transaction.atomic():
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                error_message = "User does not exist."
                return (False, error_message)

            admin_role = Role.objects.get(name='admin')            

            if user.role != admin_role:
                error_message = "You do not have permission to update a product."
                return (False, error_message)    

            # Retrieve the product using the Django ORM
            product = get_object_or_404(Product, id=product_id)
            # Check if 'price' is provided and not negative
            if 'price' in kwargs and kwargs['price'] < 0:
                return (False, "Price cannot be negative.")

            # Check if 'stock_count' is provided and not negative
            if 'stock_count' in kwargs and kwargs['stock_count'] < 0:
                return (False,"Stock count cannot be negative.")

            # Check if 'category_ids' is provided
            if 'category_ids' in kwargs:
                # Get the current category IDs associated with the product
                current_category_ids = list(product.productcategory_set.values_list('category_id', flat=True))
                print("current category_ids", current_category_ids)

                #to check if entered categories exists in the database or not
                for category_id in kwargs['category_ids']:
                    try:
                        category = Category.objects.get(id=category_id)
                    except Category.DoesNotExist:
                        return (False,f"Category with ID {category_id} does not exist. Please enter a valid category id to update." ) 

                # Convert 'category_ids' to a set for easy comparison
                new_category_ids = set(kwargs['category_ids'])
                    
                # Find categories to delete and insert
                categories_to_delete = list(set(current_category_ids) - new_category_ids)
                categories_to_insert = list(new_category_ids - set(current_category_ids))

                # Insert new rows with product_id and category_ids to insert
                if categories_to_insert:
                    for category_id in categories_to_insert:
                        #try:
                        category = Category.objects.get(id=category_id)
                        product_category = Productcategory(
                            product_id=product.id, 
                            category_id=category.id,  
                            datecreate=timezone.now(),
                            createdby=user_id
                        )
                        #category_insertion_successful = True
                        #except ObjectDoesNotExist:
                            #return (False, f"Category with ID {category_id} does not exist.")
                            #category_insertion_successful = False
                    product_category.save()

                # Delete old rows with product_id and category_ids to delete
                if categories_to_delete:
                    Productcategory.objects.filter(
                        product=product,
                        category_id__in=categories_to_delete
                    ).update(
                        datedeleted=timezone.now(),
                        deletedby=user_id
                    )


            # Update the product fields based on the provided POST data
            for field, value in kwargs.items():        
                setattr(product, field, value)

            # Update 'dateupdate' with the current time and 'updatedby' with the user_id
            product.dateupdated = timezone.now()
            product.updateby = user_id

            # Save the updated product to the database
            product.save()

            return (True, "Product info updated.")

    except Product.DoesNotExist:
        return (False, "Product not found.")
    except Exception as e:
        return (False,  f"Error updating product data: {str(e)}")


def get_product_info(product_id):
    try:
        product = Product.objects.get(id = product_id)
        
        category_ids = Productcategory.objects.filter(product_id=product_id).values_list('category_id', flat=True)
        category_id_list = list(category_ids)
       
        product_info = {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "stock_count": product.stock_count,
            "category_ids": category_id_list,
        }

        return (True,product_info)

    except Product.DoesNotExist:
        # Handle the case where the user with the given user_id does not exist
        return (False, "Product does not exists")












