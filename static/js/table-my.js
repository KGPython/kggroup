$(document).ready(function(){
    var parterVal = $('#parter').val();
    $('#parterId').val(parterVal);
    var blankVal = $('#blank').val();
    $('#blankId').val(blankVal);
});
/*
* 删除卡列表的一行，同时计算卡列表合计
* dom：删除按钮自身节点；action:操作类型（1：出卡，2：入卡）
* */
function delRow(dom,action) {
    var parnetTbody = $(dom).parent().parent().parent()[0];
    $(dom).parents('tr').remove();
    setTotalByCardList(parnetTbody);
}
$(document).on('click','.formline .btn-add',function(){
    var formBox = $(this).parent().parent().parent();
    var formLine = $(this).parent().parent().clone();
    formBox.append(formLine);
    formLine.find('input').val('');

});

//增加table的tr，根据不同场景，产生不同的tr
function addRow(obj,target){
    var tbody = $(obj).parent().parent().parent()[0];
    var columsL =$(tbody).find('tr').eq(0).find('td').length;

    var row = $("<tr></tr>");
    for(var i=0;i<columsL;i++){
        var td = $("<td></td>");
        if(target=='changeCode'){
            if(i==0 || i==1){
                var input = $("<input type='text' class='form-control changeCode'>");
                $(td).append(input);
            }else if(i==columsL-1){
                var button = $('<button type="button" class="btn btn-danger btn-xs btn-del" onclick="delRow(this,1)">删除</button>');
                $(td).append(button);
            }else if(i==2){
                var input = $("<input type='text' class='form-control hCost' disabled='disabled'>");
                $(td).append(input);
            }
        }else{
            if(i==0){
                var input = $("<input type='text' class='form-control cardId'>");
                $(td).append(input);
            }else if(i==columsL-1){
                var button = $('<button type="button" class="btn btn-danger btn-xs btn-del" onclick="delRow(this,1)">删除</button>');
                $(td).append(button);
            }else{
                var input = $("<input type='text' class='form-control' disabled='disabled'>");
                $(td).append(input);
            }
        }

        $(row).append(td);
        $(row).find('td').eq(0).find('input').eq(0).focus();
    }
    $(tbody).append(row);
    $(obj).parent().parent().next('tr').find('td').eq(0).find('input').focus();
}


/**
* 查询卡信息
* cardType-业务类型：1-卡出库，2-卡入库
* */
function doAjax(obj,ajaxOpt,showCardIfno,fn,cardType){
    $.ajax({
        url:ajaxOpt.url,
        type:ajaxOpt.method,
        dataType:'json',
        success:function(data){
            var res = data[0] ? data[0].fields : [];
            showCardIfno(obj,res);
            var parnetTbody = $(obj).parent().parent().parent()[0];
            fn(parnetTbody,cardType);
        }
    })
}

/*
* 补卡模块----查询卡信息
* */
function doAjax2(obj,ajaxOpt,showCardIfno,setTotalByCardList){
    $.ajax({
        url:ajaxOpt.url,
        type:ajaxOpt.method,
        dataType:'json',
        success:function(data){
            showCardIfno(obj,data);
            var parnetTbody = $(obj).parent().parent().parent()[0];
            if(setTotalByCardList){
                setTotalByCardList(parnetTbody);
            }
        }
    })
}

/*
* 卡校验信息展示
**/
function showCardIfno(obj,data){
    var cardVal,cardBlance,cardStu,flag=false;
    if(data.length==0){
        cardStu ='不存在';
        cardVal = 0;
        cardBlance = 0;
    }else{
        cardVal = data.card_value;
        cardBlance = data.card_blance;
        if(data.card_status==1){
            cardStu ='未激活';
            flag = true
        }else if(data.card_status==2){
            cardStu ='已激活';
        }else if(data.card_status==3){
            cardStu ='已冻结';
        }else if(data.card_status==4){
            cardStu ='已作废';
        }
    }
    if(flag && parseFloat(cardVal)==parseFloat(cardBlance)){
        $(obj).parent().parent().find('td').eq(3).find('input').eq(0).removeClass('red')
    }else{
        $(obj).parent().parent().find('td').eq(3).find('input').eq(0).addClass('red')
    }

    $(obj).parent().parent().find('td').eq(1).find('input').eq(0).val(cardVal);
    $(obj).parent().parent().find('td').eq(2).find('input').eq(0).val(cardBlance);
    $(obj).parent().parent().find('td').eq(3).find('input').eq(0).val(cardStu);
}

