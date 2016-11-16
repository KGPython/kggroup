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
    setTotal(parnetTbody);
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
//卡校验信息展示
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

// 更换卡展示信息
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
* 补卡模块----查询卡信息
* */
function doAjax2(obj,ajaxOpt,showCardIfno,setTotal){
    $.ajax({
        url:ajaxOpt.url,
        type:ajaxOpt.method,
        dataType:'json',
        success:function(data){
            showCardIfno(obj,data);
            var parnetTbody = $(obj).parent().parent().parent()[0];
            if(setTotal){
                setTotal(parnetTbody);
            }
        }
    })
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
* 计算优惠金额
* */
function createDiscount(cardsValTotal,rateInput) {
    var discCode = $(".Total #disCode input").val();
    //如果折扣授权码discCode存在，则认为是自定义折扣，取输入框内部的数值为折扣返点率
    //如果折扣授权码discCode不存在，则认为是固定返点，由系统生成折扣返点率
    var  rate= 0;
    if(discCode){
        rate = (parseFloat($(".Total #discount input").val()).toFixed(2))/100;
    }else {
        if(typeof(rates)!='undefined'){
            for(var j=0;j<rates.length;j++){
                if(rates[j].val_min<=parseFloat(cardsValTotal) && rates[j].val_max>=parseFloat(cardsValTotal)){
                    rate=rates[j].discount_rate;
                }
            }

            $(rateInput).val(rate*100);
        }
    }
    var discountVal = (parseFloat(cardsValTotal)*rate/10).toString().split(".")[0]+'0';
    $('.Total #discountVal b').text(discountVal);
    if(discountVal>0){
        $('.discBox').show();
    }else {
        $('.discBox').hide();
        $('.discountTotal #totalVal b').text(0)
    }
    return discountVal;
}

/*
* 根据出入库，产生“合计”区域相关信息
* obj：卡列表的tbody
* cardtype：出卡为1，入卡为2
* */
function setTotal(obj){
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
        //$('.discountTotal #balance b').text(discountPay);//设置“优惠管理”区域->应补差额
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
            $('.Total #totalVal b').text(cardsPayVal);
            //3.2、计算优惠返点
            var rateInput  = $('.Total #discount input')[0];
            var discountVal = createDiscount(cardsPayVal,rateInput);
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
        var fillCardPayInput  = $('.cardOutTotal #balance b');
        if(fillCardPayInput.length>0){
            var cardsOutVal = parseFloat($('.cardOutTotal #totalVal b').text());
            if(cardsOutVal!=undefined){
                var cardsInVal = parseFloat($('.cardInTotal #totalVal b').text());
                cardsInVal = isNaN(cardsInVal) ? 0:cardsInVal;
                fillCardPay = cardsOutVal - cardsInVal;
                $('.cardOutTotal #balance b').text(fillCardPay);
            }
        }
        //3、如果是换卡模块，则计算换卡补差
        var Paybox = $(".Total");
        if(Paybox.length>0){
            //3.1、计算补差金额
            var cardChangeInTotalVal = $(".cardInTotal #totalVal b").text();
            var cardsPayVal = parseFloat(cardsTotalVal)-parseFloat(cardChangeInTotalVal);
            $('.Total #totalVal b').text(cardsPayVal);
            //3.2、计算优惠返点
            var rateInput  = $('.Total #discount input')[0];
            var discountVal = createDiscount(cardsPayVal,rateInput);

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
        //3、计算销售返点
        var rateInput  = $('.'+cls+' #discount input')[0];
        var discountVal=0;
        if(rateInput){
            discountVal = createDiscount(cardsTotalVal,rateInput);
        }
        //4、优惠补差
        var discountCardTotalVal = parseFloat($(".discountTotal #totalVal b").text());
        discountPay  = discountCardTotalVal - discountVal;
        //$('.discountTotal #balance b').text(discountPay);//设置“优惠管理”区域->应补差额
        $('.Total #totalYBalance b').text(discountPay);//设置“合计”区域->优惠补差
        //5、设置订单应付金额 = 售卡列表合计金额 + 优惠补差
        $('.Total #totalPaid b').text(cardsTotalVal+discountPay);
    }

    /*// 2、计算卡列表的合计金额和合计张数
    var cardsTotal = getCardListVal(cardList,cardtype,cls);
    var cardsValTotal = cardsTotal.totalVal;
    var cardsNumTotal = cardsTotal.totalNum;



    // 优惠管理--应补差额=优惠卡列表合计-返点金额
    var discountTotal = parseFloat($('.discountTotal #totalVal b').text());
    if(discountTotal!=undefined){
        console.log(discountTotal,discountVal);
        var disBalance = discountTotal - discountVal;
        $('.discountTotal #balance b').text(disBalance);
    }*/

   //补卡补差
    var Ybalance = 0;
    var YtotalVal = parseFloat($('.cardOutTotal #totalVal b').text());
    if(YtotalVal!=undefined){
        // var discountVal = parseFloat($('.cardInTotal #totalVal b').text());
        // discountVal = isNaN(discountVal) ? 0:discountVal;

        Ybalance = YtotalVal - discountVal;
        $('.cardOutTotal #balance b').text(Ybalance);
    }

    //展示最终应缴合计金额=售卡合计+优惠补差
    /*var totalPaidObj = $('.Total #totalPaid b')[0];
    if(totalPaidObj){//如果是汇总合计区域，展示最终缴费合计数额
        //优惠补差
        // var Ybalance = parseFloat($('.discountTotal #balance b').text());
        //售卡合计金额
        // var totalCardVal = parseFloat($('.Total #totalVal b').text());
        // totalCardVal = isNaN(totalCardVal) ? 0:totalCardVal;
        // var totalPaid = totalCardVal + Ybalance;
        var totalPaid = cardsValTotal + discountTotal;
        $(totalPaidObj).text(totalPaid);
        $('.Total #totalYBalance b').text(discountTotal)
    }*/
}

//自定义折扣授权验证
$('#disBtn').click(function(){
    $('#disCode').toggle();
});


function checkDiscode(url){
    $.ajax({
        url:url,
        dataType:'json',
        method:'get',
        success:function(data){
            if(data.msg=='0'){
                $("#discount input").removeAttr('disabled').focus().val('')
            }else{
                alert('授权码无效')
            }
        }
    })
}
/***************************************************折扣返点  start****************************************************/

//自定义返点，生成优惠金额
$('.Total #discount input').blur(function(){
    //设置返点金额
    var rate = $(this).val()/100;
    var cardSaleTotalVal = parseFloat($('.Total #totalVal b').text());
    var discount = parseFloat(rate*cardSaleTotalVal).toFixed(2);
    $('.Total #discountVal b').text(discount);
    //设置优惠补差金额
    //var discCardTotal = getCardListVal($(".discount"),1).totalVal;
    var discCardTotal = parseFloat($(".discountTotal #totalVal b").text());
    var discPay = discCardTotal-discount;
    $(".Total #totalYBalance b").text(discPay);
    //设置应付金额
    var orderVal = cardSaleTotalVal + discPay;
    $('.Total #totalPaid b').text(orderVal);
    $('.discBox').show();
});

/*
* 当填写优惠返现时，更改相关金额信息
* act:当前操作类型
* obj：优惠返现input输入框
* */
function discCash(act) {
    //1、获取优惠返现金额
    // var Ycash = parseFloat($(obj).val());
    // Ycash = isNaN(Ycash)?0:parseFloat(Ycash);
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

    /*if(act=='sale'){


    }
    if(act=='change'){
        //3、计算优惠补差金额
        //3.1、获取优惠返点金额
        var discountVal = parseFloat($('.Total #discountVal b').text());
        discountVal = isNaN(discountVal) ? 0:discountVal;
        //3.2、优惠补差金额
        var discPay = discCardTotalVal - discountVal;
        $('.Total #totalYBalance b').text(discPay);
    }*/

}

/***************************************************折扣返点  end****************************************************/
//获取卡号
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
    var disCode = $('.Total #disCode input').val();
    var discountVal = parseFloat($('.Total #discountVal b').text());//优惠金额（总合计内）
    //赠卡列表
    var YcardList = getCardList($('#YcardList'),'1');
    var YtotalNum =parseInt($('.discountTotal #totalNum b').text());
    var Ycash = parseFloat($('#Ycash').val());//优惠返现
    var YtotalVal =parseFloat($('.discountTotal #totalVal b').text());//优惠列表合计=卡合计+返现合计
    //var Ybalance =parseFloat($('.discountTotal #balance b').text());//优惠补差
    //支付列表
    var payList = getPayList($('.payList'));
    var hjsStr = $('.payList #remark-hjs').val();
    //买卡人信息
    var buyerName = $('#buyerName').val();
    var buyerPhone = $('#buyerPhone').val();
    var buyerCompany = $('#buyerCompany').val();
    if(totalVal==0){
        alert('还未添加售卡信息，请核对后再尝试提交！');
        return false;
    }
    if(payTotal!=totalVal+discPay){
        alert('交款合计金额与售卡合计金额不匹配，请核对后再尝试提交！');
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
        csrfmiddlewaretoken: '{{ csrf_token }}',
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
        'buyerCompany':buyerCompany

    };
    doAjaxSave(url,data);
}



