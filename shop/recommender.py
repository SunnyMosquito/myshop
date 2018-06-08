import redis
from django.conf import settings
from .models import Product

r = redis.StrictRedis(host=settings.REDIS_HOST,
                      port=settings.REDIS_PORT,
                      db=settings.REDIS_DB)

class Recommender(object):
    def get_product_key(self, id):
        return 'product:{}:purchased_with'.format(id)
    # 迭代所有的产品 ID。对于每个 `id` ，
    # 我们迭代所有的产品 ID 并且跳过所有相同的产品，
    # 这样我们就可以得到和每个产品一起购买的产品。
    def products_bought(self, products):
        product_ids = [p.id for p in products]
        for product_id in product_ids:
            for with_id in product_ids:
                if product_id != with_id:
                    # 把有序集中的每个产品 `id` 的评分加一。评分表示另一个产品和所给产品一起购买的次数。
                    r.zincrby(self.get_product_key(product_id), with_id, amount=1)
    
    def suggest_products_for(self, products, max_result=6):
        product_ids = [p.id for p in products]
        if len(products) == 1:
            suggestions = r.zrange(self.get_product_key(product_ids[0]),
                                   0,-1,desc=True)[:max_result]
        else:
            flat_ids = ''.join([str(id) for id in product_ids])
            tmp_key = 'tmp_{}'.format(flat_ids)
            keys = [self.get_product_key(id) for id in product_ids]
            # 把包含在每个所给产品的有序集中东西的评分组合并相加，即求并集，存到tmp_key里，
            # 即求出每个有序集合里的产品score值之和
            r.zunionstore(tmp_key, keys)
            r.zrem(tmp_key, *product_ids)
            suggestions = r.zrange(tmp_key, 0, -1, desc=True)[:max_result]
            r.delete(tmp_key)
        suggest_products_ids = [int(id) for id in suggestions]
        suggest_products = list(Product.objects.filter(id__in=suggest_products_ids))
        suggest_products.sort(key=lambda x: suggest_products_ids.index(x.id))
        return suggest_products
    
    def clear_purchases(self):
        for id in Product.objects.values_list('id', flat=True):
            r.delete(self.get_product_key(id))


