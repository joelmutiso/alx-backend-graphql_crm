import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField 
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter
from django.db import transaction

# ==================================
# 1. Types (Now with Relay & Filters)
# ==================================

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone", "orders", "created_at")
        # Enable Relay (Pagination) and Filters
        interfaces = (graphene.relay.Node, )
        filterset_class = CustomerFilter

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")
        interfaces = (graphene.relay.Node, )
        filterset_class = ProductFilter

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "order_date", "total_amount")
        interfaces = (graphene.relay.Node, )
        filterset_class = OrderFilter

# ==================================
# 2. Input Types (Unchanged)
# ==================================
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()

class OrderInput(graphene.InputObjectType):
    customerId = graphene.ID(required=True)
    productIds = graphene.List(graphene.ID, required=True)

# ==================================
# 3. Mutations (Unchanged logic, just ID handling)
# ==================================
# NOTE: When using Relay, IDs become Global IDs (e.g., "CustomerType:1"). 
# For simplicity in this task, we will stick to the previous implementation 
# but be aware that relay inputs usually require decoding. 
# Since the prompt Mutations didn't change, we keep the previous logic.

class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(root, info, input):
        if Customer.objects.filter(email=input.email).exists():
            raise Exception("Email already exists")
        if input.phone and not input.phone.replace('-', '').replace('+', '').isdigit():
             raise Exception("Invalid phone format")

        customer = Customer(name=input.name, email=input.email, phone=input.phone)
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
        for data in inputs:
            try:
                if Customer.objects.filter(email=data.email).exists():
                    raise Exception(f"Email {data.email} already exists")
                customer = Customer(name=data.name, email=data.email, phone=data.phone)
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
        if input.price <= 0: raise Exception("Price must be positive")
        product = Product(name=input.name, price=input.price, stock=input.stock or 0)
        product.save()
        return CreateProduct(product=product)

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)
    order = graphene.Field(OrderType)

    def mutate(root, info, input):
        # NOTE: With Relay, if the client sends global IDs ("CustomerType:1"), 
        # you might need to decode them using `from_global_id`.
        # Assuming standard integer IDs for now based on previous task context.
        try:
            customer = Customer.objects.get(pk=input.customerId)
        except:
            raise Exception("Invalid Customer ID")
            
        products = Product.objects.filter(id__in=input.productIds)
        if not products: raise Exception("No valid products found")
        
        with transaction.atomic():
            total = sum(p.price for p in products)
            order = Order.objects.create(customer=customer, total_amount=total)
            order.products.set(products)
            order.save()
        return CreateOrder(order=order)

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

# ==================================
# 4. Query (The big update!)
# ==================================

class Query(graphene.ObjectType):
    # DjangoFilterConnectionField auto-magically handles the filtering args
    all_customers = DjangoFilterConnectionField(CustomerType)
    all_products = DjangoFilterConnectionField(ProductType)
    all_orders = DjangoFilterConnectionField(OrderType)

    # We don't strictly need resolvers for ConnectionFields, 
    # Graphene handles them via the FilterSets.