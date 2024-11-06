from django.urls import path
from . import views  

urlpatterns = [
    path('add-customer/', views.add_customer, name='add-customer'),
    path('edit-customer/<int:customer_id>/', views.add_customer, name='edit-customer'), 
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('delete-supplier/<int:supplier_id>/', views.delete_supplier, name='delete-supplier'),
    path('suppliers/', views.list_suppliers, name='list-suppliers'),
    path('view-order/', views.view_order, name='view-order'),
    path('view-order/view-order-specific/<int:orderid>/', views.view_order_specific, name='view-order-specific'),
    path('add-product/', views.add_product, name='add-product'),
    path('update-product/', views.update_product, name='update-product'),
    path('find-customer/', views.find_customer, name='find-customer'),
    path('take-order/<int:order_id>/', views.take_order, name='take-order'),
    path('take-order/delete/<int:orderlist>/', views.delete_item, name='delete-item'),
    path('take-order/confirm-order/<int:order_id>/', views.comfirm_order, name='confirm_order'),
    path('take-order/take-home-delivery/<int:order_id>/', views.take_home_delivery, name='take-home-delivery'),
    path('view-home-delivery/', views.view_home_delivery, name='view-home-delivery'),
    path('add-supplier/', views.add_supplier, name='add-supplier'),
    path('add-supply-order/', views.add_supply_order, name='add-supply-order'),
    path('view-supply-order/', views.view_supply_order, name='view-supply-order'),
    path('view-supply-order/update-invoice/<int:invoice_id>/', views.update_status, name='update-status'),
    path('printbill/<int:bill_id>/', views.printbill, name='printbill'),
]
