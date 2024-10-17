if (window.location.href.includes("/inbox")) {
    console.log("You are in the Outlook inbox.")
    chrome.runtime.sendMessage({ inInbox: true});
} else {
    console.log("You are not in the OUtlook inbox.")
    chrome.runtime.sendMessage({ inInbox: false});
}