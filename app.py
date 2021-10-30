import copy
import json

from flask import Flask, render_template, request, jsonify, abort
import pymysql
import datetime

app = Flask(__name__)
data_place = []
data_place2 = []

# 用户根据需要修改数据库配置
db = pymysql.connect(host='127.0.0.1', user='root', passwd='xjying11', db='secondhandHouse', port=3306,
                             charset='utf8')


@app.route('/', methods=['GET', 'POST'])
def index():

    now_year = datetime.datetime.now().year
    # db = pymysql.connect(host='127.0.0.1', user='root', passwd='xjying11', db='secondhandHouse', port=3306,
    #                          charset='utf8')
    cursor = db.cursor()

    sql = 'SELECT community_name, province, city, district FROM community group by province, city, district, community_name order by province, city, district, community_name'
    cursor.execute(sql)
    global data_place
    data_place = cursor.fetchall()

    sql = 'SELECT distinct province, city, district FROM community group by province, city, district, community_name order by province, city, district'
    cursor.execute(sql)
    global data_place2
    data_place2 = cursor.fetchall()

    sql = 'SELECT median_price,min_price,max_price,deal_count,deal_month,deal_year FROM community_chart WHERE province=%s and city=%s and district=%s and community_name=%s and deal_year>=%s'
    val = ('广东', '广州', '南沙', '碧桂园天玺湾', now_year-3)

    deal_month = []
    median_price = []
    min_price = []
    max_price = []
    deal_count = []
    cursor.execute(sql, val)
    data = cursor.fetchall()
    # print(data)
    for i in data:
        median_price.append(float(i[0]))
        min_price.append(float(i[1]))
        max_price.append(float(i[2]))
        deal_count.append(float(i[3]))
        deal_month.append(str(i[5]) + "." + str(i[4]))

    room_num = {
        "一房": None,
        "二房": None,
        "三房": None,
        "四房": None
    }
    deal_price_range = {
        "0-100": None,
        "100-200": None,
        "200-300": None,
        "300-400": None,
        "400-500": None,
        "500-": None
    }

    val = ('广东', '广州', '南沙', '碧桂园天玺湾', now_year-3)

    sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE house_structure regexp "1" and province=%s and city=%s and district=%s and community_name=%s and deal_year>=%s'

    cursor.execute(sql, val)
    room_num["一房"] = len(cursor.fetchall())

    sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE house_structure regexp "2" and province=%s and city=%s and district=%s and community_name=%s and deal_year>=%s'

    cursor.execute(sql, val)
    room_num["二房"] = len(cursor.fetchall())

    sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE house_structure regexp "3" and province=%s and city=%s and district=%s and community_name=%s and deal_year>=%s'

    cursor.execute(sql, val)
    room_num["三房"] = len(cursor.fetchall())

    sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE house_structure regexp "4" and province=%s and city=%s and district=%s and community_name=%s and deal_year=%s'

    cursor.execute(sql, val)
    room_num["四房"] = len(cursor.fetchall())

    sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE (deal_price<100) and province=%s and city=%s and district=%s and community_name=%s and deal_year>=%s '

    cursor.execute(sql, val)
    deal_price_range["0-100"] = len(cursor.fetchall())

    sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE (deal_price>=100 and deal_price<200) and province=%s and city=%s and district=%s and community_name=%s and deal_year>=%s '

    cursor.execute(sql, val)
    deal_price_range["100-200"] = len(cursor.fetchall())

    sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE (deal_price>=200 and deal_price<300) and province=%s and city=%s and district=%s and community_name=%s and deal_year>=%s '

    cursor.execute(sql, val)
    deal_price_range["200-300"] = len(cursor.fetchall())

    sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE (deal_price>=300 and deal_price<400) and province=%s and city=%s and district=%s and community_name=%s and deal_year>=%s '

    cursor.execute(sql, val)
    deal_price_range["300-400"] = len(cursor.fetchall())

    sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE (deal_price>=400 and deal_price<500) and province=%s and city=%s and district=%s and community_name=%s and deal_year>=%s '

    cursor.execute(sql, val)
    deal_price_range["400-500"] = len(cursor.fetchall())

    sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE (deal_price>=500) and province=%s and city=%s and district=%s and community_name=%s and deal_year>=%s '

    cursor.execute(sql, val)
    deal_price_range["500-"] = len(cursor.fetchall())

    max_room_num = [max(room_num, key=room_num.get), max(room_num.values()),
                    "%.2f%%" % (max(room_num.values()) / sum(room_num.values())*100)]
    max_deal_price_range = [max(deal_price_range, key=deal_price_range.get), max(deal_price_range.values()),
                            "%.2f%%" % (max(deal_price_range.values()) / sum(deal_price_range.values())*100)]

    # 优质房
    sql = 'SELECT SUM(deal_price), SUM(area), deal_month, deal_year FROM community natural join house natural join deal_record where province=%s and city=%s and district=%s and community_name=%s and deal_year>=%s and find_in_set("南", direction) and (floor regexp "中楼层" or floor regexp "高楼层") GROUP BY deal_year, deal_month ORDER BY deal_year, deal_month'

    val = ('广东', '广州', '南沙', '碧桂园天玺湾', now_year-3)

    cursor.execute(sql, val)
    data = cursor.fetchall()

    num1 = []
    deal_month1 = []
    for i in data:
        num1.append("%.2f" % (i[0] * 10000 / i[1]))
        deal_month1.append(str(i[3])+"."+str(i[2]))

    # 刚需房
    sql = 'SELECT SUM(deal_price), SUM(area), deal_month, deal_year FROM community natural join house natural join deal_record where province=%s and city=%s and district=%s and community_name=%s and deal_year>=%s and area < 80 GROUP BY deal_year, deal_month ORDER BY deal_year, deal_month'
    val = ('广东', '广州', '南沙', '碧桂园天玺湾', now_year-3)

    cursor.execute(sql, val)
    data = cursor.fetchall()

    num2 = []
    deal_month2 = []
    for i in data:
        num2.append("%.2f" % (i[0] * 10000 / i[1]))
        deal_month2.append(str(i[3])+"."+str(i[2]))

    # 总体走势图
    sql = 'SELECT SUM(deal_price), SUM(area), deal_month, deal_year FROM community natural join house natural join deal_record where province=%s and city=%s and district=%s and community_name=%s and deal_year>=%s GROUP BY deal_year, deal_month ORDER BY deal_year, deal_month'

    val = ('广东', '广州', '南沙', '碧桂园天玺湾', now_year-3)

    cursor.execute(sql, val)
    data = cursor.fetchall()

    num3 = []
    deal_month3 = []
    for i in data:
        num3.append("%.2f" % (i[0] * 10000 / i[1]))
        deal_month3.append(str(i[3]) + "." + str(i[2]))

    cursor.close()

    return render_template("index.html", median_price=median_price, min_price=min_price, max_price=max_price,
                           deal_month=deal_month, deal_count=deal_count,
                           max_room_num=max_room_num, max_deal_price_range=max_deal_price_range,
                           deal_month1=deal_month1, num1=num1,
                           deal_month2=deal_month2, num2=num2,
                           deal_month3=deal_month3, num3=num3)


