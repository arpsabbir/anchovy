# -*- coding: utf-8 -*-
import re
import MeCab


# 特徴語認定するためのしきい値
# センテンス結合数と出現数
from module.mecab.mecab_wrapper import MeCabWrapper

SENTENCE_LIMIT_MAP = {
    1:20,
    2:20,
    3:10,
    4:8,
    5:5,
    6:4,
    7:4,
    8:4,
    9:4,
    10:4,
    11:4,
}
SENTENCE_LIMIT_MAP = {
    1:10,
    2:5,
    3:3,
    4:2,
    5:2,
    6:2,
    7:2,
    8:2,
    9:2,
    10:2,
    11:2,
}



class MeCabAnalysis(object):
    """
    MeCabの解析結果を取りまとめる
    """
    def __init__(self, keyword_list):
        print "==========start mecab analysis=========="
        self.word_count_dict = {}
        self.key_word_dict = {}
        self.unique_word_list = []
        self.unique_word_list_single = []
        self.unique_word_list_multi = []

        self._analysis(keyword_list)


        pass

    def _analysis(self, keyword_list):
        _d = {}

        # 単語の出現数をカウントする
        for keyword in keyword_list:
            if _d.has_key(keyword):
                # 要素数のincr
                count = _d[keyword]
                _d[keyword] = count + 1
            else:
                # 要素の追加
                _d[keyword] = 1
        self.word_count_dict = _d

        # キーワードリストの生成
        self._analysis_keyword()

        # 複数センテンスからなる重複ワードを解析
        self._analysis_multi_word_sentence(keyword_list)

        # 重複を排除してユニークワードを生成
        self._make_unique_word()


    def _analysis_keyword(self):
        """
        頻出ワードを解析
        """
        _key_word_dict = {}

        # 単語出現数辞書のソート
        for k, v in sorted(self.word_count_dict.items(), key=lambda x:x[1]):
            # カウント2以上が対象
            if v >= 2:
                # print k, v, len(k)
                _key_word_dict[k] = v

            # 文字数の多い固有名詞をprint
            if v>= 2 and len(k) > 9:
                print k, v
                # 特徴後に設定
                self.unique_word_list_single.append(k)

        self.key_word_dict = _key_word_dict

    def _analysis_multi_word_sentence(self, keyword_list):
        """
        複数センテンスからなる重複ワードを解析
        """
        # 調査対象のtextを生成
        target_text = ""
        for keyword in keyword_list:
            target_text += keyword

        # 頻出単語
        for dict_key in self.key_word_dict:
            keyword = self.key_word_dict.get(dict_key)
            if keyword and self._check_keyword_type(dict_key):
                multi_sentence = self._anal(dict_key, keyword_list, target_text)

                # 調査対象のtextから該当のセンテンスを削除
                if multi_sentence:
                    # 特徴後に設定
                    self.unique_word_list_multi.append(multi_sentence)
                    target_text = target_text.replace(multi_sentence, "")

    def _check_keyword_type(self, word):
        """
        MeCabで品詞種類を調べて、フィルタする
        """
        node_feature = MeCabWrapper.get_feature(word)

        if "記号" in node_feature:
            return False

        if "名詞,数" in node_feature:
            return False

        if "名詞,接" in node_feature:
            return False

        if "動詞,自立" in node_feature:
            return False

        if "接続詞" in node_feature:
            return False

        if "助詞" in node_feature:
            return False

        return True

    def _anal(self, keyword, keyword_list, target_text):
        """
        print する
        """
        # print "+++++++++++start _anal!! SEARCH WORD:%s+++++++++++" % keyword

        index = 0
        # self._anal_show(count, keyword_list)

        # keywordの出現するindexを調べる
        for _keyword in keyword_list:
            if keyword == _keyword:
                break
            index += 1

        # キーワードの出現数を調べる
        return self._anal_show(index, keyword_list, target_text)

    def _anal_show(self, index, keyword_list, target_text):
        for sentence_count in reversed(xrange(2, 11)):
            multi_sentence = self._get_multi_sentence(keyword_list, index, sentence_count)
            if multi_sentence:
                # text中の出現数をカウントする
                text_count = target_text.count(multi_sentence)

                # しきい値以上の特徴後を抽出
                if self._check_unique_word(sentence_count, text_count):
                    print sentence_count, multi_sentence, text_count
                    return multi_sentence

        try:
            # print keyword_list[count], keyword_list[count+1]
            # print keyword_list[count], keyword_list[count+1], keyword_list[count+2]
            # print keyword_list[count], keyword_list[count+1], keyword_list[count+2], keyword_list[count+3]
            # print keyword_list[count], keyword_list[count+1], keyword_list[count+2], keyword_list[count+3], keyword_list[count+4]
            # print keyword_list[count], keyword_list[count+1], keyword_list[count+2], keyword_list[count+3], keyword_list[count+4], keyword_list[count+5]
            pass
        except IndexError:
            pass

    def _check_unique_word(self, sentence_count, text_count):
        """
        センテンス結合数と出現数から特徴後判定を実施
        """
        limit_count = SENTENCE_LIMIT_MAP.get(sentence_count)
        return limit_count <= text_count

    def _get_multi_sentence(self, keyword_list, count, sentence_count):
        multi_sentence = ""
        for x in xrange(count, count + sentence_count):
            try:
                multi_sentence += keyword_list[x]
            except IndexError:
                return None
        return multi_sentence

    def _make_unique_word(self):
        for single in self.unique_word_list_single:
            for multi in self.unique_word_list_multi:
                m = re.search(single, multi)
                if m:
                    # multiとsingleで重複があるためremoveする
                    self.unique_word_list_single.remove(single)
        self.unique_word_list = self.unique_word_list_multi + self.unique_word_list_single

    def show(self):
        print "==========START SHOW=========="
        for word in self.unique_word_list:
            print word