/*
* 更换卡展示信息
* */
function showCardIfno3(obj,data){
    var parentTbody = $(obj).parent().parent().parent()[0];
    var cls = '';

    if($(parentTbody).hasClass('cardIn')){
        cls = 'cardInTotal';
    }else if($(parentTbody).hasClass('cardOut')){
        cls = 'cardOutTotal';
    }else if($(parentTbody).hasClass('discount')){
        cls = 'discountTotal';
    }

    if(data.length==0){
         var cardStu ='不存在';
    }
    var cardVal = data.New_amount;
    var cardBlance = data.detail;


    if(data.mode=='9'){
        var cardStu = '未激活';
    }else if(data.mode=='1'){
        var cardStu = '已激活'
    }else if(data.mode=='2'){
        var cardStu ='未到账卡';
    }else if(data.mode=='r'){
        var cardStu ='已回收卡';
    }else if(data.mode=='m'){
        var cardStu ='一般挂失卡';
    }else if(data.mode=='l'){
        var cardStu = '严重挂失卡';
    }else if(data.mode=='f'){
        var cardStu = '已冻结';
    }else if(data.mode=='q'){
        var cardStu = '已退卡';
    }

    if(cls == 'cardInTotal'){
        if(data.mode!='1' || cardVal!=cardBlance){
            $(obj).parent().parent().find('td').eq(3).find('input').eq(0).addClass('red')
        }else{
            $(obj).parent().parent().find('td').eq(3).find('input').eq(0).removeClass('red')
        }
    }
    if(cls == 'cardOutTotal' || cls== 'discountTotal') {
        if(data.mode!='9' || cardVal!=cardBlance){
            $(obj).parent().parent().find('td').eq(3).find('input').eq(0).addClass('red')
        }else{
            $(obj).parent().parent().find('td').eq(3).find('input').eq(0).removeClass('red')
        }
    }

    $(obj).parent().parent().find('td').eq(1).find('input').eq(0).val(cardVal);
    $(obj).parent().parent().find('td').eq(2).find('input').eq(0).val(cardBlance);
    $(obj).parent().parent().find('td').eq(3).find('input').eq(0).val(cardStu);
}

/*
* 补卡模块----卡信息展示
* */
function showCardIfno2(obj,data){
    var cardVal = parseFloat(data.card_value);
    var cardBlance = parseFloat(data.card_blance);

    if(data.card_status=='9'){
        var cardStu ='未激活';
    }else if(data.card_status=='1'){
        var cardStu ='已激活';
        if(cardVal<cardBlance){
            cardStu ='异常卡';
        }
    }else if(data.card_status=='2'){
        var cardStu ='未到账款';
    }else if(data.card_status=='r'){
        var cardStu ='已回收';
    }else if(data.card_status=='m'){
        var cardStu ='一般挂失';
    }else if(data.card_status=='l'){
        var cardStu ='严重挂失';
    }else if(data.card_status=='f'){
        var cardStu ='已冻结';
    }else if(data.card_status=='e'){
        var cardStu ='已换卡';
    }else if(data.card_status=='q'){
        var cardStu ='退卡';
    }else if(data.card_status=='-1'){
        var cardStu ='不存在';
    }
    if(data.card_status ==1 && cardVal>=cardBlance ){
        $(obj).parent().parent().find('td').eq(3).find('input').eq(0).removeClass('red')
    }else{
        $(obj).parent().parent().find('td').eq(3).find('input').eq(0).addClass('red')
    }
    $(obj).parent().parent().find('td').eq(1).find('input').eq(0).val(cardVal);
    $(obj).parent().parent().find('td').eq(2).find('input').eq(0).val(cardBlance);
    $(obj).parent().parent().find('td').eq(3).find('input').eq(0).val(cardStu);
}

