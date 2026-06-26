from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'product_description', 'category', 'tags']

    def get_tags(self, obj):
        return [t.strip() for t in obj.tags.split(',') if t.strip()]

class ProductCreateSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(child=serializers.CharField(), write_only=True)

    class Meta:
        model = Product
        fields = ['product_name', 'product_description', 'category', 'tags']

    def create(self, validated_data):
        tags_list = validated_data.pop('tags', [])
        product = Product.objects.create(tags=','.join(tags_list), **validated_data)
        return product

class SearchResultSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    relevance_score = serializers.FloatField()
    rank_reason = serializers.CharField()

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'category', 'tags', 'relevance_score', 'rank_reason']

    def get_tags(self, obj):
        return [t.strip() for t in obj.tags.split(',') if t.strip()]
