$(function() {
  $('#direction').val('ltr'); // to avoid incosistency when reloading rtl
  function toggleDirection() {
    var dir = $('#direction').val()=='ltr'? 'rtl': 'ltr';
    $('#direction').val(dir);
    window.editor.codemirror.setOption("direction", dir);
    $('.main-content').css("direction", dir);
  }
  function update_re() {
    var re = $('#re-url').val().trim();
    $('#re-wrapper').hide();
    if (!re) {
      return;
    }
    $.ajax('/re', {data: {q: $('#re-url').val()}}).done(function(r) {
      if (r) {
        $('#re').val(r.url);
        $('#re-author').html(
        `<a target="_blank" title="${r.account.display_name }"
            href="${r.account.url}">
           <img alt="${r.account.display_name}"
             src="${r.account.avatar}"/>
         </a>`);
        $('#re-body').html(`<h5>
                              <a target="_blank"
                                 title="@${r.account.acct }"
                                 href="${r.account.url}">
                                ${r.account.display_name||'@'+r.account.acct}
                               </a>:
                             </h5>
                             ${r.spoiler_text}
                             <blockquote>${r.content}</blockquote>`);
        if (r.spoiler_text) {
          $('#title').val(r.spoiler_text);
        }
        $('#autocomplete').val('@'+r.account.acct).trigger('paste.xdsoft');
        $('.CodeMirror textarea').focus();
      } else {
        $('#re').val('');
        $('#re-author').empty();
        $('#re-body').html("<h4 align=center>Not a toot's URL.</h4>");
      }
      $('#re-wrapper').show();
    }).fail(function(jqXHR, textStatus) {
        $('#re').val('');
        $('#re-author').empty();
        $('#re-body').html(`<h5>Error: ${textStatus}</h5>`);
      $('#re-wrapper').show();
    });
  }
  $('#markdown').val('');
  $('#title').val('');
  $('#re-url').val(window.IN_REPLY_TO_URL).on('input', update_re).click(
      function() { $(this).select(); });
  update_re();
  window.editor = new SimpleMDE({
    element: document.getElementById("markdown"),
    spellChecker: false,
    promptURLs: true,
    toolbar: [
        "bold",
        "italic",
        "heading",
        "|",
        "quote",
        "unordered-list",
        "ordered-list",
        "|",
        "link",
        "image",
        "|",
        "preview",
        "side-by-side",
        "fullscreen",
        "|",
        {
            "action": toggleDirection,
            "className": "fa fa-language",
            "default": true,
            "name": "direction",
            "title": "Switch direction (LTR/RTL)"
        },
        "|",
        "guide",
        "|"
    ]
  });
  $("#autocomplete").val('').autocomplete({
    source:[ { type: "remote", url: "search?q=%QUERY%" } ],
      getValue:function(item){
      return item.value;
    },	
    getTitle:function(item){
      return item.title? `${item.value} (${item.title})`: item.value;
     },
  }).on('pick.xdsoft', function() {
    window.editor.codemirror.replaceSelection(
      $('#autocomplete').val()+' ');
    $('#autocomplete').val('');
    $('.CodeMirror textarea').focus();
    return true; // voodoo
  }); 
});
