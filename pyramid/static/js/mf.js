
/**
* Javascript library used in example dashboard
*
*
**/

   var curObject;

   var curPage = 0;

   var pageSize = 20;

   var mfsort = {};

   var mfprefix = '';

   var objectsListFields = Array();

$(function() {

$(document).on("change", ".mf-psize", function(event) {
  pageSize = $(this).val();
});

$(document).on("click", ".mf-sort", function(event) {
  var param = $(this).text();
  if(mfsort["key"]!=null && mfsort["key"]==param) {
    if(mfsort["value"]==1) { mfsort["value"] = -1; }
    else { mfsort["value"] = 1; }
  }
  else { mfsort["key"] = param; mfsort["value"] = 1; }
  loadObjectList(curObject);  
});

$(document).on("click", ".mf-next", function(event) {
  curPage = curPage + pageSize;
  loadObjectList(curObject,true);
});
$(document).on("click", ".mf-prev", function(event) {
  curPage = curPage - pageSize;
  if(curPage<0) {
    curPage = 0;
  }
  loadObjectList(curObject,true);
});



});

  /**
  * Delete an object
  */
  function mfdelete(){
    id = $("#"+curObject+"\\[_id\\]").val();
    route = mfprefix+'/'+curObject.toLowerCase()+'s/'+id;
     $.ajax({type:"DELETE", url: route,
            success: function(msg){
              if(msg["status"]==1) {
                $("#mf-flash").attr('class','alert alert-error');
                $("#mf-flash").text(curObject+" could not be deleted");
              }
              else {
                $("#mf-flash").attr('class','alert alert-success');
                $("#mf-flash").text(curObject+" deleted");
                loadObjectList(curObject);
              }               
            },
            error: function(){
                alert('An error occured during transaction');
            }
        });

  }

  /**
  * Set checkboxes values to True or False according to checked status.
  * Not very performant for the moment as it resets all checkboxes values.
  */
  function updateCheckboxValues() {
     checks = $('input[type=checkbox]').not(':checked');
     $.each(checks,function() {
       $(this).val('False');
     });
     checks = $('input:checked');
     $.each(checks,function() {
       $(this).val('True');
     });
  }

  /**
  * Search
  */
  function mfsearch() {
     updateCheckboxValues();
     $.ajax({type:"POST", data: $("#mf-search-form-"+curObject).serialize(), url: mfprefix+"/"+curObject.toLowerCase()+"s",
            success: function(msg){
               if(msg["status"]==1) {
                   $("#mf-flash").attr('class','alert alert-error');
                   $("#mf-flash").text("An error occured with the search");
               }
               else {
                   $("#mf-flash").attr('class','alert alert-success');
                   updateObjectList(msg);
               }
            },
            error: function(){
                alert('An error occured during transaction');
            }
        });

  }

  /**
  * Submit the form
  */
  function mfsubmit() {
     updateCheckboxValues();
     id = $("#"+curObject+"\\[_id\\]").val();
     method = "POST";
     if(id ==null || id == '') { method = "PUT"; id = "" }
     route = mfprefix+"/"+curObject.toLowerCase()+"s";
     if(id != "") {
        route = mfprefix+"/"+curObject.toLowerCase()+"s/"+id
     }
     $.ajax({type:method, data: $("#mf-form-"+curObject).serialize(), url: route,
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
                 $("#mf-flash").text(curObject+" could not be saved: "+msg["error"]);
               }
               else {
                 clear_form_elements("#show-"+curObject);
                 $("#mf-flash").attr('class','alert alert-success');
                 if(method == "POST") {
                   $("#mf-flash").text(curObject+" Operation successful");
                 }
                 else { 
                   $("#mf-flash").text(curObject+" successfully added");
                 }
               }
               loadObjectList(curObject,false);
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
    route = mfprefix+'/'+curObject.toLowerCase()+'s/'+id;
    $.getJSON(route, function(data) {
      json2form(data[curObject.toLowerCase()],"");
     });
  }

  function loadObjectList(id) {
    loadObjectList(id,true);
  }

  /**
  * Loads a list of objects and create a sortable table
  */
  function loadObjectList(id,clean) {
    if(clean==null || clean) {
      clear_form_elements("#show-"+curObject);
    }
    $(".mf-list").hide();
    //$(".mf-object").hide();
    $(".accordion").hide();
    //$(".mf-search").hide();
    $("#accordion"+curObject).show();
    //$("#show-"+curObject).show();
    //$("#search-"+curObject).show();
    route = mfprefix+'/'+id.toLowerCase()+'s';
    var filter='?page='+curPage+'&pagesize='+pageSize;
    if(mfsort['key']!=null) {
      filter += '&order='+mfsort['key']+'&order_type='+mfsort['value']
    }
    $.getJSON(route+filter, function(data) {
     updateObjectList(data);
     });
   }


   /**
   * Update list of object from json list
   */
   function updateObjectList(data) {
      var thead = '<thead><tr>';
      var tbody = '<tr>';

      var keys = new Array();
      var types = {};
      $.each(data, function(obj) {
        $.each(data[obj], function(key, val) {
          if( key!='id' && val!=null && ((!jQuery.isPlainObject(val)) || val['$date']!=null )) {
            var type = $('#'+curObject+'\\['+key+'\\]').attr('type');
            if ( $.inArray(key, keys) < 0) {
              if(objectsListFields[curObject]==null || $.inArray(key,objectsListFields[curObject]) >= 0) {
              keys.push(key);
              types[key] = type;
              }
            }
          }
        });

      });
      // Table header
      $.each(keys, function(key) { thead += '<th class="mf-sort">'+keys[key]+'</th>'; });
      // Now for each object get values from key
      var nbelt = 0;
      $.each(data, function(obj) {
        tbody += '<tr id="'+data[obj]["_id"]["$oid"]+'" class="mf-list-object '+curObject+'">';
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
        nbelt += 1;
      });

      thead += '</tr></thead>';
      tbody += '</tbody>';
      tfoot = '<tfoot><tr><td><form class="form-inline"><div class="control-group"><label for="psize">Page size</label><select class="mf-psize" id="psize-'+curObject+'">';
      var selected10='';
      var selected20='';
      var selected50=''; 
      if(pageSize==10) {
        selected10 = 'selected';
      }
      else if(pageSize==20) {
        selected20 = 'selected';
      }
      else if(pageSize==50) {
        selected50 = 'selected';
      }

       
      tfoot += '<option value="10" '+selected10+'>10</option>';
      tfoot += '<option value="20" '+selected20+'>20</option>';
      tfoot += '<option value="50" '+selected50+'>50</option>';
      tfoot += '</select></form></div></td><td><form class="form-inline"><div class="control-group">';
      if(curPage>0) {
      tfoot += '<i class="mf-prev icon-backward"> </i>';
      }
      if(nbelt>=pageSize) {
      tfoot += '<i class="mf-next icon-forward"> </i>';
      }
      tfoot += '</div></form></td></tr></tfoot>';
      $("#table-"+curObject).html(thead+tbody+tfoot);
      $("#list-"+curObject).show();
   }

   /**
   * Set value from object type
   */
   function setSpecificObjectValue(elt, val) {
       if(val['$date']!=null){
         var objdate = new Date(val['$date']);
         //var objdatestr = objdate.toString()
         var month = objdate.getMonth()+1;
         if (month<10) { month = '0'+month; }
         var day = objdate.getDate();
         if (day<10) { day = '0'+day; }
         var hours = objdate.getHours();
         if (hours<10) { hours = '0'+hours; }
         var minutes = objdate.getMinutes();
         if (minutes<10) { minutes = '0'+minutes; }
         var seconds = objdate.getSeconds();
         if (seconds<10) { seconds = '0'+seconds; }
         var objdatestr = objdate.getFullYear()+'/'+month+'/'+day+' '+hours+':'+minutes+':'+seconds
         var type = $('#'+elt).attr('type');
         if (type == 'date') { objdatestr = objdate.toDateString(); }
         if (type == 'time') { objdatestr = objdate.toTimeString(); }
         $('#'+elt).val(objdatestr);
       }
       else if(val['$oid']!=null){
         $('#'+elt).val(val['$oid']);
         $('#DbRef'+elt).text(val['$oid']);
         searchDbRef(elt);
       }
       else if(val['_id']!=null && val['_id']['$oid']!=null){
         // Db object reference
         $('#'+elt).val(val['_id']['$oid']);
         $('#DbRef'+elt).text(val['_id']['$oid']);
         searchDbRef(elt);
       }
       else if($('#'+elt).attr('data-type') == 'dbref') {
             // SimpleReferenceRenderer
                  searchDbRef(elt);
       }    
       else {
         // Not a specific type
         return false;
       }
       return true;
   }

   /**
   * Map a json result to a form
   */
   function json2form(data,parent) {
     $.each(data, function(key, val) {
     if(jQuery.isPlainObject(val)) {
       if( ! setSpecificObjectValue(curObject+parent+'\\['+key+'\\]',val)) {
         var newparent = parent + '\\['+key+'\\]';
         json2form(val,newparent);
       }
     }
     else {
       if(val instanceof Array) {
           arrayelts = $('#Template'+curObject+parent+'\\['+key+'\\]');
           template = $(arrayelts[0]).children();
          
           clonediv = $('#Clone'+curObject+parent+'\\['+key+'\\]');
           clonediv.children().remove();

           $.each(val, function(elt) {
             newelt = template.clone();
             
            inputs = newelt.find('input:not(.mf-dbref)');
            objlist = {};
            $.each(inputs, function(input) {
              ielt = $(inputs[input])
              oldid = ielt.attr("id");
              ielt.attr("id",oldid+'['+count+']');
              ielt.attr("name",oldid+'['+count+']');
              if(jQuery.isPlainObject(val[elt])) {
                 $.each(val[elt], function(key,value) {
                   reg1=new RegExp(key,"g");
                   if(oldid.match(reg1)) {
                     if(jQuery.isPlainObject(val[elt][key])) {
                       // Object, not simple type
                       objref= oldid+'['+count+']';
                       objref = objref.replace(/\[/g,'\\[');
                       objref = objref.replace(/\]/g,'\\]');
                       // May need to search through different elements, but elements are not yet set in document
                       // Store key/values in a list and apply them when template is put in document
                       objlist[objref] = val[elt][key];
                     }
                     else {
                       ielt.val(val[elt][key]);
                       if(ielt.attr('data-type') == 'choice') {
           			       ielt.val(val[elt][key].toString());
         			   }
                     }
                   }
                 });
              }
              else {
                 ielt.val(val[elt]);
                 // If it is a SimpleRenderer, then value is a string, but has dbref
                 // Postpone elements are above case with isPlainObject
                 if(ielt.attr('data-type') == 'dbref' && ielt.val()!=null && ielt.val()!='') {
                     objlist[oldid+'['+count+']'] = val[elt];
                 }
              }
              dbrefobj = oldid.replace(/\[/g,'\\[');
    		  dbrefobj = dbrefobj.replace(/\]/g,'\\]');
              newdbref = newelt.find("#DbRef"+dbrefobj);
              if(newdbref!=null) { 
              newdbref.attr("data-dbref",oldid+'['+count+']');
        	  newdbref.attr("id","DbRef"+oldid+'['+count+']');
        	  newdbrefclear = newelt.find("#DbRefClear"+dbrefobj);
              newdbrefclear.attr("data-dbref",oldid+'['+count+']');
              newdbrefclear.attr("id","DbRefClear"+oldid+'['+count+']');
              }
              //$('#DbRef'+oldid).attr("data-dbref",oldid+count);
              //$('#DbRef'+oldid).attr("id",oldid+count);
            });
             
             
             //oldid = newelt.find('input:not(.mf-dbref)').attr("id");
             //newelt.find('input:not(.mf-dbref)').attr("id",oldid+count);
             //newelt.find('.mf-dbref').attr("data-dbref",oldid+count);          
             //newelt.find('input:not(.mf-dbref)').val(val[elt]);
             clonediv.append(newelt);
             $.each(objlist, function(key,value) {
               setSpecificObjectValue(key,value);
             });
             objlist = {}
             newelt.find('.mf-dbref').typeahead({
                source: function (query, process) { return
getObjects(query,$(this)[0].$element[0].dataset.dbref,$(this)[0].$element[0].dataset.object,process,$(this)[0].$element[0].dataset.display);},
                updater: function (item) { $("#"+autocompleteelt).val(objList[item]);return item;},
                minLength: 3 
        	  });
             //searchDbRef(oldid+count);
             count++;
           });

       }
       else {
         elt = $('#'+curObject+parent+'\\['+key+'\\]');
         elt.val(val);
         if(elt.attr('data-type') == 'choice') {
           elt.val(val.toString());
         }

         if(elt.attr('data-type') == 'dbref' && elt.val()!=null && elt.val()!='') {
           searchDbRef(curObject+parent+'\\['+key+'\\]');
         }
         if(elt.attr('type')=='checkbox')  {
           if(val == 'true' || val == 'True' || val == 1) {
             elt.attr('checked', true);
           }
           else {
             elt.attr('checked', false);
           }
         }
       }
     }

     });
   }

  /**
  * Search the name of an object from its id and update object container.
  * get id, search in database and update name in dbref container.
  */
  function searchDbRef(container){
      id = $('#'+container).val();
      var obj = $('#DbRef'+container).attr("data-object");
      if(obj==null) { return; }
      route = mfprefix+'/'+obj.toLowerCase()+'s/'+id;
      $.getJSON(route, function(data) {
        if(data[obj.toLowerCase()]['name']!=null) {
          $('#DbRef'+container).val(data[obj.toLowerCase()]['name']);
        }
      });
  }


  /**
  * Clear the form elements
  */
  function clear_form_elements(ele) {
    $(".mf-template-clone").children().remove();
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
            case 'hidden':
            case 'date':
            case 'time':
            case 'datetime':
                //$(this).attr('class','');
                $(this).removeClass("error");
                $(this).removeClass("mf-error");
                if( $(this).attr('data-default')!=null) {
                  $(this).val($(this).attr('data-default'));
                }
                else {
                  $(this).val('');
                }
                break;
            case 'checkbox':
            case 'radio':
                $(this).removeClass("error");
                $(this).removeClass("mf-error");
                if( $(this).attr('data-default')!=null && $(this).attr('data-default')=="true") {
                  this.checked = true;
                }
                else {
                  this.checked = false;
                }
                break;
            case 'number':
                $(this).removeClass("error");
                $(this).removeClass("mf-error");
                if( $(this).attr('data-default')!=null) {
                  $(this).val($(this).attr('data-default'));
                }
                else {
                  $(this).val('0');
                }
        }
    });
  }

  /**
  * Clear the search form elements
  */
  function clear_search_form_elements(ele) {
    $(ele).find(':input').each(function() {
        switch(this.type) {
            case 'password':
            case 'select-multiple':
            case 'select-one':
            case 'text':
            case 'textarea':
            case 'date':
            case 'time':
            case 'datetime':
            case 'number':
                $(this).attr('class','');
				$(this).val('');
                break;
            case 'checkbox':
            case 'radio':
                this.checked = false;
                break;
        }
    });
  }

  /**
  * Get object list and set objList with obj name/obj id
  */
  function getObjects(query,param,objname,process,searchBy) {
    autocompleteelt = param;

    autocompleteelt = autocompleteelt.replace(/\[/g,'\\[');
    autocompleteelt = autocompleteelt.replace(/\]/g,'\\]');

    route = mfprefix + '/'+objname.toLowerCase()+'s';
    return $.ajax({type:"POST", data: 'Search'+objname+"["+searchBy+"]="+query, url: route,
            success: function(msg){
               if(msg["status"]==1) {
                   $("#mf-flash").attr('class','alert alert-error');
                   $("#mf-flash").text("An error occured with the search");
               }
               else {
                   $("#mf-flash").attr('class','alert alert-success');
                   objList = {};
                   nameList = [];
                   $.each(msg, function(obj) {
                     objList[msg[obj][searchBy]] = msg[obj]["_id"]["$oid"];
                     nameList.push(msg[obj][searchBy]);
                   });
               return process(nameList);
               }
            },
            error: function(){
                alert('An error occured during transaction');
            }
     });


  }


