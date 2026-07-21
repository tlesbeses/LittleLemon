from django.contrib import admin
from .models import Category, MenuItem, Cart, Order, OrderItem


# Inline configuration so OrderItems display right inside their corresponding Order
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('unit_price', 'price')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title',)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'category', 'featured')
    list_filter = ('category', 'featured')
    search_fields = ('title',)
    list_editable = ('price', 'featured')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'menuitem', 'quantity', 'unit_price', 'price')
    list_filter = ('user',)
    search_fields = ('user__username', 'menuitem__title')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'delivery_crew', 'status', 'total', 'date')
    list_filter = ('status', 'date', 'delivery_crew')
    search_fields = ('user__username', 'delivery_crew__username')
    list_editable = ('status', 'delivery_crew')
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'menuitem', 'quantity', 'unit_price', 'price')
    list_filter = ('order__date',)
    search_fields = ('menuitem__title', 'order__id')
