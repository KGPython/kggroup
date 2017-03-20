from sellcard.models import OrderPaymentInfo

# Create your tests here.
def test():
    data = OrderPaymentInfo.objects.get(id=10)
    print(data)

test()


