function checkPayError(payId,payIdList,payCash) {
    var payList1 = ['7','8','10','11'];
    var payList2 = ['3','4'];
    res = false;
    if (payList1.indexOf(payId) > 0) {
        if (payIdList.indexOf('1') >= 0 || payIdList.indexOf('2') >= 0 || payIdList.indexOf('3') >= 0 || payIdList.indexOf('4') >= 0 || payIdList.indexOf('5') >= 0) {
            res = true;
        }
    } else if (payId == 6) {//移动积分
        if (payCash >= DISC_RATES[0].val_min) {
            res = true;
        }
    }else if(payList2.indexOf(payId) >= 0){
        if(payIdList.indexOf('3') >= 0 || payIdList.indexOf('4') >= 0){
            res = true;
        }
    }
    return res;
}

/*
* 计算返点金额
* cardSaleTotalVal：cardSaleTotalVal：售卡总金额
* posVal：pos刷卡金额
* */
function changeDiscValByPos(cardSaleTotalVal,posVal) {
    if(cardSaleTotalVal-posVal>=DISC_RATES[0].val_min){
        setTotalBycardSaleTotalVal('',cardSaleTotalVal)
    }else{
        //4、优惠金额清零
        $('.Total #discountVal b').text(0);
        //5、优惠补差清零
        $('.Total #totalYBalance b').text(0);
        $('.Total #discount input').val(0);
        //6、设置订单应付金额 = 售卡列表合计金额 + 优惠补差
        $('.Total #totalPaid b').text(cardSaleTotalVal);
        $('.discBox').hide();
    }
}


//支付列表，三方平台切换
$(document).on('change','.payList #parter',function(){
    var val = $(this).val();
    var parentTr = $(this).parent().parent();
    $(parentTr).find('td').eq(0).find('input').val(val);
});
//支付方式--银行打款
/*var posVal = 0;
$(document).on('change','.payList #blank',function(){
    var val = $(this).val();
    var parentTr = $(this).parent().parent();
    $(parentTr).find('td').eq(0).find('input').val(val);
});*/



function changeDiscValByPayment(cardSaleTotalVal,Val,discRate) {
     $('.Total-discInfo').hide();
    //设置折扣率
    $('.Total #discount input').val(discRate*100);
    //设置折扣金额
    var discountVal = parseFloat(Val*discRate).toFixed(2);
    $('.Total #discountVal b').text(discountVal);
    //设置优惠补差
    $('.Total #totalYBalance b').text(0);
    //设置应付
    $('.Total #totalPaid b').text(cardSaleTotalVal);
    //设置优惠返现
    $('.discountTotal #Ycash').val(discountVal);
    $('#YcardList').empty();
    $(".discBox").hide();
}


function changeDiscValByPayment2(cardSaleTotalVal,Val,discRate) {
    $('.Total-discInfo').show();
    //计算折扣金额
    $('.Total #discount input').val(discRate*100);
    var discountVal = parseFloat(Val*discRate).toFixed(2);
    $('.Total #discountVal b').text(discountVal);
    //优惠补差
    $('.Total #totalYBalance b').text(0);
    //应付金额
    $('.Total #totalPaid b').text(cardSaleTotalVal);
    //设置优惠返现
    $(".discBox").show();
    $(".discountTotal #Ycash").val(discountVal)
}



