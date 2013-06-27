# horizontalpartitioning

Django で、モデルDBの水平分割を提供する。


## 使い方

### 1. models.Model の代わりに、HorizontalPartitioningModel を継承してデータモデルを作成


    from horizontalpartitioning.models import HorizontalPartitioningModel
    
    class Player(HorizontalPartitioningModel):
        """
        Game player model.
        """
        osuser_id = models.CharField(max_length=255, primary_key=True)
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now_add=True, auto_now=True)
        
        HORIZONTAL_PARTITIONING_KEY_FIELD = 'osuser_id'


### 2. save()時は、自動的に自分のシャードに保存される

(自分のシャードは、HORIZONTAL_PARTITIONING_KEY_FIELD 元に算出)

    player = Player()
    player.osuser_id = u'test0001'
    player.save() # save to test0001's shard.


### 3. getする時は、osuser_idを指定することでそのシャードからデータを取得

マネージャー(objects)の partition() メソッドでパーティションを指定する

partition() を通せば、どんなクエリメソッドも実行できる。

    player = Player.objects.partition(u'test0001').get(osuser_id=u'test0001')


## 必要な設定

    # settings.py
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'genju_hime_gree',
            :
        },
        'shard0': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'data_shard_0',
            :
        },
        :
        :
        'shard15': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'data_shard_15',
            :
        },
    }
    
    HORIZONTAL_PARTITIONING_DB_NAME_FORMAT = 'shard%d'
    HORIZONTAL_PARTITIONING_PARTITION_NUMBER = 16


この記述があれば、HorizontalPartitioningModel を継承したモデルの場合、
自動的に自分のシャードを shard0 〜 shard15 の16種類から選択し、
save()の時に使うようになる。