/*
* 卡调拨模块----查询卡信息
* */
function checkCardStu(obj,cardId,shopCode,url){
    $.ajax({
        url:url,
        type:"get",
        dataType:'json',
        async: false,
        success:function(data){
            if(data.length==0){
                alert('卡：'+cardId+'不存在');
                $(obj).val('').focus();
                return false;
            }
            else{
                var res = data[0] ? data[0].fields : [];
                if(res.card_status=='2'){
                    alert('卡：'+cardId+'已激活');
                    $(obj).val('').focus();
                     return false;
                }else if(res.card_status=='3'){
                    alert('卡：'+cardId+'已冻结');
                    $(obj).val('').focus();
                     return false;
                }
                else if(res.card_status=='4'){
                    alert('卡：'+cardId+'已作废');
                    $(obj).val('').focus();
                     return false;
                }
                if(shopCode!=res.shop_code){
                    alert('卡号：'+cardId+'不属于调出门店,无权调拨此卡！');
                    $(obj).val('').focus();
                    return false;
                }

                //卡面值赋值
                var parentTr = $(obj).parent().parent();

                if($(obj).hasClass('start')){
                    var cardType = parentTr.find('.type2').val();
                    if(cardType && cardType!=res.card_value){
                        alert('起止卡号，面值不等');
                        $(obj).val('')
                    }else {
                        parentTr.find('.type').val(res.card_value)
                    }
                }
                if($(obj).hasClass('end')){
                    var cardType = parentTr.find('.type').val();
                    if(cardType && cardType!=res.card_value){
                        alert('起止卡号，面值不等');
                        $(obj).val('')
                    }else {
                        parentTr.find('.type2').val(res.card_value)
                    }
                }
            }
        }
    })
}


/*
*  求卡列表总金额
*  cardList：卡列表所在的tbody节点
*  cardtype：出卡为1，入卡为2
* */
function getCardListVal(cardList,cardtype,cls){
    var trs = $(cardList).find('tr');
    var totalNum = 0;//卡合计数量
    var totalVal = 0.00;//卡合计金额
    for(var i=0;i<trs.length;i++){
        var status = $(trs[i]).find('td').eq(3).find('input').val();
        var val = $(trs[i]).find('td').eq(2).find('input').val();
        var type = $(trs[i]).find('td').eq(1).find('input').val();
        if(cardtype==1){
            if(status=='未激活'&& parseFloat(val)==parseFloat(type)){
                totalNum++;
                totalVal += parseFloat(val);
            }
        }else if(cardtype==2){
            if(status=='已激活' && parseFloat(val)<=parseFloat(type)){
                totalNum++;
                totalVal += parseFloat(val);
            }
        }
    }

    //如果合计区域存在处理"优惠返现"，则：优惠金额合计=优惠卡金额合计+优惠返现，
    if(cls=="discountTotal"){
        var Ycash=$('#Ycash').val();
        Ycash = Ycash=='' ?0:parseFloat(Ycash);
        totalVal +=Ycash;
    }
    //展示卡合计金额
    $('.'+cls+' #totalVal b').text(parseFloat(totalVal).toFixed(2));
    $('.'+cls+' #totalNum b').text(totalNum);

    return {'totalNum':totalNum,'totalVal':totalVal}
}

/*
* 获取卡号数组
* */
function getCardIds(obj){
    var list = [];
    var trs = $(obj).find('tr');
    for(var j=0;j<trs.length;j++){
        var cardId = $(trs[j]).find('td').eq(0).find('input').val();
        if(cardId){
            list.push($.trim(cardId));
        }
    }
    return list;
}

/*
* 获取出卡信息列表
* obj:卡列表所在table的tbody
* flag:操作类型（1：售卡(卡出库)，2：换卡）
*/
function getCardList(obj,flag){
    var list = [];
    var trs = $(obj).find('tr');
    for(var j=0;j<trs.length;j++){
        var item = {};
        var status = $(trs[j]).find('td').eq(3).find('input').val();
        var cardType = $(trs[j]).find('td').eq(1).find('input').val();
        var val = $(trs[j]).find('td').eq(2).find('input').val();
        if(flag=='1'){
            if(status=='未激活' && parseFloat(val)==parseFloat(cardType) ){
                var cardId = $(trs[j]).find('td').eq(0).find('input').val();
                var val = $(trs[j]).find('td').eq(2).find('input').val();
                item = {'cardId':cardId,'cardVal':val};
                list.push(item)
            }
        }else if(flag=='2'){
            if(status=='已激活' && parseFloat(val)==parseFloat(cardType) ){
                var cardId = $(trs[j]).find('td').eq(0).find('input').val();
                var val = $(trs[j]).find('td').eq(2).find('input').val();
                item = {'cardId':cardId,'cardVal':val};
                list.push(item)
            }
        }

    }
    return list;
}

