
/*
* 删除卡列表的一行，同时计算卡列表合计
* dom：删除按钮自身节点；action:操作类型（1：出卡，2：入卡）
* */
function delRow(dom) {
    var id = $(dom).attr('id');
    var parnetTbody = $(dom).parent().parent().parent()[0];
    $(dom).parents('tr').remove();
    if(id!='err'){
        setTotalByCardList(parnetTbody);
    }

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
        if(target=='changeCode'){//黄金手
            if(i==0 || i==1){
                var input = $("<input type='text' class='form-control changeCode'>");
                $(td).append(input);
            }else if(i==columsL-1){
                var button = $('<button type="button" class="btn btn-danger btn-xs btn-del" onclick="delRow(this)">删除</button>');
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
                var button = $('<button type="button" class="btn btn-danger btn-xs btn-del" onclick="delRow(this)">删除</button>');
                $(td).append(button);
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
        $(obj).parent().parent().find('td').eq(3).addClass('red')
    }else{
        cardVal = data.card_value;
        cardBlance = data.card_blance;
        if(data.card_status==1 && parseFloat(cardVal)==parseFloat(cardBlance) && data.is_store=='0'){
            cardStu ='可操作';
            $(obj).parent().parent().find('td').eq(3).removeClass('red')
        }else{
            cardStu ='不可操作';
            $(obj).parent().parent().find('td').eq(3).addClass('red')
        }
    }

    $(obj).parent().parent().find('td').eq(1).text(cardVal);
    $(obj).parent().parent().find('td').eq(2).text(cardBlance);
    $(obj).parent().parent().find('td').eq(3).text(cardStu);
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
    var cardVal = cardBlance = '';
    var cardStu = '可操作';
    var flag = true;
    if(!data){
        cardStu ='不存在';
        flag = false;
    } else {
        cardVal = data.New_amount;
        cardBlance = data.detail;
        if (cls == 'cardInTotal') {
            if (data.mode != '1' || cardVal != cardBlance) {
                cardStu = '不可操作';
                flag = false;
            }
        }
        if (cls == 'cardOutTotal' || cls == 'discountTotal') {
            if (data.mode != '9' || cardVal != cardBlance) {
                cardStu = '不可操作';
            }
        }
    }


    if(!flag){
        $(obj).parent().parent().find('td').eq(3).addClass('red');
    }else{
        $(obj).parent().parent().find('td').eq(3).removeClass('red');
    }
    $(obj).parent().parent().find('td').eq(1).text(cardVal);
    $(obj).parent().parent().find('td').eq(2).text(cardBlance);
    $(obj).parent().parent().find('td').eq(3).text(cardStu);
}

/*
* 补卡模块----入卡信息展示
* */
function showCardIfno2(obj,data){
    var cardVal = parseFloat(data.card_value);
    var cardBlance = parseFloat(data.card_blance);
    var cardStu ='可操作';

    if(data.card_status ==1 && cardVal>=cardBlance){
        $(obj).parent().parent().find('td').eq(3).removeClass('red')
    }else{
        cardStu ='不可操作';
        $(obj).parent().parent().find('td').eq(3).addClass('red')
    }
    $(obj).parent().parent().find('td').eq(1).text(cardVal);
    $(obj).parent().parent().find('td').eq(2).text(cardBlance);
    $(obj).parent().parent().find('td').eq(3).text(cardStu);
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
                if(res.card_status!='1'){
                    alert('不可操作卡：'+cardId);
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
                var card_value = !res.card_value ? res.card_value : 0;
                if($(obj).hasClass('start')){
                    var cardType = parentTr.find('.type2').val();

                    if(cardType && cardType!=card_value){
                        alert('起止卡号，面值不等');
                        $(obj).val('')
                    }else {
                        parentTr.find('.type').val(card_value)
                    }
                }
                if($(obj).hasClass('end')){
                    var cardType = parentTr.find('.type').val();
                    if(cardType && cardType!=card_value){
                        alert('起止卡号，面值不等');
                        $(obj).val('')
                    }else {
                        parentTr.find('.type2').val(card_value)
                    }
                }
            }
        }
    })
}


