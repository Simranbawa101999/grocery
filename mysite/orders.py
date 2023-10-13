from  .models import *
from decimal import Decimal  # Import Decimal for precision
from django.db import transaction
from django.db.models import Sum 
from django.core.exceptions import PermissionDenied


def calculate_total_amount(qty, price):
    """
    Calculate the total amount based on quantity and unit price.

    Args:
        qty (str or int): The quantity of the item.
        price (str or float): The unit price of the item.

    Returns:
        Decimal: The total amount calculated by multiplying the quantity and unit price.

    This function takes the quantity and unit price of an item, converts them to floating-point numbers,
    and calculates the total amount by multiplying them. The result is returned as a Decimal for precision.
    """
    qty_float = float(qty)
    price_float = float(price)
    return Decimal(qty_float * price_float)

@transaction.atomic
def create_order_item(order_id, product_id, qty, price):
    """
    Create a new order item and insert it into the 'OrderItem' table of a PostgreSQL database.

    Args:
        order (Order): The Order instance to which the item belongs.
        product_id (int): The ID of the product associated with the item.
        qty (int or str): The quantity of the item.
        price (float or str): The unit price of the item.

    Returns:
        OrderItem: The newly created OrderItem instance.

    This function calculates the total amount for the order item using the 'calculate_total_amount' function,
    then inserts a new record into the 'OrderItem' table with the provided details, including order,
    product ID, quantity, price, total amount, and the current timestamp for the creation date.
    It returns the newly created Orderitem instance.
    """
    total_amount = calculate_total_amount(qty, price)
    order = Order.objects.get(id=order_id)
    order_item = Orderitem.objects.create(
        order=order,
        product_id=product_id,
        qty=qty,
        price=price,
        total_amount=total_amount,
    )
    return order_item    


def fetch_order_item_data(order_id, product_id):
    """
    Fetch order item data from the 'Orderitem' model of a PostgreSQL database.

    Args:
        order_id (int): The ID of the order associated with the item.
        product_id (int): The ID of the product associated with the item.

    Returns:
        OrderItem or None: An OrderItem instance if found, or None if no matching record is found.

    This function queries the 'OrderItem' model for an order item with the specified order ID and product ID.
    If a matching record is found, it returns the OrderItem instance; otherwise, it returns None.
    """
    try:
        order_item = Orderitem.objects.get(order_id=order_id, product_id=product_id)
        return order_item
    except Orderitem.DoesNotExist:
        return None

def fetch_stock_count_price(product_id):
    """
    Fetch stock count and price data for a product from the 'Product' model of a connected PostgreSQL database.

    Args:
        product_id (int): The ID of the product for which data is to be fetched.

    Returns:
        dict or None: A dictionary containing the stock count and price data for the product if found,
                     or None if no matching record is found.

    This function queries the 'Product' model for a product with the specified product ID.
    If a matching record is found, it returns the stock count and price data as a dictionary;
    otherwise, it returns None.
    """
    try:
        product_data = Product.objects.only('stock_count', 'price').get(id=product_id)
        return {
            'stock_count': product_data.stock_count,
            'price': product_data.price,
        }
    except Product.DoesNotExist:
        return None    