@app.route('/a', methods=['GET', 'POST'])
def a():
    now_year = datetime.datetime.now().year
    # db = pymysql.connect(host='localhost', user='root', passwd='xjying11', db='secondhandHouse', port=3306,
    #                      charset='utf8')
    cursor = db.cursor()
    sql = 'SELECT median_price,min_price,max_price,deal_count, deal_month, deal_year FROM community_chart WHERE province=%s and city=%s and district=%s and community_name=%s and deal_year>=%s'
    val = None
    result = None
    if request.method == 'POST':
        result = dict(request.form)
        val = (result["province"], result["city"], result["district"], result["community_name"], now_year-3)
        if result["community_name"] == '':
            sql = 'SELECT median_price,min_price,max_price,deal_count, deal_month, deal_year FROM district_chart WHERE province=%s and city=%s and district=%s and deal_year>=%s'
            val = (result["province"], result["city"], result["district"], now_year-3)

    deal_month = []
    median_price = []
    min_price = []
    max_price = []
    deal_count = []
    cursor.execute(sql, val)
    data = cursor.fetchall()
    for i in data:
        median_price.append(float(i[0]))
        min_price.append(float(i[1]))
        max_price.append(float(i[2]))
        deal_count.append(float(i[3]))
        deal_month.append(str(i[5])+"."+str(i[4]))

    room_num = {
        "一房": None,
        "二房": None,
        "三房": None,
        "四房": None
    }
    deal_price_range = {
        "0-100": None,
        "100-200": None,
        "200-300": None,
        "300-400": None,
        "400-500": None,
        "500-": None
    }

    sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE house_structure regexp "1" and province=%s and city=%s and district=%s and community_name=%s and deal_year>=%s'
    if request.method == 'POST':
        val = (result["province"], result["city"], result["district"], result["community_name"], now_year-3)
        if result["community_name"] == '':
            sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE house_structure regexp "1" and province=%s and city=%s and district=%s and deal_year>=%s'
            val = (result["province"], result["city"], result["district"], now_year-3)
    cursor.execute(sql, val)
    room_num["一房"] = len(cursor.fetchall())

    sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE house_structure regexp "2" and province=%s and city=%s and district=%s and community_name=%s and deal_year>=%s'
    if request.method == 'POST':
        val = (result["province"], result["city"], result["district"], result["community_name"], now_year-3)
        if result["community_name"] == '':
            sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE house_structure regexp "2" and province=%s and city=%s and district=%s and deal_year>=%s'
            val = (result["province"], result["city"], result["district"], now_year-3)
    cursor.execute(sql, val)
    room_num["二房"] = len(cursor.fetchall())

    sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE house_structure regexp "3" and province=%s and city=%s and district=%s and community_name=%s and deal_year>=%s'
    if request.method == 'POST':
        val = (result["province"], result["city"], result["district"], result["community_name"], now_year-3)
        if result["community_name"] == '':
            sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE house_structure regexp "3" and province=%s and city=%s and district=%s and deal_year>=%s'
            val = (result["province"], result["city"], result["district"], now_year-3)
    cursor.execute(sql, val)
    room_num["三房"] = len(cursor.fetchall())

    sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE house_structure regexp "4" and province=%s and city=%s and district=%s and community_name=%s and deal_year>=%s'
    if request.method == 'POST':
        val = (result["province"], result["city"], result["district"], result["community_name"], now_year-3)
        if result["community_name"] == '':
            sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE house_structure regexp "4" and province=%s and city=%s and district=%s and deal_year>=%s'
            val = (result["province"], result["city"], result["district"], now_year-3)
    cursor.execute(sql, val)
    room_num["四房"] = len(cursor.fetchall())

    sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE (deal_price<100) and province=%s and city=%s and district=%s and community_name=%s and deal_year>=%s '
    if request.method == 'POST':
        val = (result["province"], result["city"], result["district"], result["community_name"], now_year-3)
        if result["community_name"] == '':
            sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE (deal_price<100) and province=%s and city=%s and district=%s and deal_year>=%s '
            val = (result["province"], result["city"], result["district"], now_year-3)
    cursor.execute(sql, val)
    deal_price_range["0-100"] = len(cursor.fetchall())

    sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE (deal_price>=100 and deal_price<200) and province=%s and city=%s and district=%s and community_name=%s and deal_year>=%s '
    if request.method == 'POST':
        val = (result["province"], result["city"], result["district"], result["community_name"], now_year-3)
        if result["community_name"] == '':
            sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE (deal_price>=100 and deal_price<200) and province=%s and city=%s and district=%s and deal_year>=%s '
            val = (result["province"], result["city"], result["district"], now_year-3)
    cursor.execute(sql, val)
    deal_price_range["100-200"] = len(cursor.fetchall())

    sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE (deal_price>=200 and deal_price<300) and province=%s and city=%s and district=%s and community_name=%s and deal_year>=%s '
    if request.method == 'POST':
        val = (result["province"], result["city"], result["district"], result["community_name"], now_year-3)
        if result["community_name"] == '':
            sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE (deal_price>=200 and deal_price<300) and province=%s and city=%s and district=%s and deal_year>=%s '
            val = (result["province"], result["city"], result["district"], now_year-3)
    cursor.execute(sql, val)
    deal_price_range["200-300"] = len(cursor.fetchall())

    sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE (deal_price>=300 and deal_price<400) and province=%s and city=%s and district=%s and community_name=%s and deal_year>=%s '
    if request.method == 'POST':
        val = (result["province"], result["city"], result["district"], result["community_name"], now_year-3)
        if result["community_name"] == '':
            sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE (deal_price>=300 and deal_price<400) and province=%s and city=%s and district=%s and deal_year>=%s '
            val = (result["province"], result["city"], result["district"], now_year-3)
    cursor.execute(sql, val)
    deal_price_range["300-400"] = len(cursor.fetchall())

    sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE (deal_price>=400 and deal_price<500) and province=%s and city=%s and district=%s and community_name=%s and deal_year>=%s '
    if request.method == 'POST':
        val = (result["province"], result["city"], result["district"], result["community_name"], now_year-3)
        if result["community_name"] == '':
            sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE (deal_price>=400 and deal_price<500) and province=%s and city=%s and district=%s and deal_year>=%s '
            val = (result["province"], result["city"], result["district"], now_year-3)
    cursor.execute(sql, val)
    deal_price_range["400-500"] = len(cursor.fetchall())

    sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE (deal_price>=500) and province=%s and city=%s and district=%s and community_name=%s and deal_year>=%s '
    if request.method == 'POST':
        val = (result["province"], result["city"], result["district"], result["community_name"], now_year-3)
        if result["community_name"] == '':
            sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE (deal_price>=500) and province=%s and city=%s and district=%s and deal_year>=%s '
            val = (result["province"], result["city"], result["district"], now_year-3)
    cursor.execute(sql, val)
    deal_price_range["500-"] = len(cursor.fetchall())

    if sum(room_num.values()) != 0:
        max_room_num = [max(room_num, key=room_num.get), max(room_num.values()),
                        "%.2f%%" % (max(room_num.values()) / sum(room_num.values()) * 100)]
    if sum(deal_price_range.values()) != 0:
        max_deal_price_range = [max(deal_price_range, key=deal_price_range.get), max(deal_price_range.values()),
                                "%.2f%%" % (max(deal_price_range.values()) / sum(deal_price_range.values()) * 100)]

    # 优质房
    sql = 'SELECT SUM(deal_price), SUM(area), deal_month, deal_year FROM community natural join house natural join deal_record where province=%s and city=%s and district=%s and community_name=%s and deal_year>=%s and find_in_set("南", direction) and (floor regexp "中楼层" or floor regexp "高楼层") GROUP BY deal_year, deal_month ORDER BY deal_year, deal_month'

    if request.method == 'POST':
        val = (result["province"], result["city"], result["district"], result["community_name"], now_year-3)
        if result["community_name"] == '':
            sql = 'SELECT SUM(deal_price), SUM(area), deal_month, deal_year FROM community natural join house natural join deal_record where province=%s and city=%s and district=%s and deal_year>=%s and find_in_set("南", direction) and (floor regexp "中楼层" or floor regexp "高楼层") GROUP BY deal_year, deal_month ORDER BY deal_year, deal_month'
            val = (result["province"], result["city"], result["district"], now_year-3)

    cursor.execute(sql, val)
    data = cursor.fetchall()

    num1 = []
    deal_month1 = []
    for i in data:
        num1.append("%.2f" % (i[0] * 10000 / i[1]))
        deal_month1.append(str(i[3])+"."+str(i[2]))

    # 刚需房
    sql = 'SELECT SUM(deal_price), SUM(area), deal_month, deal_year FROM community natural join house natural join deal_record where province=%s and city=%s and district=%s and community_name=%s and deal_year>=%s and area < 80 GROUP BY deal_year, deal_month ORDER BY deal_year, deal_month'
    if request.method == 'POST':
        val = (result["province"], result["city"], result["district"], result["community_name"], now_year-3)
        if result["community_name"] == '':
            sql = 'SELECT SUM(deal_price), SUM(area), deal_month, deal_year FROM community natural join house natural join deal_record where province=%s and city=%s and district=%s and deal_year>=%s and area < 80 GROUP BY deal_year, deal_month ORDER BY deal_year, deal_month'
            val = (result["province"], result["city"], result["district"], now_year-3)

    cursor.execute(sql, val)
    data = cursor.fetchall()

    num2 = []
    deal_month2 = []
    j = None
    for i in data:
        num2.append("%.2f" % (i[0] * 10000 / i[1]))
        deal_month2.append(str(i[3]) + "."+str(i[2]))

    # 总体走势图
    sql = 'SELECT SUM(deal_price), SUM(area), deal_month, deal_year FROM community natural join house natural join deal_record where province=%s and city=%s and district=%s and community_name=%s and deal_year>=%s GROUP BY deal_year, deal_month ORDER BY deal_year, deal_month'
    if request.method == 'POST':
        val = (result["province"], result["city"], result["district"], result["community_name"], now_year - 3)
        if result["community_name"] == '':
            sql = 'SELECT SUM(deal_price), SUM(area), deal_month, deal_year FROM community natural join house natural join deal_record where province=%s and city=%s and district=%s and deal_year>=%s GROUP BY deal_year, deal_month ORDER BY deal_year, deal_month'
            val = (result["province"], result["city"], result["district"], now_year - 3)

    cursor.execute(sql, val)
    data = cursor.fetchall()

    num3 = []
    deal_month3 = []
    for i in data:
        num3.append("%.2f" % (i[0] * 10000 / i[1]))
        deal_month3.append(str(i[3]) + "." + str(i[2]))

    # 转换成JSON数据格式
    if sum(room_num.values()) != 0 and sum(deal_price_range.values()) != 0:

        jsonData = {'median_price': median_price, 'min_price': min_price, 'max_price': max_price, 'deal_month': deal_month,
                'deal_count': deal_count, 'max_deal_price_range': max_deal_price_range, 'deal_month1': deal_month1,
                'num1': num1, 'deal_month2': deal_month2, 'num2': num2}
    # json.dumps()用于将dict类型的数据转成str，因为如果直接将dict类型的数据写入json会发生报错，因此将数据写入时需要用到该函数。
        j = json.dumps(jsonData)
    cursor.close()

    if sum(room_num.values()) != 0 and sum(deal_price_range.values()) != 0:
        return jsonify(median_price=median_price, min_price=min_price, max_price=max_price,
                   deal_month=deal_month, deal_count=deal_count,
                 max_room_num=max_room_num, max_deal_price_range=max_deal_price_range,
                  deal_month1=deal_month1, num1=num1,
                  deal_month2=deal_month2, num2=num2,
                       deal_month3=deal_month3, num3=num3
                  )
    else:
        abort(404)


