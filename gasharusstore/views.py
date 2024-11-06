from django import forms
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from . import forms
from .models import Customer, Discount, HomeDelivery, Invoice, Order, Product, OrderList, Bill, Supplier
from datetime import date
from django.db.models import Count, Sum

@login_required(login_url='login')
def add_customer(request, customer_id=None):
    if customer_id:
        customer = Customer.objects.get(id=customer_id)
    else:
        customer = None
    
    if request.method == 'POST':
        forms = CustomerForm(request.POST, instance=customer)  
        if forms.is_valid():
            customer = forms.save()  

            if not customer_id:
                Order.objects.create(customer=customer, order_amount=0)

            o = Order.objects.filter(customer=customer, order_amount=0).first()
            if o:
                return redirect('take-order', o.id)
            else:
                messages.error(request, "No valid order found for the customer.")
                return redirect('some_error_handling_view')

    else:
        forms = CustomerForm(instance=customer) 

    context = {
        'form': forms,
        'customer': customer
    }
    return render(request, 'add_customer.html', context)


@login_required(login_url='login')
def add_product(request):
    form1 = ProductForm()
    if request.method == 'POST':
        form1 = ProductForm(request.POST)
        if form1.is_valid():
            p_name = form1.cleaned_data['p_name']
            p_price = form1.cleaned_data['p_price']
            p_descp = form1.cleaned_data['p_descp']

            # Create new product
            Product.objects.create(p_name=p_name, p_price=p_price, p_descp=p_descp)
            messages.success(request, 'Product details added.')
            return redirect('homepage')
        else:
            messages.error(request, 'Invalid Details Entered.')
            return redirect(request.META['HTTP_REFERER'])

    context = {
        'form1': form1
    }
    return render(request, 'add_product.html', context)

@login_required(login_url='login')
def update_product(request):
    p = Product.objects.all()
    forms = UpdateProductForm()
    if request.method == 'POST':
        forms = ProductForm(request.POST)
        if forms.is_valid():
            product_id = request.POST.get('product_id')
            price = request.POST.get('price')
            try:
                req_product = Product.objects.get(id=product_id)
                req_product.p_price = price  # Update price directly
                req_product.save()
                messages.success(request, 'Product updated successfully.')
                return redirect('homepage')
            except Product.DoesNotExist:
                messages.error(request, 'Product not found.')
                return redirect('update-product')

    context = {
        'forms': forms,
        'p': p,
    }
    return render(request, 'update_product.html', context)

@login_required(login_url='login')
def find_customer(request):
    if request.method == 'POST':
        number = request.POST.get('number')
        if Customer.objects.filter(c_phone=number).exists():
            c = Customer.objects.get(c_phone=number)
            Order.objects.create(customer=c, order_amount=0)
            o = Order.objects.filter(customer=c, order_amount=0).first()
            if o:
                return redirect('take-order', o.id)
        else:
            new_customer = Customer.objects.create(c_phone=number, c_fname="", c_lname="", c_address="")
            return redirect('add-customer', new_customer.id)

    context = {}
    return render(request, 'find_customer.html', context)

@login_required(login_url='login')
def take_order(request, order_id):
    try:
        o = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        messages.error(request, "Order does not exist.")
        return redirect('some_error_handling_view')  # Adjust to your error handling view

    forms = OrderListForm()
    if request.method == 'POST':
        forms = OrderListForm(request.POST)
        if forms.is_valid():
            product = forms.cleaned_data['product']
            unit = request.POST['ol_unit']
            exp_date = request.POST['ol_exp_date']
            p = Product.objects.get(id=product.id)

            # Create order list item
            OrderList.objects.create(product=product, ol_unit=unit, order=o, ol_cost=0, ol_exp_date=exp_date)

            # Update costs
            ol = OrderList.objects.get(product=product, order=o)
            OrderList.objects.filter(ol_cost=0).update(ol_cost=p.p_price * ol.ol_unit)
            ol = OrderList.objects.get(product=product, order=o)
            Order.objects.filter(id=o.id).update(order_amount=o.order_amount + ol.ol_cost)

            return redirect(request.META['HTTP_REFERER'])

    ol = OrderList.objects.filter(order=o)
    context = {
        'forms': forms,
        'o': o,
        'ol': ol,
    }
    return render(request, 'take_order.html', context)

