# -*- coding: utf-8 -*-

"""
inspectionGree

inspectionのグリー用機能一覧

"""
from urllib2 import HTTPError
from django.conf import settings
from django.utils import simplejson
from gsocial.log import Log
from base import InspectionBase
from gsocial.utils.base import GsocialCache
# Inspection API を扱う

class InspectionGree(InspectionBase):
    '''
    Inspection APIを扱う（GREE用)
    キャッシュの動作などをプラットフォームにあわせて動作する
    
    Use Inspection Api from Gree.
    Adjusts the behavior of cache in regard of the platform. 
    '''
    def _get_cache_key(self, text_id):
        return 'Inspection:%s' % (text_id)

    def _api_path(self, method, text_id):
        """
            method別api_requestのpath生成
        """
        if method == 'POST':
            path = '/api/rest/inspection/@app'
        elif method == 'PUT':
            path = '/api/rest/inspection/@app/' + str(text_id)
        elif method == 'GET':
            path = '/inspection/@app/' + str(text_id)
        elif method == 'DELETE':
            path = '/inspection/@app/' + str(text_id)
        return path


    def _api_request(self, method, user_id, text_id = None, data = None):
        """
        apiにリスエスト送信
        返り値
          正常時: リスエストのレスポンス
          異常時: None
          
        Send request to api.
        Return value
           usualy: response from request
           when there are problems :None  
        """
        path = self._api_path(method, text_id)
        header = {'Content-Type': 'application/json; cahrset=utf8'}
        response = None

        for retry in xrange(self.RETRY_COUNT):
            try:
                if method in ['POST', 'PUT']:
                    response = self.container.oauth_request(
                                method,
                                user_id,
                                path,
                                data = data,
                                headers = header,
                                url_tail='',
                                body_hash=True
                                )
                else:
                    if text_id != None:
                        response = self.container.oauth_request(method, user_id, path)
                break
            except TypeError:
                Log.warn('Inspection: %s: response type error. userid:%s' % (method, user_id))
                continue
            except HTTPError as e:
                Log.warn('Inspection: %s: response HTTPError %s. textid:%s, userid:%s' %
                             (method, e.code, text_id, user_id))
                continue

        return response

    def post(self, userid, message):
        '''
        POST(新規登録)
        戻したJSONのtextIdを用いることで再度このテキストにアクセスすることができる
        
        POST(Newly register)
        You can access to this text using the textId of returned JSON.
        '''
        # ローカルではリクエストできない
        # You can`t request on local.
        if settings.OPENSOCIAL_DEBUG:
            return None

        message = self.container.encode_emoji(message)
        data = simplejson.dumps({'data': message})
        text_id = None
        json = None
        response = self._api_request('POST', userid, data = data)
        Log.debug('Inspection POST. response: %s' % (response))
        json = simplejson.loads(response)

        if 'entry' in json:
            entry = json['entry'][0]
            if 'textId' in entry:
                text_id = entry['textId']
        Log.debug('Inspection: post: textId:%s' % text_id)

        if not json:
            error = self.container.ResponseError('post', 'Inspection POST')
            raise error
        return text_id
    
    def put(self, userid, text_id, message):
        '''
        PUT（更新）
        POSTで得られたitemIdを用いることでテキストデータを更新することができる
        
        PUT(update)
        You can update the text data using the itemId you got from POST.
        '''
        # ローカルではリクエストできない
        # You can`t request on local.
        if settings.OPENSOCIAL_DEBUG:
            return None

        message = self.container.encode_emoji(message)
        data = simplejson.dumps({'data': message})
        response = self._api_request('PUT', userid, text_id = str(text_id), data = data)
        Log.debug('Inspection PUT. response: %s' % (response))
        # GET のために削除
        # Delete for GET
        GsocialCache.delete_cache(self._get_cache_key(text_id))
        return None

    def delete(self, userid, text_id):
        '''
        DELETE（削除）
        item_idはPOSTで得られたitemId
        
        DELETE
        item_id is the itemId you got from POST.
        '''
        # ローカルではリクエストできない
        # You can`t request on local. 
        if settings.OPENSOCIAL_DEBUG:
            return None

        response = self._api_request('DELETE', userid, text_id = text_id)
        Log.debug('Inspection DELETE. response: %s' % (response))
        # 削除
        # delete
        GsocialCache.delete_cache(self._get_cache_key(text_id))
        # test
        #cache =GsocialCache.get_cache(self._get_cache_key(text_id))
        #print 'delete cache', cache
        return None

    def gets_dict(self, userid, text_ids, caching = True, retry_count = None):
        '''
        複数ID指定のGET（取得）
        返す場合に、text_idとdata、jsonのhashを返す
        
        GET with Multi-IDs.
        Return a hash includes text_id,data, and json. 
        '''
        # ローカルではリクエストできない
        # You can`t request on local
        if settings.OPENSOCIAL_DEBUG:
            return {}

        result_dict = {}
        result_list = self.gets(userid, text_ids, caching, retry_count)
        for result in result_list:
            text_id, data, json = result
            result_dict[text_id] = (data, json)
        return result_dict

    def gets(self, userid, text_ids, caching = True, retry_count = None):
        '''
        複数ID指定のGET（取得）
        text_ids は、listのような複数のIDをいれたiterableなもの
        
        GET with Multi-IDs.
        text_ids is a iterable thing that contain multiple IDs(list).
        '''
        # ローカルではリクエストできない
        # You can`t request on local
        if settings.OPENSOCIAL_DEBUG:
            return []

        retry_count = retry_count if retry_count else self.RETRY_COUNT
        get_text_ids = []
        result_list = []
        for text_id in text_ids:
            # 一つずつキャッシュを確認する
            # Confirms cache each by each. 
            cache_key = self._get_cache_key(text_id)
            id_data_entry = None
            if caching:
                id_data_entry = GsocialCache.get_cache(cache_key)
                #print 'cache:', id_data_entry
            if id_data_entry is None:
                #print 'not cache:', id_data_entry
                get_text_ids.append(text_id)
                id_data_entry = (text_id, None, None)
            # None の場合は None で構わない
            # None doesn`t necessary indicate the problems is underlying.
            result_list.append(id_data_entry)

        # 取得すべきIDだけとりにいく（すべてある場合はキャッシュで解決する筈）
        # You get the ID you need(caching might solve if all of them are already there)
        if len(get_text_ids) > 0:
            get_entry_dict = {}
            text_ids = ','.join(get_text_ids)

            response = self._api_request('GET', userid, text_id = text_ids)
            Log.debug('response: %s' % response)

            if response != None:
                json = simplejson.loads(response)
                if 'entry' in json:
                    entry_list = json['entry']

                    for entry in entry_list:
                        if 'data' in entry:
                            data = entry['data']
                        else:
                            data = u''
                        data = self.container.decode_emoji(data)
                        if caching:
                            text_id = entry['textId']
                            cache_key = self._get_cache_key(text_id)
                            status = int(entry['status'])
                            if status == self.STATUS_INSPECTING:
                                # 検査中
                                # 監査中の場合、３時間までキャッシュ可能
                                timeout = 3 * 60 * 60
                            elif status == self.STATUS_OK:
                                # 監査OK
                                # 監査OKの場合、２４時間までキャッシュ可能
                                timeout = 24 * 60 * 60
                            elif status == self.STATUS_NG:
                                # 監査NG
                                # 監査NGの場合、無期限でキャッシュ可能だが、２４時間
                                timeout = 24 * 60 * 60
                            else:
                                timeout = None
                            if timeout:
                                # textId 毎のキャッシュを必ずつくる
                                GsocialCache.set_cache(cache_key, (text_id, data, entry), timeout=timeout)
                                Log.debug('Inspection Cache Set status: %d(%d).' % (status, timeout))
                        # リストの該当箇所に突っ込む
                        get_entry_dict[text_id] = (text_id, data, entry)

            new_result_list = []
            for result in result_list:
                if result[0] in get_entry_dict:
                    result = get_entry_dict[result[0]]
                new_result_list.append(result)
            result_list = new_result_list
        return result_list

    def get(self, userid, item_id, caching = True, retry_count = None):
        '''
        GET（取得）
        '''
        # ローカルではリクエストできない
        # You can`t request on local.
        if settings.OPENSOCIAL_DEBUG:
            return None

        result_list = self.gets(userid, [item_id], caching, retry_count)
        
        return result_list[0]
