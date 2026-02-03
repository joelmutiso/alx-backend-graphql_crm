import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from django.db import transaction

# ==================================
# 1. Define Types (For Reading Data)
# ==================================

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone", "orders")

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "order_date", "total_amount")

# ==================================
# 2. define Input Types (For Mutations)
# ==================================

class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()

# ==================================
# 3. Define Mutations (For Writing Data)
# ==================================

class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(root, info, input):
        # Validation: Check if email exists
        if Customer.objects.filter(email=input.email).exists():
            raise Exception("Email already exists")
        
        # Validation: Basic phone check (simple implementation)
        if input.phone and not input.phone.replace('-', '').replace('+', '').isdigit():
             raise Exception("Invalid phone format")

        customer = Customer(
            name=input.name,
            email=input.email,
            phone=input.phone
        )
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully")

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        inputs = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(root, info, inputs):
        created_customers = []
        error_messages = []

        # We process each input individually to allow partial success
        for data in inputs:
            try:
                if Customer.objects.filter(email=data.email).exists():
                    raise Exception(f"Email {data.email} already exists")
                
                customer = Customer(
                    name=data.name,
                    email=data.email,
                    phone=data.phone
                )
                customer.save()
                created_customers.append(customer)
            except Exception as e:
                error_messages.append(str(e))

        return BulkCreateCustomers(customers=created_customers, errors=error_messages)

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    def mutate(root, info, input):
        if input.price <= 0:
            raise Exception("Price must be positive")
        
        # Determine stock (default to 0 if not provided)
        stock_val = input.stock if input.stock is not None else 0
        if stock_val < 0:
             raise Exception("Stock cannot be negative")

        product = Product(
            name=input.name,
            price=input.price,
            stock=stock_val
        )
        product.save()
        return CreateProduct(product=product)

class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)

    order = graphene.Field(OrderType)

    def mutate(root, info, customer_id, product_ids):
        # 1. Validate Customer
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid Customer ID")

        # 2. Validate Products
        if not product_ids:
            raise Exception("Order must contain at least one product")

        products = Product.objects.filter(id__in=product_ids)
        if len(products) != len(product_ids):
             raise Exception("One or more Product IDs are invalid")

        # 3. Create Order (Using transaction to ensure integrity)
        with transaction.atomic():
            # Calculate total amount
            total = sum(p.price for p in products)

            order = Order.objects.create(
                customer=customer,
                total_amount=total
            )
            order.products.set(products)
            order.save()

        return CreateOrder(order=order)

# ==================================
# 4. Group Mutations & Queries
# ==================================

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

# Don't forget the Query class required by the main schema!
class Query(graphene.ObjectType):
    # Basic list queries to help you test
    all_customers = graphene.List(CustomerType)
    all_products = graphene.List(ProductType)
    all_orders = graphene.List(OrderType)

    def resolve_all_customers(root, info):
        return Customer.objects.all()

    def resolve_all_products(root, info):
        return Product.objects.all()

    def resolve_all_orders(root, info):
        return Order.objects.all()