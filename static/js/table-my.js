$(document).ready(function(){
    $(document).on('click','.table tr .btn-del',function(){
        setTotal(this);
        $(this).parents('tr').remove();
    });



    $(document).on('click','.formline .btn-add',function(){
        var formBox = $(this).parent().parent().parent()[0];
        var formLine = $(this).parent().parent().clone();
        $(formBox).append(formLine)
    })
});


function addRow(obj){
    var tbody = $(obj).parent().parent().parent()[0];
    var columsL =$(tbody).find('tr').eq(0).find('td').length;

    var row = $("<tr></tr>");
    for(var i=0;i<columsL;i++){
        var td = $("<td></td>");
        if(i==0){
            var input = $("<input type='text' class='form-control cardId'>");
            $(td).append(input);
        }else if(i==columsL-1){
            var button = $('<button type="button" class="btn btn-danger btn-xs btn-del">删除</button>');
            $(td).append(button);
        }else{
            var input = $("<input type='text' class='form-control' readonly='readonly'>");
            $(td).append(input);
        }
        $(row).append(td);
        $(row).find('td').eq(0).find('input').eq(0).focus();
    }
    $(tbody).append(row);
    $(obj).parent().parent().next('tr').find('td').eq(0).find('input').focus();
}
function doAjax(obj,ajaxOpt,showCardIfno,setTotal){
    $.ajax({
        url:ajaxOpt.url,
        type:ajaxOpt.method,
        dataType:'json',
        success:function(data){
            var res = data[0] ? data[0].fields : [];
            showCardIfno(obj,res);
            setTotal(obj);
        }
    })
}
function showCardIfno(obj,data){
    var cardVal = data.card_value;

    if(data.card_status==1){
        var cardStu ='未激活';
    }else if(data.card_status==2){
        var cardStu ='已激活';
    }else if(data.card_status==3){
        var cardStu ='待作废';
    }else if(data.card_status==4){
        var cardStu ='已作废';
    }
    $(obj).parent().parent().find('td').eq(2).find('input').eq(0).val(cardVal);
    $(obj).parent().parent().find('td').eq(3).find('input').eq(0).val(cardStu);
}
function setTotal(obj){
    var parentTbody = $(obj).parent().parent().parent()[0];
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
    var parentTbody = $(obj).parent().parent().parent()[0];
    var trs = $(parentTbody).find('tr');
    var totalNum = 0;
    var totalVal = 0.00;

    for(var i=0;i<trs.length;i++){
        var status = $(trs[i]).find('td').eq(3).find('input').val();
        var val = $(trs[i]).find('td').eq(2).find('input').val();
        if(status=='未激活'){
            totalNum++;
            totalVal += parseInt(val);
        }
    }
    $('.'+cls+' #totalVal b').text(parseFloat(totalVal).toFixed(2));
    $('.'+cls+' #totalNum b').text(totalNum);

    //增卡补差
    var YtotalVal = parseFloat($('.discountTotal #totalVal b').text());
    if(YtotalVal){
        var discountVal = parseFloat($('.Total #discountVal b').text());
        var Ybalance = YtotalVal - discountVal;
        $('.discountTotal #balance b').text(Ybalance);
    }

}
/*$(document).on("keyup",".cardId",function(){
    //查询卡信息
    var cardId = $(this).val();
    var _this = $(this);
    $.ajax({
        url:ajaxUrl+"?cardId="+cardId,
        method:'get',
        dataType:'json',
        success:function(data){
            var cardInfo = data[0].fields;
            var cardVal = cardInfo.card_value;
            var cardStu = cardInfo.card_status;
            $(_this).parent().parent().find('td').eq(2).find('input').eq(0).val(cardVal);
            $(_this).parent().parent().find('td').eq(3).find('input').eq(0).val(cardStu);

            //table增加一行空白记录
            var tbody = $(_this).parent().parent().parent()[0];
            var columsL =$(tbody).find('tr').eq(0).find('td').length;
            var trsL = $(tbody).find('tr').length;

            var row = $("<tr></tr>");
            for(var i=0;i<columsL;i++){
                var td = $("<td></td>");
                if(i==0){
                    var input = $("<input type='text' class='form-control cardId'>");
                }else{
                    var input = $("<input type='text' class='form-control' readonly='readonly'>");
                }
                $(td).append(input);
                $(row).append(td);
                $(row).find('td').eq(0).find('input').eq(0).focus();
            }
            $(tbody).append(row);
            $(_this).parent().parent().next('tr').find('td').eq(0).find('input').focus();

            //计算合计
            var parentTbody = $(_this).parent().parent().parent()[0];
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
            $('.'+cls+' #totalNum b').text(trsL);
            var totalVal = 0;
            for(var j=0;j<trsL;j++){
                var val = $(tbody).find('tr').eq(j).find('td').eq(2).find('input').val();
                val = val!=='' ? parseInt(val): 0.00;
                totalVal +=  val;
            }
            $('.'+cls+' #totalVal b').html(parseFloat(totalVal).toFixed(2));
        }
    });




        });*/
$(document).on('blur','.payList tr',function(){
    palyList = $('.payList').find('tr');
    var totalStr = '';
    var payTotal=0;
    for(var i=0;i<palyList.length;i++){
        var checkBox = $(palyList[i]).find('td').eq(0).find('input')[0];
        var flag = $(checkBox).is(':checked');
        var payName = '';
        var payVal = '';
        if(flag){
            if($(palyList[i]).find('td').eq(1).find('select')[0]){
                payName = $(palyList[i]).find('td').eq(1).find('select option:selected').text();
            }else{
                payName = $(palyList[i]).find('td').eq(1).find('input').val();
            }
            payVal= $(palyList[i]).find('td').eq(2).find('input').val();
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


//支付方式--三方平台
$(document).on('change','.payList #parter',function(){
    var val = $(this).val();
    var parentTr = $(this).parent().parent();
    $(parentTr).find('td').eq(0).find('input').val(val);
});
$(document).ready(function(){
    var parterVal = $('#parter').val();
    $('#parterId').val(parterVal)
});





