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


class AdminUser(models.Model):
    user_name = models.CharField(max_length=45)
    password = models.CharField(max_length=32)
    name = models.CharField(max_length=15, blank=True, null=True)
    shop_id = models.IntegerField()
    shop_code = models.CharField(max_length=11)
    depart = models.CharField(max_length=45, blank=True, null=True)
    salt = models.CharField(max_length=10, blank=True, null=True)
    last_login = models.DateTimeField()
    last_ip = models.CharField(max_length=15)
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
    card_type = models.IntegerField(blank=True, null=True)
    card_nums = models.SmallIntegerField(blank=True, null=True)
    cardno_start = models.CharField(max_length=20, blank=True, null=True)
    cardno_end = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'allocation_info'


class CardInventory(models.Model):
    card_no = models.CharField(max_length=32)
    card_value = models.DecimalField(max_digits=12, decimal_places=2)
    card_status = models.CharField(max_length=1)
    card_action = models.CharField(max_length=1)
    card_addtime = models.DateTimeField()
    shop_code = models.CharField(max_length=16, blank=True, null=True)
    card_blance = models.DecimalField(max_digits=12, decimal_places=2)
    charge_time = models.DateTimeField(blank=True, null=True)
    order_sn = models.CharField(max_length=32, blank=True, null=True)
    sheetid = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'card_inventory'


class CardReceive(models.Model):
    shop_code = models.CharField(max_length=16)
    rec_sn = models.CharField(max_length=45)
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


class Departs(models.Model):
    depart_id = models.CharField(max_length=10)
    depart_name = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'departs'


class DiscountRate(models.Model):
    shopcode = models.CharField(max_length=16)
    val_min = models.DecimalField(max_digits=12, decimal_places=2)
    val_max = models.DecimalField(max_digits=12, decimal_places=2)
    discount_rate = models.DecimalField(max_digits=6, decimal_places=2)

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


class OrderChangeCard(models.Model):
    order_sn = models.CharField(max_length=20)
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

    class Meta:
        managed = False
        db_table = 'order_change_card'


class OrderChangeCardInfo(models.Model):
    order_sn = models.CharField(max_length=32)
    card_no = models.CharField(max_length=32)
    card_attr = models.CharField(max_length=1, blank=True, null=True)
    card_value = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    card_balance = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    add_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'order_change_card_info'


class OrderInfo(models.Model):
    order_id = models.IntegerField()
    card_id = models.IntegerField()
    card_balance = models.DecimalField(max_digits=11, decimal_places=2)
    card_action = models.CharField(max_length=1)
    card_attr = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'order_info'


class OrderPaymentInfo(models.Model):
    order_id = models.IntegerField()
    pay_id = models.IntegerField()
    pay_value = models.DecimalField(max_digits=11, decimal_places=2)
    remarks = models.TextField(blank=True, null=True)
    is_pay = models.CharField(max_length=1, blank=True, null=True)
    change_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_payment_info'


class OrderUpCard(models.Model):
    order_sn = models.CharField(max_length=20)
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
    card_value = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    card_balance = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    created_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_up_card_info'


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
    y_cash = models.DecimalField(max_digits=11, decimal_places=0, blank=True, null=True)
    diff_price = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    discount_rate = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'orders'


class Payment(models.Model):
    payment_name = models.CharField(max_length=60)

    class Meta:
        managed = False
        db_table = 'payment'


class ReceiveInfo(models.Model):
    rec_id = models.IntegerField()
    card_value = models.IntegerField()
    card_nums = models.IntegerField()
    card_id_start = models.CharField(max_length=32)
    card_id_end = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = 'receive_info'


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

    class Meta:
        managed = False
        db_table = 'shops'
