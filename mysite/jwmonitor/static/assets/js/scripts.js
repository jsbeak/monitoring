
var intervalTime = 10000;
var project_list = []; 
var intervalCnt = 0; 

// 실시간 서버 상태정보 최대 노출개수
var SERVER_DB_CNT = 6;


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
      
      var stateClass = "success";
      var stateText = "Active";
      if( response.time == 0 ){
        stateClass = "danger";
        stateText = "Expired";
      }

      var html ='' ;
      
      html += '<tr class="' + ( response.time == 0 ?  'table-active' : '')  + '"  style="display: none;">';
      html += '<td class="text-bold-500">' + project.fields.pro_client_nm + '</td>';
      html += '<td><a href="' + project.fields.pro_url +'" target="_blank">'+ project.fields.pro_url + '</a></td></td>';
      html += '<td class="sorting_1"><i class="bx bxs-circle ' + stateClass +' font-small-1 mr-50"></i><span>' + stateText +'/'  + response.time + 'ms</span></td>';
      html += '<td class="sorting_1"><i class="bx bxs-circle ' + stateClass +' font-small-1 mr-50"></i><span> - </span></td>';
      html += '<td>' + response.date + '</td>';
      html += '</tr>';

      
      var curCnt = $("#server-db-table tbody tr").not(".table-active").length;

      // 최대개수 노출시 마지막값을 삭제
      if( curCnt == SERVER_DB_CNT ){
        //$("#server-db-table tbody tr").not(".table-active").last().remove();
        $("#server-db-table tbody tr").last().fadeOut(300 , function(){
          $(this).remove();
        })
      }

      if( $("#server-db-table tbody tr").length == 0 ){
        
        $("#server-db-table tbody").append(html);
        $("#server-db-table tbody tr:hidden").delay(500).show(1200);
        

      }else{
        $("#server-db-table tbody").prepend(html);
        $("#server-db-table tbody tr:hidden").delay(500).show(1200);  
        
      }

    }
  });
}




/**
 *  프로젝트 리스트 정보 호출
 */
function getProject(){

  $.ajax({
    url: "/get_project", 
    dataType: "json",
    async: false,
    success: function(response){ 
        
        project_list = response;
        
    }
  });
}