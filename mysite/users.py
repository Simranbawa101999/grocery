from  mysite.models import *
from django.db import transaction
from django.db import IntegrityError
import bcrypt 
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from .models import User


@transaction.atomic
def create_user(first_name, middle_name, last_name,email, phone_no, password):
    """
    Create a new user with the provided information.

    Parameters:
    - first_name (str): First name of the user.
    - middle_name (str): Middle name of the user.
    - last_name (str): Last name of the user.
    - email (str): Email address of the user.
    - phone_no (str): Phone number of the user.
    - password (str): Password for the user account.

    Returns:
    - tuple: A tuple containing a boolean indicating success (True) or failure (False),
            and either the user ID if successful or an error message if unsuccessful.
    """    
    try:
        with transaction.atomic():    
            #salt = bcrypt.gensalt(rounds=12)
            #print(salt)
            #hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
            #print("decode salt", salt.decode("utf-8"))
            # Check if a user with the same email already exists
            try:
                existing_user = User.objects.get(email=email.lower())
                return (False, f"User with email '{email}' already exists.")
            except ObjectDoesNotExist:
                pass  # User with this email does not exist, continue creating


            # Check if the role_id exists in the Role model


            try:
                role = Role.objects.get(name="customer")  # Adjust the criteria as needed
            except Role.DoesNotExist:
                return (False, "Role for 'customer' does not exist.")

            user= User(
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                email=email.lower(),
                phone_no=phone_no,
                role =role ,
                password=make_password(password),
            )

            user.save()
            return (True,user.id)

    except Exception as e:
        error_message = f"Error: {e}"
        return (False, error_message)

@transaction.atomic
def get_user_info(user_id):
    """
    Retrieve user information from the database using the provided user ID.

    Args:
        user_id (int): The unique identifier of the user.

    Returns:
        dict or None: A dictionary containing user information if the user is found, or None if the user does not exist.
    """
    try:
        # Fetch the user's data from the database using the provided user_id
        user = User.objects.get(id=user_id)

        # You can return the user data as a dictionary or any other format you prefer
        user_info = {
            "id": user.id,
            "first_name": user.first_name,
            "middle_name": user.middle_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone_no": user.phone_no,
            "role_id" : user.role_id,
            "password" : user.password,
            # Add more fields as needed
        }

        return user_info

    except User.DoesNotExist:
        # Handle the case where the user with the given user_id does not exist
        return None

@transaction.atomic
def create_role(role_name):
    """
    Create a new role in the 'role' table of a Connected PostgreSQL database using Django ORM.

    Args:
        role_name (str): The name of the role to be created.

    Returns:
        tuple: A tuple containing a boolean indicating success, the role ID, and role name.
    """
    try:
        role_name = role_name.lower()
        role = Role.objects.create(name=role_name, datecreate=timezone.now())
        print(f"Role created with roleid: {role.id}, rolename: {role.name}")
        return (True, role.id, role.name)

    except IntegrityError:
        error_message = f"Role with name '{role_name}' already exists."
        return (False, error_message)

    except Exception as e:
        error_message = f"An error occurred: {e}"
        return (False, error_message)


def create_country(country_name):
    try:
        with transaction.atomic():
            # Normalize the country name (convert to lowercase).
            normalized_country_name = country_name.lower()

            # Check if a category with the same name already exists.
            if Country.objects.filter(name__iexact=normalized_country_name).exists():
                error_message = "Country with the same name already exists."
                return (False, error_message)

            # Create the category and save it to the database.
            country = Country(name=country_name)
            country.save()
            return (True, country.id)

    except Exception as e:
        error_message = f"Error: {e}"
        return (False, error_message)  


def create_state(state_name, country_name):
    try:
        with transaction.atomic():
            # Normalize the country name (convert to lowercase).
            normalized_state_name = state_name.lower()
            normalized_country_name = country_name.lower()

            # Check if a country with the same name exists.
            try:
                country = Country.objects.get(name__iexact=normalized_country_name)
            except Country.DoesNotExist:
                error_message = "Country does not exist in the database."
                return (False, error_message)

            # Check if a category with the same name already exists.
            if State.objects.filter(name__iexact=normalized_state_name).exists():
                error_message = "State with the same name already exists."
                return (False, error_message)

            # Create the category and save it to the database.
            state = State(name=state_name, country=country)
            state.save()
            return (True, state.id)

    except Exception as e:
        error_message = f"Error: {e}"
        return (False, error_message)  

def create_city(city_name, state_name):
    try:
        with transaction.atomic():
            # Normalize the city and state names (convert to lowercase).
            normalized_city_name = city_name.lower()
            normalized_state_name = state_name.lower()

            # Check if a state with the same name exists.
            try:
                state = State.objects.get(name__iexact=normalized_state_name)
                print(state)
                
            except State.DoesNotExist:
                error_message = "State does not exist in the database."
                return (False, error_message)

            # Check if a city with the same name already exists in the database.
            existing_city = City.objects.filter(name__iexact=normalized_city_name,state__name__iexact=normalized_state_name)
            print(existing_city )
            city_with_same_name = existing_city.first() # Get the first matching city

            if city_with_same_name:
                # Check if the existing city has a different state.
                if city_with_same_name.state != state:
                    # If the city with the same name has a different state, create a new city.
                    city = City(name=city_name, state=state)
                    city.save()
                    return (True, city.id)
                else:
                    error_message = "City with the same name already exists for the same state."
                    return (False, error_message)

            else:            
                # Create the city and associate it with the state.
                city = City(name=city_name, state=state)
                city.save()
                return (True, city.id)

    except Exception as e:
        error_message = f"Error: {e}"
        return (False, error_message)        