# 指数走势图
@app.route('/b', methods=['GET', 'POST'])

def b():
    now_year = datetime.datetime.now().year
    # db = pymysql.connect(host='localhost', user='root', passwd='xjying11', db='secondhandHouse', port=3306,
    #                      charset='utf8')
    cursor = db.cursor()
    val = None
    result = None

    sql = 'SELECT SUM(deal_price), SUM(area), deal_month, deal_year FROM community natural join house natural join deal_record where province=%s and city=%s and district=%s and community_name=%s and deal_year>=%s GROUP BY deal_year, deal_month ORDER BY deal_year, deal_month'

    if request.method == 'POST':
        val = (result["province"], result["city"], result["district"], result["community_name"], now_year - 3)
        if result["community_name"] == '':
            sql = 'SELECT SUM(deal_price), SUM(area), deal_month, deal_year FROM community natural join house natural join deal_record where province=%s and city=%s and district=%s and deal_year>=%s GROUP BY deal_year, deal_month ORDER BY deal_year, deal_month'
            val = (result["province"], result["city"], result["district"], now_year - 3)

    cursor.execute(sql, val)
    data = cursor.fetchall()

    num3 = []
    deal_month3 = []
    for i in data:
        num3.append("%.2f" % (i[0] * 10000 / i[1]))
        deal_month3.append(str(i[3]) + "." + str(i[2]))

    cursor.close()
    return jsonify(num3=num3, deal_month3=deal_month3)




