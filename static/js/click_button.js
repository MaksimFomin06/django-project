'use strict'

function viewSnippet(){
    const snipped_num = document.getElementById('snippet_id').value;
    const form = document.getElementById("view_snippet_form");
    form.action = `/snippets/${snipped_num}`;
    form.submit();
}
document.getElementById("view_snippet_form").addEventListener("submit", viewSnippet);