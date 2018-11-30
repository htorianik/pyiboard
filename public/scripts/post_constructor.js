window.addEventListener('load', () => {
    document.getElementById('submit-button').addEventListener('click', ()=>{
        const parent_post_id = get_query_arg('parent_post_id')
        const head = document.getElementById('head-field').value
        const body = document.getElementById('body-field').value
        document.location.href = get_board_determinate_suffix() + 
            `/make_post?head=${head}&body=${body}&parent_post_id=${parent_post_id}`;
    });
});