# 走势图，成交量
# @app.route('/abc', methods=['GET', 'POST'])
# def abc():
#
#     if request.method == 'POST':
#         db = pymysql.connect(host='127.0.0.1', user='root', passwd='xjying11', db='secondhandHouse', port=3306,
#                              charset='utf8')
#         cursor = db.cursor()
#
#         result = dict(request.form)
#         # print(result)
#         # print(result)
#         # print(result["province"])
#
#         sql = 'SELECT median_price,min_price,max_price,deal_count, deal_month FROM community_chart WHERE province=%s and city=%s and district=%s and community_name=%s and deal_year=%s'
#         # sql = 'SELECT median_price,min_price,max_price,deal_count, deal_month FROM community_chart WHERE province=%s and city=%s and district=%s and community_name=%s and deal_year=%s'
#
#         val = (result["province"], result["city"], result["district"], result["community_name"], result["deal_year"])
#         # print(result)
#         deal_month = []
#         median_price = []
#         min_price = []
#         max_price = []
#         deal_count = []
#         cursor.execute(sql, val)
#         data = cursor.fetchall()
#         for i in data:
#             median_price.append(float(i[0]))
#             min_price.append(float(i[1]))
#             max_price.append(float(i[2]))
#             deal_count.append(float(i[3]))
#             deal_month.append(i[4])
#
#         room_num = {
#             "一房": None,
#             "二房": None,
#             "三房": None,
#             "四房": None
#         }
#         deal_price_range = {
#             "0-100": None,
#             "100-200": None,
#             "200-300": None,
#             "300-400": None,
#             "400-500": None,
#             "500-": None
#         }
#
#         val = (result["province"], result["city"], result["district"], result["deal_year"])
#
#         sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE house_structure regexp "1" and province=%s and city=%s and district=%s and deal_year=%s'
#         cursor.execute(sql, val)
#         room_num["一房"] = len(cursor.fetchall())
#         sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE house_structure regexp "2" and province=%s and city=%s and district=%s and deal_year=%s'
#         cursor.execute(sql, val)
#         room_num["二房"] = len(cursor.fetchall())
#         sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE house_structure regexp "3" and province=%s and city=%s and district=%s and deal_year=%s'
#         cursor.execute(sql, val)
#         room_num["三房"] = len(cursor.fetchall())
#         sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE house_structure regexp "4" and province=%s and city=%s and district=%s and deal_year=%s'
#         cursor.execute(sql, val)
#         room_num["四房"] = len(cursor.fetchall())
#         sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE (deal_price<100) and province=%s and city=%s and district=%s and deal_year=%s '
#         cursor.execute(sql, val)
#         deal_price_range["0-100"] = len(cursor.fetchall())
#         sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE (deal_price>=100 and deal_price<200) and province=%s and city=%s and district=%s and deal_year=%s '
#         cursor.execute(sql, val)
#         deal_price_range["100-200"] = len(cursor.fetchall())
#         sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE (deal_price>=200 and deal_price<300) and province=%s and city=%s and district=%s and deal_year=%s '
#         cursor.execute(sql, val)
#         deal_price_range["200-300"] = len(cursor.fetchall())
#         sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE (deal_price>=300 and deal_price<400) and province=%s and city=%s and district=%s and deal_year=%s '
#         cursor.execute(sql, val)
#         deal_price_range["300-400"] = len(cursor.fetchall())
#         sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE (deal_price>=400 and deal_price<500) and province=%s and city=%s and district=%s and deal_year=%s '
#         cursor.execute(sql, val)
#         deal_price_range["400-500"] = len(cursor.fetchall())
#         sql = 'SELECT distinct house_id FROM community natural join house natural join deal_record WHERE (deal_price>=500) and province=%s and city=%s and district=%s and deal_year=%s '
#         cursor.execute(sql, val)
#         deal_price_range["500-"] = len(cursor.fetchall())
#
#         max_room_num = [max(room_num, key=room_num.get), max(room_num.values()), max(room_num.values())/sum(room_num.values())]
#         max_deal_price_range = [max(deal_price_range, key=deal_price_range.get), max(deal_price_range.values()), max(deal_price_range.values())/sum(deal_price_range.values())]
#         # print(median_price)
#         cursor.close()
#         db.close()
#
#         return render_template("index.html", median_price=median_price, min_price=min_price, max_price=max_price,
#                                deal_month=deal_month, deal_count=deal_count,
#                                max_room_num=max_room_num, max_deal_price_range=max_deal_price_range)


