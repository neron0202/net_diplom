from django.contrib import admin
from django.urls import path

from orbackend.views import AccountRegister, AccountLogin, GoodsUpload, BasketView, ContactView, OrderView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/register', AccountRegister.as_view(), name='user-register'),
    path('user/login', AccountLogin.as_view(), name='user-login'),
    path('basket', BasketView.as_view(), name='basket'),
    path('order', OrderView.as_view(), name='order'),
    path('user/contact', ContactView.as_view(), name='user-contact'),
    path('partner/', GoodsUpload.as_view())
]