/*
* 获取补卡信息列表
* */
function getCardFillList(obj,type){
    var list = [];
    var trs = $(obj).find('tr');
    for(var j=0;j<trs.length;j++){
        var item = {};
        var status = $(trs[j]).find('td').eq(3).find('input').val();
        if(type=="1"){
            if(status=='未激活'){
                var cardId = $(trs[j]).find('td').eq(0).find('input').val();
                var val = $(trs[j]).find('td').eq(1).find('input').val();
                var balance = $(trs[j]).find('td').eq(2).find('input').val();
                item = {'cardId':cardId,'cardVal':val,'balance':balance};
                list.push(item)
            }
        }else{
             if(status=='已激活'){
                var cardId = $(trs[j]).find('td').eq(0).find('input').val();
                var val = $(trs[j]).find('td').eq(1).find('input').val();
                var balance = $(trs[j]).find('td').eq(2).find('input').val();
                item = {'cardId':cardId,'cardVal':val,'balance':balance};
                list.push(item)
            }
        }

    }
    return list;
}

/*
* 获取支付列表
* */
function getPayList(obj){
    var list = [];
    var trs = $(obj).find('tr');
    for(var j=0;j<trs.length;j++){
        var item = {};
        var checkBox = $(trs[j]).find('td').eq(0).find('input')[0];
        var flag = $(checkBox).is(':checked');
        var payVal= $(trs[j]).find('td').eq(2).find('input').val();
        if(flag && payVal){
            var payId = $(checkBox).val();
            if(!payId){
                alert('请选择三方支付方式');
                return false;
            }
            var payRmarks = $(trs[j]).find('td').eq(3).find('input').val();
            item = {'payId':payId,'payVal':payVal,'payRmarks':payRmarks};
            list.push(item)
        }
    }
    return list;
}

/*
* 1、设置优惠返点率
* 2、计算优惠金额
* */
function createDiscount(discRate,cardsValTotal) {
    var rateInput  = $('.Total #discount input');
    var discCode = $(".Total #disCode").val();
    var  rate= 0;
    if(discRate!==''){
        rate = discRate;
    }else{
        if(discCode){//如果折扣授权码discCode存在，则认为是自定义折扣，取输入框内部的数值为折扣返点率
            rate = (parseFloat(rateInput.val()).toFixed(2))/100;
        }else {//如果折扣授权码discCode不存在，则认为是固定返点，由系统生成折扣返点率
            if(typeof(DISC_RATES)!='undefined'){
                for(var j=0;j<DISC_RATES.length;j++){
                    if(DISC_RATES[j].val_min<=parseFloat(cardsValTotal) && DISC_RATES[j].val_max>=parseFloat(cardsValTotal)){
                        rate=DISC_RATES[j].discount_rate;
                    }
                }
                rateInput.val(parseFloat(rate*100).toFixed(2));
                $("#discRateStandard").val(parseFloat(rate*100).toFixed(2));
            }
        }
    }

    //处理特殊返点
    var discountVal = 0;
    if((SHOP=='C010' || SHOP=='C023') && cardsValTotal>=3000 &&cardsValTotal<=3030){
        discountVal = 100
    }else{
        discountVal = (parseFloat(cardsValTotal)*rate).toString().split(".")[0];
    }

    $('.Total #discountVal b').text(discountVal);
    if(discountVal>0){
        $('.discBox').show();
    }else {
        $('.discBox').hide();
        $('.discountTotal #totalVal b').text(0);
        $('.discountTotal #Ycash').val(0);
    }
    return discountVal;
}


/***************************************************优惠管理  start****************************************************/

/*
* 当填写优惠返现时，更改相关金额信息
* act:当前操作类型
* obj：优惠返现input输入框
* */
function discCash() {
    //2、获取优惠返卡合计
    var discCardList = $('#YcardList');
    var discCardTotalVal = getCardListVal(discCardList,1,'discountTotal').totalVal;
    $('.discountTotal #totalVal b').text(discCardTotalVal);

    //3、计算优惠补差金额
    //获取优惠返点金额
    var discountVal = parseFloat($('.Total #discountVal b').text());
    discountVal = isNaN(discountVal) ? 0:discountVal;
    //优惠补差金额
    var discPay = discCardTotalVal - discountVal;
    $('.Total #totalYBalance b').text(discPay);
    //3.3、计算缴费合计金额
    var saleCardTotalVal = parseFloat($('.Total #totalVal b').text());
    saleCardTotalVal = isNaN(saleCardTotalVal) ? 0:saleCardTotalVal;
    var orderVal = saleCardTotalVal + discPay;
    $('.Total #totalPaid b').text(orderVal);
}

/***************************************************优惠管理  end****************************************************/


