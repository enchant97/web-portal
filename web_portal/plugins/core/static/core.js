"use-strict";

const core__sleep = (delay) => new Promise((resolve) => setTimeout(resolve, delay));

/**
 * Setup a clock widget, starting a infinite loop for updating the display
 * @param {string} widget_id - The widgets outer element id
 */
async function core__clock_init(widget_id) {
    let time_display = document.querySelector(`#${widget_id} .core__clock_display .time`);
    let date_display = document.querySelector(`#${widget_id} .core__clock_display .date`);
    while (true) {
        core__clock_update(time_display, date_display);
        await core__sleep(1000);
    };
}

/**
 * Update the clocks display
 * @param {Element} time_display - The time element
 * @param {Element} date_display - The date element
 */
function core__clock_update(time_display, date_display) {
    let current_dt = new Date();

    let hour = current_dt.getHours().toString().padStart(2, "0");
    let minute = current_dt.getMinutes().toString().padStart(2, "0");
    let second = current_dt.getSeconds().toString().padStart(2, "0");
    time_display.innerText = `${hour}:${minute}:${second}`;

    let day = current_dt.getDate().toString().padStart(2, "0");
    let month = (current_dt.getMonth() + 1).toString().padStart(2, "0");
    let year = current_dt.getFullYear().toString();
    let date_text = `${day}-${month}-${year}`;
    // only update date if different
    if (date_display.innerText !== date_text) {
        date_display.innerText = date_text;
    }
}
