from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Q
from .models import Product
from .serializers import ProductSerializer, ProductCreateSerializer, SearchResultSerializer
from .ranking import rank_products

class ProductSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        limit = int(request.query_params.get('limit', 20))
        category_filter = request.query_params.get('category_filter', '').strip()

        if not query:
            return Response({"error": "Query parameter 'q' is required."}, status=status.HTTP_400_BAD_REQUEST)

        q_lower = query.lower()

        # Pre-filter: only products that have at least some mention of the query
        qs = Product.objects.filter(
            Q(category__icontains=q_lower) |
            Q(tags__icontains=q_lower) |
            Q(product_name__icontains=q_lower) |
            Q(product_description__icontains=q_lower)
        )

        if category_filter:
            qs = qs.filter(category__iexact=category_filter)

        ranked = rank_products(qs, query)
        total = len(ranked)

        # Pagination
        page = int(request.query_params.get('page', 1))
        start = (page - 1) * limit
        page_results = ranked[start:start + limit]

        results = []
        for product, score, reason in page_results:
            product.relevance_score = score
            product.rank_reason = reason
            results.append(product)

        serializer = SearchResultSerializer(results, many=True)
        return Response({
            "query": query,
            "total_results": total,
            "page": page,
            "limit": limit,
            "results": serializer.data
        })


class ProductDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(ProductSerializer(product).data)


class ProductByCategoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, category):
        products = Product.objects.filter(category__iexact=category)
        if not products.exists():
            return Response({"error": f"No products found in category '{category}'."}, status=status.HTTP_404_NOT_FOUND)
        return Response({
            "category": category,
            "count": products.count(),
            "results": ProductSerializer(products, many=True).data
        })


class ProductCreateView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = ProductCreateSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