/*
*  求卡列表总金额
*  cardList：卡列表所在的tbody节点
*  cardtype：（1：出卡，2：入卡,3：补卡入库），
* */
function getCardListVal(cardList,cardtype,cls){
    var trs = $(cardList).find('tr');
    var totalNum = 0;//卡合计数量
    var totalVal = 0.00;//卡合计金额

    for(var i=0;i<trs.length;i++){
        var status = $(trs[i]).find('td').eq(3).text();
        var val = $(trs[i]).find('td').eq(2).text();
        var type = $(trs[i]).find('td').eq(1).text();
        if(cardtype==1 || cardtype==2)
        {
            if(status=='可操作'&& parseFloat(val)==parseFloat(type)){
                totalNum++;
                totalVal += parseFloat(val);
            }
        }
        else if(cardtype==3)
        {
            if(status=='可操作' && parseFloat(val)<=parseFloat(type)){
                totalNum++;
                totalVal += parseFloat(val);
            }
        }
    }
    //如果合计区域存在处理"优惠返现"，则：优惠金额合计=优惠卡金额合计+优惠返现，
    if(cls=="discountTotal"){
        var Ycash=$('#Ycash').val();
        if(!Ycash){
            Ycash=0;
        }
        totalVal += parseFloat(Ycash);
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
function getCardList(obj){
    var list = [];
    var trs = $(obj).find('tr');
    for(var j=0;j<trs.length;j++){
        var item = {};
        var status = $(trs[j]).find('td').eq(3).text();
        var cardType = $(trs[j]).find('td').eq(1).text();
        var val = $(trs[j]).find('td').eq(2).text();
        if(status=='可操作' && parseFloat(val)==parseFloat(cardType) ){
            var cardId = $(trs[j]).find('.cardId').eq(0).val();
            item = {'cardId':cardId,'cardVal':val};
            list.push(item)
        }
    }
    return list;
}
function getCardIdList(obj){
    var list = [];
    var trs = $(obj).find('tr');
    for(var j=0;j<trs.length;j++){
        var status = $(trs[j]).find('td').eq(3).text();
        var cardType = $(trs[j]).find('td').eq(1).text();
        var val = $(trs[j]).find('td').eq(2).text();
        if(status=='可操作' && parseFloat(val)==parseFloat(cardType) ){
            var cardId = $(trs[j]).find('.cardId').eq(0).val();
            list.push(cardId.trim())
        }
    }
    return list;
}
/*
* 获取补卡信息列表
* */
function getCardFillList(obj){
    var list = [];
    var trs = $(obj).find('tr');
    for(var j=0;j<trs.length;j++){
        var item = {};
        var status = $(trs[j]).find('td').eq(3).text();
        if(status=='可操作'){
            var cardId = $(trs[j]).find('td').eq(0).find('input').val();
            var val = $(trs[j]).find('td').eq(1).text();
            var balance = $(trs[j]).find('td').eq(2).text();
            item = {'cardId':cardId,'cardVal':val,'balance':balance};
            list.push(item)
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
            }else if((payId==3 || payId == 4)){
                if((!$('#buyerName').val() || !$('#buyerPhone').val() || !$('#buyerCompany').val())){
                    alert('使用赊销和汇款支付，顾客信息不能为空');
                    return false;
                }
            }
            var payRmarks = $(trs[j]).find('td').eq(3).find('input').val();
            item = {'payId':payId,'payVal':payVal,'payRmarks':payRmarks};
            list.push(item)
        }
    }
    return list;
}

function getPayList1(obj){
    var data ={};
    var payList = [];
    var totalVal = 0;
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
            //拼接支付列表
            var payRmarks = $(trs[j]).find('td').eq(3).find('input').val();
            item = {'payId':payId,'payVal':payVal,'payRmarks':payRmarks};
            if(payId==3){
                item['bankName'] = $('#bankName').val();
                item['bankSn'] = $('#bankSn').val();
                item['payCompany'] = $('#payCompany').val();
            }
            payList.push(item);
            //计算支付合计
            totalVal  += parseFloat(payVal);
        }
    }
    data['payList'] = payList;
    data['totalVal'] = totalVal;
    return data;
}

