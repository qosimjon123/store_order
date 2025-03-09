from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from Order.views import OrderItemViewSet, OrderViewSet

router = DefaultRouter()
router.register('', OrderViewSet, basename='order')


order_router = NestedDefaultRouter(router, r'', lookup='order')

order_router.register(r'items', OrderItemViewSet , basename='order-items')

urlpatterns = router.urls + order_router.urls