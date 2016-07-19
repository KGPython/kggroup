$(document).ready(function(){
    $(document).on('click','.table tr .btn-del',function(){
        $(this).parents('tr').remove();
    });
    /*$('.widget-box .btn-add').click(function(){
        var table = $(this).parent().parent().siblings('.widget-content').find('table')[0];
        var thead = $(table).find('thead')[0];
        var tbody = $(table).find('tbody')[0];
        var columsL = $(thead).find('tr').find('th').length;
        var row = $("<tr></tr>");
        for(var i=0;i<columsL;i++){
            var td = $("<td></td>");
            if(i==0){
                var input = $("<input type='text' class='form-control'>");
            }else if(i==columsL-1){
                var input = $('<button type="button" class="btn btn-danger btn-xs btn-del">删除</button>');
            }else{
                var input = $('<input type="text" class="form-control" readonly="readonly">');
            }
            $(td).append(input);
            $(row).append(td);
        }
        $(tbody).append(row)
    });*/


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
            if(data[0]){
                var res = data[0].fields;
                showCardIfno(obj,res);
                setTotal(obj,res);
            }
        }
    })
}
function showCardIfno(obj,data){
    var cardVal = data.card_value;
    var cardStu = data.card_status;
    $(obj).parent().parent().find('td').eq(2).find('input').eq(0).val(cardVal);
    $(obj).parent().parent().find('td').eq(3).find('input').eq(0).val(cardStu);
}
function setTotal(obj,data){
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
    var totalNum = parseInt($('.'+cls+' #totalNum b').text());
    var totalVal = parseFloat($('.'+cls+' #totalVal b').text());
    totalVal += parseInt(data.card_value);
    totalNum++;

    $('.'+cls+' #totalVal b').text(parseFloat(totalVal).toFixed(2));
    $('.'+cls+' #totalNum b').text(totalNum);

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
$(document).on('click','#pay-btn',function(){
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
            totalStr += payName +' : '+payVal+'元, ';
            $('.Total #payInfo span').html(totalStr);
            payTotal +=parseFloat(payVal);
            $('.Total #payTotal b').html(payTotal)
        }
    }
});
$(document).on('blur','.payList .payVal',function(){
    var totalStr = $('.Total #payInfo span').text();
    var parentTr = $(this).parent().parent();
    var checkBox = $(parentTr).find('td').eq(0).find('input')[0];
    var flag = $(checkBox).is(':checked');
    var payName = '';
    var payVal = '';
    if(flag){
        if($(parentTr).find('td').eq(1).find('select')[0]){
            payName = $(parentTr).find('td').eq(1).find('select option:selected').text();
        }else{
            payName = $(parentTr).find('td').eq(1).find('input').val();
        }
        payVal= $(parentTr).find('td').eq(2).find('input').val();
        totalStr += payName +' : '+payVal+', ';
        $('.Total #payInfo span').html(totalStr)
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





