# -*- coding: utf-8 -*-
import MeCab
import sys
import string


class MeCabWrapper(object):
    def __init__(self, sentence):
        self.word_list = []
        self._parse(sentence)

    def _parse(self, sentence):
        #print MeCab.VERSION

        # t = MeCab.Tagger (" ".join(sys.argv))
        t = MeCab.Tagger (" ")

        # encode utf8
        # http://shogo82148.github.io/blog/2012/12/15/mecab-python/
        sentence = sentence.encode('utf-8')

        # print t.parse(sentence)

        m = t.parseToNode(sentence)
        while m:
            # print m.surface, "\t", m.feature
            self._count(m)
            m = m.next
            #print "EOS"

        # lattice = MeCab.Lattice()
        # t.parse(lattice)
        # lattice.set_sentence(sentence)
        # len = lattice.size()
        # for i in range(len + 1):
        #     b = lattice.begin_nodes(i)
        #     e = lattice.end_nodes(i)
        #     while b:
        #         print "B[%d] %s\t%s" % (i, b.surface, b.feature)
        #         b = b.bnext
        #     while e:
        #         print "E[%d] %s\t%s" % (i, e.surface, e.feature)
        #         e = e.bnext
        #print "EOS";

        #d = t.dictionary_info()
        # while d:
        #     print "filename: %s" % d.filename
        #     print "charset: %s" %  d.charset
        #     print "size: %d" %  d.size
        #     print "type: %d" %  d.type
        #     print "lsize: %d" %  d.lsize
        #     print "rsize: %d" %  d.rsize
        #     print "version: %d" %  d.version
        #     d = d.next

    def _count(self, node):
        """
        node.surface, "\t", m.feature

        node.surface ・・・ 新生
        node.feature ・・・ 名詞,固有名詞,組織,*,*,*,新生,シンセイ,シンセイ
        """
        #print node.surface, "\t", node.feature

        word = node.surface

        if not word:
            return

        # スレタイから特定品詞を除外
        if not self._check_subjects_feature(node):
            return

        self.word_list.append(node.surface)

    @classmethod
    def _check_subjects_feature(cls, node):
        """
        スレタイから、特定品詞を除外する
        記号とか
        """
        if "記号" in node.feature:
            return False

        # if "非自立" in node.feature:
        #     return False
        #
        # if "連体詞" in node.feature:
        #     return False


        return True

    @classmethod
    def get_feature(cls, sentence):
        t = MeCab.Tagger (" ")
        m = t.parseToNode(sentence)
        while m:
            if m.surface:
                # print m.surface, "\t", m.feature
                return m.feature
            m = m.next
        return None

class MeCabParser(object):
    """
    メカブをパースする。
    """
    def __init__(self):
        pass

