$(function(){
    $('.tree li:has(ul)').addClass('parent_li').find('> span').attr('title','Collapse this branch')
    $('.tree li.parent_li > span').on('click',function(e){
        var children = $(this).parent('li.parent_li').find(' > ul > li');
        if (children.is(":visible")){
            children.hide('fast');
            $(this).attr('title','Expand this branch').find(' > i').addClass("class-plus").removeClass('class-minus');
        }
        else{
            children.show('fast',function(){ $(this).css('overflow','visible')});
            $(this).attr('title','Collapse this branch').find(' > i').addClass('class-minus').removeClass('class-plus');
        }
        e.stopPropagation();
    });    
});


