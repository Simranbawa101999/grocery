from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import EmailValidator, RegexValidator


class Role(models.Model):
    name = models.CharField(unique=True, max_length=100)
    datecreate = models.DateTimeField(auto_now_add=True)
    dateupdate = models.DateTimeField(null=True)
    datedeleted = models.DateTimeField(null=True)

    def __str__(self):
        return self.name



class Product(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200, null=True)
    price = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(1)])
    stock_count = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    createdby = models.IntegerField()
    updateby = models.IntegerField(null=True,blank=True)
    deletedby = models.IntegerField(null=True,blank=True)
    datecreated = models.DateTimeField(auto_now_add=True)
    dateupdated = models.DateTimeField(null=True,blank=True)
    datedeleted = models.DateTimeField(null=True,blank=True)

    def clean(self):
        if self.stock_count < 0:
            raise ValidationError(
                {'title': "stock count can not be negative"})  
        if self.price <= 0:
            raise ValidationError(
                {'title': "price can not be zero or negative"})  

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class CustomUserManager(BaseUserManager):

    '''def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)  '''     


class User(AbstractBaseUser): #abstractuser, abstractbaseuser
    #breakpoint()
    def is_valid_phone_number(self, value):
        if len(value) != 10:
            raise ValidationError('Phone number must be exactly 10 digits.')

    def is_valid_email(self, value):
        email_validator = EmailValidator()
        try:
            email_validator(value)
        except ValidationError:
            raise ValidationError('Invalid email format. An email address must contain "@" and at least one "." character.')

    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=50, null=True)
    email = models.EmailField(max_length=50, unique=True)
    phone_no = models.CharField(max_length=10 ,validators=[RegexValidator(r'^\d{10}$', message='Phone number must be exactly 10 digits.')]) 
    
    print("phone number",phone_no)
    #hashed_password = models.CharField(max_length=500)
    role = models.ForeignKey('Role', on_delete = models.PROTECT)
    datecreate=  models.DateTimeField(auto_now_add=True)
    dateupdate = models.DateTimeField(null=True, blank =True)
    datedeleted = models.DateTimeField(null=True, blank = True)
    #salt = models.CharField(max_length=500)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name","phone_no","role","password"]  


    def clean(self):
        if not len(self.phone_no) == 10:
            raise ValidationError(
                {'title': "Phone Number should have exactly 10 digits"})  


    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}"


class Category(models.Model):
    name = models.CharField(unique=True, max_length=100)
    datecreate = models.DateTimeField(auto_now_add=True)
    dateupdate = models.DateTimeField(null=True)
    datedeleted = models.DateTimeField(null=True)
    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=30)
    datecreate = models.DateTimeField(auto_now_add=True)
    dateupdate = models.DateTimeField(null=True)
    datedeleted = models.DateTimeField(null=True)    
    def __str__(self):
        return self.name


class State(models.Model):
    name = models.CharField(max_length=50)
    country = models.ForeignKey('Country', on_delete= models.PROTECT)
    datecreate = models.DateTimeField(auto_now_add=True)
    dateupdate = models.DateTimeField(null=True)
    datedeleted = models.DateTimeField(null=True)    
    def __str__(self):
        return self.name



class City(models.Model):
    name = models.CharField(max_length=50)
    state = models.ForeignKey('State', on_delete= models.PROTECT)
    datecreate = models.DateTimeField(auto_now_add=True)
    dateupdate = models.DateTimeField(null=True)
    datedeleted = models.DateTimeField(null=True)    
    def __str__(self):
        return f"{self.name} {self.state}"



class Productcategory(models.Model):
    product = models.ForeignKey('Product', on_delete = models.PROTECT)
    category = models.ForeignKey('Category', on_delete= models.PROTECT)
    datecreate = models.DateTimeField(auto_now_add=True)
    dateupdate = models.DateTimeField(null=True)
    datedeleted = models.DateTimeField(null=True)
    createdby =models.IntegerField()
    updatedby = models.IntegerField(null=True)
    deletedby = models.IntegerField(null=True)

    def __str__(self):
        return str(self.id)
  



class Address(models.Model):
    user = models.ForeignKey('User', on_delete = models.PROTECT)
    country = models.ForeignKey('Country', on_delete= models.PROTECT)
    state = models.ForeignKey('State',on_delete= models.PROTECT)
    city = models.ForeignKey('City',on_delete= models.PROTECT)
    pincode = models.CharField(max_length=50)
    address = models.CharField(max_length=50)
    isdefault = models.BooleanField(null=True)
    datecreate = models.DateTimeField(auto_now_add=True)
    dateupdate = models.DateTimeField(null=True)
    datedeleted = models.DateTimeField(null=True)
    def __str__(self):
         return f"ID: {self.id}, User: {self.user}, Country: {self.country}, State: {self.state}, City: {self.city}, Address: {self.address}, Pincode: {self.pincode}"


class Order(models.Model):
    user = models.ForeignKey('User',on_delete= models.PROTECT)
    address = models.ForeignKey('Address', null=True, on_delete= models.PROTECT)
    total_amount = models.DecimalField(max_digits=80, decimal_places=2, null=True)
    order_date = models.DateTimeField(null=True)
    STATUS = [
    ("In Cart", "In Cart"),
    ("Placed", "Placed"),
    ("Cancelled", "Cancelled"),
    ("Delivered", "Delivered")]
    status =  models.CharField(max_length=20, choices=STATUS)
    datecreate = models.DateTimeField(auto_now_add=True)
    dateupdate = models.DateTimeField(null=True)
    datedeleted = models.DateTimeField(null=True)

    def __str__(self):
        return str(self.id)

class Orderitem(models.Model):
    order = models.ForeignKey('Order',on_delete=models.PROTECT)
    product = models.ForeignKey('Product',on_delete= models.PROTECT)
    qty = models.DecimalField(max_digits=4, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=20, decimal_places=2)
    datecreate = models.DateTimeField(auto_now_add=True)
    dateupdate = models.DateTimeField(blank=True, null=True)
    datedeleted = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return str(self.id)