//获取补卡信息列表
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
        csrfmiddlewaretoken: '{{ csrf_token }}',
        'cardInStr':JSON.stringify(cardInList),
        'cardInTotalNum':cardInTotalNum,
        'cardInTotalVal':cardInTotalVal,
        'user_name':user_name,
        'user_phone':user_phone,
        'action_type':action_type
    };
    doAjaxSave(url,data);
}

function updateCardFillOrder(url,target_url){
    //入卡列表
    var cardOutList = getCardFillList($('#cardOutList'),"1");
   
    var cardOutTotalNum = parseInt($('.cardOutTotal #totalNum b').text());
    var cardOutTotalVal = parseFloat($('.cardOutTotal #totalVal b').text());
    var cardOutBalance = parseFloat($('.cardOutTotal #balance b').text());

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

    $.ajax({
        url:url,
        type:'post',
        dataType:'json',
        data:{
            csrfmiddlewaretoken: '{{ csrf_token }}',
            'cardOutStr':JSON.stringify(cardOutList),
            'cardOutTotalNum':cardOutTotalNum,
            'cardOutTotalVal':cardOutTotalVal,
            'order_sn':order_sn,
            'paymoney':paymoney
        },
        success:function(data){
            if(data.msg==1){
                alert('操作成功');
                window.location.reload(true);
                window.location.href=target_url;
            }else if(data.msg==0){
                if(data.msg_err){
                    alert(data.msg_err);
                }else{
                    alert('操作失败');
                }
            }
        },
        error:function(XMLHttpRequest, textStatus, errorThrown){
            alert(errorThrown);
        }
    })
}

