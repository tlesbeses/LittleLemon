from django.urls import path
from .views import (
    CategoryViewSet,
    MenuItemViewSet,
    CartView,
    OrderViewSet,
    GroupManagementViewSet,
)

urlpatterns = [
    # Category endpoints
    path('categories/', CategoryViewSet.as_view({'get': 'list', 'post': 'create'}), name='category-list'),
    path('categories/<int:pk>/', CategoryViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='category-detail'),

    # Menu Item endpoints
    path('menu-items/', MenuItemViewSet.as_view({'get': 'list', 'post': 'create'}), name='menuitem-list'),
    path('menu-items/<int:pk>/', MenuItemViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='menuitem-detail'),

    path("cart/menu-items/", CartView.as_view()),
  
    # Order endpoints
    path('orders/', OrderViewSet.as_view({'get': 'list', 'post': 'create'}), name='order-list'),
    path('orders/<int:pk>/', OrderViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='order-detail'),
    
    path(
        "groups/<str:group_name>/users/",
        GroupManagementViewSet.as_view({
            "get": "list",
            "post": "create",
        }),
    ),
    path(
        "groups/<str:group_name>/users/<int:pk>/",
        GroupManagementViewSet.as_view({
            "delete": "destroy",
        }),
    ),
    
     path(
        "orders/",
        OrderViewSet.as_view({
            "get": "list",
            "post": "create",
        }),
        name="order-list",
    ),
    path(
        "orders/<int:pk>/",
        OrderViewSet.as_view({
            "get": "retrieve",
            "put": "update",
            "patch": "partial_update",
            "delete": "destroy",
        }),
        name="order-detail",
    ),
    
]