//保存售卡订单
function saveCardSaleOrder(action_type,url,cardList,orderSns){
    //售卡列表
    var cardList = cardList;
    var orderSnList = '';
    if(orderSns){
        orderSnList = orderSns;
    }
    var totalNum = parseInt($('.Total #totalNum b').text());
    var totalVal = parseFloat($('.Total #totalVal b').text());//卡合计金额
    var payTotal = parseFloat($('.Total #payTotal b').text());//支付合计
    var discPay =parseFloat($('.Total #totalYBalance b').text());//优惠补差
    var discount = parseFloat($('.Total #discount input').val());//折扣比率
    var disCode = $('.Total #disCode').val();
    var discountVal = parseFloat($('.Total #discountVal b').text());//优惠金额
    var YcardList = [];
    var YtotalNum=0,Ycash=0,YtotalVal=0;
    if(discountVal){
        //赠卡列表
        YcardList = getCardList($('#YcardList'),'1');
        YtotalNum =parseInt($('.discountTotal #totalNum b').text());
        Ycash = parseFloat($('#Ycash').val());//优惠返现
        YtotalVal =parseFloat($('.discountTotal #totalVal b').text());//优惠列表合计=卡合计+返现合计
    }

    //支付列表
    var payList = getPayList($('.payList'));
    var hjsStr = $('.payList #remark-hjs').val();
    //买卡人信息
    var buyerName = $('#buyerName').val();
    var buyerPhone = $('#buyerPhone').val();
    var buyerCompany = $('#buyerCompany').val();

    var postToken = $('#post-token').val();

    if(totalVal==0){
        alert('还未添加售卡信息，请核对后再尝试提交！');
        return false;
    }
    if(payTotal!=totalVal+discPay){
        alert('支付金额与应付金额不等，请核对后提交！');
        return false;
    }

    if(discountVal>0){
        //优惠补差
        if(discPay<0){
            alert('优惠补差不能为负数！');
            return false;
        }
    }
    var data = {
        csrfmiddlewaretoken: CSRF,
        'actionType':action_type,//操作类型
        'cardStr':JSON.stringify(cardList),//售卡列表
        'orderSnList':orderSnList,
        'totalNum':totalNum,//售卡总数
        'totalVal':totalVal,//售卡总价
        'discount':discount,//返点百分比
        'disCode':disCode,//返点自定义授权
        'discountVal':discountVal,//优惠返点金额
        'YcardStr':JSON.stringify(YcardList),//优惠卡列表
        'YtotalNum':YtotalNum,//优惠卡总数
        'Ycash':Ycash,//优惠返现
        'YtotalVal':YtotalVal,//优惠区域合计
        'Ybalance':discPay,//优惠补差
        'payStr':JSON.stringify(payList),//支付列表
        'hjsStr':hjsStr,//黄金手列表
        'buyerName':buyerName,
        'buyerPhone':buyerPhone,
        'buyerCompany':buyerCompany,
        'postToken':postToken
    };
    // console.log(data);
    doAjaxSave(url,data);
}

//保存补卡订单
function saveCardFillOrder(url){
    //入卡列表
    var cardInList = getCardFillList($('#cardInList'),"2");
    var cardInTotalNum = parseInt($('.cardInTotal #totalNum b').text());
    var cardInTotalVal = parseFloat($('.cardInTotal #totalVal b').text());

    //补卡人信息
    var action_type = $('#action_type').val();
    var user_name = $('#user_name').val();
    var user_phone = $('#user_phone').val();

    if(cardInTotalNum==0){
        alert('还未添加入卡信息，请核对后再尝试提交！');
        return false;
    }
    var data = {
        csrfmiddlewaretoken: CSRF,
        'cardInStr':JSON.stringify(cardInList),
        'cardInTotalNum':cardInTotalNum,
        'cardInTotalVal':cardInTotalVal,
        'user_name':user_name,
        'user_phone':user_phone,
        'action_type':action_type
    };
    doAjaxSave(url,data);
}

