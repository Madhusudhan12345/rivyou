from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Product
from .ranking import score_product, rank_products

User = get_user_model()

def make_product(id, name, category, tags, desc="A product"):
    return Product(id=id, product_name=name, product_description=desc, category=category, tags=tags)

class RankingLogicTests(TestCase):
    def test_category_match_scores_highest(self):
        phone = make_product(1, "iPhone 15", "Smartphones", "5g,camera")
        charger = make_product(2, "USB Charger", "Chargers", "fast-charging,smartphone")
        score_phone, reason_phone = score_product(phone, "smartphone")
        score_charger, reason_charger = score_product(charger, "smartphone")
        self.assertGreater(score_phone, score_charger)
        self.assertEqual(reason_phone, "Category match")
        self.assertIn("Tag match", reason_charger)

    def test_tier1_always_before_tier2(self):
        p1 = make_product(1, "Galaxy S24", "Smartphones", "5g,android")
        p2 = make_product(2, "Back Cover", "Back Covers", "smartphone,protection")
        ranked = rank_products([p1, p2], "smartphone")
        self.assertEqual(ranked[0][0].id, 1)

    def test_exact_tag_beats_partial_tag(self):
        p_exact = make_product(1, "Fast Charger", "Chargers", "smartphone,usb")
        p_partial = make_product(2, "Charger Plus", "Chargers", "smartphones,cable")
        s_exact, _ = score_product(p_exact, "smartphone")
        s_partial, _ = score_product(p_partial, "smartphone")
        self.assertGreaterEqual(s_exact, s_partial)

    def test_no_match_excluded(self):
        p = make_product(1, "Toothbrush", "Health", "dental,hygiene", "Clean your teeth")
        ranked = rank_products([p], "smartphone")
        self.assertEqual(len(ranked), 0)

    def test_name_match_is_tier3(self):
        p = make_product(1, "SmartPhone Stand", "Accessories", "desk,holder")
        score, reason = score_product(p, "smartphone")
        self.assertEqual(reason, "Name match")
        self.assertLess(score, 0.40)

    def test_case_insensitive(self):
        p = make_product(1, "iPhone 15", "Smartphones", "5G,Camera")
        score, reason = score_product(p, "SMARTPHONE")
        self.assertEqual(reason, "Category match")

class AuthAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register(self):
        res = self.client.post('/api/auth/register', {
            "username": "testuser", "email": "test@example.com", "password": "securepass"
        }, format='json')
        self.assertEqual(res.status_code, 201)
        self.assertIn("token", res.data)

    def test_login(self):
        User.objects.create_user("loginuser", "login@example.com", "pass1234")
        res = self.client.post('/api/auth/login', {
            "username": "loginuser", "password": "pass1234"
        }, format='json')
        self.assertEqual(res.status_code, 200)
        self.assertIn("token", res.data)

    def test_invalid_login_returns_401(self):
        res = self.client.post('/api/auth/login', {
            "username": "nobody", "password": "wrong"
        }, format='json')
        self.assertEqual(res.status_code, 401)

class ProductSearchAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user("searcher", "s@example.com", "pass1234")
        res = self.client.post('/api/auth/login', {"username": "searcher", "password": "pass1234"}, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['token']}")
        Product.objects.create(id=1, product_name="iPhone 15", product_description="Flagship phone", category="Smartphones", tags="5g,camera")
        Product.objects.create(id=2, product_name="USB Charger", product_description="Fast charger", category="Chargers", tags="fast-charging,smartphone")
        Product.objects.create(id=3, product_name="Back Cover", product_description="Fits smartphone", category="Back Covers", tags="smartphone,protection")

    def test_search_returns_smartphones_first(self):
        res = self.client.get('/api/products/search?q=smartphone')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['results'][0]['category'], "Smartphones")

    def test_search_requires_auth(self):
        self.client.credentials()
        res = self.client.get('/api/products/search?q=smartphone')
        self.assertEqual(res.status_code, 401)

    def test_search_missing_q_returns_400(self):
        res = self.client.get('/api/products/search')
        self.assertEqual(res.status_code, 400)

    def test_product_detail(self):
        res = self.client.get('/api/products/1')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['product_name'], "iPhone 15")

    def test_product_detail_404(self):
        res = self.client.get('/api/products/9999')
        self.assertEqual(res.status_code, 404)

    def test_category_endpoint(self):
        res = self.client.get('/api/products/category/Smartphones')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['count'], 1)
