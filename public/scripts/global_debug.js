const get_board_determinate_suffix = () => {
    dirs = document.location.pathname.split('/')
    return `/${dirs[1]}`;
}

const get_query_arg = (name) => {
    const UrlParams = new URLSearchParams(window.location.search);
    return UrlParams.get(name);
}