# 优质房指数
# @app.route('/better', methods=['GET', 'POST'])
# def better():
#
#     if request.method == "POST":
#         db = pymysql.connect(host='127.0.0.1', user='root', passwd='xjying11', db='secondhandHouse', port=3306,
#                              charset='utf8')
#         cursor = db.cursor()
#
#         result = dict(request.form)
#
#         sql = 'SELECT SUM(deal_price), SUM(area), deal_month FROM community natural join house natural join deal_record where province=%s and city=%s and district=%s and deal_year=%s and find_in_set("南", direction) and (floor regexp "中楼层" or floor regexp "高楼层") GROUP BY deal_month ORDER BY deal_month'
#         val = (result["province"], result["city"], result["district"], result["deal_year"])
#
#         cursor.execute(sql, val)
#         data = cursor.fetchall()
#
#         num = []
#         deal_month = []
#         for i in data:
#             num.append(i[0]*10000/i[1])
#             deal_month.append(i[2])
#
#         cursor.close()
#         db.close()
#
#         return render_template("", num=num, deal_month=deal_month)


# 刚需房指数
# @app.route('/need', methods=['GET', 'POST'])
# def need():
#     if request.method == 'POST':
#         db = pymysql.connect(host='127.0.0.1', user='root', passwd='xjying11', db='secondhandHouse', port=3306,
#                              charset='utf8')
#         cursor = db.cursor()
#
#         result = dict(request.form)
#         sql = 'SELECT SUM(deal_price), SUM(area), deal_month FROM community natural join house natural join deal_record where province=%s and city=%s and district=%s and deal_year=%s and area < 80 GROUP BY deal_month ORDER BY deal_month'
#         val = (result["province"], result["city"], result["district"], result["deal_year"])
#
#         cursor.execute(sql, val)
#         data = cursor.fetchall()
#
#         num = []
#         deal_month = []
#         for i in data:
#             num.append(i[0] * 10000 / i[1])
#             deal_month.append(i[2])
#
#         cursor.close()
#         db.close()
#         return jsonify({"num": num, "deal_month": deal_month})
#         # return render_template("", num=num, deal_month=deal_month)