//更新补卡订单
function updateCardFillOrder(url){
    //入卡列表
    var cardOutList = getCardFillList($('#cardOutList'),"1");
   
    var cardOutTotalNum = parseInt($('.cardOutTotal #totalNum b').text());
    var cardOutTotalVal = parseFloat($('.cardOutTotal #totalVal b').text());
    var cardOutBalance = parseFloat($('.cardOutTotal #balance span').text());

    //订单信息
    var order_sn = $('#order_sn').val();
    var paymoney = $('#paymoney').val();
    if(!paymoney){
        paymoney = 0.0
    }else{
        paymoney = parseFloat(paymoney)
    }
    if(cardOutTotalNum==0){
        alert('还未添加出卡信息，请核对后再尝试提交！');
        return false;
    }
    if(cardOutBalance!=paymoney){
        alert('实收补差金额与应收补差金额不等，请核实后提交！');
        return false;
    }
    var data = {
        csrfmiddlewaretoken: CSRF,
        'cardOutStr':JSON.stringify(cardOutList),
        'cardOutTotalNum':cardOutTotalNum,
        'cardOutTotalVal':cardOutTotalVal,
        'order_sn':order_sn,
        'paymoney':paymoney
    };
    doAjaxSave(url,data);

}

// 保存换卡订单
function saveCardChangeOrder(url){
    //入卡列表
    var cardListIn = getCardList($('#cardInList'),'2');
    var totalNumIn = parseInt($('.cardInTotal #totalNum b').text());// 卡张数合计
    var totalValIn = parseFloat($('.cardInTotal #totalVal b').text());//卡合计金额
    //出卡列表
    var cardListOut = getCardList($('#ListOut'),'1');
    var totalNumOut =parseInt($('.cardOutTotal #totalNum b').text());
    var totalValOut =parseFloat($('.cardOutTotal #totalVal b').text());

    //订单支付信息
    var orderVal = parseFloat($('.Total #totalPaid b').text());
    var discVal = parseFloat($('.Total #discountVal b').text());
    var discPay = parseFloat($('.Total #totalYBalance b').text());
    var cardsOutVal = parseFloat($('.Total #totalVal b').text());
    var disRate =  (parseFloat($('.Total #discount input').val()).toFixed(2))/100;
    var discCode = $('.Total #disCode').val();
    //支付列表
    var payList = getPayList($('.payList'));
    var hjsStr = $('.payList #remark-hjs').val();

    //优惠列表信息
    var discCardList = [];
    var discCash = 0;
    if(discVal>0){
        discCardList = getCardList($('#YcardList'),'1');
        discCash = parseFloat($('.discountTotal #Ycash').val());
    }

    //买卡人信息
    var buyerName = $('#buyerName').val();
    var buyerPhone = $('#buyerPhone').val();
    var buyerCompany = $('#buyerCompany').val();
    if(totalValIn==0){
        alert('还未添加入卡信息，请核对后再尝试提交！');
        return false;
    }
    if(totalValOut==0){
        alert('还未添加出卡信息，请核对后再尝试提交！');
        return false;
    }
    if((cardsOutVal+discPay)!=orderVal){
        alert('支付金额与应付金额不等，请核对后提交！');
        return false;
    }

    if(discVal>0){
        //优惠补差
        if(discPay<0){
            alert('优惠补差不能为负数！');
            return false;
        }
    }
    $("#btn-enter").attr('disable',true);
    var data ={
        csrfmiddlewaretoken: CSRF,
        'cardListIn':JSON.stringify(cardListIn),
        'totalNumIn':totalNumIn,
        'totalValIn':totalValIn,
        'cardListOut':JSON.stringify(cardListOut),
        'totalNumOut':totalNumOut,
        'totalValOut':totalValOut,
        'discList':JSON.stringify(discCardList),
        'discCash':discCash,
        'discCode':discCode,
        'disRate':disRate,
        'disc':discVal,
        'discPay':discPay,
        'payStr':JSON.stringify(payList),//支付列表
        'hjsStr':hjsStr,//黄金手列表
        // 支付人信息
        'buyerName':buyerName,
        'buyerPhone':buyerPhone,
        'buyerCompany':buyerCompany,
        'postToken':$('#post-token').val()
    };

    doAjaxSave(url,data);
}

//ajax传输保存订单操作的数据
function doAjaxSave(url,data){
    $("#btn-enter").attr('disabled',true);
    $.ajax({
        url:url,
        type:'post',
        dataType:'json',
        data:data,
        success:function(data){
            $("#btn-enter").removeAttr('disabled');
            if(data.msg==1){
                alert('提交成功');
                // $('input[type=text]').not('.payName').val('');
                // $('input[type=checkbox]').prop('checked',false);
                window.location.reload(true);
                if(data.urlRedirect){
                    window.location.href=data.urlRedirect;
                }
            }else if(data.msg==0){
                if(data.msg_err){
                    alert(data.msg_err);
                }else{
                    alert('提交失败');
                }
            }
        },
        error:function(XMLHttpRequest, textStatus, errorThrown){
             $("#btn-enter").removeAttr('disabled');
            alert('提交失败,失败原因：'+errorThrown);
        }
    })
}


