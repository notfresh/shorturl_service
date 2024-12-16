document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('jumperInput');
    const button = document.getElementById('jumpButton');

    const handleJump = () => {
        const inputValue = input.value.trim();
        if (inputValue) {
            const url = `https://jumper.pub/${inputValue}`;
            chrome.tabs.create({ url });
            window.close();
        }
    };

    // 点击按钮时跳转
    button.addEventListener('click', handleJump);

    // 按回车键时跳转
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleJump();
        }
    });

    // 按ESC键关闭窗口
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            window.close();
        }
    });

    // 自动聚焦到输入框
    input.focus();
}); 