# 次新

# 次新
@app.route('/letter', methods=['GET', 'POST'])
def letter():
    if request.method == 'POST':
        # db = pymysql.connect(host='localhost', user='root', passwd='xjying11', db='secondhandHouse', port=3306,
        #                      charset='utf8')
        cursor = db.cursor()

        result = dict(request.form)
        print(result)
        if result['coreWhether'] == '1':
            sql = 'SELECT distinct community_name, province, city, district, unit_price FROM community WHERE (2021 - build_year >= 4 and 2021-build_year <=15 ) and district IN %s and unit_price < %s*10000 and unit_price > 0'
            val = (('天河', '越秀'), result["moneyLess"])

        else:
            sql = 'SELECT distinct community_name, province, city, district, unit_price FROM community WHERE (2021 - build_year >= 4 and 2021-build_year <=15 ) and unit_price < %s*10000 and unit_price > 0'
            val = (result["moneyLess"],)

        cursor.execute(sql, val)
        data = cursor.fetchall()

        letter_house = []
        community_name = []
        province = []
        city = []
        district = []

        for i in data:
            community_name.append(i[0])
            province.append(i[1])
            city.append(i[2])
            district.append(i[3])

            letter_house.append({
                "community_name": i[0],
                "province": i[1],
                "city": i[2],
                "district": i[3],
                "avg_price": i[4]
            })

        cursor.close()

        limit = request.form.get("limit")
        page = request.form.get("page")
        moneyLess = request.form.get("moneyLess")
        if not limit:
            limit = 10
        if not page:
            page = 1
        if moneyLess:
            # 模糊查询
            table_result = {"code": 0, "msg": None, "data": list(letter_house)}
            return jsonify(table_result)
        else:
            # 全部数据列表
            table_result = {"code": 0, "msg": None, "data": list(letter_house)}
            return jsonify(table_result)