/******************************  支付相关 start   *****************************************/

//支付列表，黄金手复选框：控制黄金手验证框的开关
$('.payList #hjs').click(function(){
    var flag = $(this).is(':checked');
    if(flag){
        $('#hjsBox').show()
    }
});

//黄金手验证框，底部按钮
$('.modal-footer #close').click(function(){
    $('#hjsBox').hide()
});

//黄金手--合计
$('.modal-footer #submit').click(function(){
    var trs = $('#hjsBox tbody').find('tr');
    var totalVal=0.00;
    var codesStr = '';
    for(var i=0;i<trs.length;i++){
        var val = $(trs[i]).find('td').eq(2).find('input').val();
        if(parseFloat(val)){
            totalVal += parseFloat(val);
            var code = $(trs[i]).find('td').eq(0).find('input').val();
            codesStr +=code+',';
        }
    }
    $('.payList #hjsStr').val(codesStr);
    $('.payList #remark-hjs').val(codesStr);
    $('.payList #hjsVal').val(parseFloat(totalVal));
    $('#hjs').focus();
    $('#buyerName').focus();
    $('#hjsBox').hide();
});

//黄金手--校验
$(document).on('change','#hjsBox .changeCode',function(){
    var _this = $(this);
    var parentTr = _this.parent().parent();
    var hNo = parentTr.find('td').eq(0).find('input').val();
    var hPassword = parentTr.find('td').eq(1).find('input').val();

    if(hNo&&hPassword){
         $.ajax({
            url:'/kg/sellcard/changcodecheck/',
            method:'post',
            dataType:'json',
            async:false,
            data:{
                csrfmiddlewaretoken: CSRF,
                'code':hNo,
                'camilo':hPassword
            },
            success:function(data){
                if(data.cost){
                    if(data.shop_code){
                        parentTr.find('td').eq(2).find('input').val('已使用');
                    }else{
                        parentTr.find('td').eq(2).find('input').val(data.cost);
                    }
                }else{
                    parentTr.find('td').eq(2).find('input').val('0');
                }
                addRow(_this,'changeCode');
            }
        })
    }else if(!hNo&&!hPassword){
        alert('卡号和卡密不能为空！');
        return false;
    }else{
        return false;
    }

});

