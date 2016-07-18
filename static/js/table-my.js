$(document).ready(function(){
    $(document).on('click','.table tr .btn-del',function(){
        $(this).parents('tr').remove();
    });
    $('.widget-box .btn-add').click(function(){
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
    });


    $(document).on('click','.formline .btn-add',function(){
        var formBox = $(this).parent().parent().parent()[0];
        var formLine = $(this).parent().parent().clone();
        $(formBox).append(formLine)
    })
});



//$('.table').find('.cardId').eq(0).focus();
$(document).on("keyup",".cardId",function(){
    var tbody = $(this).parent().parent().parent()[0];
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
    $(this).parent().parent().next('tr').find('td').eq(0).find('input').focus();

    var parentTbody = $(this).parent().parent().parent()[0];
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
        val = val!='' ? parseFloat(val).toFixed(2): 0.00;
        totalVal +=  val;
    }
    $('.'+cls+' #totalVal b').text(totalVal);
});
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
                payName = $(palyList[i]).find('td').eq(1).find('select').val();
            }else{
                payName = $(palyList[i]).find('td').eq(1).find('input').val();
            }
            payVal= $(palyList[i]).find('td').eq(2).find('input').val();
            totalStr += payName +' : '+payVal+'元, ';
            $('.Total #payInfo span').html(totalStr)
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
            payName = $(parentTr).find('td').eq(1).find('select').val();
        }else{
            payName = $(parentTr).find('td').eq(1).find('input').val();
        }
        payVal= $(parentTr).find('td').eq(2).find('input').val();
        totalStr += payName +' : '+payVal+', ';
        $('.Total #payInfo span').html(totalStr)
    }
});





