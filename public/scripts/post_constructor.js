window.addEventListener('load', () => {

    const chosen_files = document.getElementById('chosen-files');
    var files_to_attach = []

    document.getElementById('submit-button').addEventListener('click', ()=>{

        const parent_post_id = get_query_arg('parent_post_id');
        const head = document.getElementById('head-field').value;
        const body = document.getElementById('body-field').value.replace (/[\n\r]/g, 'u[nl]').replace (/\s{2,}/g, 'u[nl]')

        if(parent_post_id == -1) {
            document.location.href = get_board_determinate_suffix() + 
                `/make_thread_post?head=${head}&body=${body}&files=[${files_to_attach}]`;
        } else {
            document.location.href = get_board_determinate_suffix() + 
               `/make_post?head=${head}&body=${body}&parent_post_id=${parent_post_id}&files=[${files_to_attach}]`;
        }

    });

    const uploadFile = (file) => {

        var data = new FormData();
        data.append('file', file);

        url_suffix = '';
        content_type = '';
        ext = file.name.split('.')[file.name.split('.').length - 1];

        fetch(`${get_board_determinate_suffix()}/upload`, {
            method: 'POST',
            body: data
        }).then(
            res => res.json()
        ).then(
            res => {
                if(res["Response"] == "OK")
                {
                    chosen_files.innerHTML += `<img class='file' src='${get_board_determinate_suffix()}/files/${res["filename"]}'>`;
                    files_to_attach.push(res["filename"].split('.')[0]);
                    console.log(files_to_attach)
                }
            }
        )
    }

    document.getElementById('file-field').addEventListener('change', ()=>{
        uploadFile(document.getElementById('file-field').files[0]);
    });
}); 