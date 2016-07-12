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
        var parent = $(this).parents('form');
        var formLine = $(this).parents('.formline').clone();
        //console.log(formLine)
        $(parent).append(formLine)
    })
});
