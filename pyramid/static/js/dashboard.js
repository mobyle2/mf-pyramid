


   var curObject;

  /**
  * Submit the form
  */
  function mfsubmit(prefix) {
     id = $("#"+curObject+"\\[_id\\]").val();
     method = "POST";
     if(id ==null || id == '') { method = "PUT"; id = "" }
     $.ajax({type:method, data: $("#mf-form-"+curObject).serialize(), url: prefix+"/"+curObject.toLowerCase()+"s/"+id,
            success: function(msg){
               if(msg["status"]==1) {
                 $.each(msg["error"], function(err){
                     params = msg["error"][err].split('.');
                     errparam = '';
                     for(var i=0;i<params.length;i++) {
                       errparam += '\\['+params[i]+'\\]'
                     }
                     $("#"+curObject+errparam).attr('class','mf-error');
                  });

                 $("#mf-flash").attr('class','alert alert-error');
                 $("#mf-flash").text(curObject+" could not be saved");
               }
               else {
                 clear_form_elements("#show-"+curObject);
                 $("#mf-flash").attr('class','alert alert-success');
                 if(method == "POST") {
                   $("#mf-flash").text(curObject+" successfully updated");
                 }
                 else { 
                   $("#mf-flash").text(curObject+" successfully added");
                 }
               }

            },
            error: function(){
                alert('An error occured during transaction');
            }
        });
   }


  /**
  * Loads an object and shows its form
  */
  function loadObject(id) {
    clear_form_elements("#show-"+curObject);
    route = '/'+curObject.toLowerCase()+'s/'+id;
    $.getJSON(route, function(data) {
      json2form(data["user"],"");
     });
  }

  /**
  * Loads a list of objects and create a sortable table
  */
  function loadObjectList(id) {
    clear_form_elements("#show-"+curObject);
    $(".mf-list").hide();
    $(".mf-object").hide();
    $("#show-"+curObject).show();
    route = '/'+id.toLowerCase()+'s/';
    $.getJSON(route, function(data) {
      var thead = '<thead><tr>';
      var tbody = '<tr>';

      var keys = new Array();
      var types = {};
      $.each(data, function(obj) {
        //tbody += '<tr id="'+data[obj]["_id"]["$oid"]+'" class="mf-list-object '+id+'">';
        $.each(data[obj], function(key, val) {
          if( (!jQuery.isPlainObject(val)) || val['$date']!=null) {
            var type = $('#'+curObject+'\\['+key+'\\]').attr('type');
            if ( $.inArray(key, keys) < 0) {
              keys.push(key)
              types[key] = type
            }
            //tbody += "<td>"+val+"</td>";
          }
        });
        //tbody += "</tr>";

      });
      // Table header
      $.each(keys, function(key) { thead += "<th>"+keys[key]+"</th>"; });
      // Now for each object get values from key
      $.each(data, function(obj) {
        tbody += '<tr id="'+data[obj]["_id"]["$oid"]+'" class="mf-list-object '+id+'">';
        $.each(keys, function(key) {
           var val = data[obj][keys[key]];
           // Bson does not permit python time or date conversion, so we store them as string.
           if((jQuery.isPlainObject(val) && val['$date']!=null) || (types[keys[key]] == 'date') || (types[keys[key]] == 'time')) {          
             if (types[keys[key]] == 'date') {
               //val = dateFormat(val,'yyyy/mm/dd');
             }
             else if (types[keys[key]] == 'time') {
               //val = dateFormat(val,'hh:MM:ss');
             }
             else {
               val = new Date(val['$date']);
               val = dateFormat(val,'yyyy/mm/dd hh:MM:ss');
             }
           }
          tbody += "<td>"+val+"</td>";
        });
        tbody += "</tr>";
      });

      thead += '</tr></thead>';
      tbody += '</tbody>';
      $("#table-"+id).html(thead+tbody);
      $("#list-"+id).show();
     });
   }


   /**
   * Map a json result to a form
   */
   function json2form(data,parent) {
     $.each(data, function(key, val) {
     if(jQuery.isPlainObject(val)) {
       if(val['$date']!=null){
         var objdate = new Date(val['$date']);
         var objdatestr = objdate.toString()
         var type = $('#'+curObject+parent+'\\['+key+'\\]').attr('type');
         if (type == 'date') { objdatestr = objdate.toDateString(); }
         if (type == 'time') { objdatestr = objdate.toTimeString(); }
         $('#'+curObject+parent+'\\['+key+'\\]').val(objdatestr);
       }
       else if(val['$oid']!=null){
         $('#'+curObject+parent+'\\['+key+'\\]').val(val['$oid']);
       }
       else {
         var newparent = parent + '\\['+key+'\\]';
         json2form(val,newparent);
       }
     }
     else { 
       $('#'+curObject+parent+'\\['+key+'\\]').val(val);
       if($('#'+curObject+parent+'\\['+key+'\\]').attr('type')=='checkbox')  {
         if(val == 'True' || val == 1) {
           $('#'+curObject+parent+'\\['+key+'\\]').attr('checked', true);
         }
         else {
           $('#'+curObject+parent+'\\['+key+'\\]').attr('checked', true);
         }
       }
     }

     });
   }

  /**
  * Clear the form elements
  */
  function clear_form_elements(ele) {
    $("div").removeClass("error");
    $("#mf-flash").attr('class','');
    $("#mf-flash").text("");
    $(ele).find(':input').each(function() {
        switch(this.type) {
            case 'password':
            case 'select-multiple':
            case 'select-one':
            case 'text':
            case 'textarea':
                $(this).attr('class','');
                $(this).val('');
                break;
            case 'checkbox':
            case 'radio':
                this.checked = false;
        }
    });
  }


