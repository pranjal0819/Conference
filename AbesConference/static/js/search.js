function myFunction12() {
    var input, filter, table, tr, td1, td2, i;
    input = document.getElementById("search");
    filter = input.value.toUpperCase();
    table = document.getElementById("myTable");
    tr = table.getElementsByTagName("tr");
    for (i = 0; i < tr.length; i++) {
        td1 = tr[i].getElementsByTagName("td")[1];
        td2 = tr[i].getElementsByTagName("td")[2];
        if (td1 || td2) {
            if ((td1.innerHTML.toUpperCase().indexOf(filter) > -1) ||
                (td2.innerHTML.toUpperCase().indexOf(filter) > -1)) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}

function myFunction123() {
    var input, filter, table, tr, td1, td2, td3, i;
    input = document.getElementById("search");
    filter = input.value.toUpperCase();
    table = document.getElementById("myTable");
    tr = table.getElementsByTagName("tr");
    for (i = 0; i < tr.length; i++) {
        td1 = tr[i].getElementsByTagName("td")[1];
        td2 = tr[i].getElementsByTagName("td")[2];
        td3 = tr[i].getElementsByTagName("td")[3];
        if (td1 || td2 || td3) {
            if ((td1.innerHTML.toUpperCase().indexOf(filter) > -1) ||
                (td2.innerHTML.toUpperCase().indexOf(filter) > -1) ||
                (td3.innerHTML.toUpperCase().indexOf(filter) > -1)) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}

function myFunction1245() {
    var input, filter, table, tr, td1, td2, td4, td5, i;
    input = document.getElementById("search");
    filter = input.value.toUpperCase();
    table = document.getElementById("myTable");
    tr = table.getElementsByTagName("tr");
    for (i = 0; i < tr.length; i++) {
        td1 = tr[i].getElementsByTagName("td")[1];
        td2 = tr[i].getElementsByTagName("td")[2];
        td4 = tr[i].getElementsByTagName("td")[4];
        td5 = tr[i].getElementsByTagName("td")[5];
        if (td1 || td2 || td4 || td5) {
            if ((td1.innerHTML.toUpperCase().indexOf(filter) > -1) ||
                (td2.innerHTML.toUpperCase().indexOf(filter) > -1) ||
                (td4.innerHTML.toUpperCase().indexOf(filter) > -1) ||
                (td5.innerHTML.toUpperCase().indexOf(filter) > -1)) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}

function myFunction12456() {
    var input, filter, table, tr, td1, td2, td4, td5, td6, i;
    input = document.getElementById("search");
    filter = input.value.toUpperCase();
    table = document.getElementById("myTable");
    tr = table.getElementsByTagName("tr");
    for (i = 0; i < tr.length; i++) {
        td1 = tr[i].getElementsByTagName("td")[1];
        td2 = tr[i].getElementsByTagName("td")[2];
        td4 = tr[i].getElementsByTagName("td")[4];
        td5 = tr[i].getElementsByTagName("td")[5];
        td6 = tr[i].getElementsByTagName("td")[6];
        if (td1 || td2 || td4 || td5 || td6) {
            if ((td1.innerHTML.toUpperCase().indexOf(filter) > -1) ||
                (td2.innerHTML.toUpperCase().indexOf(filter) > -1) ||
                (td4.innerHTML.toUpperCase().indexOf(filter) > -1) ||
                (td5.innerHTML.toUpperCase().indexOf(filter) > -1) ||
                (td6.innerHTML.toUpperCase().indexOf(filter) > -1)) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}