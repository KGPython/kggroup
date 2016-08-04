$(document).ready(function(){
    var parterVal = $('#parter').val();
    $('#parterId').val(parterVal);
    var blankVal = $('#blank').val();
    $('#blankId').val(blankVal)
});

//删除tr
$(document).on('click','.table tr .btn-del',function(){
    var parnetTbody = $(this).parent().parent().parent()[0];
    $(this).parents('tr').remove();
    cardType='1';
    setTotal(parnetTbody,cardType);
});

$(document).on('click','.formline .btn-add',function(){
    var formBox = $(this).parent().parent().parent();
    var formLine = $(this).parent().parent().clone();
    formBox.append(formLine);
    formLine.find('input').val('');

});


function addRow(obj,target){
    var tbody = $(obj).parent().parent().parent()[0];
    var columsL =$(tbody).find('tr').eq(0).find('td').length;

    var row = $("<tr></tr>");
    for(var i=0;i<columsL;i++){
        var td = $("<td></td>");
        if(target=='changeCode'){
            if(i==0 || i==1){
                var input = $("<input type='text' class='form-control'>");
                $(td).append(input);
            }else if(i==columsL-1){
                var button = $('<button type="button" class="btn btn-danger btn-xs btn-del">删除</button>');
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
                var button = $('<button type="button" class="btn btn-danger btn-xs btn-del">删除</button>');
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

//卡校验 cardType-业务类型：1-出卡，2-入卡
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
    if(data.length==0){
         var cardStu ='不存在';
    }

    var cardVal = data.card_value;
    var cardBlance = data.card_blance;

    if(data.card_status==1){
        var cardStu ='未激活';
    }else if(data.card_status==2){
        var cardStu ='已激活';
    }else if(data.card_status==3){
        var cardStu ='已冻结';
    }else if(data.card_status==4){
        var cardStu ='已作废';
    }

    if(data.card_status!=1 || cardVal!=cardBlance){
        $(obj).parent().parent().find('td').eq(3).find('input').eq(0).addClass('red')
    }else{
        $(obj).parent().parent().find('td').eq(3).find('input').eq(0).removeClass('red')
    }

    $(obj).parent().parent().find('td').eq(1).find('input').eq(0).val(cardVal);
    $(obj).parent().parent().find('td').eq(2).find('input').eq(0).val(cardBlance);
    $(obj).parent().parent().find('td').eq(3).find('input').eq(0).val(cardStu);
}

function doAjax2(obj,ajaxOpt,showCardIfno,setTotal,cardType){
    $.ajax({
        url:ajaxOpt.url,
        type:ajaxOpt.method,
        dataType:'json',
        success:function(data){
            showCardIfno(obj,data);
            var parnetTbody = $(obj).parent().parent().parent()[0];
            if(setTotal){
                setTotal(parnetTbody,cardType);
            }
        }
    })
}
//补卡卡校验信息展示
function showCardIfno2(obj,data){
    var cardVal = data.card_value;
    var cardBlance = data.card_blance;

    if(data.card_status=='1'){
        var cardStu ='已激活';
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
    $(obj).parent().parent().find('td').eq(1).find('input').eq(0).val(cardVal);
    $(obj).parent().parent().find('td').eq(2).find('input').eq(0).val(cardBlance);
    $(obj).parent().parent().find('td').eq(3).find('input').eq(0).val(cardStu);
}

$('.Total #discount input').blur(function(){
    var rate = $(this).val()/100;
    var totalVal = parseFloat($('.Total #totalVal b').text());
    var discount = rate*totalVal;
    $('.Total #discountVal b').text(discount);

});
/*
* 计算卡列表合计信息
* obj：卡列表的tbody
* cardtype：出卡为1，入卡为2
* */
function setTotal(obj,cardtype){
    var parentTbody = obj;
    var cls = '';
    if($(parentTbody).hasClass('discount')){
        cls = 'discountTotal';
    }else if($(parentTbody).hasClass('cardIn')){
        cls = 'cardInTotal';
    }else if($(parentTbody).hasClass('cardOut')){
        cls = 'cardOutTotal';
    }else{
        cls = 'Total';
    }

    //计算合计
    var trs = $(parentTbody).find('tr');
    var totalNum = 0;
    var totalVal = 0.00;

    for(var i=0;i<trs.length;i++){
        var status = $(trs[i]).find('td').eq(3).find('input').val();
        var val = $(trs[i]).find('td').eq(2).find('input').val();
        var type = $(trs[i]).find('td').eq(1).find('input').val();
        if(cardtype=='1'){
            if(status=='未激活'&& parseFloat(val)==parseFloat(type)){
                totalNum++;
                totalVal += parseFloat(val);
            }
        }else if(cardtype=='2'){
            if(status=='已激活'){
                totalNum++;
                totalVal += parseFloat(val);
            }
        }
    }

    //处理优惠返现
    var Ycash=$('.'+cls).find('#Ycash').length;
    console.log($('.'+cls));
    if(Ycash>0){
        var Ycash=$('#Ycash').val();
        Ycash = Ycash=='' ?0:parseFloat(Ycash);
        totalVal +=Ycash;
    }
    $('.'+cls+' #totalVal b').text(parseFloat(totalVal).toFixed(2));
    $('.'+cls+' #totalNum b').text(totalNum);

    var rateInput  = $('.Total #discount input')[0];
    var rate= 0,discountVal=0;
    if(rateInput){
        if(typeof(rates)!='undefined'){
            for(var j=0;j<rates.length;j++){
                if(rates[j].val_min<=parseFloat(totalVal) && rates[j].val_max>=parseFloat(totalVal)){
                    rate=rates[j].discount_rate;
                    discountVal = Math.round(parseFloat(totalVal)*rate);
                }
                $(rateInput).val(rate*100);
                $('.Total #discountVal b').text(discountVal);
            }
        }
    }

    //赠卡补差
    var YtotalVal = parseFloat($('.discountTotal #totalVal b').text());
    discountVal = parseFloat($('.Total #discountVal b').text());
    if(YtotalVal && discountVal){
        discountVal = isNaN(discountVal) ? 0:discountVal;
        var Ybalance = YtotalVal - discountVal;
        $('.discountTotal #balance b').text(Ybalance);
    }
   //补卡补差
    var YtotalVal = parseFloat($('.cardOutTotal #totalVal b').text());
    if(YtotalVal!=undefined){
        var discountVal = parseFloat($('.cardInTotal #totalVal b').text());
        var Ybalance = YtotalVal - discountVal;
        $('.cardOutTotal #balance b').text(Ybalance);
    }
}
//优惠返现
$('#Ycash').blur(function(){
    var Ycash = parseFloat($(this).val());
    Ycash = Ycash=='' ?0:parseFloat(Ycash);
    var trs = $('#YcardList').find('tr');
    var totalVal = Ycash;
    for(var i=0;i<trs.length;i++){
        var status = $(trs[i]).find('td').eq(3).find('input').val();
        var val = $(trs[i]).find('td').eq(2).find('input').val();
        var type = $(trs[i]).find('td').eq(1).find('input').val();
        if(status=='未激活'&& parseFloat(val)==parseFloat(type)){
            totalVal += parseFloat(val);
        }
    }
    $('.discountTotal #totalVal b').text(totalVal)
});
//获取卡号
function getCardIds(obj){
    var list = [];
    var trs = $(obj).find('tr');
    for(var j=0;j<trs.length;j++){
        var cardId = $(trs[j]).find('td').eq(0).find('input').val();
        if(cardId){
            list.push(cardId)
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
//黄金手--开关
$('.payList #hjs').click(function(){
    var flag = $(this).is(':checked');
    if(flag){
        $('#hjsBox').show()
    }
});
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
    $('.payList #hjsVal').focus();
    $('#hjsBox').hide();
});
//黄金手--校验
$(document).on('click','#hjsBox .hCost',function(){
    var _this = $(this);
    var parentTr = _this.parent().parent();
    var hNo = parentTr.find('td').eq(0).find('input').val();
    var hPassword = parentTr.find('td').eq(1).find('input').val();
    if(!hNo||!hPassword){
        alert('卡号和卡密不能为空！');
        return false;
    }
    addRow(_this,'changeCode');
    $.ajax({
        url:'/kg/sellcard/changcodecheck/',
        method:'post',
        dataType:'json',
        data:{
            'code':hNo,
            'camilo':hPassword
        },
        success:function(data){
            if(data.cost){
                parentTr.find('td').eq(2).find('input').val(data.cost);
            }else{
                parentTr.find('td').eq(2).find('input').val('0');
            }
        }
    })
});

//支付方式--三方平台
$(document).on('change','.payList #parter',function(){
    var val = $(this).val();
    var parentTr = $(this).parent().parent();
    $(parentTr).find('td').eq(0).find('input').val(val);
});
//支付方式--银行打款
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
//支付合计
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

function saveCardSaleOrder(action_type,url){
    //售卡列表
    var cardList = getCardList($('#cardList'),'1');
    var totalNum = parseInt($('.Total #totalNum b').text());
    var totalVal = parseFloat($('.Total #totalVal b').text());//卡合计金额
    var payTotal = parseFloat($('.Total #payTotal b').text());//支付合计
    var discount = parseFloat($('.Total #discount input').val());
    var discountVal = parseFloat($('.Total #discountVal b').text());
    //赠卡列表
    var YcardList = getCardList($('#YcardList'),'1');
    var YtotalNum =parseInt($('.discountTotal #totalNum b').text());
    var Ycash = parseFloat($('#Ycash').val());//优惠返现
    var YtotalVal =parseFloat($('.discountTotal #totalVal b').text());
    var Ybalance =parseFloat($('.discountTotal #balance b').text());//优惠补差
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
    if(payTotal!=totalVal){
        alert('交款合计金额与售卡合计金额不匹配，请核对后再尝试提交！');
        return false;
    }
    if(discountVal>0 && YtotalVal==0){
        alert('请完善优惠列表后再尝试提交！');
        return false;
    }
    $.ajax({
        url:url,
        type:'post',
        dataType:'json',
        data:{
            csrfmiddlewaretoken: '{{ csrf_token }}',
            'actionType':action_type,
            'cardStr':JSON.stringify(cardList),
            'totalNum':totalNum,
            'totalVal':totalVal,
            'discount':discount,
            'YcardStr':JSON.stringify(YcardList),
            'YtotalNum':YtotalNum,
            'Ycash':Ycash,
            'YtotalVal':YtotalVal,
            'Ybalance':Ybalance,//
            'payStr':JSON.stringify(payList),
            'hjsStr':hjsStr,
            'buyerName':buyerName,
            'buyerPhone':buyerPhone,
            'buyerCompany':buyerCompany

        },
        success:function(data){
            if(data.msg==1){
                alert('订单提交成功');
                window.location.reload();
                $('input[type=text]').not('.payName').val('');
                $('input[type=checkbox]').prop('checked',false);
            }else if(data.msg==0){
                alert('订单提交失败');
            }
        },
        error:function(XMLHttpRequest, textStatus, errorThrown){
            alert('订单提交失败,失败原因：'+errorThrown);
        }
    })
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

    $.ajax({
        url:url,
        type:'post',
        dataType:'json',
        data:{
            csrfmiddlewaretoken: '{{ csrf_token }}',
            'cardInStr':JSON.stringify(cardInList),
            'cardInTotalNum':cardInTotalNum,
            'cardInTotalVal':cardInTotalVal,
            'user_name':user_name,
            'user_phone':user_phone,
            'action_type':action_type
        },
        success:function(data){
            if(data.msg==1){
                alert('订单提交成功');
                window.location.reload();
            }else if(data.msg==0){
                alert('订单提交失败');
            }
        },
        error:function(XMLHttpRequest, textStatus, errorThrown){
            alert(errorThrown);
        }
    })
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
            'paymoney':paymoney,
        },
        success:function(data){
            if(data.msg==1){
                alert('操作成功');
                window.location.href=target_url;
            }else if(data.msg==0){
                alert('操作失败');
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
function saveCardChangeOrder(action_type,url){
    //入卡列表
    var cardListIn = getCardList($('#ListIn'),'2');
    var totalNumIn = parseInt($('.cardInTotal #totalNum b').text());// 卡张数合计
    var totalValIn = parseFloat($('.cardInTotal #totalVal b').text());//卡合计金额
    //出卡列表
    var cardListOut = getCardList($('#ListOut'),'1');
    var totalNumOut =parseInt($('.cardOutTotal #totalNum b').text());
    var totalValOut =parseFloat($('.cardOutTotal #totalVal b').text());
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
    if(totalValIn!=totalValOut){
        alert('入卡出卡合计面值不匹配，请核对后再尝试提交！');
        return false;
    }
    $.ajax({
        url:url,
        type:'post',
        dataType:'json',
        data:{
            csrfmiddlewaretoken: '{{ csrf_token }}',
            'actionType':action_type,
            'cardListIn':JSON.stringify(cardListIn),
            'totalNumIn':totalNumIn,
            'totalValIn':totalValIn,
            'cardListOut':JSON.stringify(cardListOut),
            'totalNumOut':totalNumOut,
            'totalValOut':totalValOut,
            // 支付人信息
            'buyerName':buyerName,
            'buyerPhone':buyerPhone,
            'buyerCompany':buyerCompany

        },
        success:function(data){
            if(data.msg==1){
                alert('订单提交成功');
                window.location.reload();
                $('input[type=text]').not('.payName').val('');
                $('input[type=checkbox]').prop('checked',false);
            }else if(data.msg==0){
                alert('订单提交失败');
            }
        },
        error:function(XMLHttpRequest, textStatus, errorThrown){
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

// 更换卡展示信息
function showCardIfno3(obj,data){
    var parentTbody = $(obj).parent().parent().parent()[0];
    var cls = '';

    if($(parentTbody).hasClass('cardIn')){
        cls = 'cardInTotal';
    }else if($(parentTbody).hasClass('cardOut')){
        cls = 'cardOutTotal';
    }

    if(data.length==0){
         var cardStu ='不存在';
    }
    var cardVal = data.card_value;
    var cardBlance = data.card_blance;

    if(data.card_status==1){
        var cardStu ='未激活';
    }else if(data.card_status==2){
        var cardStu ='已激活';
    }else if(data.card_status==3){
        var cardStu ='已冻结';
    }else if(data.card_status==4){
        var cardStu ='已作废';
    }

    if(cls == 'cardInTotal'){
        if(data.card_status!=2 || cardVal!=cardBlance){
            $(obj).parent().parent().find('td').eq(3).find('input').eq(0).addClass('red')
        }else{
            $(obj).parent().parent().find('td').eq(3).find('input').eq(0).removeClass('red')
        }
    }
    if(cls == 'cardOutTotal') {
        if(data.card_status!=1 || cardVal!=cardBlance){
            $(obj).parent().parent().find('td').eq(3).find('input').eq(0).addClass('red')
        }else{
            $(obj).parent().parent().find('td').eq(3).find('input').eq(0).removeClass('red')
        }
    }

    $(obj).parent().parent().find('td').eq(1).find('input').eq(0).val(cardVal);
    $(obj).parent().parent().find('td').eq(2).find('input').eq(0).val(cardBlance);
    $(obj).parent().parent().find('td').eq(3).find('input').eq(0).val(cardStu);
}


