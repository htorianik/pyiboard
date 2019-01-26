window.addEventListener('load', () => {
    document.getElementById('login-button').addEventListener('click', ()=>{
        const login = document.getElementById('login-input').value
        const password = document.getElementById('password-input').value
        document.location.href = `/authentication?login=${login}&password=${password}`
    });
});