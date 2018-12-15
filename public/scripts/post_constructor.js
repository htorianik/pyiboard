window.addEventListener('load', () => {
    document.getElementById('submit-button').addEventListener('click', ()=>{

        const parent_post_id = get_query_arg('parent_post_id');
        const head = document.getElementById('head-field').value;
        const body = document.getElementById('body-field').value.replace (/[\n\r]/g, 'u[nl]').replace (/\s{2,}/g, 'u[nl]')

        if(parent_post_id == -1) {
            document.location.href = get_board_determinate_suffix() + 
                `/make_thread_post?head=${head}&body=${body}`;
        } else {
            document.location.href = get_board_determinate_suffix() + 
               `/make_post?head=${head}&body=${body}&parent_post_id=${parent_post_id}`;
        }

    });

    const uploadFile = (file) => {

        var data = new FormData();
        data.append('file', file);

        url_suffix = '';
        content_type = '';
        ext = file.name.split('.')[file.name.split('.').length - 1];

        fetch('/upload', {
            method: 'POST',
            body: data
        }).then(
            res => res.json()
        ).then(
            res => {
                console.log(res);
            }
        )
    }

    document.getElementById('file-field').addEventListener('change', ()=>{
        uploadFile(document.getElementById('file-field').files[0]);
    });
}); 