@login_required(login_url='login')
def delete_item(request, orderlist):
    try:
        ol = OrderList.objects.get(id=orderlist)
        o = Order.objects.get(id=ol.order_id)
        Order.objects.filter(id=ol.order_id).update(order_amount=o.order_amount - ol.ol_cost)
        OrderList.objects.filter(id=orderlist).delete()
        messages.success(request, 'Item deleted successfully.')
    except (OrderList.DoesNotExist, Order.DoesNotExist):
        messages.error(request, 'Item or order not found.')

    return redirect(request.META['HTTP_REFERER'])

@login_required(login_url='login')
def view_order(request):
    today = date.today()
    o = Order.objects.all().order_by('-order_date')

    if request.method == 'POST':
        orderdate = request.POST['orderdate']
        o = Order.objects.filter(order_date=orderdate)

        context = {
            'o': o
        }
        return render(request, 'view_order.html', context)

    context = {
        'o': o
    }
    return render(request, 'view_order.html', context)

@login_required(login_url='login')
def view_order_specific(request, orderid):
    ol = OrderList.objects.filter(order_id=orderid)
    try:
        bill = Bill.objects.get(order_id=orderid)
        o = Order.objects.get(id=orderid)
    except (Bill.DoesNotExist, Order.DoesNotExist):
        messages.error(request, "Order or bill does not exist.")
        return redirect('some_error_handling_view')

    context = {
        'ol': ol,
        'bill': bill,
        'o': o
    }
    return render(request, 'view_order_specific.html', context)

@login_required(login_url='login')
def take_home_delivery(request, order_id):
    try:
        o = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        messages.error(request, "Order does not exist.")
        return redirect('some_error_handling_view')

    forms = HomeDeliveryForm()
    if request.method == 'POST':
        forms = HomeDeliveryForm(request.POST)
        if forms.is_valid():
            address = forms.cleaned_data['hd_address']
            delivery_date = request.POST['hd_date']
            delivery_time = request.POST['hd_time']
            instruction = forms.cleaned_data['hd_instruction']
            HomeDelivery.objects.create(order=o, hd_address=address, hd_date=delivery_date, hd_time=delivery_time, hd_instruction=instruction)
            return redirect('confirm_order', o.id)

    context = {
        'forms': forms,
        'o': o,
    }
    return render(request, 'take_homedelivery.html', context)

@login_required(login_url='login')
def view_home_delivery(request):
    h = HomeDelivery.objects.all().order_by('-hd_date')
    if request.method == 'POST':
        date_given = request.POST.get('date')
        if HomeDelivery.objects.filter(hd_date=date_given).exists():
            h = HomeDelivery.objects.filter(hd_date=date_given)
            context = {
                'h': h
            }
            return render(request, 'view_homedelivery.html', context)

    context = {
        'h': h
    }
    return render(request, 'view_homedelivery.html', context)

@login_required(login_url='login')
def comfirm_order(request, order_id):
    try:
        o = Order.objects.get(id=order_id)
        d = Discount.objects.get(id=1)  # Ensure this discount exists
    except (Order.DoesNotExist, Discount.DoesNotExist):
        messages.error(request, "Order or discount does not exist.")
        return redirect('some_error_handling_view')

    if request.method == 'POST':
        bill = Bill.objects.create(order=o, bill_amt=o.order_amount, discount=d)
        extracharge = request.POST['extra_charge']
        paymode = request.POST['paymode']
        delivery_mode = request.POST['delivery_mode']
        feedback = request.POST['feedback']
        Order.objects.filter(id=o.id).update(delivery_mode=delivery_mode, feedback=feedback)

        Bill.objects.filter(id=bill.id).update(extra_charge=extracharge, bill_amt=bill.bill_amt, pay_mode=paymode, balance=0)
        createdbill = Bill.objects.get(id=bill.id)
        Bill.objects.filter(id=createdbill.id).update(bill_amt=createdbill.bill_amt + createdbill.extra_charge)

        return redirect('printbill', bill.id)

    context = {
        'o': o
    }
    return render(request, 'confirm_order.html', context)

