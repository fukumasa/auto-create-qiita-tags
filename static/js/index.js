function switchTagResults() {
    var select_tag = document.getElementById("sort-value");
    var tag_value = document.getElementById("tag-value");
    var tag_followers = document.getElementById("tag-followers");
    var tag_counts = document.getElementById("tag-counts");

    var idx = select_tag.selectedIndex;
    var value = select_tag.options[idx].value;
    switch(value) {
        case 'value':
            tag_value.style.display = "";
            tag_followers.style.display = "None";
            tag_counts.style.display = "None";
            break;
        case 'followers':
            tag_value.style.display = "None";
            tag_followers.style.display = "";
            tag_counts.style.display = "None";
            break;
        case 'counts':
            tag_value.style.display = "None";
            tag_followers.style.display = "None";
            tag_counts.style.display = "";
            break;
        defalt:
            break;
    }
}