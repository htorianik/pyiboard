const get_board_determinate_suffix = () => {
    dirs = document.location.pathname.split('/')
    if(dirs[1] != 'board') {
        return null;
    }
    else
    {
        return `/board/${dirs[2]}`;
    }
}