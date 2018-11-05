from decimal import Decimal
import re
import zenhan

def ExtractNumber(org_str, data_type):
    """
    引数で渡された文字列を半角に変換し、数字のみを抽出して返す。
    param: org_str。例：'(0120)123-456
    param: data_type。例：1=電話番号用、2=郵便番号用、3=法人番号用
    return: org_strから数字のみを抽出した文字列。例：'0120123456'
    """
    # 全角→半角変換
    han_org_str = zenhan.z2h(org_str)
    if data_type == 1 : # 電話番号用
        # カッコとハイフン以外を抽出
        filterd_str = re.findall(r'[^\(\)\-（）−]+', han_org_str)
    elif data_type == 2 : # 郵便番号用
        # ハイフン以外を抽出
        filterd_str = re.findall(r'[^\-−]+', han_org_str)
    elif data_type == 3 : # 法人番号用
        # 法人番号は数字のみなので正規表現の抽出は行わない
        filterd_str = han_org_str
    # filterd_strは配列なので結合した文字列を返す
    return ''.join(filterd_str)

def DecimalDefaultProc(obj):
    """
    DecimalをJSONで出力可能にする
    """
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

