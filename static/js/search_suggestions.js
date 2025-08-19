$(function() {
  $('#user-search').on('input', function() {
    let query = $(this).val().trim();
    if (query.length < 1) {
      $('#user-suggestions').hide();
      return;
    }
    $.getJSON('/search_users', { q: query }, function(data) {
      if (data.length === 0) {
        $('#user-suggestions').hide();
        return;
      }
      let listItems = '';
      data.forEach(function(user) {
        listItems += `
          <li style="padding:6px; cursor:pointer; display:flex; align-items:center;" data-id="${user.id}">
            <img src="${user.profilePhoto}" alt="" style="width:28px; height:28px; border-radius:50%; margin-right:10px; object-fit:cover;">
            <span>${user.displayName}</span>
          </li>`;
      });
      $('#user-suggestions').html(listItems).show();
    });
  });

  $('#user-suggestions').on('click', 'li', function() {
    let userId = $(this).data('id');
    window.location.href = '/user/' + userId;
  });

  $(document).on('click', function(e) {
    if (!$(e.target).closest('#user-search, #user-suggestions').length) {
      $('#user-suggestions').hide();
    }
  });
});