function getPayList2(obj){
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
    if((SHOP=='C010' || SHOP=='C023') && cardsValTotal>=3000 &&cardsValTotal<=3030 && rate>0){
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
        $('#YcardList .cardId').val('');
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


function saveBorrowPayOrder(action_type,url,orderSns){
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
        YcardList = getCardList($('#YcardList'));
        YtotalNum =parseInt($('.discountTotal #totalNum b').text());
        Ycash = parseFloat($('#Ycash').val());//优惠返现
        YtotalVal =parseFloat($('.discountTotal #totalVal b').text());//优惠列表合计=卡合计+返现合计
    }
    //支付列表
    var payList = getPayList2($('.payList'));
    if(!payList){
        return false;
    }
    // var hjsStr = $('.payList #remark-hjs').val();
    var postToken = $('#post-token').val();
    if(orderSns.length==0){
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
        'actionType':action_type,
        'orderSnList':orderSns,
        'totalNum':totalNum,
        'totalVal':totalVal,
        'discount':discount,
        'disCode':disCode,
        'discountVal':discountVal,
        'YcardStr':JSON.stringify(YcardList),
        'YtotalNum':YtotalNum,
        'Ycash':Ycash,
        'YtotalVal':YtotalVal,
        'Ybalance':discPay,
        'payStr':JSON.stringify(payList),
        'postToken':postToken
    };
    doAjaxSave(url,data);
}

//保存售卡订单
function saveCardSaleOrder(action_type,url,cardList){
    //售卡列表
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
        YcardList = getCardList($('#YcardList'));
        YtotalNum =parseInt($('.discountTotal #totalNum b').text());
        Ycash = parseFloat($('#Ycash').val());//优惠返现
        YtotalVal =parseFloat($('.discountTotal #totalVal b').text());//优惠列表合计=卡合计+返现合计
    }

    //支付列表
    var payList = getPayList($('.payList'));
    if(!payList){
        return false;
    }
    // var hjsStr = $('.payList #remark-hjs').val();
    //买卡人信息
    var buyerName = $('#buyerName').val();
    var buyerPhone = $('#buyerPhone').val();
    var buyerCompany = $('#buyerCompany').val();

    var postToken = $('#post-token').val();

    if(cardList.length==0){
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
        // 'hjsStr':hjsStr,//黄金手列表
        'buyerName':buyerName,
        'buyerPhone':buyerPhone,
        'buyerCompany':buyerCompany,
        'postToken':postToken
    };
    doAjaxSave(url,data);
}

