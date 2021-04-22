(function(window, undefined) {
  'use strict';

  /*
  NOTE:
  ------
  PLACE HERE YOUR OWN JAVASCRIPT CODE IF NEEDED
  WE WILL RELEASE FUTURE UPDATES SO IN ORDER TO NOT OVERWRITE YOUR JAVASCRIPT CODE PLEASE CONSIDER WRITING YOUR SCRIPT HERE.  */


  $(".progress-bar").each(function(){
    var width = $(this).data('width');
    
    $(this).animate({
        width: width + '%'
    }, 2000);
    });

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
  

})(window);