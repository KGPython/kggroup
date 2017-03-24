# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.db import models


class ActionLog(models.Model):
    id = models.BigIntegerField(primary_key=True)
    action = models.CharField(max_length=45, blank=True, null=True)
    url = models.CharField(max_length=100, blank=True, null=True)
    u_name = models.CharField(max_length=45)
    cards_in = models.TextField(blank=True, null=True)
    cards_out = models.TextField(blank=True, null=True)
    err_msg = models.TextField(blank=True, null=True)
    add_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'action_log'


class AdminUser(models.Model):
    user_name = models.CharField(max_length=45)
    password = models.CharField(max_length=32)
    name = models.CharField(max_length=15, blank=True, null=True)
    shop_id = models.IntegerField(blank=True, null=True)
    shop_code = models.CharField(max_length=11, blank=True, null=True)
    depart = models.CharField(max_length=45, blank=True, null=True)
    salt = models.CharField(max_length=10, blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    last_ip = models.CharField(max_length=15,blank=True, null=True)
    role_id = models.CharField(max_length=11)

    class Meta:
        managed = False
        db_table = 'admin_user'


class Allocation(models.Model):
    order_sn = models.CharField(max_length=20)
    shopin_code = models.CharField(max_length=16, blank=True, null=True)
    shopout_code = models.CharField(max_length=16, blank=True, null=True)
    total_num = models.SmallIntegerField(blank=True, null=True)
    total_value = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    add_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'allocation'


class AllocationInfo(models.Model):
    order_sn = models.CharField(max_length=20)
    card_type = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    card_nums = models.SmallIntegerField(blank=True, null=True)
    cardno_start = models.CharField(max_length=20, blank=True, null=True)
    cardno_end = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'allocation_info'


class CardInventory(models.Model):
    card_no = models.CharField(unique=True, max_length=32)
    card_value = models.CharField(max_length=12)
    card_status = models.CharField(max_length=1)
    card_action = models.CharField(max_length=1)
    card_addtime = models.DateTimeField()
    shop_code = models.CharField(max_length=16, blank=True, null=True)
    card_blance = models.DecimalField(max_digits=12, decimal_places=2)
    charge_time = models.DateTimeField(blank=True, null=True)
    order_sn = models.CharField(max_length=32, blank=True, null=True)
    sheetid = models.CharField(max_length=32, blank=True, null=True)
    is_store = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'card_inventory'

class CardReceive(models.Model):
    shop_code = models.CharField(max_length=16)
    rec_sn = models.CharField(max_length=20)
    rec_name = models.CharField(max_length=60)
    add_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'card_receive'


class CardType(models.Model):
    card_type_name = models.CharField(max_length=12)

    class Meta:
        managed = False
        db_table = 'card_type'


class CashierAuthorization(models.Model):
    license = models.CharField(db_column='License', max_length=19, blank=True, null=True)  # Field name made lowercase.
    mac = models.CharField(db_column='Mac', max_length=17, blank=True, null=True)  # Field name made lowercase.
    md5 = models.CharField(db_column='MD5', max_length=32, blank=True, null=True)  # Field name made lowercase.
    shop = models.CharField(db_column='Shop', max_length=4, blank=True, null=True)  # Field name made lowercase.
    cashier = models.CharField(db_column='Cashier', max_length=10, blank=True, null=True)  # Field name made lowercase.
    state = models.CharField(db_column='State', max_length=1, blank=True, null=True)  # Field name made lowercase.
    effective = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cashier_authorization'


class CashierList(models.Model):
    username = models.CharField(max_length=32, blank=True, null=True)
    password = models.CharField(max_length=64, blank=True, null=True)
    pass_field = models.CharField(db_column='pass', max_length=6, blank=True, null=True)  # Field renamed because it was a Python reserved word.
    name = models.CharField(max_length=255, blank=True, null=True)
    shop_code = models.CharField(max_length=4, blank=True, null=True)
    login_cashier = models.CharField(db_column='login_Cashier', max_length=4, blank=True, null=True)  # Field name made lowercase.
    satate = models.CharField(max_length=1, blank=True, null=True)
    effective = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cashier_list'


class CashierLog(models.Model):
    uid = models.CharField(max_length=10, blank=True, null=True)
    sid = models.CharField(max_length=10, blank=True, null=True)
    cid = models.CharField(max_length=10, blank=True, null=True)
    card_no = models.CharField(max_length=255, blank=True, null=True)
    card_shop = models.CharField(max_length=10, blank=True, null=True)
    card_value = models.CharField(max_length=10, blank=True, null=True)
    card_blance = models.CharField(max_length=10, blank=True, null=True)
    coutent = models.TextField(blank=True, null=True)
    time = models.CharField(max_length=255, blank=True, null=True)
    addtime = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'cashier_log'


class CashierOrder(models.Model):
    uid = models.CharField(max_length=10, blank=True, null=True)
    sid = models.CharField(max_length=10, blank=True, null=True)
    cid = models.CharField(max_length=10, blank=True, null=True)
    card_no = models.CharField(max_length=255, blank=True, null=True)
    card_shop = models.CharField(max_length=10, blank=True, null=True)
    card_value = models.CharField(max_length=10, blank=True, null=True)
    card_blance = models.CharField(max_length=10, blank=True, null=True)
    coutent = models.TextField(blank=True, null=True)
    time = models.CharField(max_length=255, blank=True, null=True)
    addtime = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'cashier_order'


class Departs(models.Model):
    depart_id = models.CharField(max_length=10)
    depart_name = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'departs'


class DisCode(models.Model):
    dis_code = models.CharField(max_length=10, blank=True, null=True)
    shopcode = models.CharField(max_length=16, blank=True, null=True)
    flag = models.CharField(max_length=1)
    change_time = models.DateTimeField(blank=True, null=True)
    order_sn = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dis_code'


class DiscountRate(models.Model):
    shopcode = models.CharField(max_length=16)
    val_min = models.DecimalField(max_digits=12, decimal_places=2)
    val_max = models.DecimalField(max_digits=12, decimal_places=2)
    discount_rate = models.DecimalField(max_digits=6, decimal_places=4)

    class Meta:
        managed = False
        db_table = 'discount_rate'


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class ExchangeCode(models.Model):
    cost = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    code = models.CharField(max_length=45, blank=True, null=True)
    camilo = models.CharField(max_length=45, blank=True, null=True)
    plat = models.CharField(max_length=1, blank=True, null=True)
    add_time = models.DateTimeField(blank=True, null=True)
    exchange_time = models.DateTimeField(blank=True, null=True)
    shop_code = models.CharField(max_length=16, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'exchange_code'


class KfJobsCoupon(models.Model):
    coupon_code = models.CharField(max_length=255)
    coupon_name = models.CharField(max_length=255)
    batch = models.IntegerField()
    shop_code = models.CharField(max_length=255)
    type = models.IntegerField()
    values = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    range = models.CharField(max_length=255)
    payment_type = models.IntegerField()
    pay_account = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    credit_account = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    amount = models.IntegerField()
    print_amount = models.IntegerField(blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    remark = models.CharField(max_length=400, blank=True, null=True)
    create_uesr_id = models.IntegerField(blank=True, null=True)
    create_user_name = models.CharField(max_length=255, blank=True, null=True)
    create_date = models.CharField(max_length=8, blank=True, null=True)
    start_sn = models.CharField(max_length=255, blank=True, null=True)
    end_sn = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'kf_jobs_coupon'


class KfJobsCouponBatch(models.Model):
    batch = models.IntegerField()
    shopid = models.CharField(db_column='shopID', max_length=255, blank=True, null=True)  # Field name made lowercase.
    createdate = models.CharField(max_length=8, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'kf_jobs_coupon_batch'


class KfJobsCouponCredit(models.Model):
    coupon_code = models.CharField(max_length=255, blank=True, null=True)
    payment_type = models.IntegerField(blank=True, null=True)
    pay_account = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    create_uesr_id = models.IntegerField(blank=True, null=True)
    create_user_name = models.CharField(max_length=255, blank=True, null=True)
    create_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'kf_jobs_coupon_credit'


class KfJobsCouponGoodsDetail(models.Model):
    batch = models.CharField(max_length=255)
    goodname = models.CharField(max_length=255, blank=True, null=True)
    goodcode = models.CharField(max_length=255, blank=True, null=True)
    amount = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'kf_jobs_coupon_goods_detail'


class KfJobsCouponOld(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    couponname = models.CharField(db_column='CouponName', max_length=255)  # Field name made lowercase.
    batch = models.CharField(max_length=255)
    shopid = models.CharField(db_column='ShopID', max_length=10)  # Field name made lowercase.
    couponno = models.CharField(db_column='CouponNO', max_length=19)  # Field name made lowercase.
    coupontypeid = models.IntegerField(db_column='CouponTypeID')  # Field name made lowercase.
    startdate = models.DateTimeField(db_column='StartDate')  # Field name made lowercase.
    enddate = models.DateTimeField(db_column='EndDate')  # Field name made lowercase.
    cpwdflag = models.IntegerField(db_column='CPwdFlag')  # Field name made lowercase.
    cpwd = models.CharField(db_column='CPwd', max_length=32, blank=True, null=True)  # Field name made lowercase.
    usetime = models.IntegerField(db_column='UseTime')  # Field name made lowercase.
    maxusetime = models.IntegerField(db_column='MaxUseTime')  # Field name made lowercase.
    value = models.DecimalField(db_column='Value', max_digits=12, decimal_places=3)  # Field name made lowercase.
    giftvalue = models.DecimalField(db_column='GiftValue', max_digits=12, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    discount = models.IntegerField(db_column='Discount')  # Field name made lowercase.
    flag = models.IntegerField(db_column='Flag')  # Field name made lowercase.
    fromsheettype = models.IntegerField(db_column='FromSheetType', blank=True, null=True)  # Field name made lowercase.
    rangeremark = models.CharField(db_column='RangeRemark', max_length=400, blank=True, null=True)  # Field name made lowercase.
    createuserid = models.CharField(db_column='CreateUserID', max_length=10)  # Field name made lowercase.
    updateuserid = models.CharField(db_column='UpdateUserID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    updatetime = models.DateTimeField(db_column='UpdateTime', blank=True, null=True)  # Field name made lowercase.
    fromsheetid = models.CharField(db_column='FromSheetID', max_length=20, blank=True, null=True)  # Field name made lowercase.
    fromsdate = models.CharField(db_column='FromSDate', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    fromlistno = models.CharField(db_column='FromListNO', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    fromposid = models.CharField(db_column='FromPOSID', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    serialid = models.CharField(db_column='SerialID', max_length=20)  # Field name made lowercase.
    clearflag = models.IntegerField(db_column='ClearFlag')  # Field name made lowercase.
    clearvalue = models.DecimalField(db_column='ClearValue', max_digits=12, decimal_places=3)  # Field name made lowercase.
    clearshopid = models.CharField(db_column='ClearShopID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    clearsheettype = models.IntegerField(db_column='ClearSheetType', blank=True, null=True)  # Field name made lowercase.
    clearsheetid = models.CharField(db_column='ClearSheetID', max_length=16, blank=True, null=True)  # Field name made lowercase.
    clearsdate = models.CharField(db_column='ClearSDate', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    clearlistno = models.CharField(db_column='ClearListNO', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    clearposid = models.CharField(db_column='ClearPOSID', max_length=1000, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'kf_jobs_coupon_old'


class KfJobsCouponSn(models.Model):
    sn = models.CharField(max_length=6)
    batch = models.CharField(max_length=3)
    voucher = models.CharField(max_length=13)
    salt = models.CharField(max_length=16)
    result = models.CharField(max_length=32)
    request_shop = models.CharField(max_length=255, blank=True, null=True)
    request_name = models.CharField(max_length=255, blank=True, null=True)
    request_date = models.DateTimeField(blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    coupon_code = models.CharField(max_length=255, blank=True, null=True)
    serial_id = models.CharField(max_length=20, blank=True, null=True)
    used_flag = models.IntegerField(blank=True, null=True)
    used_shop = models.CharField(max_length=255, blank=True, null=True)
    used_name = models.CharField(max_length=255, blank=True, null=True)
    used_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'kf_jobs_coupon_sn'


class NavList(models.Model):
    nav_id = models.CharField(max_length=32)
    nav_name = models.CharField(max_length=45)
    parent_id = models.CharField(max_length=32)
    url = models.CharField(max_length=120)
    icon = models.CharField(max_length=16, blank=True, null=True)
    sort_id = models.IntegerField()
    flag = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'nav_list'


class OrderBorrow(models.Model):
    order_sn = models.CharField(unique=True, max_length=20)
    order_val = models.DecimalField(max_digits=11, decimal_places=2)
    order_num = models.IntegerField()
    shopcode = models.CharField(max_length=16)
    operator = models.SmallIntegerField()
    borrow_depart = models.CharField(max_length=10)
    borrow_depart_code = models.CharField(max_length=12)
    borrow_name = models.CharField(max_length=12)
    borrow_phone = models.CharField(max_length=12)
    add_time = models.DateTimeField()
    is_paid = models.CharField(max_length=1)
    paid_time = models.DateTimeField(blank=True, null=True)
    reply_order = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_borrow'


class OrderBorrowInfo(models.Model):
    order_sn = models.CharField(max_length=20, blank=True, null=True)
    card_no = models.CharField(max_length=20, blank=True, null=True)
    card_type = models.CharField(max_length=12, blank=True, null=True)
    card_balance = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    is_back = models.CharField(max_length=1, blank=True, null=True)
    back_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_borrow_info'


class OrderChangeCard(models.Model):
    order_sn = models.CharField(unique=True, max_length=20)
    operator_id = models.SmallIntegerField()
    depart = models.CharField(max_length=10, blank=True, null=True)
    shop_code = models.CharField(max_length=16)
    action_type = models.CharField(max_length=1, blank=True, null=True)
    user_name = models.CharField(max_length=32, blank=True, null=True)
    user_phone = models.CharField(max_length=16, blank=True, null=True)
    total_in_amount = models.IntegerField(blank=True, null=True)
    total_in_price = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    total_out_amount = models.IntegerField(blank=True, null=True)
    total_out_price = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    add_time = models.DateTimeField()
    disc_rate = models.DecimalField(max_digits=11, decimal_places=4, blank=True, null=True)
    disc = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    disc_pay = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    disc_cash = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_change_card'


class OrderChangeCardInfo(models.Model):
    order_sn = models.CharField(max_length=20)
    card_no = models.CharField(max_length=32)
    card_attr = models.CharField(max_length=1, blank=True, null=True)
    card_value = models.CharField(max_length=12, blank=True, null=True)
    card_balance = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    type = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_change_card_info'
        unique_together = (('order_sn', 'card_no'),)


class OrderChangeCardPayment(models.Model):
    order_id = models.CharField(max_length=20)
    pay_id = models.IntegerField()
    pay_value = models.DecimalField(max_digits=11, decimal_places=2)
    remarks = models.TextField(blank=True, null=True)
    is_pay = models.CharField(max_length=1, blank=True, null=True)
    change_time = models.DateTimeField(blank=True, null=True)
    bank_name = models.CharField(max_length=12, blank=True, null=True)
    bank_sn = models.CharField(max_length=25, blank=True, null=True)
    pay_company = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_change_card_payment'


class OrderInfo(models.Model):
    order_id = models.CharField(max_length=20)
    card_id = models.CharField(max_length=32)
    card_balance = models.DecimalField(max_digits=11, decimal_places=2)
    card_action = models.CharField(max_length=1)
    card_attr = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'order_info'

class Payment(models.Model):
    payment_name = models.CharField(max_length=60)
    flag = models.CharField(max_length=255)
    dis_rate = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payment'


class OrderPaymentInfo(models.Model):
    # order_id = models.CharField(max_length=20)
    # pay_id = models.IntegerField()
    order = models.ForeignKey('Orders',to_field='order_sn')
    pay = models.ForeignKey('Payment',related_name='pay_set')
    pay_value = models.DecimalField(max_digits=11, decimal_places=2)
    remarks = models.TextField(blank=True, null=True)
    is_pay = models.CharField(max_length=1, blank=True, null=True)
    change_time = models.DateTimeField(blank=True, null=True)
    bank_name = models.CharField(max_length=12, blank=True, null=True)
    bank_sn = models.CharField(max_length=25, blank=True, null=True)
    pay_company = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_payment_info'

# class OrderPaymentInfo(models.Model):
#     order_id = models.CharField(max_length=20)
#     # pay_id = models.IntegerField()
#     pay_id = models.ForeignKey(Payment)
#     pay_value = models.DecimalField(max_digits=11, decimal_places=2)
#     remarks = models.TextField(blank=True, null=True)
#     is_pay = models.CharField(max_length=1, blank=True, null=True)
#     change_time = models.DateTimeField(blank=True, null=True)
#     bank_name = models.CharField(max_length=12, blank=True, null=True)
#     bank_sn = models.CharField(max_length=25, blank=True, null=True)
#     pay_company = models.CharField(max_length=15, blank=True, null=True)
#
#     class Meta:
#         managed = False
#         db_table = 'order_payment_info'


class OrderUpCard(models.Model):
    order_sn = models.CharField(unique=True, max_length=20)
    action_type = models.CharField(max_length=1)
    total_amount = models.IntegerField(blank=True, null=True)
    total_price = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    fill_amount = models.IntegerField(blank=True, null=True)
    fill_price = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    diff_price = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    user_name = models.CharField(max_length=32, blank=True, null=True)
    user_phone = models.CharField(max_length=16, blank=True, null=True)
    state = models.SmallIntegerField(blank=True, null=True)
    shop_code = models.CharField(max_length=16)
    operator_id = models.IntegerField(blank=True, null=True)
    depart = models.CharField(max_length=10, blank=True, null=True)
    created_id = models.IntegerField(blank=True, null=True)
    add_time = models.DateTimeField(blank=True, null=True)
    modified_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_up_card'


class OrderUpCardInfo(models.Model):
    order_sn = models.CharField(max_length=20)
    card_no = models.CharField(max_length=32)
    card_attr = models.CharField(max_length=1)
    card_value = models.CharField(max_length=12, blank=True, null=True)
    card_balance = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    created_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_up_card_info'
        unique_together = (('order_sn', 'card_no'),)


class Orders(models.Model):
    order_sn = models.CharField(unique=True, max_length=20)
    operator_id = models.SmallIntegerField()
    depart = models.CharField(max_length=10, blank=True, null=True)
    shop_code = models.CharField(max_length=16, blank=True, null=True)
    action_type = models.CharField(max_length=1)
    total_amount = models.DecimalField(max_digits=11, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=11, decimal_places=2)
    disc_amount = models.DecimalField(max_digits=11, decimal_places=2)
    buyer_name = models.CharField(max_length=45, blank=True, null=True)
    buyer_tel = models.CharField(max_length=11, blank=True, null=True)
    buyer_company = models.CharField(max_length=60, blank=True, null=True)
    add_time = models.DateTimeField()
    y_cash = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    diff_price = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    discount_rate = models.DecimalField(max_digits=6, decimal_places=4, blank=True, null=True)
    remark = models.TextField(blank=True, null=True)
    print_num = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'orders'

class OrderErr(models.Model):
    order_sn = models.CharField(max_length=20)
    record = models.CharField(max_length=255)
    u_id = models.IntegerField()
    shop = models.CharField(max_length=16)
    c_time = models.DateField()
    type = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'order_err'






class PrintExplain(models.Model):
    order_sn = models.CharField(max_length=20)
    remark = models.TextField()

    class Meta:
        managed = False
        db_table = 'print_explain'


class ReceiveInfo(models.Model):
    rec_id = models.CharField(max_length=20)
    card_value = models.CharField(max_length=12)
    card_nums = models.IntegerField()
    card_id_start = models.CharField(max_length=32)
    card_id_end = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = 'receive_info'
        unique_together = (('card_id_start', 'card_id_end'),)


class Role(models.Model):
    role_name = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'role'


class RoleNav(models.Model):
    id = models.BigIntegerField(primary_key=True)
    role_id = models.IntegerField(blank=True, null=True)
    nav_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'role_nav'


class Shops(models.Model):
    id = models.IntegerField(primary_key=True)
    shop_name = models.CharField(max_length=60)
    shop_code = models.CharField(max_length=16, blank=True, null=True)
    tel = models.CharField(max_length=12, blank=True, null=True)
    disc_level = models.CharField(max_length=1, blank=True, null=True)
    city = models.CharField(max_length=12, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'shops'

class Vip(models.Model):
    company = models.CharField(max_length=50, blank=True, null=True)
    person = models.CharField(max_length=15, blank=True, null=True)
    tel = models.CharField(max_length=11, blank=True, null=True)
    add_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'vip'


class VipBank(models.Model):
    id = models.BigIntegerField(primary_key=True)
    vip_id = models.IntegerField()
    bank_name = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vip_bank'