@transaction.atomic
def add_or_update_order_item(user_id, product_id, qty):
    try:
        if qty <= 0:
            error_message = "Entered quantity cannot be negative or 0."
            return (False, error_message)        
        # Check if there is an existing 'In Cart' order for the user
        order = Order.objects.filter(user_id=user_id, status='In Cart').first()

        if order:
            # Check if the product is already in the cart
            order_item = Orderitem.objects.filter(order=order, product_id=product_id).first()

            if order_item:
                stock_price_data = fetch_stock_count_price(product_id)
                stock_count = stock_price_data['stock_count']

                if float(stock_count) >= float(qty):
                    price = stock_price_data['price']
                    total_amount = calculate_total_amount(qty, price)

                    order_item.qty = qty
                    order_item.total_amount = total_amount
                    order_item.save()

                    order.total_amount = Orderitem.objects.filter(order=order).aggregate(Sum('total_amount'))['total_amount__sum']
                    order.save()
                    message = f"Order updated, product qty updated: {qty} and orderitem_id is {order_item.id}"
                    return (True, message)
                else:
                    error_message = "Selected product quantity out of stock. Select a lesser quantity."
                    return (False, error_message)
            else:
                stock_price_data = fetch_stock_count_price(product_id)
                stock_count = stock_price_data['stock_count']

                if float(stock_count) >= float(qty):
                    price = stock_price_data['price']
                    order_item = Orderitem.objects.create(
                        order=order,
                        product_id=product_id,
                        qty=qty,
                        price=price,
                        total_amount=calculate_total_amount(qty, price)
                    )

                    if order_item:
                        order.total_amount = Orderitem.objects.filter(order=order).aggregate(Sum('total_amount'))['total_amount__sum']
                        order.save()
                        message = f"Order updated, product added: {product_id} and orderitem_id is {order_item.id}"
                        return (True, message)
                    else:
                        error_message = "Could not add a new product into the cart."
                        return (False, error_message)
                else:
                    error_message = "Selected product quantity out of stock. Select a lesser quantity."
                    return (False, error_message)
        else:
            stock_price_data = fetch_stock_count_price(product_id)
            stock_count = stock_price_data['stock_count']

            if float(stock_count) >= float(qty):
                price = stock_price_data['price']
                total_amount = calculate_total_amount(qty, price)

                order = Order.objects.create(
                    user_id=user_id,
                    total_amount=total_amount,
                    status='In Cart'
                )

                if order:
                    order_item = Orderitem.objects.create(
                        order=order,
                        product_id=product_id,
                        qty=qty,
                        price=price,
                        total_amount=total_amount
                    )

                    if order_item:
                        order.total_amount = Orderitem.objects.filter(order=order).aggregate(Sum('total_amount'))['total_amount__sum']
                        order.save()
                        message = f"Order is created with order_id as: {order.id} and order item created with id as {order_item.id}"
                        return (True, message)
                    else:
                        error_message = "Could not add a new product into the cart."
                        return (False, error_message)
                else:
                    error_message = "Order creation failed."
                    return (False, error_message)
            else:
                error_message = "Selected product quantity out of stock. Select a lesser quantity."
                return (False, error_message)
    except Exception as e:
        error_message = f"Error: {e}"
        return (False, error_message)                



def update_product_stock_count(updated_stock_count, product_id):
    """
    Update the stock count of a product in the 'Product' model of a PostgreSQL database.

    Args:
        updated_stock_count (int): The updated stock count for the product.
        product_id (int): The ID of the product to be updated.

    Returns:
        None

    This function updates the stock count of a product in the 'Product' model with the specified
    updated stock count and product ID. It then saves the changes to the database using Django's ORM.
    The function does not return any values.
    """
    try:
        product = Product.objects.get(id=product_id)
        product.stock_count = updated_stock_count
        product.save()
        return("Product stock count updated for product ID:", product_id)
    except Product.DoesNotExist:
        return(f"Product not found with ID: {product_id}")       


def place_order(address_id, order_id):
    """
    Place an order in the 'Order' model of a PostgreSQL database.

    Args:
        address_id (int): The ID of the address to associate with the order.
        order_id (int): The ID of the order to be placed.

    Returns:
        None

    This function updates the status of an order in the 'Order' model to 'Placed', associates it with
    the specified address, and records the order date and update date as the current timestamp.
    The changes are then saved to the database using Django's ORM. The function does not return any values.
    """
    try:
        order = Order.objects.get(id=order_id)
        order.status = 'Placed'
        order.address_id = address_id
        order.order_date = timezone.now()
        order.dateupdate = timezone.now()
        order.save()
        return("Order placed for order ID:", order_id)
    except Order.DoesNotExist:
        return("Order not found with ID:", order_id)   


