# horizontalpartitioning

Implement horizontal partitioning of DB,using Django.


## Usage

### 1. Inherit HorizontalPartitioningModel,instead of models.Model,to create data model.

    from horizontalpartitioning.models import HorizontalPartitioningModel
    
    class Player(HorizontalPartitioningModel):
        """
        Game player model.
        """
        osuser_id = models.CharField(max_length=255, primary_key=True)
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now_add=True, auto_now=True)
        
        HORIZONTAL_PARTITIONING_KEY_FIELD = 'osuser_id'

### 2. When you run save(),it will automaticaly saves data on your shards.
(The shardes will be decide from HORIZONTAL_PARTITIONING_KEY_FIELD)

    player = Player()
    player.osuser_id = u'test0001'
    player.save() # save to test0001's shard.

### 3. When you run get(),specifing osuser_id  will bring the data from the shards.  
You can specify the partition from partition() method of manager(objects).
You can run any query method,if you use partition().

    player = Player.objects.partition(u'test0001').get(osuser_id=u'test0001')

## Settings

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

If you write settings.py like this,save() will automaticaly chose the shard from shard0 〜 shard15.
This is only valid to models which inherit HorizontalPartitioningModel.


