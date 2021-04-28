
var intervalTime = 10000;
var project_list = []; 
var intervalCnt = 0; 


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

  
  
  // 프로젝트 정보 호출 
  getProject();

  // 서버 상태 및 디비 체크 interval 시작
  initClientCheckInterval();
  

})(window);



function initClientCheckInterval(){

  
  var checkClient = setInterval(function() { 
    
    var project = project_list[intervalCnt];
    intervalCnt++;

    updateServerStatus(project);

    // 리스트 사이즈 만큼 돌았으면 멈추고 다시 프로젝트 정보를 호출한다??
    if( project_list.length == ( intervalCnt ) ){
      intervalCnt = 0;
      clearInterval(checkClient); // 인터벌 중지
      initClientCheckInterval(); // 시작
    }
  }, intervalTime );
}

// 메인 대시보드 server / db 상태 갱신
function updateServerStatus(project){

  //console.log(  project.fields.pro_craw_url )     
  $.ajax({
    type : "POST",
    url: "/get_client_status", 
    dataType: "json",
    data  : { 'client_host' : project.fields.pro_url },
    async: false,
    success: function(response){ 

        var html ='' ;
        
        html += '<tr class="' + ( response.time == 0 ?  'table-active' : '')  + '" >';
        html += '<td class="text-bold-500">연세대학교</td>';
        html += '<td><a href="#">http://www.yonsei.ac.kr</a></td></td>';
        html += '<td class="sorting_1"><i class="bx bxs-circle danger font-small-1 mr-50"></i><span>Expired</span></td>';
        html += '<td class="sorting_1"><i class="bx bxs-circle success font-small-1 mr-50"></i><span>200ms</span></td>';
        html += '<td>11.08.18</td>';
        html += '</tr>';
        
    }
  });
}



var isCheckStatus = false;

function getProject(){

  $.ajax({
    url: "/get_project", 
    dataType: "json",
    async: false,
    success: function(response){ 
        //var data = response 
        project_list = response;
        //intervalTime = project_list.length * 10000; // 프로젝트당 10초
        //for( var i=0; i< data.length; i++ ){
        //  console.log(  data[i].fields.pro_url )
        //  console.log(  data[i].fields.pro_craw_url ) 
        //}
        //isCheckStatus = false;
    }
  });
}