def update_user(user_id, **kwargs):
    """
    Update user information using Django ORM.

    Args:
        user_id (int): The ID of the user to be updated.
        **kwargs: Keyword arguments representing fields to update and their new values.

    Keyword Args:
        Fields to update and their new values. Possible fields include:
        - first_name (str): The user's first name.
        - middle_name (str): The user's middle name.
        - last_name (str): The user's last name.
        - password (str): The user's password (will be hashed before updating).

    Returns:
        tuple: A tuple containing a boolean indicating success and a message.

    This function allows for the update of various user information fields in the 'User' model.
    It supports updating the first name, middle name, last name, and password.
    Passwords are securely hashed before updating, and other fields are updated as provided.
    The function returns a tuple indicating whether the update was successful and a message.
    """    
    try:
        #breakpoint()
        with transaction.atomic():
            # Retrieve the user object by user_id
            user = User.objects.get(pk=user_id)
            print("old password", user.password)
            print("older role id:", user.role)
            print("kwargs values:",kwargs.items)

            # Update user fields based on keyword arguments
            for field, value in kwargs.items():
                print("field and valesus", field)
                if field == 'password':
                    #salt = bcrypt.gensalt()
                    #hashed_password = bcrypt.hashpw(value.encode("utf-8"), salt)
                    #user.salt = salt.decode("utf-8")
                    #user.hashed_password = hashed_password.decode("utf-8")
                    password = make_password(value)
                    user.password = password
                    #user.save()

                elif field == "email":
                    return (False, "You can not update your email address. Please make a new account.") 

                elif field == "role_id":    
                    return (False, "You can not update your role_id.")  

                else:
                    setattr(user, field, value)

            # Update the 'dateupdate' field with the current timestamp
            user.dateupdate = timezone.now()
        

            # Save the updated user object
            user.save()
            print("new password", user.password)
            print("new role id:", user.role)

            return (True, 'User info updated.')
            

    except User.DoesNotExist:
        error_message = f"User with ID {user_id} does not exist."
        return (False, error_message)

    except IntegrityError:
        error_message = "Integrity error occurred."
        return (False, error_message)

    except Exception as e:
        error_message = f"Error updating user data: {e}"
        return (False, error_message)

def update_role(user_id, new_role_id):
    try:
        # Retrieve the user by user_id
        user = User.objects.get(pk=user_id)

        try:
            # Retrieve the new role by role_id
            new_role = Role.objects.get(id=new_role_id)

            # Update the user's role
            user.role = new_role

            # Save the updated user
            user.save()

            return (True, "Role updated.")  # Role updated successfully
        except Role.DoesNotExist:
            return (False, 'Role does not exist.')  # Role with the given ID does not exist
    except User.DoesNotExist:
        return (False, 'User does not exist.')  # User with the given ID does not exist

def create_address(user_id, country_id, state_id, city_id, pincode, address, isdefault):
    """
    Create a new address entry in the 'Address' model.

    Args:
        user_id (int): The ID of the user associated with the address.
        country_id (int): The ID of the country for the address.
        state_id (int): The ID of the state for the address.
        city_id (int): The ID of the city for the address.
        pincode (str): The pincode of the address.
        address (str): The detailed address information.
        isdefault (bool): Indicates whether the address is the default address for the user.

    Returns:
        tuple: A tuple containing a boolean indicating success and a message.

    This function inserts a new address entry into the 'Address' model with the specified details,
    including the associated user, country, state, city, pincode, and address information.
    It also handles updating the default address flag if necessary and checks for errors,
    including foreign key constraint violations. If the address is created successfully,
    it returns the address ID, otherwise, it returns None.
    """


    try:
        with transaction.atomic():
        # Check if there is already any default address in the table for the user
            if isdefault:
                existing_default_address = Address.objects.filter(user__id=user_id, isdefault=True).first()
                if existing_default_address:
                    # Update the existing default address to set isdefault to False
                    existing_default_address.isdefault = False
                    existing_default_address.save()


            # Retrieve the related objects using their IDs
            try:
                user = User.objects.get(id=user_id)
                country = Country.objects.get(id=country_id)
                state = State.objects.get(id=state_id)
                city = City.objects.get(id=city_id)
            except ObjectDoesNotExist as e:
                # Handle the case where the related objects do not exist
                error_message = f"Any of the ids that you have mentioned for for city, state and country do not exists. Please try again."
                return (False, error_message)

            # Check if the specified country_id matches the country_id in the State table
            try:
                state = State.objects.get(id=state_id, country=country)
            except State.DoesNotExist:
                # Handle the case where the state with the specified id does not exist for the specified country
                error_message = "The state with the specified id does not exist for the specified country."
                return (False, error_message)

            # Check if the specified country_id matches the country_id in the State table
            try:
                city = City.objects.get(id=city_id, state=state)
            except City.DoesNotExist:
                # Handle the case where the state with the specified id does not exist for the specified country
                error_message = "The city with the specified id does not exist for the specified State."
                return (False, error_message)                
            
            # Create a new Address object with related objects
            new_address = Address(
                user=user,
                country=country,
                state=state,
                city=city,
                pincode=pincode,
                address=address,
                isdefault=isdefault,
            )
            new_address.save()

            return (True, f"Congratulations! Address created with id: {new_address.id}")

    except Exception as e:
        error_message = f"Error: {e}"
        return (False, error_message)

