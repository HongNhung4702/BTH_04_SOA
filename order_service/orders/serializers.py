from rest_framework import serializers
from .models import Order, OrderItem
import requests
from django.conf import settings

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product_id', 'product_name', 'quantity', 'unit_price', 'total_price']
        read_only_fields = ['order', 'product_name', 'unit_price', 'total_price']

    def validate(self, attrs):
        quantity = attrs.get('quantity', 0)
        if quantity <= 0:
            raise serializers.ValidationError({'quantity': 'Quantity must be > 0'})
        return attrs

    def create(self, validated_data):
        validated_data['total_price'] = validated_data['unit_price'] * validated_data['quantity']
        return super().create(validated_data)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, required=False)

    class Meta:
        model = Order
        fields = ['id', 'customer_name', 'customer_email', 'total_amount', 'status', 'created_at', 'updated_at', 'items']
        read_only_fields = ['total_amount', 'created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        request = self.context.get('request') if hasattr(self, 'context') else None
        headers = {}
        if request and 'Authorization' in request.headers:
            headers['Authorization'] = request.headers.get('Authorization')

        order = Order.objects.create(**validated_data)

        total_amount = 0
        for item in items_data:
            product_id = item['product_id']
            quantity = int(item['quantity'])

            # Lấy thông tin sản phẩm + kiểm tra tồn kho
            try:
                resp = requests.get(f"{settings.PRODUCT_SERVICE_BASE_URL}/products/{product_id}/", headers=headers)
                if resp.status_code != 200:
                    raise serializers.ValidationError({'error': 'Không tìm thấy sản phẩm'})
                product = resp.json()
            except Exception as e:
                raise serializers.ValidationError({'error': f'Lỗi kết nối đến product_service: {str(e)}'})

            if product['quantity'] < quantity:
                raise serializers.ValidationError({'error': 'Số lượng trong kho không đủ'})

            unit_price = float(product['price'])
            total_price = unit_price * quantity

            OrderItem.objects.create(
                order=order,
                product_id=product_id,
                product_name=product['name'],
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price,
            )

            # Trừ tồn kho sản phẩm
            new_quantity = product['quantity'] - quantity
            requests.put(
                f"{settings.PRODUCT_SERVICE_BASE_URL}/products/{product_id}/",
                headers=headers,
                data={
                    'name': product['name'],
                    'description': product['description'],
                    'price': product['price'],
                    'quantity': new_quantity,
                }
            )

            total_amount += total_price

        order.total_amount = total_amount
        order.save(update_fields=['total_amount'])
        return order
