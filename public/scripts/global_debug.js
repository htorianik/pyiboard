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

const get_query_arg = (name) => {
    const UrlParams = new URLSearchParams(window.location.search);
    return UrlParams.get(name);
}