function saveVipOrder(action_type,url){
    var cardList = getCardList($('#correctOut'));
    var totalNum = parseInt($('.Total #totalNum b').text());
    var totalVal = parseFloat($('.Total #totalVal b').text());//卡合计金额
    var payTotal = parseFloat($('.Total #payTotal b').text());//支付合计
    var discPay =parseFloat($('.Total #totalYBalance b').text());//优惠补差
    var discount = parseFloat($('.Total #discount input').val());//折扣比率
    var disCode = $('.Total #disCode').val();
    var disc_state = $("input[name='disc_state']:checked").val();
    var disc_val = parseFloat($("#discountVal b").text());
    var YcardList = [];
    var YtotalNum=0,Ycash=0,YtotalVal=0;
    if(disc_state==0){
        r = confirm('确认此单不参加累计返点？');
        if(!r){
            return false;
        }
    }
    if(disc_val>0){
        if(disc_state == 1){
            alert('请核对累计返点状态');
            return false;
        }
        if(discPay<0){
            alert('优惠补差不能为负数！');
            return false;
        }
        //赠卡列表
        YcardList = getCardList($('#YcardList'));
        YtotalNum =parseInt($('.discountTotal #totalNum b').text());
        Ycash = parseFloat($('#Ycash').val());//优惠返现
        YtotalVal =parseFloat($('.discountTotal #totalVal b').text());//优惠列表合计=卡合计+返现合计
    }

    //支付列表
    var payList = getPayList($('.payList'));
    if(!payList){
        return false;
    }
    // var hjsStr = $('.payList #remark-hjs').val();
    //买卡人信息
    var buyerName = $('#buyerName').val();
    var buyerPhone = $('#buyerPhone').val();
    var buyerCompany = $('#buyerCompany').val();
    var vipId = $('#vipId').val();

    var postToken = $('#post-token').val();

    if(cardList.length==0){
        alert('还未添加售卡信息，请核对后再尝试提交！');
        return false;
    }
    if(payTotal!=totalVal+discPay){
        alert('支付金额与应付金额不等，请核对后提交！');
        return false;
    }
    var data = {
        csrfmiddlewaretoken: CSRF,
        'actionType':action_type,//操作类型
        'cardStr':JSON.stringify(cardList),//售卡列表
        'totalNum':totalNum,//售卡总数
        'totalVal':totalVal,//售卡总价
        'discount':discount,//返点百分比
        'disCode':disCode,//返点自定义授权
        'discountVal':disc_val,//优惠返点金额
        'YcardStr':JSON.stringify(YcardList),//优惠卡列表
        'YtotalNum':YtotalNum,//优惠卡总数
        'Ycash':Ycash,//优惠返现
        'YtotalVal':YtotalVal,//优惠区域合计
        'Ybalance':discPay,//优惠补差
        'payStr':JSON.stringify(payList),//支付列表
        // 'hjsStr':hjsStr,//黄金手列表
        'buyerName':buyerName,
        'buyerPhone':buyerPhone,
        'buyerCompany':buyerCompany,
        'vipId':vipId,
        'discState':disc_state,
        'postToken':postToken
    };
    doAjaxSave(url,data);
}

function saveVipSettlement(action_type,url,orderSns) {
    if(!orderSns){
        alert('还未选择结算订单');
        return false;
    }
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
        YcardList = getCardList($('#YcardList'));
        YtotalNum =parseInt($('.discountTotal #totalNum b').text());
        Ycash = parseFloat($('#Ycash').val());//优惠返现
        YtotalVal =parseFloat($('.discountTotal #totalVal b').text());//优惠列表合计=卡合计+返现合计
    }

    //支付列表
    var payList = getPayList($('.payList'));
    if(!payList){
        return false;
    }
    //买卡人信息
    var buyerName = $('#buyerName').val();
    var buyerPhone = $('#buyerPhone').val();
    var buyerCompany = $('#buyerCompany').val();
    var postToken = $('#post-token').val();
    var vipId = $('#vipId').val();
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
        'orderSns':orderSns,
        'actionType':action_type,//操作类型
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
        'buyerName':buyerName,
        'buyerPhone':buyerPhone,
        'buyerCompany':buyerCompany,
        'vipId':vipId,
        'postToken':postToken
    };
    doAjaxSave(url,data);
}

