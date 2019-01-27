var files_to_attach = [];
var uploaded_files = undefined;

const updateUploadedFiles = () => {
    markup_to_append = "";
    for(var i = 0; i < files_to_attach.length; i++)
    {
        uploaded_file = files_to_attach[i];
        markup_to_append += `
        <div class=\'uploaded-file\'>
            <div class=\'uploaded-file-preview\'>
                <a href=\'${uploaded_file.file_path}\'><img src=\'${uploaded_file.preview_path}\'></a> 
            </div>
            <div></div>
            <div class=\'uploaded-file-info\'>
                ${uploaded_file.id}.${uploaded_file.ext} (${uploaded_file.info})
                <input class='delete-btn' type='button' value='Удалить' onclick='delete_file(${uploaded_file.id})'>
            </div>
        </div>
        `
    }
    uploaded_files.innerHTML = markup_to_append;
}

const delete_file = (id) => {
    element = files_to_attach.find(val => val.id == id);
    files_to_attach.splice(files_to_attach.indexOf(element), 1);
    updateUploadedFiles()
}

window.addEventListener('load', () => {

    var chosen_files = document.getElementById('chosen-files');
    var upload_btn = document.getElementById('upload-btn');
    var file_input = document.getElementById('file-input');
    uploaded_files = document.getElementById('uploaded-files');
    
    document.getElementById('submit-button').addEventListener('click', ()=>{
        const parent_post_id = get_query_arg('parent_post_id');
        const head = document.getElementById('head-input').value;
        const body = document.getElementById('body-input').value.replace (/[\n\r]/g, 'u[nl]').replace (/\s{2,}/g, 'u[nl]')

        ids_to_attach = files_to_attach.map(file => file.id)

        if(parent_post_id == -1) {
            document.location.href = get_board_determinate_suffix() + 
                `/make_thread_post?head=${head}&body=${body}&files=[${ids_to_attach}]`;
        } else {
            document.location.href = get_board_determinate_suffix() + 
               `/make_post?head=${head}&body=${body}&parent_post_id=${parent_post_id}&files=[${ids_to_attach}]`;
        }
    });

    const uploadFile = (file) => {
        var data = new FormData();
        data.append('file', file);
        fetch(`${get_board_determinate_suffix()}/upload`, {
            method: 'POST',
            body: data
        }).then(
            res => res.json()
        ).then(
            res => {
                if(res["Response"] == "OK")
                {
                    files_to_attach.push(res.file);
                    updateUploadedFiles();
                }
            }
        )
    }

    upload_btn.addEventListener('click', () => { 
        uploadFile(file_input.files[0]);
    });
}); 