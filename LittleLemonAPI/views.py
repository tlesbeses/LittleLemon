from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import (
    CategorySerializer,
    MenuItemSerializer,
    CartSerializer,
    OrderSerializer,
    OrderItemSerializer,
)


# Category Views
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [
                IsAuthenticated,
                DjangoModelPermissions,
            ]

        return [permission() for permission in permission_classes]
    
# MenuItem Views
class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer
    def get_permissions(self):
            if self.request.method == 'GET':
                permission_classes = [IsAuthenticated]
            else:
                permission_classes = [
                    IsAuthenticated,
                    DjangoModelPermissions,
                ]

            return [permission() for permission in permission_classes]


# Cart Views (User-specific)
class CartListCreateView(generics.ListCreateAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user).select_related('menuitem')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartClearView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        Cart.objects.filter(user=request.user).delete()
        return super().delete(request, *args, **kwargs)


# Order Views
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)