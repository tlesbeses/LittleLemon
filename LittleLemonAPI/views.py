from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from rest_framework.response import Response


from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import (
    CategorySerializer,
    MenuItemSerializer,
    CartSerializer,
    OrderSerializer,
    OrderItemSerializer,
    UserSerializer,
)


from rest_framework.permissions import IsAdminUser

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