# 3-5年涨幅最大的小区
@app.route('/up', methods=['GET', 'POST'])
def up():
    now_year = datetime.datetime.now().year
    if request.method == "POST":
        db = pymysql.connect(host='127.0.0.1', user='root', passwd='xjying11', db='secondhandHouse', port=3306,
                             charset='utf8')
        cursor = db.cursor()
        # sql = 'SELECT SUM(deal_price), SUM(area), deal_year FROM community natural join house natural join deal_record where province=%s and city=%s and district=%s and community_name=%s GROUP BY deal_year, deal_month ORDER BY deal_year, deal_month'
        sql = 'SELECT price, deal_year, community_name from community natural join up_chart_year where province=%s and city=%s and district=%s ORDER BY community_name, deal_year'

        result = dict(request.form)
        print(request.get_data())
        print(result)
        data = []
        data_up = [None] * len(data_place2)
        index = 0
        print(data_place2)
        for i in data_place2:
            val = (i[0], i[1], i[2])
            cursor.execute(sql, val)

            data_price = cursor.fetchall()
            max_up = 0
            max_up2 = 0
            if len(data_price) > 0:
                base_price = 0
                for k in range(0, len(data_price) - 1):
                    if (data_price[k][1] > int(now_year) - int(result["threeTofive"]) ):

                        if (data_price[k][2] == data_price[k + 1][2]):
                            if base_price == 0:
                                base_price = data_price[k][0]
                            if (data_price[k + 1][0] - base_price > max_up):
                                max_up = data_price[k + 1][0] - base_price
                        else:
                            if max_up > max_up2:
                                max_up2 = max_up
                                data_up[index] = {
                                    "province": i[0],
                                    "city": i[1],
                                    "district": i[2],
                                    "community_name": data_price[k][2],
                                    "upRate": "%.2f%%" % (max_up2/base_price*100),
                                    "nowPointNumber": data_price[k][0]
                                }
                                base_price = 0
                                max_up = 0
                            continue
            index += 1

        cursor.close()
        # for i in data_up:
        #     print(i)

        limit = request.form.get("limit")
        page = request.form.get("page")
        threeTofive = request.form.get("threeTofive")
        if not limit:
            limit = 10
        if not page:
            page = 1
        if threeTofive:
            # 模糊查询
            table_result = {"code": 0, "msg": None, "data": list(data_up)}
            return jsonify(table_result)
        else:
            # 全部数据列表
            table_result = {"code": 0, "msg": None, "data": list(data_up)}
            return jsonify(table_result)

        # return jsonify(data_up)


# 过去一年内还没有涨的次新小区
@app.route('/up2', methods=['GET', 'POST'])
def up2():
    now_year = datetime.datetime.now().year
    if request.method == "POST":

        db = pymysql.connect(host='127.0.0.1', user='root', passwd='xjying11', db='secondhandHouse', port=3306,
                             charset='utf8')
        cursor = db.cursor()

        result = dict(request.form)
        # print(result)
        sql = 'SELECT price, deal_month, build_year from community natural join up_chart_month where province="广东" and city="广州" and district=%s and community_name=%s and deal_year=%s and (2021 - build_year >= 4 and 2021-build_year <=15 ) ORDER BY deal_month'

        sql_community = 'SELECT distinct community_name FROM community where province="广东" and city="广州" and district=%s'
        cursor.execute(sql_community, result["tablethreeInput"])
        data_place3 = cursor.fetchall()
        data = []
        down_data = []
        for i in data_place3:
            # print(i)
            down = True
            val = (result["tablethreeInput"], i[0], now_year-1)
            cursor.execute(sql, val)

            data_price = cursor.fetchall()
            if len(data_price) > 0:
                for k in range(1, len(data_price)):
                    if (data_price[k][0] > data_price[k - 1][0]):
                        down = False
                        break
                rate = (data_price[-1][0] - data_price[0][0]) / data_price[0][0]
                if down is True and rate != 0:
                    down_data.append({
                        "province": "广东",
                        "city": "广州",
                        "district": result["tablethreeInput"],
                        "community_name": i[0],
                        # "build_year": data[0]["build_year"]
                        "build_year": 2021 - data_price[0][2],
                        "nowPointNumber": data_price[-1][0],
                        "downRate": "%.2f%%" % (rate*100)
                    })

            data.clear()

        cursor.close()
        limit = request.form.get("limit")
        page = request.form.get("page")
        tablethreeInput = request.form.get("tablethreeInput")
        if not limit:
            limit = 10
        if not page:
            page = 1
        if tablethreeInput:
            # 模糊查询
            table_result = {"code": 0, "msg": None, "data": list(down_data)}
            return jsonify(table_result)
        else:
            # 全部数据列表
            table_result = {"code": 0, "msg": None, "data": list(down_data)}
            return jsonify(table_result)

        # return jsonify(down_data2)


