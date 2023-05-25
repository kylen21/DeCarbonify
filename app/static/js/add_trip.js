let trip_num = 1;

function addTripClick(){
    //Increment trip_num
    trip_num++;

    //Create new div for new trip
    let new_div = document.createElement("div")

    //Add divider from previous ttrip
    new_div.appendChild(document.createElement("hr"))

    //Create and add trip label ("Trip 1")
    let new_trip_label = document.createElement("b")
    new_trip_label.innerHTML = "Flight "+trip_num+":"
    new_div.appendChild(new_trip_label)

    //Create and add trip input fields
    let new_trip_info = document.getElementById("trip_info").cloneNode(true)
    new_div.appendChild(new_trip_info)

    //Add div to trip form
    document.getElementById("trip_form").appendChild(new_div)
}