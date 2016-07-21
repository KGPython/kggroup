# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.
#-*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class AdminUser(models.Model):
    user_name = models.CharField(max_length=45)
    password = models.CharField(max_length=32)
    salt = models.CharField(max_length=10, blank=True, null=True)
    last_login = models.DateTimeField()
    last_ip = models.CharField(max_length=15)
    role_id = models.CharField(max_length=11)
    shop_id = models.CharField(max_length=11)

    class Meta:
        managed = False
        db_table = 'admin_user'


class CardInventory(models.Model):
    card_no = models.CharField(max_length=32)
    card_value = models.IntegerField()
    card_status = models.CharField(max_length=1)
    card_action = models.CharField(max_length=1)
    card_addtime = models.DateTimeField()
    shop_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'card_inventory'


class CardReceive(models.Model):
    shop_id = models.IntegerField()
    rec_sn = models.CharField(max_length=45)
    rec_name = models.CharField(max_length=60)
    total = models.IntegerField()
    add_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'card_receive'


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


class NavList(models.Model):
    nav_id = models.CharField(max_length=32)
    nav_name = models.CharField(max_length=45)
    parent_id = models.CharField(max_length=32)
    url = models.CharField(max_length=120)
    icon = models.CharField(max_length=16)
    sort_id = models.IntegerField()
    flag = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'nav_list'


class OrderInfo(models.Model):
    order_id = models.IntegerField()
    card_id = models.IntegerField()
    card_balance = models.IntegerField()
    card_action = models.CharField(max_length=1)
    is_give = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'order_info'


class OrderPaymentInfo(models.Model):
    order_id = models.IntegerField()
    pay_id = models.IntegerField()
    pay_value = models.IntegerField()
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_payment_info'


class Orders(models.Model):
    order_sn = models.CharField(max_length=20)
    user_id = models.SmallIntegerField()
    shop_id = models.IntegerField()
    action_type = models.CharField(max_length=1)
    total_amount = models.IntegerField()
    paid_amount = models.IntegerField()
    disc_amount = models.IntegerField()
    buyer_name = models.CharField(max_length=45, blank=True, null=True)
    buyer_tel = models.CharField(max_length=11, blank=True, null=True)
    buyer_company = models.CharField(max_length=60, blank=True, null=True)
    add_time = models.DateTimeField()
    order_status = models.IntegerField(blank=True, null=True)
    diff_price = models.IntegerField(blank=True, null=True)

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
    user_type = models.CharField(max_length=45)
    shop_id = models.IntegerField()

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


# class CompressedTextField(models.TextField):
#     """
#     转化数据库中的字符到python的变量
#     """
#
#     def from_db_value(self, value, expression, connection, context):
#         if not value:
#             return value
#         try:
#             return value.decode('base64').decode('bz2').decode('utf-8')
#         except Exception:
#             return value
#
#     def to_python(self, value):
#         if not value:
#             return value
#         try:
#             return value.decode('base64').decode('bz2').decode('utf-8')
#         except Exception:
#             return value
#
#
#     def get_prep_value(self, value):
#         if not value:
#             return value
#         try:
#             value.decode('base64')
#             return value
#         except Exception:
#             try:
#                 return value.encode('utf-8').encode('bz2').encode('base64')
#             except Exception:
#                 # return value