@login_required(login_url='login')
def printbill(request, bill_id):
    try:
        bill = Bill.objects.get(id=bill_id)
        ol = OrderList.objects.filter(order_id=bill.order_id)
    except Bill.DoesNotExist:
        messages.error(request, "Bill does not exist.")
        return redirect('some_error_handling_view')

    context = {
        'bill': bill,
        'ol': ol
    }
    return render(request, 'printbillview.html', context)

@login_required(login_url='login')
def add_supplier(request):
    if request.method == 'POST':
        s_name = request.POST['s_name']
        s_phone = request.POST['s_phone']
        s_address = request.POST['s_address']
        Supplier.objects.create(s_name=s_name, s_phone=s_phone, s_address=s_address)
        return redirect('add-supply-order')

    return render(request, 'add_supplier.html')

@login_required(login_url='login')
def delete_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    
    if request.method == 'POST':
        supplier.delete()
        messages.success(request, f'Supplier {supplier.s_name} has been deleted.')
        return redirect('list-suppliers')

    return render(request, 'delete_supplier_confirm.html', {'supplier': supplier})

@login_required(login_url='login')
def list_suppliers(request):
    suppliers = Supplier.objects.all()
    return render(request, 'list_suppliers.html', {'suppliers': suppliers})

@login_required(login_url='login')
def add_supply_order(request):
    today = date.today()
    forms = InvoiceForm()
    if request.method == 'POST':
        forms = InvoiceForm(request.POST)
        if forms.is_valid():
            supplier = forms.cleaned_data['supplier']
            order_date = request.POST['order_date']
            invoice_amount = request.POST['invoice_amount']
            invoice_num = request.POST['invoice_num']
            Invoice.objects.create(supplier=supplier, order_date=order_date, receive_date=today, invoice_amount=invoice_amount, invoice_num=invoice_num)
            return redirect('view-supply-order')

    context = {
        'forms': forms
    }
    return render(request, 'add_supplyorder.html', context)

@login_required(login_url='login')
def view_supply_order(request):
    ip = Invoice.objects.filter(invoice_status='pending').order_by('-order_date')
    ir = Invoice.objects.all().order_by('-order_date')

    context = {
        'ir': ir,
        'ip': ip
    }
    return render(request, 'view_supplyorders.html', context)

@login_required(login_url='login')
def update_status(request, invoice_id):
    try:
        i = Invoice.objects.get(id=invoice_id)
    except Invoice.DoesNotExist:
        messages.error(request, "Invoice does not exist.")
        return redirect('some_error_handling_view')

    if request.method == 'POST':
        r_date = request.POST.get('r_date')
        Invoice.objects.filter(id=invoice_id).update(receive_date=r_date, invoice_status='received')
        return redirect('view-supply-order')

    context = {
        'i': i
    }
    return render(request, 'update_supply.html', context)

def dashboard_view(request):
    today = date.today()
    o = Order.objects.filter(order_date=today)
    p = Product.objects.all()
    pol = OrderList.objects.all().order_by('-ol_cost')[:5]
    total_orders = Order.objects.filter(order_date=today).count()
    customer = Customer.objects.filter(created=today).count()
    total_products = OrderList.objects.filter(order__order_date=today).count()
    ps = OrderList.objects.annotate(number_of_units=Sum('ol_unit'))
    olp = (OrderList.objects.values('product_id')).annotate(total=Sum('ol_unit'))[:5]

    context = {
        'order': total_orders,
        'products': total_products,
        'olp': olp,
        'o': o,
        'p': p,
        'customer': customer,
        'pol': pol,
        'ps': ps,
    }
    return render(request, 'dashboard.html', context)

