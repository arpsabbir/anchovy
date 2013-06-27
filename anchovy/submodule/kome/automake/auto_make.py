# coding: utf-8

import itertools

def generate_enum(d):
    values = ["    %s = '%s'\n" % (x, x) for x in d['values']]
    anyof = """
    @classmethod
    def any_of(cls, value):
        vs = [%s]
        return any([value == v for v in vs])""" % ','.join(['cls.%s' % x for x in d['values']])

    return """
class %s:
%s%s
""" % (d['name'], "".join(values), anyof)


def generate_func(d, enums):
    def get_enum(type):
        xs = [e for e in enums if e['name'] == type]
        return xs[0] if len(xs) != 0 else None

    # パラメータリストの文字列
    def params_str(d):
        def default(p):
            return ' = ' + str(p['default']) if 'default' in p else ''
        ns = [p['name'] + default(p) + ', ' for p in d['params']]
        return ''.join(ns)

    # 説明部分の文字列
    def desc_str(d):
        params = d['params']
        if 'description' not in d and len(params) == 0:
            return ''

        def description_str(d):
            if 'description' not in d:
                return ''
            lines = d['description'].lstrip('\n').rstrip().split('\n')
            indent = min([len(list(itertools.takewhile(lambda c: c == ' ', line))) for line in lines if line.count(' ') != len(line)])
            padlines = [' ' * indent if line.count(' ') == len(line) else line for line in lines]
            return '\n        \n' + '\n'.join(['        ' + line[indent:] for line in padlines])

        def enum_str(param):
            e = get_enum(param['type']) if 'type' in param else None
            return '(%s.[%s])' % (e['name'], ','.join(e['values'])) if e is not None else ""
        def optional(param):
            return ' (opt)' if 'default' in param else ''

        ps = ['\n        ' + p['name'] + optional(p) + ' -- ' + p['summary'] + enum_str(p) for p in params]
        return '\n        ' + ''.join(ps) + description_str(d)

    # 型チェックassert部分の文字列
    def asserts_str(d):
        def type_check_str(param, type):
            e = get_enum(type)
            if e is not None:
                return '%s.any_of(%s)' % (e['name'], param['name'])
            else:
                return '_isinstance(%s, %s)' % (param['name'], type)

        def assert_str(param):
            if isinstance(param['type'], list):
                s = ' or '.join([type_check_str(param, type) for type in param['type']])
            else:
                s = type_check_str(param, param['type'])
            # デフォルト引数がある場合はそれも含める
            if 'default' in param:
                d = ' or %s == %s' % (param['name'], str(param['default']))
            else:
                d = ''
            return s + d

        return ''.join(['        assert %s\n' % assert_str(param) for param in d['params'] if 'type' in param])

    # 関数によるassert部分の文字列
    def func_asserts_str(d):
        def assert_str(param):
            return '%s(%s)' % (param['assert'], param['name'])
        return ''.join(['        assert %s\n' % assert_str(param) for param in d['params'] if 'assert' in param])

    # 引数部分の文字列
    def args_str(d):
        return ''.join([',\n                        ' + p['name'] + ' = ' + p['name'] for p in d['params']])

    # 関数全体の定義
    return """
    def %s(self, %s**opt):
        u\"\"\"
        %s%s
        \"\"\"
%s%s
        return self.log('%s'%s,
                        **opt)""" % (d['name'],
                                     params_str(d),
                                     d['summary'],
                                     desc_str(d),
                                     asserts_str(d),
                                     func_asserts_str(d),
                                     d['name'],
                                     args_str(d))

