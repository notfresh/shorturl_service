chrome.commands.onCommand.addListener((command) => {
    if (command === 'toggle-feature') {
        console.log('Command received:', command);
        chrome.windows.create({
            url: 'popup.html',
            type: 'popup',
            width: 250,
            height: 150
        }, (window) => {
            if (chrome.runtime.lastError) {
                console.error(chrome.runtime.lastError);
            } else {
                console.log('Popup window created');
            }
        });
    } else if (command === 'open-jumper') {
        chrome.windows.getCurrent((currentWindow) => {
            const popupWidth = 350;
            const popupHeight = 200;
            
            const left = Math.round(currentWindow.left + (currentWindow.width - popupWidth) / 2);
            const top = Math.round(currentWindow.top + (currentWindow.height - popupHeight) / 2);

            chrome.windows.create({
                url: 'input.html',
                type: 'popup',
                width: popupWidth,
                height: popupHeight,
                left: left,
                top: top
            }, (window) => {
                if (chrome.runtime.lastError) {
                    console.error(chrome.runtime.lastError);
                } else {
                    console.log('Jumper input window created');
                }
            });
        });
    }
});