(function(window, undefined) {
  'use strict';

  /*
  NOTE:
  ------
  PLACE HERE YOUR OWN JAVASCRIPT CODE IF NEEDED
  WE WILL RELEASE FUTURE UPDATES SO IN ORDER TO NOT OVERWRITE YOUR JAVASCRIPT CODE PLEASE CONSIDER WRITING YOUR SCRIPT HERE.  */

  /**
   *  프로그레스바 애니메이션 
   */
  $(".progress-bar").each(function(){
    var width = $(this).data('width');
    
    $(this).animate({
        width: width + '%'
    }, 2000);
    });

  /**
   * 
   *  대시보드 숫자 카운트 증가 애니메이션 
   */  
  $(".counter-up").each(function () {
    $(this).prop('Counter', 0).animate({
      Counter:  $(this).text() 
    }, {
      duration: 1500,
      easing: 'swing',
      step: function (now) {
        $(this).text(Math.ceil(now).toString() )
      }
    });
  }); // end of each
  
  /**
   *   테이블 리프레쉬 
   */
  /*$("table.table-action tbody tr").fadeOut(1000);*/
  $("table.table-action tbody tr").each(function(index){
    $(this).delay(index*500).show(500);
  });


})(window);