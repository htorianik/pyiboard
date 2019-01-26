window.addEventListener('load', ()=>{
    document.getElementById('registration-button').addEventListener('click', ()=>{
        const login = document.getElementById('login-input').value
        const password_1 = document.getElementById('password-input-1').value
        const password_2 = document.getElementById('password-input-2').value
        
        document.location.href = `/register?login=${login}&password=${password_1}`
    });
});