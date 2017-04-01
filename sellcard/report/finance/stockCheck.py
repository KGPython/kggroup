#-*- coding:utf-8 -*-
from django.shortcuts import render
import datetime

from sellcard.common import Method as mth
def index(request):
    role_id = request.session.get('s_roleid')
    shop = request.session.get('s_shopcode')
    role = request.session.get('s_roleid')
    user = request.session.get('s_uid')

    if request.method == 'POST':
        start = request.POST.get('start','')
        end = request.POST.get('end','')
        endTime = str(datetime.datetime.strptime(end,'%Y-%m-%d').date() + datetime.timedelta(1))
        conn = mth.getMysqlConn()
        cur = conn.cursor()
        whereStr ="WHERE 1 = 1 "

        if role in ('2','10') :
            whereStr += " AND s.shop_code ='"+shop+"'"

        shopsCode= ''
        if role_id == '9':
            shopsCode = mth.getCityShopsCode('T')
            shopsCodeStr = "'" + "','".join(shopsCode) + "'"
            whereStr += " AND s.shop_code IN (" + shopsCodeStr + ")"
        if role_id == '8':
            shopsCode = mth.getCityShopsCode('C')
            shopsCodeStr = "'" + "','".join(shopsCode) + "'"
            whereStr += " AND s.shop_code IN (" + shopsCodeStr + ")"


        sql = """
SELECT
	s.shop_name,
	IFNULL(u.initial_stock, 0) AS initial_stock,
	IFNULL(v.period_stock, 0) AS period_stock,
	IFNULL(w.cash, 0) AS cash,
	IFNULL(w.pos, 0) AS pos,
	IFNULL(w.remittance, 0) AS remittance,
	IFNULL(w.voucher, 0) AS voucher,
	IFNULL(w.third_party, 0) AS third_party,
	IFNULL(x.borrow_already, 0) AS borrow_already,
	IFNULL(y.hang_sale, 0) AS hang_sale,
	IFNULL(z.disc, 0) AS disc,
	IFNULL(h.end_stock, 0) AS end_stock,
	IFNULL(i.borrow_not, 0) AS borrow_not,
	IFNULL(j.credit_not, 0) AS credit_not
FROM
	shops s
LEFT JOIN (
	SELECT
		a.shop_code,
		sum(a.card_value) AS initial_stock
	FROM
		card_inventory a
	WHERE
		a.card_addtime < '"""+start+"""'
	GROUP BY
		a.shop_code
) u ON s.shop_code = u.shop_code
LEFT JOIN (
	SELECT
		a.shop_code,
		sum(a.card_value) AS period_stock
	FROM
		card_inventory a
	WHERE
		a.card_addtime >= '"""+start+"""'
	AND a.card_addtime < '"""+endTime+"""'
	GROUP BY
		a.shop_code
) v ON s.shop_code = v.shop_code
LEFT JOIN (
	SELECT
		m.shop_code,
		sum(
			CASE
			WHEN m.pay_id = 1 THEN
				m.pay_value
			ELSE
				0
			END
		) AS cash,
		sum(
			CASE
			WHEN m.pay_id = 5 THEN
				m.pay_value
			ELSE
				0
			END
		) AS pos,
		sum(
			CASE
			WHEN m.pay_id = 3 THEN
				m.pay_value
			ELSE
				0
			END
		) AS remittance,
		sum(
			CASE
			WHEN m.pay_id = 2 THEN
				m.pay_value
			ELSE
				0
			END
		) AS voucher,
		sum(
			CASE
			WHEN m.pay_id in (6, 7, 8, 9, 10, 11) THEN
				m.pay_value
			ELSE
				0
			END
		) AS third_party
	FROM
		(
			SELECT
				a.shop_code,
				b.pay_id,
				b.pay_value
			FROM
				orders a,
				order_payment_info b
			WHERE
				a.order_sn = b.order_id
			AND a.add_time >= '"""+start+"""'
			AND a.add_time < '"""+endTime+"""'
			AND b.is_pay = '1'
			AND a.action_type IN ('1', '2')
			UNION ALL
				SELECT
					a.shop_code,
					b.pay_id,
					b.pay_value
				FROM
					order_change_card a,
					order_change_card_payment b
				WHERE
					a.order_sn = b.order_id
				AND a.add_time >= '"""+start+"""'
				AND a.add_time < '"""+endTime+"""'
				AND b.is_pay = '1'
				UNION ALL
					SELECT
						a.shop_code,
						1 AS pay_id,
						a.total_price AS pay_value
					FROM
						order_up_card a
					WHERE
						a.add_time >= '"""+start+"""'
					AND a.add_time < '"""+endTime+"""'
		) m
	GROUP BY
		m.shop_code
) w ON s.shop_code = w.shop_code
LEFT JOIN (
	SELECT
		a.shop_code,
		sum(a.total_amount) AS borrow_already
	FROM
		orders a
	WHERE
		a.add_time >= '"""+start+"""'
	AND a.add_time < '"""+endTime+"""'
	AND a.action_type = '3'
	GROUP BY
		a.shop_code
) x ON s.shop_code = x.shop_code
LEFT JOIN (
	SELECT
		a.shop_code,
		sum(a.total_amount) AS hang_sale
	FROM
		orders a
	WHERE
		a.add_time >= '"""+start+"""'
	AND a.add_time < '"""+endTime+"""'
	AND a.action_type = '6'
	GROUP BY
		a.shop_code
) y ON s.shop_code = y.shop_code
LEFT JOIN (
	SELECT
		n.shop_code,
		sum(n.disc) AS disc
	FROM
		(
			SELECT
				a.shop_code,
				a.disc_amount AS disc
			FROM
				orders a
			WHERE
				a.add_time >= '"""+start+"""'
			AND a.add_time < '"""+endTime+"""'
			AND a.action_type IN ('1', '2', '3', '6')
			UNION ALL
				SELECT
					a.shop_code,
					a.disc
				FROM
					order_change_card a
				WHERE
					a.add_time >= '"""+start+"""'
				AND a.add_time < '"""+endTime+"""'
				UNION ALL
					SELECT
						a.shop_code,
						a.total_amount AS disc
					FROM
						orders a
					WHERE
						a.add_time >= '"""+start+"""'
					AND a.add_time < '"""+endTime+"""'
					AND a.action_type = '5'
		) n
	GROUP BY
		n.shop_code
) z ON s.shop_code = z.shop_code
LEFT JOIN (
	SELECT
		a.shop_code,
		sum(a.card_value) AS end_stock
	FROM
		card_inventory a
	WHERE
		a.card_status = '1'
	GROUP BY
		a.shop_code
) h ON s.shop_code = h.shop_code
LEFT JOIN (
	SELECT
		a.shopcode AS shop_code,
		sum(a.order_val) AS borrow_not
	FROM
		order_borrow a
	WHERE
		a.add_time >= '"""+start+"""'
	AND a.add_time < '"""+endTime+"""'
	AND a.is_paid = '0'
	GROUP BY
		a.shopcode
) i ON s.shop_code = i.shop_code
LEFT JOIN (
	SELECT
		k.shop_code,
		sum(k.pay_value) AS credit_not
	FROM
		(
			SELECT
				a.shop_code,
				b.pay_value
			FROM
				orders a,
				order_payment_info b
			WHERE
				a.order_sn = b.order_id
			AND a.add_time >= '"""+start+"""'
			AND a.add_time < '"""+endTime+"""'
			AND b.is_pay = '0'
			AND b.pay_id = 4
			AND a.action_type IN ('1', '2')
			UNION ALL
				SELECT
					a.shop_code,
					b.pay_value
				FROM
					order_change_card a,
					order_change_card_payment b
				WHERE
					a.order_sn = b.order_id
				AND a.add_time >= '"""+start+"""'
				AND a.add_time < '"""+endTime+"""'
				AND b.is_pay = '0'
				AND b.pay_id = 4
		) k
	GROUP BY
		k.shop_code
) j ON s.shop_code = j.shop_code
"""+whereStr+"""
ORDER BY
	s.shop_code
        """
        cur.execute(sql)
        List = cur.fetchall()

        # nopay = """+start+"""
        #
        # cur.execute(nopay)
        # nopayDict = cur.fetchone()
        #
        # payTotal = 0.00
        # for row in List:
        #     payTotal += float(row['pay_value'])
    return render(request, 'report/finance/stockCheck.html', locals())
