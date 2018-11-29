window.addEventListener('load', () => {
    document.getElementById('submit-button').addEventListener('click', ()=>{
        const head = document.getElementById('head-field').value
        const body = document.getElementById('body-field').value
        document.location.href = get_board_determinate_suffix() + `/make_thread_post?head=${head}&body=${body}`;
    });
});