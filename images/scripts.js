function timeToSeconds(time) {
    const [hours, minutes, seconds] = time.split(':').map(Number);
    return hours * 3600 + minutes * 60 + (seconds || 0);
}

function secondsToTime(seconds) {
    seconds = seconds % 86400; // Ensure seconds wrap around after 24 hours
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${String(hrs).padStart(2, '0')}:${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

function updateTable() {
    const sunriseToday = document.getElementById('sunriseToday').value ;
    const sunsetToday = document.getElementById('sunsetToday').value ;
    const sunriseTmrw = document.getElementById('sunriseTmrw').value ;
    const weekday = document.getElementById('weekday').value;
    const total = "24:00:00";
    console.log("sunriseToday", sunriseToday);
    console.log("sunsetToday", sunsetToday);
    console.log("sunriseTmrw", sunriseTmrw);
    console.log("total", total);

    const sunriseTodaySec = timeToSeconds(sunriseToday);
    const sunsetTodaySec = timeToSeconds(sunsetToday);
    const sunriseTmrwSec = timeToSeconds(sunriseTmrw);
    const totalSec = timeToSeconds(total);
    console.log("sunriseTodaySec", sunriseTodaySec);
    console.log("sunsetTodaySec", sunsetTodaySec);
    console.log("sunriseTmrwSec", sunriseTmrwSec);
    console.log("totalSec", totalSec);

    const interval1 = (sunsetTodaySec - sunriseTodaySec) / 30;
    const interval2 = ((totalSec + sunriseTmrwSec) - sunsetTodaySec) / 30;
    console.log("interval1", interval1);
    console.log("interval2", interval2);
    const tableBody = document.getElementById('table-body');
    tableBody.innerHTML = ''; // Clear existing table rows
    

    let currentSec = sunriseTodaySec;
    const columnD = [];

    // Generate rows for 30 cells
    for (let i = 0; i < 30; i++) {
        const start = secondsToTime(currentSec);
        currentSec += interval1;
        const end = secondsToTime(currentSec);

        tableBody.innerHTML += `
            <tr>
                <td>${start}</td>
                <td>${end}</td>
                <td></td>
                <td></td> <!-- Placeholder for Column D -->
                <td></td> <!-- Placeholder for Column E -->
                <td>${i + 1}</td>
                <td></td>
                <td></td>
            </tr>
        `;
        columnD.push(end); // Store values for column D
    }

    // Column D calculation (starting from A32) and Column E setup
    const rows = tableBody.querySelectorAll('tr');
    let previousD = timeToSeconds(columnD[29]); // Start with the last value from columnD

    for (let i = 0; i < rows.length; i++) {
        const cells = rows[i].querySelectorAll('td');
        if (cells.length >= 5) {
            // Update Column D values
            if (i === 0) {
                cells[3].textContent = secondsToTime(previousD); // D2 = A32
            } else {
                previousD += interval2;
                cells[3].textContent = secondsToTime(previousD); // D[i] = D[i-1] + interval1
            }

            // Update Column E with next Column D value
            if (i < rows.length) {
                const nextD = timeToSeconds(cells[3].textContent);
                cells[4].textContent = secondsToTime(nextD + interval2); // E[i] = D[i+1]
            }
            let wkd = document.getElementById("weekday-html");
            
            // Apply blue background to specific rows in Column C
            const MondayRow = [0, 5, 12, 13, 26, 29];
            if (MondayRow.includes(i) && weekday=="Monday") {  
                cells[2].style.backgroundColor = '#002060'; // Apply blue color
                wkd.innerHTML = "Monday";
            }
            const TuesdayRow = [3, 4, 9, 10,11, 13,14,15,16,17,20,22,23,24,26];
            if (TuesdayRow.includes(i) && weekday=="Tuesday") {  
                cells[2].style.backgroundColor = '#002060'; // Apply blue color
                wkd.innerHTML = "TuesdayRow";
            }
            const WednesdayRow = [2, 3, 6, 7, 8, 9,11,21,29,31];
            if (WednesdayRow.includes(i) && weekday=="Wednesday") {  
                cells[2].style.backgroundColor = '#002060'; // Apply blue color
                wkd.innerHTML = "Wednesday";
            }
            const ThursdayRow = [4, 7, 10, 15, 16, 17,18,20,21,22,25,26,29,30];
            if (ThursdayRow.includes(i) && weekday=="Thursday") {  
                cells[2].style.backgroundColor = '#002060'; // Apply blue color
                wkd.innerHTML = "Thursday";
            }
            const FridaydayRow = [3, 6, 8, 10,16,18,20,21,24,25,26,27,28,30];
            if (FridaydayRow.includes(i) && weekday=="Fridayday") {  
                cells[2].style.backgroundColor = '#002060'; // Apply blue color
                wkd.innerHTML = "Fridayday";
            }
            const SaturdayRow = [0, 5, 12, 13, 26, 29];
            if (SaturdayRow.includes(i) && weekday=="Saturday") {  
                cells[2].style.backgroundColor = '#002060'; // Apply blue color
                wkd.innerHTML = "Saturday";
            }

            const SundayRow = [2, 10, 11, 13, 14,19, 24,25,27];
            if (SundayRow.includes(i) && weekday=="Sunday") {  
                cells[2].style.backgroundColor = '#002060'; // Apply blue color
                wkd.innerHTML = "Sunday";
            }












            const update = [0,1,2,3,4,5]
            console.log("update.includes(i)",update.includes(i))
            if (update.includes(i)) { 
                if (update[i]==0){
                        cells[6].textContent =secondsToTime(interval1)
                        cells[6].style.backgroundColor = '#B4C6E7';  
                }
                if (update[i]==1){
                        cells[6].textContent =secondsToTime(interval2) 
                        cells[6].style.backgroundColor = '#B4C6E7';  
                }
                if (update[i]==2){
                        cells[6].textContent =total 
                        cells[6].style.backgroundColor = '#B4C6E7';   
                }
                if (update[i]==3){
                        cells[6].textContent ="sunriseToday"
                        cells[7].textContent = sunriseToday
                        cells[6].style.backgroundColor = '#ED7D31'; 
                        cells[7].style.backgroundColor = ''; 
                }
                if (update[i]==4){
                        cells[6].textContent ="sunsetToday"
                        cells[7].textContent = sunsetToday  
                        cells[6].style.backgroundColor = '#FF0000'; 
                        cells[7].style.backgroundColor = '';  
                }
                if (update[i]==5){
                        cells[6].textContent ="sunriseTmrw"
                        cells[7].textContent = sunriseTmrw   
                        cells[6].style.backgroundColor = '#FFD966'; 
                        cells[7].style.backgroundColor = ''; 
                }
        }

        }
    }

    const lastA = secondsToTime(currentSec);
    // Calculate the last cell for column D
    const lastD = secondsToTime(previousD + interval2);

    // Append the last row with specific values for columns A and D
    const lastRow = document.createElement('tr');
    lastRow.innerHTML = `
        <td>${lastA}</td>
        <td></td>
        <td></td>
        <td>${lastD}</td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
    `;
    tableBody.appendChild(lastRow);
}

document.addEventListener("DOMContentLoaded", function() {
    updateTable();
});
