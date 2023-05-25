'use strict';

function handleSearchResponse(response){
    $('#results').html(response)
}

let request = null

function updateSearch(){
    let field = encodeURIComponent($('#searchbar').val());

    let url = '/updatesearch?' + 'user=' + field

    if (request != null){
        request.abort()
    }

    request = $.ajax(
        {
            type: 'GET',
            url: url,
            success: handleSearchResponse
        }
    )
}

function setup(){
    $('#searchbar').on('input', updateSearch);
    $(document).ready(function(){
        $('#search').toggleClass('nav-link').toggleClass('nav-link active');
    });
}

$('document').ready(setup);