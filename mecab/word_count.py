# -*- coding: utf-8 -*-


# ファイルを開く
path = r"C:\Users\sub\Dropbox\private\Project\python\wiki\test_mecab\result4.txt"

f = open(path)
count = {}

for line in f:
    # 開業排除
    line = line[:-1]

    # 名詞のみを対象とする
    if not "名詞" in line:
        continue

    # 代名詞は除外
    if "代名詞" in line:
        continue

    # 非自立は除外
    if "非自立" in line:
        continue

    # 2文字以上のみカウント
    itemList = line.split('\t')
    line = itemList[0]
    # print word, len(word)
    if len(line) < 7:
        continue

    if line in count:
        count[line] += 1
    else:
        count[line] = 1
f.close()


# 辞書全体を出力
for k, v in sorted(count.items(), key=lambda x:x[1]): # for/if文では文末のコロン「:」を忘れないように
    # カウント2以上が対象
    if v >= 2:
        print k, v