//保存补卡订单
function saveCardFillOrder(url){
    //入卡列表
    var cardInList = getCardFillList($('#cardFillInList'));
    var cardInTotalNum = parseInt($('.cardFillInTotal #totalNum b').text());
    var cardInTotalVal = parseFloat($('.cardFillInTotal #totalVal b').text());

    //补卡人信息
    var action_type = $('#action_type').val();
    var user_name = $('#user_name').val();
    var user_phone = $('#user_phone').val();
    if(cardInList.length==0 || cardInTotalVal==0){
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
    var cardOutList = getCardFillList($('#cardFillOutList'));
   
    var cardOutTotalNum = parseInt($('.cardFillOutTotal #totalNum b').text());
    var cardOutTotalVal = parseFloat($('.cardFillOutTotal #totalVal b').text());
    var cardOutBalance = parseFloat($('.cardFillOutTotal #balance span').text());

    //订单信息
    var order_sn = $('#order_sn').val();
    var paymoney = $('#paymoney').val();
    if(!paymoney){
        paymoney = 0.0
    }else{
        paymoney = parseFloat(paymoney)
    }
    if(cardOutList.length==0){
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
    var cardListIn = getCardList($('#correctIn'));
    var totalNumIn = parseInt($('.cardInTotal #totalNum b').text());// 卡张数合计
    var totalValIn = parseFloat($('.cardInTotal #totalVal b').text());//卡合计金额
    //出卡列表
    var cardListOut = getCardList($('#correctOut'));
    var totalNumOut =parseInt($('.cardOutTotal #totalNum b').text());
    var totalValOut =parseFloat($('.cardOutTotal #totalVal b').text());

    //订单支付信息
    var payVal = parseFloat($('.Total #payTotal b').text());
    var orderVal = parseFloat($('.Total #totalPaid b').text());
    var discVal = parseFloat($('.Total #discountVal b').text());
    var discPay = parseFloat($('.Total #totalYBalance b').text());
    var cardsOutVal = parseFloat($('.Total #totalVal b').text());
    var disRate =  (parseFloat($('.Total #discount input').val()).toFixed(2))/100;
    var discCode = $('.Total #disCode').val();
    //支付列表
    var payList = getPayList($('.payList'));
    if(!payList){
        return false;
    }
    // var hjsStr = $('.payList #remark-hjs').val();

    //优惠列表信息
    var discCardList = [];
    var discCash = 0;
    if(discVal>0){
        discCardList = getCardList($('#YcardList'));
        discCash = parseFloat($('.discountTotal #Ycash').val());
    }

    //买卡人信息
    var buyerName = $('#buyerName').val();
    var buyerPhone = $('#buyerPhone').val();
    var buyerCompany = $('#buyerCompany').val();
    if(cardListIn.length==0 || totalValIn==0){
        alert('还未添加入卡信息，请核对后再尝试提交！');
        return false;
    }
    if(cardListOut.length==0 || totalValOut==0){
        alert('还未添加出卡信息，请核对后再尝试提交！');
        return false;
    }

    if(payVal!=orderVal){
        alert('出入库金额不相等！');
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
        // 'hjsStr':hjsStr,//黄金手列表
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
            if(data.status==1){
                alert('提交成功');
                window.location.reload(true);
                if(data.urlRedirect){
                    window.location.href=data.urlRedirect;
                }
            }else if(data.status==0){
                if(data.msg){
                    alert(data.msg);
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
    var cardtype = '';
    // 1、判断合计展示的位置
    if($(cardList).hasClass('discount'))//优惠管理区域
    {
        cardtype = 1;
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
    }
    else if($(cardList).hasClass('discount2'))//实物团购返点
    {
        cardtype = 1;
        cls = 'discountTotal';
        var cardsTotal = getCardListVal(cardList,cardtype,cls);
        var cardsTotalVal = cardsTotal.totalVal;
        var discVal = parseFloat($("#discTotal").val());
        if(!discVal){discVal=0}
        //补差
        discPay = parseFloat(cardsTotalVal) - parseFloat(discVal);
        $('#totalYBalance b').text(discPay);
    }
    else if($(cardList).hasClass('cardIn'))//换卡入库
    {
        cls = 'cardInTotal';
        cardtype = 2;
        setOrderInfoByCardList(cardList,cls,cardtype);
    }
    else if($(cardList).hasClass('cardOut'))//换卡出库
    {
        cardtype=1;
        cls = 'cardOutTotal';
        setOrderInfoByCardList(cardList,cls,cardtype);
    }
    else if($(cardList).hasClass('cardFillIn'))//补卡入库
    {
        cls = 'cardFillInTotal';
        cardtype = 3;
        setOrderInfoByCardFill(cardList,cls,cardtype);
    }
    else if($(cardList).hasClass('cardFillOut'))//补卡出库
    {
        cardtype=1;
        cls = 'cardFillOutTotal';
        // 2、计算卡列表的合计金额和合计张数
        var cardsTotal = getCardListVal(cardList,cardtype,cls);
        var totalVal = parseFloat(cardsTotal.totalVal).toFixed(2);
        //3、计算补卡补差
        var cardsInVal = parseFloat($('.cardFillInTotal #totalVal b').text()).toFixed(2);
        var fillCardPay = parseFloat(totalVal - cardsInVal).toFixed(1);
        $('.cardFillOutTotal #balance span').text(fillCardPay);
    }
    else{
        cardtype=1;
        cls = 'Total';
        setOrderInfoByCardList(cardList,cls,cardtype);
    }
}
function setOrderInfoByCardList(cardList,cls,cardtype) {
    // 2、计算卡列表的合计金额和合计张数
    var data = getCardListVal(cardList,cardtype,cls);
    var totalVal = data.totalVal;
    var module = $('#content').attr('data-module');
    var cardsPayVal = 0;
    if(module=='sale'){
        cardsPayVal = totalVal
    }else if(module=='change'){
        if(cardtype==1){
            var cardChangeInTotalVal = $(".cardInTotal #totalVal b").text();
            cardsPayVal = parseFloat(totalVal)-parseFloat(cardChangeInTotalVal);
        }
        else
        {
            var cardChangeOutTotalVal = $(".cardOutTotal #totalVal b").text();
            cardsPayVal = parseFloat(cardChangeOutTotalVal)-parseFloat(totalVal);
        }
        //3.1、计算补差金额
        if(cardsPayVal>0){
            $('.payment').show();
            $('.Total').show();
        }
        else {
            $('.payment').hide();
            $('.Total').hide();
            $('.payList .payVal').val('')
        }
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
function setOrderInfoByCardFill(cardList,cls,cardtype) {
    // 2、计算卡列表的合计金额和合计张数
    var data = getCardListVal(cardList,cardtype,cls);
    $(".Total #totalVal b").text(data.totalVal);
    $(".Total #totalNum b").text(data.totalNum);
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
function setTotalByOrderTotalVal(discRate,cardSaleTotalVal) {
    var discountVal = createDiscount(discRate,cardSaleTotalVal);
    //2、计算优惠补差
    var discountCardTotalVal = parseFloat($(".discountTotal #totalVal b").text());
    discountPay  = discountCardTotalVal - discountVal;
    $('.Total #totalYBalance b').text(discountPay);
    //3、计算应付金额
    $('.Total #totalPaid b').text(discountPay);
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
function checkAll(obj) {
    var _this = obj;
    $(_this).click(function(){
        var check_status=$(_this).prop('checked');
        var tbody = $(_this).parents('table').find('tbody');
        if(check_status){
            tbody.find("input[type='checkbox']").prop('checked',true);
        }else{
            tbody.find("input[type='checkbox']").prop('checked',false);
        }
    });
}

function getCheckedIdList(checkBoxList){

    var list = [] ;
    checkBoxList.find(':checked').each(function () {
        var orderSn = $(this).val();
        list.push(orderSn);
    });
    return list;
}
function getCheckedOrder(checkBoxList){
    var list = [] ;
    var totalVal = 0;
    checkBoxList.find(':checked').each(function () {
        var orderSn = $(this).attr('id');
        list.push(orderSn);
        var val = parseFloat($(this).parent().siblings('td.rowVal').text());
        totalVal += val;
    });
    return {list:list,totalVal:totalVal};
}


$(document).ready(function(){
    var parterVal = $('#parter').val();
    $('#parterId').val(parterVal);
    var blankVal = $('#blank').val();
    $('#blankId').val(blankVal);
});