/*
* 产生“合计”区域相关信息 -- 根据出入库卡列表
* obj：卡列表的tbody
* cardtype：出卡为1，入卡为2
* */
function setTotalByCardList(obj){
    var cardList = obj;
    var cls = '';
    var cardtype = 1;//默认为卡出库
    // 1、判断合计展示的位置
    if($(cardList).hasClass('discount')){
        //优惠管理区域
        cls = 'discountTotal';
        // 2、计算卡列表的合计金额和合计张数
        var data = getCardListVal(cardList,cardtype,cls);
        var cardsTotalVal = data.totalVal;
        //3、获取优惠返点
        var discountVal = parseFloat($('.Total #discountVal b').text());
        // 4、计算优惠差额=优惠卡列表合计-返点金额
        var discountPay = cardsTotalVal - discountVal;
        $('.Total #totalYBalance b').text(discountPay);
        //5、设置订单应付金额 = 售卡列表合计金额 + 优惠补差
        var cardsSaleVal = parseFloat($('.Total #totalVal b').text());//售卡列表合计金额
        var orderVal = cardsSaleVal + discountPay;
        $('.Total #totalPaid b').text(orderVal)

    }else if($(cardList).hasClass('cardIn')){
        //换卡入库、补卡入库
        cls = 'cardInTotal';
        cardtype = 2;
        // 2、计算卡列表的合计金额和合计张数
        var data = getCardListVal(cardList,cardtype,cls);
        var cardsInTotalVal = data.totalVal;

        //3、如果是换卡模块，则计算换卡补差
        var Paybox = $(".Total");
        if(Paybox.length>0){
            //3.1、计算补差金额
            var cardChangeOutTotalVal = $(".cardOutTotal #totalVal b").text();
            var cardsPayVal = parseFloat(cardChangeOutTotalVal)-parseFloat(cardsInTotalVal);
            if(cardsPayVal>0){
                $('.payment').show();
                $('.Total').show();
            }else {
                $('.payment').hide();
                $('.Total').hide();
                $('.payList .payVal').val('')
            }
            $('.Total #totalVal b').text(cardsPayVal);
            //3.2、计算优惠返点
            var discountVal = createDiscount('',cardsPayVal);
            //3.3、计算订单总额
            var discBoxVal = parseFloat($('.discountTotal #totalVal b').text());
            var discPay = discBoxVal - discountVal;
            $(".Total #totalYBalance b").text(discPay);
            var orderVal = cardsPayVal + discPay;
            $(".Total #totalPaid b").text(orderVal);
        }

    }else if($(cardList).hasClass('cardOut')){
        //换卡出库、补卡出库
        cls = 'cardOutTotal';
        // 2、计算卡列表的合计金额和合计张数
        var cardsTotal = getCardListVal(cardList,cardtype,cls);
        var cardsTotalVal = cardsTotal.totalVal;

        //3、如果是补卡模块，则计算补卡补差
        var fillCardPayInput  = $('.cardOutTotal #balance span');
        if(fillCardPayInput.length>0){
            var cardsOutVal = parseFloat($('.cardOutTotal #totalVal b').text()).toFixed(2);
            if(cardsOutVal!=undefined){
                var cardsInVal = parseFloat($('.cardInTotal #totalVal b').text()).toFixed(2);
                cardsInVal = isNaN(cardsInVal) ? 0:cardsInVal;
                fillCardPay = parseFloat(cardsOutVal - cardsInVal).toFixed(1);
                $('.cardOutTotal #balance span').text(fillCardPay);
            }
        }
        //3、如果是换卡模块，则计算换卡补差
        var Paybox = $(".Total");
        if(Paybox.length>0){
            //3.1、计算补差金额
            var cardChangeInTotalVal = $(".cardInTotal #totalVal b").text();
            var cardsPayVal = parseFloat(cardsTotalVal)-parseFloat(cardChangeInTotalVal);
            if(cardsPayVal>0){
                $('.payment').show();
                $('.Total').show();
            }else {
                $('.payment').hide();
                $('.Total').hide();
                $('.payList .payVal').val('')
            }
            $('.Total #totalVal b').text(cardsPayVal);
            //3.2、计算优惠返点
            var discountVal = createDiscount('',cardsPayVal);

            //3.3、计算订单总额
            var discBoxVal = parseFloat($('.discountTotal #totalVal b').text());
            var discPay = discBoxVal - discountVal;
            $(".Total #totalYBalance b").text(discPay);
            var orderVal = cardsPayVal + discPay;
            $(".Total #totalPaid b").text(orderVal);

        }
    }else{
        cls = 'Total';
        // 2、计算卡列表的合计金额和合计张数
        var cardsTotal = getCardListVal(cardList,cardtype,cls);
        var cardsTotalVal = cardsTotal.totalVal;
        var discountVal = createDiscount('',cardsTotalVal);
        //4、优惠补差
        var discountCardTotalVal = parseFloat($(".discountTotal #totalVal b").text());
        discountPay  = discountCardTotalVal - discountVal;
        $('.Total #totalYBalance b').text(discountPay);//设置“合计”区域->优惠补差
        //5、设置订单应付金额 = 售卡列表合计金额 + 优惠补差
        $('.Total #totalPaid b').text(cardsTotalVal+discountPay);
    }

   //补卡补差
    var Ybalance = 0;
    var YtotalVal = parseFloat($('.cardOutTotal #totalVal b').text());
    if(YtotalVal!=undefined){
        Ybalance = YtotalVal - discountVal;
        $('.cardOutTotal #balance b').text(Ybalance);
    }
}

/*
* 产生“合计”区域相关信息 -- 根据当前“售卡合计”
* cardSaleTotalVal：售卡合计
* */
function setTotalBycardSaleTotalVal(discRate,cardSaleTotalVal){
    $('.Total-discInfo').show();
    var discountVal = createDiscount(discRate,cardSaleTotalVal);
    //2、计算优惠补差
    var discountCardTotalVal = parseFloat($(".discountTotal #totalVal b").text());
    discountPay  = discountCardTotalVal - discountVal;
    $('.Total #totalYBalance b').text(discountPay);
    //3、计算应付金额
    $('.Total #totalPaid b').text(cardSaleTotalVal+discountPay);
}





/******************************  支付相关 end   *****************************************/

function closeFun() {
    self.location=document.referrer;
}
Array.prototype.remove = function(val) {
    var index = this.indexOf(val);
    if (index > -1) {
    this.splice(index, 1);
    }
};