Array.prototype.remove = function(val) {
    var index = this.indexOf(val);
    if (index > -1) {
    this.splice(index, 1);
    }
};

// 更换卡
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

    var discCode = $('.Total #disCode input').val();
    //优惠列表信息
    var discCardList = [];
    var discCardsVal = 0;
    var discCash = 0;
    //支付列表
    var payList = getPayList($('.payList'));
    var hjsStr = $('.payList #remark-hjs').val();

    if(discVal>0){
        discCardList = getCardList($('#YcardList'),'1');
        discCardsVal = parseFloat($('.discountTotal #totalVal b').text());
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
        alert('请核对支付金额后再尝试提交！');
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
        csrfmiddlewaretoken: '{{ csrf_token }}',
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
        'buyerCompany':buyerCompany
    };

    doAjaxSave(url,data);
}
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
                alert('订单提交成功');
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
                    alert('订单提交失败');
                }
            }
        },
        error:function(XMLHttpRequest, textStatus, errorThrown){
             $("#btn-enter").removeAttr('disabled');
            alert('订单提交失败,失败原因：'+errorThrown);
        }
    })
}
// 更换卡计算合计
function setTotal3(obj){
    var parentTbody = obj;
    var cls = '';
    if($(parentTbody).hasClass('cardIn')){
        cls = 'cardInTotal';
    }else if($(parentTbody).hasClass('cardOut')){
        cls = 'cardOutTotal';
    }

    //计算合计
    var trs = $(parentTbody).find('tr');
    var totalNum = 0;
    var totalVal = 0.00;

    for(var i=0;i<trs.length;i++){
        var status = $(trs[i]).find('td').eq(3).find('input').val();
        var val = $(trs[i]).find('td').eq(2).find('input').val();
        var type = $(trs[i]).find('td').eq(1).find('input').val();
        if(cls=='cardOutTotal'){
            if(status=='未激活'&& parseFloat(val)==parseFloat(type)){
                totalNum++;
                totalVal += parseFloat(val);
            }
        }else if(cls=='cardInTotal'){
            if(status=='已激活' && parseFloat(val)==parseFloat(type)){
                totalNum++;
                totalVal += parseFloat(val);
            }
        }
    }

    $('.'+cls+' #totalVal b').text(parseFloat(totalVal).toFixed(2));
    $('.'+cls+' #totalNum b').text(totalNum);
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


//支付列表，三方平台切换
$(document).on('change','.payList #parter',function(){
    var val = $(this).val();
    var parentTr = $(this).parent().parent();
    $(parentTr).find('td').eq(0).find('input').val(val);
});

//支付方式--银行打款
var posVal = 0;
$(document).on('change','.payList #blank',function(){
    var val = $(this).val();
    var parentTr = $(this).parent().parent();
    $(parentTr).find('td').eq(0).find('input').val(val);
});
//获取支付列表
function getPayList(obj){
    var list = [];
    var trs = $(obj).find('tr');
    for(var j=0;j<trs.length;j++){
        var item = {};
        var checkBox = $(trs[j]).find('td').eq(0).find('input')[0];
        var flag = $(checkBox).is(':checked');
        if(flag){
            var payId = $(checkBox).val();
            var payVal= $(trs[j]).find('td').eq(2).find('input').val();
            var payRmarks = $(trs[j]).find('td').eq(3).find('input').val();
            item = {'payId':payId,'payVal':payVal,'payRmarks':payRmarks};
            list.push(item)
        }
    }
    return list;
}

/*
* 计算返点金额
* cardSaleTotalVal：cardSaleTotalVal：售卡总金额
* posVal：pos刷卡金额
* */
function changeDiscountVal(cardSaleTotalVal,posVal) {
    if(cardSaleTotalVal-posVal>=rates[0].val_min){
        //4、计算销售返点
        var rateInput  = $('.Total #discount input')[0];
        var discountVal=0;
        if(rateInput){
            discountVal = createDiscount(cardSaleTotalVal,rateInput);
        }
        //计算补差
        var discountCardTotalVal = parseFloat($(".discountTotal #totalVal b").text());
        discountPay  = discountCardTotalVal - discountVal;
        //$('.discountTotal #balance b').text(discountPay);//设置“优惠管理”区域->应补差额
        $('.Total #totalYBalance b').text(discountPay);//设置“合计”区域->优惠补差
        //6、设置订单应付金额 = 售卡列表合计金额 + 优惠补差
        $('.Total #totalPaid b').text(cardSaleTotalVal+discountPay);
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

//计算混合支付的合计金额
$(document).on('blur','.payList tr',function(){
    palyList = $('.payList').find('tr');
    var totalStr = '';
    var payTotal=0;
    for(var i=0;i<palyList.length;i++){
        var checkBox = $(palyList[i]).find('td').eq(0).find('input')[0];
        var flag = $(checkBox).is(':checked');
        var payName = '';
        var payVal= $(palyList[i]).find('td').eq(2).find('input').val();
        if(flag && payVal){
            if($(palyList[i]).find('td').eq(1).find('select')[0]){
                payName = $(palyList[i]).find('td').eq(1).find('select option:selected').text();
                //处理pos刷卡与现金的返点差异问题
                //规则：1、订单超过最小返点金额+1000，则现金与pos的返点无差异；
                //      2、订单金额在最小返点金额和最小返点金额+1000之间，返点区分现金与pos
                //1、判断订单金额
                var cardSaleTotalVal = parseFloat($(".Total #totalVal b").text());
                //如果售卡金额合计在各门店：最小返点金额和最小返点金额+1000之间，则进行区别
                if(cardSaleTotalVal<(rates[0].val_min+1000) && cardSaleTotalVal>=rates[0].val_min && disc_level=='1'){
                    //2、判断支付方式
                    var payId = $(palyList[i]).find('td').eq(1).find('select option:selected').val();
                    if(payId == 5){
                        var posVal =  parseFloat($(palyList[i]).find('td').eq(2).find('input').val());
                        changeDiscountVal(cardSaleTotalVal,posVal)
                    }
                }
            }else{
                payName = $(palyList[i]).find('td').eq(1).find('input').val();
            }
            totalStr += payName +' : '+payVal+'元 ';
            remarks = $(palyList[i]).find('td').eq(3).find('input').val();
            if(remarks){
                totalStr += '(备注：'+remarks+'), ';
            }else{
                totalStr += ', ';
            }
            payTotal +=parseFloat(payVal);
        }

        $('.Total #payInfo span').html(totalStr);
        $('.Total #payTotal b').html(payTotal)
    }
});

/******************************  支付相关 end   *****************************************/