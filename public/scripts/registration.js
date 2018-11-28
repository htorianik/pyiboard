window.addEventListener('load', ()=>{

    const url = new URL(document.location.href)
    const params = url.searchParams;
    console.log(params.get('register_err'))

    if(params.get('register_err'))
    {
        document.getElementById('register-err').style.visibility = true;
    }

    document.getElementById('login-button').addEventListener('click', ()=>{
        const login = document.getElementById('login-input').value
        const password_1 = document.getElementById('password-input-1').value
        const password_2 = document.getElementById('password-input-2').value

        if(password_1 != password_2)
        {
            document.getElementById('pass-eq-err').style.visibility = true;
        }

        document.location.href = `/register?login=${login}&password=${password}`
    });
});