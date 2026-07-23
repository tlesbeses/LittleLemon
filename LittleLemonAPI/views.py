from decimal import Decimal

from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied


from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import (
    CategorySerializer,
    MenuItemSerializer,
    CartSerializer,
    OrderSerializer,
    UserSerializer,
)

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

class CartView(generics.ListCreateAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        menu_item = serializer.validated_data["menuitem"]
        quantity = serializer.validated_data["quantity"]
        
        cart_item = Cart.objects.filter(
                user=self.request.user,
                menuitem=menu_item
            ).first()

        if cart_item:
            cart_item.quantity += quantity
            cart_item.price = cart_item.quantity * cart_item.unit_price
            cart_item.save()
            return
        
        serializer.save(
            user=self.request.user,
            unit_price=menu_item.price,
            price=menu_item.price * quantity,
        )
    def delete(self, request):
        Cart.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_200_OK)
    
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.groups.filter(name="Manager").exists():
            return Order.objects.all()

        if user.groups.filter(name="Delivery crew").exists():
            return Order.objects.filter(delivery_crew=user)

        return Order.objects.filter(user=user)

    def perform_create(self, serializer):
        cart_items = Cart.objects.filter(user=self.request.user)

        if not cart_items.exists():
            raise ValidationError("Cart is empty.")

        total = Decimal("0.00")

        for item in cart_items:
            total += item.price

        order = serializer.save(
            user=self.request.user,
            total=total
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price
            )

        cart_items.delete()
        
    def update(self, request, *args, **kwargs):
        order = self.get_object()
        user = request.user

        # Manager
        if user.groups.filter(name="Manager").exists():
            serializer = self.get_serializer(
                order,
                data=request.data,
                partial=kwargs.get("partial", False)
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        # Delivery crew
        if user.groups.filter(name="Delivery crew").exists():
            serializer = self.get_serializer(
                order,
                data={"status": request.data.get("status")},
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        raise PermissionDenied("Customers cannot update orders.")

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="Manager").exists():
            raise PermissionDenied("Only managers can delete orders.")

        return super().destroy(request, *args, **kwargs) 
    
class GroupManagementViewSet(viewsets.ViewSet):
    
    def get_permissions(self):
        if not self.request.user.groups.filter(name="Manager").exists():
            self.permission_denied(
                self.request,
                message="You do not have permission."
            )

        return []

    def get_group(self):
        group_name = self.kwargs["group_name"]
        return get_object_or_404(Group, name=group_name)

    # GET /groups/<group_name>/users/
    def list(self, request, group_name=None):
        group = self.get_group()
        users = group.user_set.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    # POST /groups/<group_name>/users/
    def create(self, request, group_name=None):
        user_id = request.data.get("userId")

        if not user_id:
            return Response(
                {"detail": "userId is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = get_object_or_404(User, pk=user_id)
        group = self.get_group()

        group.user_set.add(user)

        return Response(
            {"detail": f"{user.username} added to {group.name}."},
            status=status.HTTP_201_CREATED
        )

    # DELETE /groups/<group_name>/users/<userId>/
    def destroy(self, request, pk=None, group_name=None):
        group = self.get_group()

        user = get_object_or_404(User, pk=pk)

        if not user.groups.filter(id=group.id).exists():
            return Response(
                {"detail": "User is not in this group."},
                status=status.HTTP_404_NOT_FOUND
            )

        group.user_set.remove(user)

        return Response(
            {"detail": "User removed successfully."},
            status=status.HTTP_200_OK
        )