# 广州十个区，过去整体房价涨幅排名
@app.route('/up3', methods=['GET', 'POST'])
def up3():
    now_year = datetime.datetime.now().year
    if request.method == "POST":
        db = pymysql.connect(host='127.0.0.1', user='root', passwd='xjying11', db='secondhandHouse', port=3306,
                             charset='utf8')
        cursor = db.cursor()
        # sql = 'SELECT SUM(deal_price), SUM(area), deal_year FROM community natural join house natural join deal_record where province=%s and city=%s and district=%s and community_name=%s GROUP BY deal_year, deal_month ORDER BY deal_year, deal_month'
        sql = 'SELECT price, deal_year, district from up_chart_district where province=%s and city=%s and district=%s ORDER BY deal_year'

        data_up = [None] * len(data_place2)
        index = 0
        for i in data_place2:
            val = (i[0], i[1], i[2])
            cursor.execute(sql, val)

            data_price = cursor.fetchall()
            rate = 0
            if len(data_price) > 0:
                rate = (data_price[-1][0]-data_price[0][0])/data_price[0][0]

            data_up[index] = {
                "rate": rate,
                "province": i[0],
                "city": i[1],
                "district": i[2],
                "housePrice": data_price[-1][0]

            }
            index += 1
        data_up.sort(key=lambda k: (k.get('rate', 0)), reverse=True)

        index = 0
        for index in range(0, len(data_up)):
            data_up[index]["rate"] = "%.2f%%" % ((data_up[index]["rate"]) * 100)

        cursor.close()

        limit = request.form.get("limit")
        page = request.form.get("page")
        if not limit:
            limit = 10
        if not page:
            page = 1

        # 模糊查询
        table_result = {"code": 0, "msg": None, "data": list(data_up)}
        return jsonify(table_result)

        # return jsonify(data_up)


# 广州各个小区近三年的涨幅
@app.route('/up4', methods=['GET', 'POST'])
def up4():

    if request.method == "POST":
        now_year = datetime.datetime.now().year
        s_time = datetime.datetime.now()
        db = pymysql.connect(host='127.0.0.1', user='root', passwd='xjying11', db='secondhandHouse', port=3306,
                             charset='utf8')
        cursor = db.cursor()
        # sql = 'SELECT SUM(deal_price), SUM(area), deal_year FROM community natural join house natural join deal_record where province=%s and city=%s and district=%s and community_name=%s GROUP BY deal_year, deal_month ORDER BY deal_year, deal_month'
        sql = 'SELECT distinct price, deal_year, community_name from community natural join up_chart_year where province=%s and city=%s and district=%s ORDER BY community_name, deal_year'

        result = dict(request.form)

        data_up = []
        index = 0
        for i in data_place2:
            val = (i[0], i[1], i[2])
            cursor.execute(sql, val)

            data_price = cursor.fetchall()
            max_up = 0
            if len(data_price) > 0:
                base_price = 0
                prices = {"2019": None,
                          "2020": None,
                          "2021": None}
                rates = {}
                for k in range(0, len(data_price) - 1):
                    if (data_price[k][1] > int(now_year) - 4):
                        if (data_price[k][2] == data_price[k + 1][2]):
                            max_up = data_price[k + 1][0] - base_price
                            prices[str(data_price[k][1])] = data_price[k][0]

                        else:
                            prices[str(data_price[k][1])] = data_price[k][0]
                            if copy.deepcopy(prices)["2019"] is not None and copy.deepcopy(prices)["2020"] is not None and copy.deepcopy(prices)["2021"] is not None:
                                data_up.append({
                                    "province": i[0],
                                    "city": i[1],
                                    "district": i[2],
                                    "community_name": data_price[k][2],
                                    "year": data_price[k][1],
                                    "2019price": copy.deepcopy(prices)["2019"],
                                    "2020price": copy.deepcopy(prices)["2020"],
                                    "2021price": copy.deepcopy(prices)["2021"]
                                })
                            prices = {"2019": None,
                                      "2020": None,
                                      "2021": None}
                            continue
            # print(data_up[index])

            index += 1

        cursor.close()

        up_data2 = []
        for i in data_up:
            if i["district"] == result["TableFiveInput"]:
                up_data2.append(i)

        limit = request.form.get("limit")
        page = request.form.get("page")
        if not limit:
            limit = 10
        if not page:
            page = 1

        # 模糊查询
        table_result = {"code": 0, "msg": None, "data": list(up_data2)}
        return jsonify(table_result)


if __name__ == '__main__':

    app.run(debug=True,port=8080)


