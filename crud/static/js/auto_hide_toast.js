setTimeout(() => {
    const successToastMessage = document.getElementbyId('toast-success')
    if(successToastMessage) {
        successToastMessage.style.display = 'none'
    }
}, 3000)