@transaction.atomic
def get_address_info(address_id):
    try:
        #breakpoint()
        # Fetch the user's data from the database using the provided user_id
        address = Address.objects.get(id=address_id)     
        print("older adress", address)  
        address_info = {
            "id": address.id,
            "pincode": address.pincode,
            "address": address.address,
            "isdefault": address.isdefault,
            "user_id": address.user_id,
            "country_id":address.country_id,
            "state_id" : address.state_id,
            "city_id" :address.city_id,
            
        }

        return (True,address_info)

    except Address.DoesNotExist:
        # Handle the case where the user with the given user_id does not exist
        return (False, "Mentioned Address does not exists.")

def update_address(user_id, address_id, **kwargs):
    """
    Update address information in the 'Address' model.

    Args:
        address_id (int): The ID of the address to be updated.
        **kwargs: Keyword arguments representing fields to update and their new values.

    Keyword Args:
        Fields to update and their new values. Possible fields include:
        - pincode (str): The postal code or PIN code of the address.
        - address (str): The street address or location.
        - isdefault (bool): Whether the address should be set as the default address for the user.

    Returns:
        tuple: A tuple containing a boolean indicating success and a message.

    This function allows for the update of various address information fields in the 'Address' model.
    It supports updating the country ID, state ID, city ID, pincode, address, and isdefault flag.
    If the 'isdefault' flag is set to True, it will update the default address for the user.
    The function returns a tuple indicating whether the update was successful and a message.
    """
    try:
        #breakpoint()
        with transaction.atomic():
        
        # Check if the address exists and is associated with the user
            address = Address.objects.get(id=address_id, user__id=user_id)

            # Update address fields based on keyword arguments
            for field, value in kwargs.items():

                #if field == "state_id" or field == "city_id" or field == "country_id":
                    #return(False, "Sorry! You can not update state, city or country. Please make a new address.")
                if field == 'isdefault':
                    print("is default wala block")
                    if value == "True":
                        existing_default_address = Address.objects.filter(user__id=user_id, isdefault=True).exclude(id=address_id).first()
                        print("existing default address",existing_default_address )
                        if existing_default_address:
                            print("is existing default address wala block")
                            if existing_default_address.id != address_id:
                                print("is existing default address wala block 2")
                                # Update the existing default address to set isdefault to False
                                existing_default_address.isdefault = False
                                existing_default_address.save()
                        address.isdefault = True
                        print("make address default true")
                        address.save()
                                
                    # If the user wants to make this address as not a default address.
                    else:
                        # Make the address isdefault value False.
                        address.isdefault = False
                        
                else:
                    setattr(address, field, value)

            address.dateupdate = timezone.now()
            address.save()
            return (True, 'Address info is updated.')

    except Address.DoesNotExist:
        error_message = f"Address with ID {address_id} does not exist or is not associated with the user."
        return (False, error_message)

    except Exception as e:
        error_message = f"Error updating address data: {e}"
        return (False, error_message)        


'''
def check_password(input_password, hashed_password):
    return bcrypt.checkpw(input_password.encode("utf-8"), hashed_password.encode("utf-8"))
'''

def is_existing_user(user_data):
    try:
        # Check if a user with the provided email exists in the User model
        existing_user = User.objects.get(email=user_data['email'])
        print("existing user value:",existing_user)
        print('existing user salt value:', existing_user.salt)
        # User exists, return the user object
        return (True, existing_user)
    except User.DoesNotExist:
        # User does not exist
        return (False, "User does not exist, please sign up first.")    

'''def check_password_with_salt(input_password, stored_hashed_password, salt):
    # Encode the input password and salt to bytes
    input_password_bytes = input_password.encode("utf-8")
    salt_bytes = salt.encode("utf-8")
    print("input password", input_password)
    print("salt", salt_bytes)
    print('decoded salt', salt)

    # Combine the salt and input password
    combined_password = salt_bytes + input_password_bytes
    print("cobined password", combined_password)
    print()

    # Hash the combined password
    hashed_input_password  = bcrypt.hashpw(input_password.encode("utf-8"), salt_bytes)
    #hashed_input_password = bcrypt.hashpw(combined_password, stored_hashed_password.encode("utf-8"))

    # Compare the computed hashed password with the stored hashed password
    return hashed_input_password == stored_hashed_password.encode("utf-8")
'''