@transaction.atomic
def update_orders(order_id, status, address_id=None, use_default_address=False):
    """
    Update the status of an order in the 'Order' model of a PostgreSQL database.

    Args:
        order_id (int): The ID of the order to be updated.
        status (str): The status to set for the order, either 'place order' or 'cancel order'.
        address_id (int, optional): The ID of the address to associate with the order (required for 'place order').
        use_default_address (bool, optional): If True, use the default address for the user (required for 'place order').

    Returns:
        tuple: A tuple containing a boolean indicating success or failure and a message.

    This function allows users to update the status of an order in the 'Order' model. It supports two actions:
    1. Placing an order ('place order') by specifying an address ID or using the default address.
    2. Canceling an order ('cancel order') that is either in the 'In Cart' or 'Placed' status.
    
    The function handles various scenarios, including checking for valid status, verifying order existence,
    associating addresses, checking stock availability, and updating the order status accordingly.
    It returns a tuple containing a boolean indicating success or failure and a message.
    """
    try:
        order = Order.objects.get(id=order_id)
        order_status = order.status

        if status == "place order" and order_status == 'In Cart':
            if not (address_id or use_default_address):
                return (False, "Please enter an address or choose the default address to proceed.")
            elif address_id:
                try:
                    address = Address.objects.get(id=address_id, user=order.user)
                except Address.DoesNotExist:
                    return (False, "Please enter a correct address ID.")
            elif use_default_address:
                try:
                    address = Address.objects.get(user=order.user, isdefault=True)
                except Address.DoesNotExist:
                    return (False, "No default address found for the user.")
            
            order_items = Orderitem.objects.filter(order=order)
            for order_item in order_items:
                product = order_item.product

                if product.stock_count < order_item.qty:
                    print("stock count exceeds qty")
                    return (False, f"Quantity of product {product.id} in your order exceeds available stock. Please select lesser quantity and try again")

            # Update stock counts and place order
            for order_item in order_items:
                product = order_item.product
                product.stock_count -= order_item.qty
                product.save()
            order.status = 'Placed'
            order.address = address
            order.order_date = timezone.now()
            order.dateupdate = timezone.now()
            order.save()

            return (True, "Order placed successfully.")

        elif status == "cancel order":
            if order_status == 'In Cart':
                order.status = 'Cancelled'
                order.dateupdate = timezone.now()
                order.save()
                return (True, "Order in cart cancelled successfully.")
            elif order_status == 'Placed':
                order_items = Orderitem.objects.filter(order=order)
                for order_item in order_items:
                    product = order_item.product
                    product.stock_count += order_item.qty
                    product.save()
                order.status = 'Cancelled'
                order.dateupdate = timezone.now()
                order.save()
                return (True, "Placed order cancelled successfully.")
            else:
                return (False, "Order cannot be cancelled.")
        else:
            return (False, "Please check your entered parameters again.")

    except Order.DoesNotExist:
        return (False, "No order found.")
    except Address.DoesNotExist:
        return (False, "Please enter a correct address ID.")
    except Exception as e:
        return (False, f"Error updating order: {e}")              

def get_cart_items(user_id):
    """
    Get a list of products in the user's existing cart.

    Args:
        user_id (int): The ID of the user.

    Returns:
        tuple: A tuple containing a boolean indicating success or failure and a message.

    This function retrieves the list of products in the user's existing cart. It returns a tuple containing
    a boolean indicating success or failure and a message with the cart items.
    """
    try:
        # Check if the user exists
        user = User.objects.get(id=user_id)
        
        # Get the user's "In Cart" order
        order = Order.objects.get(user_id=user_id, status='In Cart')
        
        # Get the order items associated with the order
        order_items = Orderitem.objects.filter(order=order)
        
        if order_items:
            order_list = []
            for order_item in order_items:
                product = order_item.product
                order_dict = {
                    "orderitem_id": order_item.id,
                    "order_id": order_item.order.id,
                    "product_id": product.id,
                    "product_qty": str(order_item.qty),
                    "price": str(order_item.price),
                    "subtotal": str(order_item.total_amount)
                }
                order_list.append(order_dict)
            return (True, f'You have the following items in your cart: {order_list}')
        else:
            return (False, "Your cart is empty.")

    except User.DoesNotExist:
        return (False, "User not found.")

    except Order.DoesNotExist:
        return (False, "Your cart is empty.")

    except Exception as e:
        return (False, f"Error retrieving cart items: {e}")        



def get_orders_for_product(user_id, product_id):
    #breakpoint()
    try:
        # Check if the product with the specified ID exists
        product = Product.objects.get(id=product_id)

        # Get the user
        user = User.objects.get(id=user_id)

        # Check if the user has the role of an admin
        admin_role = Role.objects.get(name='admin')  
        if user.role_id == admin_role.id:
            
            # Fetch orders for the given product
            orders = Orderitem.objects.filter(product_id=product_id, order__order_date__isnull=False)
            print("orders:",orders)

            order_details = []
            for order_item in orders:
                order = order_item.order
                order_detail = {
                    "order_id": order.id,
                    "product_id": order_item.product.id,
                    "user_id": order.user.id,
                    "address_id": order.address.id,
                    "order_date": order.order_date.strftime('%Y-%m-%d %H:%M:%S'),
                    "status": order.status,
                    "qty": order_item.qty,
                    "price": order_item.price,
                    "total_amount": order_item.total_amount,
                }
                order_details.append(order_detail)

            return (True, f"Here are the order details for product {product_id}: {order_details}")
        else:
            raise PermissionDenied("You do not have permission for this activity.")

#To handle when product is not found
    except Product.DoesNotExist:
        return (False, "Product not found.")  

#to handle if user id is invalid
    except User.DoesNotExist:
        return (False, "User not found.")

#to handle situation where user do not have permission         
    except PermissionDenied:
        return (False, "You do not have permission for this activity.")
        
#to handle any other errors
    except Exception as e:
        return (False, f"Error retrieving order details: {e}")